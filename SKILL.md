---
name: user-manual-generator-skill
description: Create source-checked customer user manuals and user guides for desktop, web, or CLI software. Use when users need step-by-step CN/EN offline HTML documentation with privacy-reviewed screenshots and output examples; not for repository README files or developer architecture docs.
license: MIT
metadata:
  short-description: Source-checked HTML user manuals for software
---

# User Manual Generator Skill

Create a manual that helps a user complete the product's actual workflow. The packaged renderer is self-contained and does not depend on another design skill.

## Inputs and evidence

1. Identify the exact source, release, or live deployment being documented. If these differ, label the manual with the chosen authority and do not claim runtime or release verification from source inspection alone.
2. Inspect the current UI/CLI, user-facing configuration, examples, and existing docs. Verify each operational step and numeric rule against the chosen authority. Record conflicts and unresolved behavior instead of copying old text as fact. See [extraction guide](references/extraction-guide.md) when source discovery is nontrivial.
3. Produce separate CN and EN HTML files by default. If the user explicitly requests one language, generate only that file. Each language must stand alone and reflect the same verified product version.
4. Before choosing image files, write a short visual storyboard for the actual user journey: which page or interaction state each image must prove, and which input/result examples are supplementary. For a GUI guide, include the entry or registration screen, the main action screen, and a meaningful result screen when those states exist. If the manual describes named output files in separate cards, plan an adjacent visual example for each file when a verified sanitized sample exists. If it does not, state the image gap beside that file; do not let a general report image imply that every listed output was illustrated. Do not count template headers or report previews as screenshots of the application UI. Add the storyboard as `visual_plan` in the JSON spec so missing planned states fail generation. See [screenshot guidance](references/screenshot-sanitize.md).
5. Capture the selected screens from the chosen product version with an isolated demo profile or reviewed synthetic data. Reuse an existing image only when its version, UI language, state and privacy are verified. Record `role`, `visual_id`, `origin`, `ui_language`, `version`, `alt` and `caption` for every image. Never substitute a missing screen with a different screen or present demo output as a live run.

## Content and rendering

Use the seven-chapter outline in [manual structure](references/manual-structure.md) as a starting point; combine or rename chapters for the product. Cover purpose, first use, navigation, main workflow, outputs and rules, data handling, and troubleshooting. State unknowns and edition-specific differences where readers will encounter them.

Author a UTF-8 JSON spec using [spec format](references/spec-format.md). Run the bundled renderer:

```text
python scripts/render_manual.py --spec path/to/manual.json --out-dir path/to/output
```

The renderer creates separate, offline CN and EN HTML files. It embeds reviewed local PNG/JPEG images, checks navigation anchors, visual-plan coverage, image signatures and paths, and permits only explicit HTTPS user links. It does not extract product facts, translate text, or capture screenshots; the JSON spec is an editorial input. Review every claim and image against evidence.

## Acceptance

- Open each HTML offline or through a localhost static server. Inspect every selected image at the actual manual display width, especially text legibility, clipped controls or tooltips, large empty areas, language agreement, caption accuracy, and whether the screenshot shows the intended state. Walk the text card by card: verify that named files have their own nearby example or an explicit gap label, and distinguish actual screenshots from reformatted source excerpts or field maps. The count of loaded images is only a technical check. If the visual storyboard is not fulfilled, report visual coverage as incomplete even if HTML validation passes.
- Verify that every requested language file opens offline, with working navigation, readable images, and no clipped content at desktop and phone widths. Check external links only when the user requested them.
- Report the exact source revision, tested output modes, verified items, unresolved items, and whether the result is a source draft or a release-verified customer guide.
- Keep generated files in an isolated output directory. Do not overwrite a release manual or publish it unless that action was requested.
