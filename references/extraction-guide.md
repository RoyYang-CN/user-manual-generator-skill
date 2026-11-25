# Extracting facts for a customer manual

Choose one authority: current source, a specific binary, or a deployed service. Record its version or commit. A README can supply context and wording, but confirm numeric limits, menu labels, file names, and workflow against the chosen authority. If the README and source disagree, report the mismatch; do not silently pick whichever sounds better.

Inspect only the product-facing paths needed for the manual:

- Desktop: entrypoint, menu/navigation labels, dialogs, templates, import/export handlers, configuration and licensing UI.
- Web: routes, page labels, forms, user-visible states and API behavior that affects the workflow.
- CLI: `--help`, command definitions, flags, configuration and sample output.

For long repositories, search headings and relevant symbols before opening large files. Capture the order a customer actually follows: start, configure, provide data, run, inspect output, recover from common errors.

Build a small evidence table before authoring:

| Claim | Source path or observed screen | Version | Status |
|---|---|---|---|
| Import file size limit | parser configuration | commit hash | source verified |
| Export button creates a file | observed UI | release build | runtime verified |

Use status labels such as `source verified`, `runtime verified`, `release verified`, and `unknown`. Do not turn source-level checks into end-to-end acceptance. For data or license rules, describe what the user sees and the practical limit. Avoid embedding credentials, customer data, private paths, or real order identifiers in the manual or its JSON spec.
