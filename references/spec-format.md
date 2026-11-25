# Manual JSON spec

The renderer accepts a UTF-8 JSON object:

```json
{
  "product": "Example Pro",
  "version": "v1.2",
  "source_revision": "git abc123",
  "source_kind": "source draft",
  "product_type": "gui",
  "image_root": ".",
  "languages": {
    "cn": {
      "title": "使用说明书",
      "subtitle": "从数据导入到结果复核",
      "notice": "以源码为依据，尚未验收发行包。",
      "visual_plan": [
        {"id": "start-screen", "purpose": "让读者找到第一步操作界面"}
      ],
      "chapters": [
        {
          "id": "start",
          "title": "启动与授权",
          "blocks": [
            {"type": "html", "content": "<p>打开程序并选择输入文件。</p>"},
            {"type": "image", "role": "ui-page", "visual_id": "start-screen", "path": "demo/screen.png", "alt": "演示数据界面", "caption": "独立演示环境中的实际界面。", "origin": "isolated UI capture", "ui_language": "cn", "version": "v1.2"}
          ]
        }
      ]
    }
  }
}
```

- `image_root` is resolved relative to the JSON spec file unless it is an absolute path. Every image must exist below that root. The renderer rejects path traversal and remote image sources.
- `product_type` is `gui` or `cli`. GUI manuals require a nonempty `visual_plan` in each selected language. Write it before selecting assets; each planned `id` must be covered by exactly one image block with the same `visual_id`. Do not shrink the plan merely to make generation pass.
- Plan output examples separately when the guide names several artifacts. Put each example next to its file description; if a sanitized example is unavailable, note that gap in the content. The plan checker enforces IDs supplied by the author, so final editorial review must still catch omitted files.
- `languages` may define `cn` and `en`. The default command writes one HTML file per language. Each selected language needs complete `title`, `chapters`, unique chapter IDs, and nonempty content.
- `html` blocks allow basic paragraphs, headings, lists, details, code, tables, local fragment links, and explicit HTTPS links that open only when clicked. Scripts, remote image/style resources, embedded images, event handlers, and unsupported tags are removed. Use `image` blocks for all figures.
- Every image block requires `role` (`ui-page`, `ui-interaction`, `input-example`, or `result-example`), `alt`, `caption`, `origin`, `ui_language`, and `version`; UI roles also require `visual_id`. If the UI language differs from the manual language, explain that in the caption. The renderer accepts PNG and JPEG with matching file signatures and readable dimensions. It does not judge image composition: manually check legibility, obstruction, blank areas, and accuracy. Portrait images are allowed. `source_revision` and `source_kind` appear on the cover.
- `notice` is shown prominently for a source draft, old release, or any other material validation boundary.
- `--language` is a comma-separated selection of `cn` and `en`; the default is `cn,en`, producing two independent offline HTML files.
