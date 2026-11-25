# User Manual Generator Skill

**Turn working software into a user guide customers can actually follow.** This open Agent Skill helps an AI agent write source-checked software user manuals for desktop apps, web products, and command-line tools. It produces separate Chinese and English HTML files that open offline, with reviewed screenshots and practical examples of inputs and results.

The goal is a usable operating guide: what the product does, who it helps, how to complete the main workflow, what the output means, and what to do when a step fails.

## The problem it addresses

Shipping a working product does not automatically give customers a useful manual. Common gaps are:

| Pain point | How this skill responds |
| --- | --- |
| The README, source, and released app describe different versions or limits. | Choose one source of truth and mark each important claim as source, runtime, or release verified. |
| Screenshots show the wrong page, an obsolete UI, or customer data. | Plan screenshots by user step, capture with synthetic or reviewed data, and inspect the final pixels. |
| A guide lists output files but never shows what users should look for. | Place a relevant, labeled example beside each important file or state; state gaps when no safe example exists. |
| A translated guide omits steps or changes technical meaning. | Review the Chinese and English versions independently against the same product evidence. |
| HTML renders successfully, but the guide is still hard to use. | Check navigation, image readability, captions, phone layout, and the full user journey before calling it ready. |

These checks help readers find the right controls and interpret results. They do not substitute for testing the product itself.

## What you get

- Two independent, self-contained HTML files by default: one Chinese (`cn`), one English (`en`). You can request just one language.
- A customer-facing structure covering purpose, first use, main workflow, outputs and limits, data handling, and common failures. Adapt the chapters to the product.
- Local PNG/JPEG screenshots embedded in the HTML, with captions that distinguish a real interface capture from a sanitized example or a field diagram.
- A small Python renderer that checks image paths and file signatures, visual-plan IDs, and navigation anchors. Explicit HTTPS links remain clickable; scripts and remote image/style assets are not included.

**How much is automatic?** The agent investigates the chosen product version, drafts the content, and reviews the images. `scripts/render_manual.py` only turns an *already reviewed* JSON spec into HTML. It does not inspect a repository, translate prose, take screenshots, or prove a release works on its own.

## Use with an AI agent

The repository follows the [Agent Skills `SKILL.md` format](https://agentskills.io/specification). Place this folder in the skill directory supported by your agent, keeping the folder name `user-manual-generator-skill`. Installation paths and tool permissions vary by agent. The renderer needs Python 3.9+ and access to local product files.

Example request to your agent:

> Use `user-manual-generator-skill` to create separate Chinese and English HTML user guides for this product version. Verify the main workflow and rules against the selected source or release. Use only synthetic or reviewed screenshots, show important output examples, and label anything that has not been runtime tested.

For a real product, follow [SKILL.md](SKILL.md). The [JSON format](references/spec-format.md), [fact extraction guide](references/extraction-guide.md), and [image review guide](references/screenshot-sanitize.md) provide details when needed.

## Try the renderer

The included spec describes a **fictional CLI product** so that you can test the renderer without using private product data:

```text
python scripts/render_manual.py --spec examples/cli-manual.json --out-dir .temp/demo
```

The command writes `Example_CLI_v0.1_cn.html` and `Example_CLI_v0.1_en.html`. To render one language, add `--language cn` or `--language en`. Images in a real spec can use paths relative to that JSON file.

Run the behavior checks with `python -m unittest discover -s tests -v`. The renderer uses only the Python standard library. Its output is a documentation draft until someone verifies the claims, images, and user steps against the intended product build.

## Scope

This skill creates **product user manuals and user guides as offline HTML**. It does not generate a repository `README.md`, PDF, or developer architecture documentation. The MIT license covers this skill and renderer, not software documented with it.

The skill format is intended for agents that support `SKILL.md` and can access local files. So far, the full workflow has been tested in Codex on Windows; compatibility with other agents has not yet been independently verified.

---

## 中文介绍

**让“软件能运行”变成“客户看得懂、照着能操作”。** 这个通用 Agent Skill 面向桌面软件、网页产品和命令行工具，帮助智能体编写中英两份独立的离线 HTML 使用说明书。它关注产品做什么、解决什么问题、用户怎样完成主要操作、结果怎么看，以及遇到问题如何处理。

实际痛点往往不在排版：README 与发行版规则不一致；截图用错版本或泄露客户数据；说明书列了输出文件却不给示例；英文版遗漏步骤；网页虽然生成成功，用户仍找不到下一步。本技能要求先确定被说明的版本，逐步核对事实，为操作与结果规划图片，检查脱敏，并实际查看最终 HTML 的导航、图片和手机排版。

默认分别输出中文和英文 HTML，也可只输出一种语言。图片会嵌入文件，方便离线查看。**渲染器只负责把已审阅的 JSON 变成网页**；分析源码或发行包、编写内容、翻译、截屏和验收仍由智能体按技能流程完成，不能把“成功生成文件”当作产品验证通过。

本仓库采用通用的 [Agent Skills 格式](https://agentskills.io/specification)。把文件夹放到所用智能体支持的技能目录，并保持目录名为 `user-manual-generator-skill`。运行渲染脚本需要 Python 3.9+ 和本地文件访问权限；不同智能体的安装位置与权限设置可能不同。目前完整流程在 Windows 上的 Codex 环境通过验证，其他智能体尚待独立实测。

可运行上面的虚构 CLI 示例查看输出；真实项目请从 [SKILL.md](SKILL.md) 开始。此技能生成产品使用说明书，不生成项目 README、PDF 或开发架构文档。MIT 许可只覆盖本技能，不覆盖被说明的产品。
