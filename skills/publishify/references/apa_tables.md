# APA 7th edition tables

Use these rules when building the spec JSON for `scripts/csv_to_apa_docx.py`.

## Layout (the script handles these)
- **Table number** in bold on its own line ("Table 2"). The **title** goes below it in italic Title Case. Both are double-spaced.
- Use **horizontal lines only**: above the column headings, below the headings, under spanners, and at the bottom. There are no vertical lines and no lines between body rows.
- The first column (row labels) is left-aligned. Numeric columns are centered. Keep the same number of decimals within a column so the decimals line up.
- **Note** goes below the table, starting with italic "*Note.*". Order: general note, then specific notes, then the probability legend.
- Use Times New Roman 12 pt unless the manuscript uses another APA font (Calibri 11, Arial 11, Georgia 11).
- Show missing cells as an em dash (—). Use a true minus sign (−) for negative numbers.

## Number formatting (your decisions in the spec)
- **Leading zero:** drop it (`"leading_zero": false`) for statistics that cannot exceed 1. These include *p*, *r*, β (standardized), α, *R*², η², and proportions such as accuracy, F1 and AUC. Keep it (the default) for values that can exceed 1, such as *M*, *SD*, *t*, *F*, *d*, *B*, and *SE*.
  - If a column is a proportion but you're not sure the user reports it that way (for example, accuracy as 0.81 or as 81%), ask.
- **Decimals:** usually 2. Use 3 for *p* values when needed to show *p* < .001 cases, though the APA preference is to report exact *p* to 2–3 decimals. Use 0 for counts (*N*, *df* when it's a whole number). Use `"thousands_separator": true` for counts ≥ 1,000.
- **Statistical symbols** in headers are italic: write `*M*`, `*SD*`, `*p*`, `*r*`, `*N*`, `*t*`, `*F*`, `*df*`. Greek letters are not italic. The script italicises text wrapped in `*`.
- **Significance stars:** add `"stars_from": "<p column>"` to the column that carries the estimate, and set `"significance_note": true`. Drop the raw *p* column from `columns` if the stars replace it. The thresholds are fixed at .05, .01 and .001.
- **Bolding the best value** is uncommon in APA. Use `bold_best` only if the user asks, and then explain it in the note ("Best values in bold.").

## Content
- The title should be brief and describe the contents ("Descriptive Statistics for Study Variables"), not the finding.
- Headers should be plain words, not variable names: `acc_mean` becomes "Accuracy", and `rt_ms` becomes "RT (ms)".
- Explain every abbreviation in the general note ("RT = response time.").
- Use `row_group` (a CSV column) for grouped rows such as conditions or model families. Use `spanners` for a heading that covers several columns, such as *M* and *SD* under "Study 1".
- Use `"landscape": true` only when the table has more than about 7 columns.

## Spec reference
```json
{
  "table_number": 1,
  "title": "Descriptive Statistics for Study Variables",
  "note": "RT = response time.",
  "significance_note": true,
  "row_group": "condition",
  "spanners": [{"label": "Study 1", "columns": ["m1", "sd1"]}],
  "landscape": false,
  "font": "Times New Roman",
  "font_size": 12,
  "columns": [
    {"source": "variable", "label": "Variable"},
    {"source": "m1", "label": "*M*", "decimals": 2},
    {"source": "sd1", "label": "*SD*", "decimals": 2},
    {"source": "r", "label": "*r*", "decimals": 2, "leading_zero": false, "stars_from": "p"}
  ]
}
```
Column keys: `source` (CSV column, required), `label`, `decimals`, `leading_zero`, `thousands_separator`, `stars_from`, `bold_best` (`"max"` or `"min"`). Only CSV columns listed in `columns` appear in the table, in that order. The `row_group` column becomes heading rows rather than a column, so leave it out of `columns`.
