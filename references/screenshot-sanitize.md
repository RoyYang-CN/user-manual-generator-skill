# Screenshot storyboard, capture, and privacy review

## Plan before selecting assets

For each language, list the screen states a new user must recognize: first-use/registration, navigation/settings, the main input/action screen, a progress or decision state if relevant, and the result they will inspect. Adapt this list to the product. A CLI may use terminal states instead of UI pages. Give each state a stable `visual_id` in the spec's `visual_plan`, and put the matching image near its explanatory step. A template header is an input example; a report preview is a result example. Neither substitutes for the application's run screen.

For output documentation, review every named file, report, and audit artifact. A list of file descriptions is not visually covered by one unrelated report screenshot. Use a verified sanitized excerpt near each relevant description, or mark the missing example explicitly. A reformatted excerpt or field map can explain data safely, but label it as an excerpt or diagram rather than a screenshot of the product or exported file.

## Capture the actual product safely

Prefer a fresh capture from the source or release named on the manual cover, with a disposable profile and synthetic or reviewed sample data. For desktop apps, an isolated user profile and a widget/window capture can avoid exposing personal configuration. Verify that fonts render correctly; some offscreen Qt backends omit CJK fonts. For web apps, a local/test deployment with synthetic data is usually easiest. Capture interaction states only after the expected state appears. Never create demo records in production merely to take screenshots.

Keep the product's true UI structure. Do not generate an imitation of the app screen or composite several states into a fake operational screenshot. Record the capture source, build/revision, language, state, and whether the data is synthetic. A historical asset may be included as an example, but label it as historical when it differs from the documented build.

## Review the raster and the final page

Review the complete image, including chart labels, legends, table cells, paths, emails, keys, order IDs, coordinates, and customer identifiers. Use synthetic data and recapture when possible. If masking is necessary, inspect the final pixels; changing HTML text does not remove data already in a bitmap. Preserve enough application chrome to orient the reader, while keeping the control or result legible at the manual's actual width.

Reject or recapture images with clipped tooltips, open menus covering the target, missing fonts, unreadable labels, or excessive blank space. Portrait screens and tall reports are valid when they remain readable at the actual HTML display width. Do not treat successful image loading, a high pixel count, or a small file size as visual quality proof.

If a required screen cannot be captured safely or accurately, record the gap and label the draft visually incomplete. Do not quietly replace it with a template crop or unrelated output preview.
