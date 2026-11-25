"""Behavior checks for the public HTML renderer."""

import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_manual.py"
SPEC = importlib.util.spec_from_file_location("render_manual", SCRIPT)
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


def png_chunk(kind, payload):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


def portrait_png(width=390, height=844):
    row = b"\0" + b"\x4a\x85\xc5" * width
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(row * height))
        + png_chunk(b"IEND", b"")
    )


class RendererTests(unittest.TestCase):
    def test_fictional_cli_generates_separate_offline_languages(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--spec", str(ROOT / "examples" / "cli-manual.json"),
                 "--out-dir", temp],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            files = sorted(Path(temp).iterdir())
            self.assertEqual([p.suffix for p in files], [".html", ".html"])
            self.assertIn("HTML", result.stdout)
            cn = next(p for p in files if p.stem.endswith("_cn")).read_text(encoding="utf-8")
            en = next(p for p in files if p.stem.endswith("_en")).read_text(encoding="utf-8")
            self.assertIn("开始使用", cn)
            self.assertIn("Get started", en)
            self.assertIn("synthetic-fixture-v1", cn + en)
            self.assertNotIn("Get started", cn)
            self.assertNotIn("开始使用", en)
            self.assertNotIn("<script", cn + en)
            rejected = subprocess.run(
                [sys.executable, str(SCRIPT), "--spec", str(ROOT / "examples" / "cli-manual.json"),
                 "--out-dir", temp, "--pdf"],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("unrecognized arguments", rejected.stderr)

    def test_portrait_gui_image_and_relative_root(self):
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            image_dir = spec_dir / "images"
            image_dir.mkdir()
            (image_dir / "screen.png").write_bytes(portrait_png())
            payload = {
                "title": "使用说明书", "subtitle": "手机示例", "notice": "合成界面测试。",
                "visual_plan": [{"id": "start", "purpose": "找到启动界面"}],
                "chapters": [{"id": "first", "title": "开始", "blocks": [{
                    "type": "image", "role": "ui-page", "visual_id": "start",
                    "path": "screen.png", "alt": "合成竖屏", "caption": "合成测试图。",
                    "origin": "synthetic fixture", "ui_language": "cn", "version": "fixture v1",
                }]}],
            }
            spec = {
                "product": "Phone Example", "version": "v1", "source_revision": "fixture v1",
                "source_kind": "synthetic test", "product_type": "gui",
                "image_root": "images", "languages": {"cn": payload},
            }
            html = RENDERER.render(spec, "cn", spec_dir)
            self.assertIn("data:image/png;base64,", html)
            self.assertIn('href="#cn-first"', html)
            with self.assertRaisesRegex(ValueError, "spec directory"):
                RENDERER.render(spec, "cn")
            (image_dir / "wrong.jpg").write_bytes(portrait_png())
            bad = dict(payload["chapters"][0]["blocks"][0], path="wrong.jpg")
            with self.assertRaisesRegex(ValueError, "extension and file content disagree"):
                RENDERER.image_html(bad, image_dir, "cn")
            (spec_dir / "outside.png").write_bytes(portrait_png())
            escape_root = dict(bad, path="../outside.png")
            with self.assertRaisesRegex(ValueError, "out-of-root"):
                RENDERER.image_html(escape_root, image_dir, "cn")

    def test_only_explicit_https_links_survive(self):
        rendered = RENDERER.safe_html(
            '<p><a href="https://example.com/help?q=1&amp;x=2">Help</a>'
            '<a href="javascript:alert(1)">Bad</a><img src="https://example.com/pixel.png"></p>'
        )
        self.assertIn('href="https://example.com/help?q=1&amp;x=2"', rendered)
        self.assertIn('rel="noopener noreferrer"', rendered)
        self.assertNotIn("javascript:", rendered)
        self.assertNotIn("pixel.png", rendered)
        self.assertNotIn("<img", rendered)


if __name__ == "__main__":
    unittest.main()
