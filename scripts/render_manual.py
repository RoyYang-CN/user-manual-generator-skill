#!/usr/bin/env python3
"""Render a reviewed JSON manual spec to separate offline CN and EN HTML files."""

import argparse
import base64
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import urlsplit


TAGS = {"p", "div", "span", "strong", "b", "em", "i", "br", "h3", "h4", "ul", "ol", "li", "code", "pre", "table", "thead", "tbody", "tr", "th", "td", "details", "summary", "a", "blockquote", "small"}
DROP = {"script", "style", "iframe", "object", "embed", "form", "input", "button", "select", "textarea", "svg", "img", "link", "meta"}
CSS = """
:root{--ink:#15263f;--muted:#586b83;--blue:#244bda;--line:#dce5f1;--paper:#fff;--bg:#f3f6fb}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.7 'Segoe UI','Microsoft YaHei',Arial,sans-serif}
.hero{padding:48px max(22px,calc((100vw - 1100px)/2));background:linear-gradient(115deg,#143271,#3159e3,#0aa4ca);color:#fff}
.hero h1{margin:0;font-size:clamp(28px,4vw,42px);line-height:1.25}.hero p{margin:12px 0 0}.meta{font-size:13px;opacity:.88}
.wrap{max-width:1100px;margin:auto;padding:26px 20px 70px}.notice{padding:14px 18px;background:#fff8e6;border-left:4px solid #df9817;border-radius:10px;margin-bottom:22px}
.toc{position:sticky;top:0;z-index:5;display:flex;gap:8px;overflow:auto;white-space:nowrap;padding:13px 15px;margin-bottom:28px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 7px 20px #153c6417}
.toc a{padding:5px 9px;border-radius:7px;color:#405473;text-decoration:none;font-size:13px}.toc a:hover,.toc a:focus-visible{background:#e8eeff;color:#2348cf}
.chapter{scroll-margin-top:75px;margin:30px 0 46px}.chapter h2{font-size:27px;margin:0 0 16px}.chapter-body{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px;box-shadow:0 9px 30px #1b3a6410}
.chapter-body h3{margin:25px 0 10px;color:#123f81}.chapter-body h3:first-child{margin-top:0}.chapter-body p{margin:10px 0}.chapter-body div{max-width:100%}
.chapter-body .grid,.chapter-body .grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.chapter-body .mini,.chapter-body .step{border:1px solid var(--line);border-radius:10px;padding:13px;margin:7px 0}.chapter-body .callout{padding:14px;border-left:4px solid var(--blue);background:#eff5ff;border-radius:8px;margin:12px 0}.chapter-body .warn{background:#fff7e8;border-color:#df9817}.chapter-body .danger{background:#fff0f0;border-color:#d33}.chapter-body .good{background:#edfaf4;border-color:#18a16d}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:9px 11px}th{background:#eef3fb}
.chapter-body .table-wrap{overflow-x:auto}pre{overflow:auto;background:#152239;color:#edf4ff;border-radius:9px;padding:14px}code{font-family:Consolas,monospace}figure{margin:24px 0;padding:12px;background:#fafcff;border:1px solid var(--line);border-radius:11px}figure img{display:block;width:100%;height:auto;border-radius:6px}figcaption{font-size:13px;color:var(--muted);padding:9px 3px 2px}.tag{display:inline-block;color:#36569c;background:#e9f1ff;border-radius:99px;padding:2px 8px;font-size:12px}
.footer{border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:13px}
@media(max-width:700px){.hero{padding:37px 17px}.wrap{padding:17px 12px 45px}.chapter-body{padding:16px}.chapter h2{font-size:23px}.toc{border-radius:8px}table{min-width:540px}}
"""


def esc(value):
    return html.escape(str(value), quote=True)


class SafeFragment(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.stack = []
        self.drop_depth = 0

    def handle_starttag(self, tag, attrs):
        if self.drop_depth:
            self.drop_depth += 1
            return
        if tag in DROP:
            if tag not in {"img", "input", "link", "meta"}:
                self.drop_depth = 1
            return
        if tag not in TAGS:
            return
        output_attrs = []
        for key, value in attrs:
            if key == "class" and value:
                clean = " ".join(re.findall(r"[A-Za-z0-9_-]+", value))
                if clean:
                    output_attrs.append(f' class="{esc(clean)}"')
            elif key == "href" and tag == "a" and value:
                if re.fullmatch(r"#[A-Za-z0-9_-]+", value):
                    output_attrs.append(f' href="{esc(value)}"')
                elif safe_https_link(value):
                    output_attrs.extend((f' href="{esc(value)}"', ' target="_blank"', ' rel="noopener noreferrer"'))
            elif key == "open" and tag == "details":
                output_attrs.append(" open")
            elif key in {"colspan", "rowspan"} and tag in {"th", "td"} and value and value.isdigit():
                output_attrs.append(f' {key}="{value}"')
        self.parts.append("<" + tag + "".join(output_attrs) + ">")
        if tag not in {"br"}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.drop_depth:
            self.drop_depth -= 1
            return
        if tag in self.stack:
            while self.stack:
                current = self.stack.pop()
                self.parts.append(f"</{current}>")
                if current == tag:
                    break

    def handle_data(self, data):
        if not self.drop_depth:
            self.parts.append(esc(data))

    def get_html(self):
        while self.stack:
            self.parts.append(f"</{self.stack.pop()}>")
        return "".join(self.parts)


def safe_html(content):
    parser = SafeFragment()
    parser.feed(content)
    return parser.get_html()


def safe_https_link(value):
    if any(char.isspace() or ord(char) < 32 for char in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def raster_dimensions(raw):
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24:
        return struct.unpack(">II", raw[16:24])
    if raw.startswith(b"\xff\xd8"):
        pos = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while pos + 4 <= len(raw):
            if raw[pos] != 0xFF:
                break
            while pos < len(raw) and raw[pos] == 0xFF:
                pos += 1
            if pos >= len(raw):
                break
            marker = raw[pos]
            pos += 1
            if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
                continue
            if marker == 0xDA or pos + 2 > len(raw):
                break
            length = struct.unpack(">H", raw[pos:pos + 2])[0]
            if length < 2 or pos + length > len(raw):
                break
            if marker in sof and length >= 7:
                height, width = struct.unpack(">HH", raw[pos + 3:pos + 7])
                return width, height
            pos += length
    return None


def image_html(block, root, language):
    for field in ("path", "role", "alt", "caption", "origin", "ui_language", "version"):
        if not block.get(field):
            raise ValueError(f"Image block missing {field}")
    role = block["role"]
    if role not in {"ui-page", "ui-interaction", "input-example", "result-example"}:
        raise ValueError(f"Unknown image role: {role}")
    if role.startswith("ui-") and not block.get("visual_id"):
        raise ValueError("UI image missing visual_id")
    relative = Path(block["path"])
    if relative.is_absolute():
        raise ValueError(f"Image path must be relative: {relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Missing or out-of-root image: {relative}")
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(path.suffix.lower())
    if not mime:
        raise ValueError(f"Unsupported image type: {path}")
    caption = block["caption"]
    if block["ui_language"] != language:
        lowered = caption.lower()
        if not any(term in lowered for term in ("英文", "中文", "english", "chinese")):
            raise ValueError(f"Cross-language image caption must explain UI language: {relative}")
    raw = path.read_bytes()
    if (mime == "image/png" and not raw.startswith(b"\x89PNG\r\n\x1a\n")) or (
        mime == "image/jpeg" and not raw.startswith(b"\xff\xd8")
    ):
        raise ValueError(f"Image extension and file content disagree: {relative}")
    dimensions = raster_dimensions(raw)
    if not dimensions or any(size <= 0 for size in dimensions):
        raise ValueError(f"Unreadable image dimensions: {relative}")
    data = base64.b64encode(raw).decode("ascii")
    return f'<figure><img src="data:{mime};base64,{data}" alt="{esc(block["alt"])}"><figcaption>{esc(caption)}</figcaption></figure>'


def validate_visual_plan(language, payload, product_type):
    plan = payload.get("visual_plan", [])
    if product_type == "gui" and not plan:
        raise ValueError(f"GUI manual missing visual_plan for {language}")
    planned = []
    for item in plan:
        ident = item.get("id", "")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident) or not item.get("purpose"):
            raise ValueError(f"Invalid visual plan item for {language}: {item}")
        planned.append(ident)
    if len(planned) != len(set(planned)):
        raise ValueError(f"Duplicate visual plan id for {language}")
    provided = [block.get("visual_id") for chapter in payload.get("chapters", [])
                for block in chapter.get("blocks", []) if block.get("type") == "image" and block.get("visual_id")]
    if len(provided) != len(set(provided)):
        raise ValueError(f"Duplicate visual_id in images for {language}")
    missing = set(planned) - set(provided)
    unknown = set(provided) - set(planned)
    if missing or unknown:
        raise ValueError(f"Visual plan mismatch for {language}: missing={sorted(missing)}, unplanned={sorted(unknown)}")


def render_chapters(language, payload, root):
    chapters = payload.get("chapters") or []
    if not chapters:
        raise ValueError(f"No chapters for {language}")
    ids = [str(ch.get("id", "")) for ch in chapters]
    if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident) for ident in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"Invalid or duplicate chapter id for {language}")
    nav = [f'<nav class="toc" aria-label="{esc(language)} chapters">']
    body = [f'<div lang="{"zh-CN" if language == "cn" else "en"}">']
    for number, chapter in enumerate(chapters, 1):
        ident = f'{language}-{chapter["id"]}'
        title = chapter.get("title")
        blocks = chapter.get("blocks") or []
        if not title or not blocks:
            raise ValueError(f"Empty chapter {ident}")
        nav.append(f'<a href="#{ident}">{number:02d} {esc(title)}</a>')
        body.append(f'<section class="chapter" id="{ident}"><h2>{number}. {esc(title)}</h2><div class="chapter-body">')
        for block in blocks:
            kind = block.get("type")
            if kind == "html":
                if not block.get("content"):
                    raise ValueError(f"Empty HTML block in {ident}")
                body.append(safe_html(block["content"]))
            elif kind == "image":
                body.append(image_html(block, root, language))
            else:
                raise ValueError(f"Unknown block type {kind!r}")
        body.append("</div></section>")
    nav.append("</nav>")
    body.append("</div>")
    return "".join(nav), "".join(body)


def validate_output(markup):
    ids = re.findall(r'\bid="([^"]+)"', markup)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate output IDs")
    missing = set(re.findall(r'href="#([^"]+)"', markup)) - set(ids)
    if missing:
        raise ValueError(f"Broken anchors: {sorted(missing)}")
    for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', markup):
        if not src.startswith("data:image/"):
            raise ValueError("Nonembedded image detected")
    if re.search(r'<(?:script|iframe)\b', markup, re.I):
        raise ValueError("External or active resource detected")
    for href in re.findall(r'<link\b[^>]*\bhref="([^"]+)"', markup, re.I):
        if href != "data:,":
            raise ValueError("External link resource detected")


def render(spec, mode, spec_dir=None):
    for key in ("product", "version", "source_revision", "source_kind", "product_type", "image_root", "languages"):
        if not spec.get(key):
            raise ValueError(f"Missing spec field: {key}")
    if spec["product_type"] not in {"gui", "cli"}:
        raise ValueError("product_type must be gui or cli")
    root = Path(spec["image_root"]).expanduser()
    if not root.is_absolute():
        if spec_dir is None:
            raise ValueError("Relative image_root requires the spec directory")
        root = spec_dir / root
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Image root does not exist: {root}")
    if mode not in {"cn", "en"}:
        raise ValueError(f"Unsupported language: {mode}")
    selected = [mode]
    if any(language not in spec["languages"] for language in selected):
        raise ValueError(f"Missing language content for {mode}")
    page_title = f'{spec["product"]} {spec["version"]} — {" / ".join(spec["languages"][l]["title"] for l in selected)}'
    chunks = ['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              f'<title>{esc(page_title)}</title><link rel="icon" href="data:,"><style>{CSS}</style></head><body>']
    first = spec["languages"][selected[0]]
    chunks.append(f'<header class="hero"><h1>{esc(spec["product"])} {esc(spec["version"])}</h1><p>{esc(first["subtitle"])}</p><p class="meta">{esc(spec["source_kind"])} · {esc(spec["source_revision"])}</p></header><main class="wrap">')
    for language in selected:
        payload = spec["languages"][language]
        if not payload.get("title") or not payload.get("subtitle") or not payload.get("notice"):
            raise ValueError(f"Missing title, subtitle, or notice for {language}")
        validate_visual_plan(language, payload, spec["product_type"])
        chunks.append(f'<div class="notice" lang="{"zh-CN" if language == "cn" else "en"}"><strong>{esc(payload["title"])}</strong><br>{esc(payload["notice"])}</div>')
        nav, body = render_chapters(language, payload, root)
        chunks.extend((nav, body))
    chunks.append(f'<footer class="footer">{esc(spec["product"])} · {esc(spec["version"])} · {esc(spec["source_revision"])}</footer></main></body></html>')
    output = "".join(chunks)
    validate_output(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--language", default="cn,en", help="cn, en, or cn,en")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    modes = [part.strip() for part in args.language.split(",")]
    if len(modes) != len(set(modes)) or any(mode not in {"cn", "en"} for mode in modes):
        parser.error("--language must select unique cn and/or en modes")
    spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for mode in modes:
        markup = render(spec, mode, args.spec.resolve().parent)
        stem = f'{re.sub(r"[^A-Za-z0-9_-]+", "_", spec["product"])}_{spec["version"]}_{mode}'
        html_path = args.out_dir / f"{stem}.html"
        html_path.write_text(markup, encoding="utf-8")
        print(f"HTML {html_path} ({html_path.stat().st_size} bytes)")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
