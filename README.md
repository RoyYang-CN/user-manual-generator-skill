# Project Manual Generator

A Codex skill for writing customer-facing software manuals as two independent, offline HTML files: Chinese (`cn`) and English (`en`). It guides source and version checks, screenshot selection, privacy review, and final visual acceptance. The bundled Python renderer turns an **already reviewed** JSON spec into HTML; it does not inspect a product, translate prose, or capture screens by itself.

## Use

Copy this directory to your Codex skills directory (for example, `~/.codex/skills/project-manual-generator`) or keep it in a repository where Codex can load `SKILL.md`. Ask Codex to use `project-manual-generator` for a customer user guide and give it access to the product version you want documented.

Requires Python 3.9 or newer. The renderer uses only the Python standard library. Images must be local PNG or JPEG files. Output HTML embeds them, so each file can be opened offline. Explicit HTTPS links are retained and open only when a reader clicks them.

```text
python scripts/render_manual.py --spec examples/cli-manual.json --out-dir .temp/demo
```

This sample uses a **fictional CLI product** and creates separate `*_cn.html` and `*_en.html` files. It tests rendering; it is not evidence about a real product. For one language, add `--language cn` or `--language en`.

For a real product, first verify the chosen source, binary, or deployment and prepare screenshots with synthetic or reviewed data. Follow [SKILL.md](SKILL.md), the [JSON spec](references/spec-format.md), and the [image review guidance](references/screenshot-sanitize.md). A successful render does not prove that the manual's claims or images match the product.

Run the included checks with `python -m unittest discover -s tests -v`. The license covers this skill and renderer, not any product that a user documents with it.

## 中文说明

本技能用于编写面向客户的软件使用说明书，默认分别生成中文和英文两份可离线打开的 HTML。它要求核对产品版本、操作步骤、截图来源及脱敏情况。Python 脚本只负责把**已审阅的 JSON 内容**渲染成 HTML，不会自动分析产品、翻译或截屏。

需要 Python 3.9 或更新版本；渲染脚本仅使用标准库。上面的命令用虚构命令行产品验证输出。制作真实产品说明书时，请先核对源码、发行包或线上版本，并使用合成或已审阅的数据。测试命令为 `python -m unittest discover -s tests -v`。

MIT 许可证仅适用于本技能及其渲染脚本，不适用于使用本技能编写说明书的产品。
