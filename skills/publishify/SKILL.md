---
name: publishify
description: Turn research results into publication-ready tables and figures for APA 7th edition (psychology journals; Word or Google Docs manuscripts) or ACL (NLP conferences; LaTeX). Given a CSV, it produces an APA-formatted .docx table or an ACL booktabs .tex table. Given a plotting script (Python or R), it edits the script in place to follow Healy's Data Visualization (socviz) and Tufte's principles and the venue's size, font and format specs, and keeps the previous version as a comment block. Use this whenever the user wants to make a table or figure "publication-ready", "camera-ready", "APA style", "ACL style", "for the paper" or "for the manuscript", or points at a results CSV or figure script and mentions a journal, conference, Word, LaTeX or Overleaf, even if they don't say "publishify".
argument-hint: "<apa|acl> <path to .csv or figure script>"
---

# publishify

The goal is to get from a pipeline output to an artifact that can be pasted into a manuscript in one pass. Make sensible formatting decisions yourself, show them briefly, and ask only when a choice changes the meaning of what's shown.

## 1. Parse the request
- **Venue:** `apa` or `acl`. If it's not given and you can't tell from context (Word or Google Docs or a psychology journal means APA; LaTeX, Overleaf or an *ACL, EMNLP or NAACL conference means ACL), ask once.
- **Input:** a `.csv` file is a table (§2). A `.py`, `.R`, `.qmd`, `.Rmd` or `.ipynb` file is a figure (§3).
- **Project root:** the nearest folder upward with `.git`, `pyproject.toml`, `renv.lock`, `*.Rproj` or `README.md`. Otherwise use the current directory. All outputs go under `<root>/artifacts/`. Never write into `results/` or `data/`.
- **Output paths are fixed.** If the request names another output location, including a brief from a coordinating agent (for example `results/figures/publish/`), still write under `<root>/artifacts/` and say so in the report.

## 2. Tables (CSV → .docx or .tex)

1. Read the venue's reference file first: `references/apa_tables.md` or `references/acl_tables.md`.
2. Look at the CSV (`head`, dtypes, value ranges) so you know what each column is: counts, proportions, *p*-values, means and so on.
3. Write a spec JSON to the scratchpad. Its format is in the reference file. Choose labels, decimals, leading zeros, stars, spanners, row groups, the title and the note.
   - Values that are long-form (one row per model × metric) need pivoting first. In that case, pivot with pandas into a new CSV in the scratchpad. Never edit the source CSV.
4. Show the user a compact summary of the spec: the title, the columns with their labels and decimals, and anything non-obvious. Ask only about real ambiguities, such as a proportion that might be reported as a percentage, or which direction is "best". Otherwise proceed.
5. Run the script. It checks row counts and checks that numbers only changed by rounding. It refuses to overwrite an existing file unless you pass `--overwrite`, and you should do that only if the user agrees.
   ```bash
   uv run ~/.claude/skills/publishify/scripts/csv_to_apa_docx.py <csv> <spec.json> <root>/artifacts/tables/<csv_stem>_apa.docx
   uv run ~/.claude/skills/publishify/scripts/csv_to_acl_latex.py <csv> <spec.json> <root>/artifacts/tables/<csv_stem>_acl.tex
   ```
6. Check the result:
   - **APA:** run `pandoc <out>.docx -t markdown` to see the structure.
   - **ACL:** compile the snippet in the scratchpad inside a minimal doc. The doc is `\documentclass{article}\usepackage[T1]{fontenc}\usepackage{booktabs}\begin{document}\input{<out>}\end{document}`. Compile with `latexmk -pdf`. Then look at the PDF if you can render it.
7. Report the output path and say how to use it.
   - **APA:** open the .docx in Word, or upload it to Google Drive and open it with Google Docs, then copy the table into the manuscript.
   - **ACL:** `\input{}` the file or paste it, and add `\usepackage{booktabs}`.
   - If you changed the spec, offer to save it next to the output as `<csv_stem>_<venue>.spec.json`, so the table can be regenerated when results change.

## 3. Figures (edit the plotting script in place)

Read `references/figures.md` (the design guide: workflow, worked examples, colour rules, statistical clarity, final checks) and `references/venue_specs.md` first. The user's `~/.claude/CLAUDE.md` coding rules apply to the code you write:
- descriptive names
- no dense one-liners
- short comments that explain why
- match the existing style
- plotnine and ggplot2 are the defaults, but stay in whatever library the script already uses

1. **Check whether this is a first or a later run.** The script has been through publishify before if it already contains a `publishify: previous version` block or saves into `artifacts/figures/`.
   - **First run:** use the figure the script already produces as the before image. If it doesn't exist, run the script with the project's own runner (`uv run`, or `Rscript` from the project root) to make it. Look at it.
   - **Later run:** the before image is the existing artifact. If the new venue is different, the script already has a publishify design for another venue. Keep that design and its save, and add the new venue (see step 4).
2. **Plan the changes.** Follow the workflow in `figures.md`: state the figure's question in a sentence, then choose the plot, design and colours that make that comparison clear. Change presentation only:
   - **Allowed:**
     - choosing which quantities the script already computes to show (for example, CIs that were computed but not plotted)
     - changing scales, such as log axes, if you say so in the axis title
     - ordering, faceting, colours and labels
     - hiding intervals that only some series have, so uncertainty is shown consistently (say so in the caption)
   - **Not allowed:** new calculations, different filtering or aggregation, and dropping data points.
   - List every judgment call, such as a log scale or an added CI layer, in the final report so the user can veto it.
3. **Keep the previous version.** Copy the script's current full text, before your edit, into a comment block at the very end of the file:
   ```
   # ---- publishify: previous version (saved YYYY-MM-DD, before <venue> edit) ----
   # <each original line, prefixed with "# ">
   # ---- end previous version ----
   ```
   - `<venue>` is the venue of the edit you're making now. The block holds whatever the code was just before that edit.
   - If the file already has a publishify block, **replace it** with the new one, so there is only ever one. The old block's own text is left out of the copy.
   - Find an existing block by its first line, which starts with `# ---- publishify: previous version`, and its last line, `# ---- end previous version ----`. presentify writes the same markers.
   - **Before replacing an existing block, check it.** Does it hold a save call or output (for example, another venue's save, or a presentify slide save) that the current code no longer has? Then replacing the block deletes that code for good. Ask the user whether to restore it first.
   - The user wants one source of truth plus a local before/after diff. They don't want history piling up. Earlier versions are the job of git or editor history.
   - For `.ipynb` files, put the block in a new markdown cell at the end of the notebook, with the old code in a fenced code block.
4. **Edit the plotting code in place.**
   - Set the exact size, fonts and formats from `venue_specs.md`. Save to `<root>/artifacts/figures/<script_stem>_<venue>.{pdf,png}`. ACL needs PDF. APA needs PNG at 600 dpi plus PDF.
   - On the first run, replace the old save call, for example the one writing to `results/`. It's still visible in the comment block.
   - **Several venues in one script:** build the plot once. Put each venue's styling (theme, fonts, size) in a small function, for example `style_for_acl(plot)` and `style_for_apa(plot)` or `theme_acl()` and `theme_apa()`. Save once per venue. Adding a venue must not remove an existing venue's output, and that includes a slide variant (`style_for_slides` or `theme_slides`) added by presentify.
   - Create the output folder in code with `Path(...).mkdir(parents=True, exist_ok=True)` or `dir.create(..., recursive = TRUE, showWarnings = FALSE)`.
5. **Run the edited script and look at the after image** at print size. To view a PDF, first convert it to an image with `pdftoppm -r 300 -png -singlefile <pdf> <scratch_prefix>`.
   - Fix clipped or overlapping labels, unreadable fonts and wasted space, then re-run.
   - Check that fonts are embedded and are not Type 3 by running `pdffonts <pdf>`. The type column should say TrueType or Type 1.
   - Check the palette you used with `uv run ~/.claude/skills/publishify/scripts/check_palette.py <hex> ...`. If pairs are too close under a colour-vision simulation, separate them with labels, shapes or panels, or swap a colour.
   - Go through the final checks in `figures.md`.
   - If the script fails, fix it. Don't hand back a broken script.
6. **Report:**
   - a short list of what changed and why, covering only the consequential design choices and any unresolved assumptions (don't repeat the checklist)
   - the palette check result, or that it wasn't run
   - the output paths
   - for ACL, a ready-to-paste `\begin{figure}[t] ... \caption{} \label{fig:<stem>} \end{figure}` snippet
   - for APA, the "**Figure N**" and *Title* lines to place above the image, and a *Note.* line if it's needed. Leave "N" as a placeholder unless the user gave the number.

## Principles
- Never change the numbers. Rounding in tables and visual encoding in figures are the only transformations. If something in the data or analysis looks off, mention it and leave it alone.
- Don't overwrite existing artifacts without asking, and never edit raw data.
- Keep the user's time in mind: one round of brief confirmation at most, then deliver.
