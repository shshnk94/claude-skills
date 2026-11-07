# ACL (*ACL, EMNLP, NAACL, TACL-style) tables

Use these rules when building the spec JSON for `scripts/csv_to_acl_latex.py`. The output is a LaTeX snippet. The user pastes it, or `\input{}`s it, into a paper that uses the official ACL template (`acl.sty`, two columns on A4).

## Layout (the script handles these)
- Use `booktabs` rules only (`\toprule`, `\midrule`, `\bottomrule`, `\cmidrule` under spanners). There are no vertical lines and no `\hline`.
- `\small` inside the float. Don't use `\resizebox` to squeeze a table: it shrinks fonts unevenly, and reviewers notice.
- The **caption goes below the table**, as in the ACL template. Then `\label{tab:...}`.
- The first column is left-aligned. Numeric columns are right-aligned, with equal decimals within each column so they line up.
- Negative numbers are typeset as `$-$`, missing cells as `--`, and stars as superscripts.
- The only package needed is `booktabs`. The snippet says so in its first line.

## Your decisions in the spec
- **Width:** a single column is about 7.7 cm wide (3.03 in). If the table has more than about 5 numeric columns, or row labels longer than about 25 characters, set `"wide": true`. That uses `table*`, which spans both columns (16 cm).
- **Bold the best result** per metric column (`"bold_best": "max"`, or `"min"` for error rates, perplexity and loss). This is the NLP convention. Ties are all bolded. If the table has a baseline group, mention bolding in the caption only if it isn't obvious.
- **Decimals:** match the precision the paper reports elsewhere. Usually 1 decimal for percentages (81.2) and 2–3 for proportions. Keep leading zeros (`leading_zero` stays true), because ACL papers don't follow the APA convention, except for *p* and *r* if the user prefers.
- **Header symbols:** use `"label_latex"` for math, such as `"$\\Delta$ F1"`, `"$\\uparrow$ Acc."` or `"$\\rho$"`. Plain `label` text is escaped automatically. `*x*` in `label` becomes `\textit{x}`.
- **Caption:** the title becomes the first sentence. A `note` is appended as further sentences, followed by the star legend if `significance_note` is true. ACL captions describe what's shown and how to read it, for example "Best results in bold. ↑ higher is better." They're more informative than APA titles.
- **Label:** `tab:<short_name>` built from the CSV stem, for example `tab:main_results`.
- **Row groups:** use `row_group` for model families or datasets. Each group gets an italic heading row and a `\midrule` between groups.

## Spec reference
```json
{
  "title": "Results on the test set",
  "note": "Mean over 3 seeds. Best results in bold.",
  "label": "tab:main_results",
  "wide": false,
  "row_group": "family",
  "spanners": [{"label": "SST-2", "columns": ["sst_acc", "sst_f1"]}],
  "columns": [
    {"source": "model", "label": "Model"},
    {"source": "sst_acc", "label": "Acc.", "decimals": 1, "bold_best": "max"},
    {"source": "sst_f1", "label": "F1", "decimals": 1, "bold_best": "max"}
  ]
}
```
