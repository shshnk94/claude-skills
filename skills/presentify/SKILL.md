---
name: presentify
description: Turn research results (CSV tables and plotting scripts) into slides for a talk, collected in one 16:9 PowerPoint deck (.pptx). Tables become native, editable PowerPoint tables. Figures are re-rendered from their source script as large-font PNGs in the paper figure's colours. Slides are neutral by default (descriptive titles, no story emphasis) so the user can add their own narrative; emphasis and takeaway titles only when the user states the story. Details cut for legibility go into the speaker notes. Use this whenever the user wants results, a table or a figure "for slides", "for a talk", "for a presentation", "for lab meeting", "for a poster or keynote", or "in PowerPoint / Google Slides / Keynote", or wants to simplify a paper figure or table for an audience, even if they don't say "presentify". For journal or conference paper formatting, use publishify instead.
argument-hint: "[deck=<name>] <file.csv | script.py | image.png from script.py> ... [template=<deck.pptx>] [svg]"
---

# presentify

A paper reports everything; a slide shows one artifact large and legible enough to read from the back of the room. **The story is the user's**: make clear, neutral slides they can narrate and emphasise later, and add emphasis only where they ask. Everything you cut for legibility still matters, so it goes into the speaker notes for Q&A rather than being lost.

Requires the publishify skill next to this one (`~/.claude/skills/publishify/scripts/table_format.py` is imported for number formatting and the integrity check).

## 1. Parse the request
The user lists every artifact in one prompt, in slide order. All of them go into **one deck**.
- `*.csv` is a **table slide**.
- `script.py` / `script.R` (or `.qmd`, `.Rmd`, `.ipynb`), or `<image> from <script>`, is a **figure slide**.
- A **bare image with no script**: don't search the project for its source. That costs a lot of time and tokens for an uncertain match. Collect all such images and ask **one** question: "Which scripts make these: …?"
- `deck=<name>` sets the deck name. It defaults to the project folder's name. The deck is `<root>/artifacts/slides/<name>.pptx`, where the project root is the nearest folder upward with `.git`, `pyproject.toml`, `renv.lock`, `*.Rproj` or `README.md`.
- **Output paths are fixed.** If the request names another output location, including a brief from a coordinating agent (for example `results/presentation/`), still write under `<root>/artifacts/slides/` and say so in the report.
- `template=<path.pptx>`: start a new deck from the user's template (its theme, fonts and layouts).
- `svg`: also export figures as SVG.

Read only the paths given (plus the CSV a script reads, if you need it to understand the plot).

## 2. Slide titles and notes, once for the whole deck
**Don't infer the story.** The user decides which result is the headline, and may not have decided yet. For each artifact, draft:
- a **descriptive title** naming what is shown ("Assessment accuracy by memory mechanism and outcome"), stating no finding
- a **cut list**: what is dropped for legibility (rows, metrics, decimals, panels), and what moves to the speaker notes

If the user states a story, claim or titles in the request, follow `references/slide_storytelling.md` for those slides instead: a takeaway title and emphasis on what they named.

Ask at most one round of questions, and only when needed: the question about bare images (§1) and any warning about an old previous-version block (§4.1). Otherwise build without asking.

## 3. Table slides
1. Write a slide spec. It uses publishify's column format (`source`, `label`, `decimals`, `leading_zero`, `bold_best`, `thousands_separator`) plus:
   - `keep_rows`: raw values of the **first column listed in the spec's `columns`** (not necessarily the CSV's first column), in display order. Use it to keep about 4–6 rows.
   - `highlight_rows`: raw values in that same column for rows to emphasise. These get an accent colour, bold text and a light fill. **Leave it empty unless the user names the rows** (or states a claim about them); then highlight every row the claim is about.
   - `row_labels`: an optional map from a raw value to its display name, for example `{"Fine-tuned_BERT": "Fine-tuned BERT"}`.
   - `font_size`: defaults to 24 for tables of 5 rows or fewer and 20 for longer ones. Never below 18.
2. Keep 3–4 columns. Use the fewest decimals that show the differences honestly: enough to show a real difference, but don't add decimals that turn a tie into a fake gap. Use plain-word headers, and no *SD* or *p* columns. If a qualifier matters ("Mean of 3 seeds; all differences p < .01"), put it in the slide `footer`.
3. If the CSV is long-form or needs pivoting, write a reshaped CSV to the scratchpad. Never edit the source.
4. Values are only selected and rounded, never changed. `build_deck.py` runs publishify's integrity check on the cells that are shown.

## 4. Figure slides
Read `~/.claude/skills/publishify/references/figures.md` (the shared design guide) and `references/slide_specs.md`. Then edit the named script **in place**, even if asked to work on a copy: the slide variant lives next to the publication variant, and a copy drifts from it.
1. **Previous-version block.** Copy the script's current full text into a comment block at the very end of the file:
   ```
   # ---- publishify: previous version (saved YYYY-MM-DD, before slides edit) ----
   # <each line prefixed with "# ">
   # ---- end previous version ----
   ```
   - Find an existing block by its first line, which starts with `# ---- publishify: previous version`. It ends with `# ---- end previous version ----`. Both skills use these markers, so either skill replaces the other's block and there is only ever one.
   - The old block's own text is left out of the copy.
   - For `.ipynb` files, use a final markdown cell.
   - **Before replacing an existing block, check it.** Does it hold a save call or output path (for example `_acl.pdf`) that the current code no longer has? Then that code exists nowhere else, and replacing the block would delete it for good. Add it to the step 2 question ("The old block holds the ACL save, which the current code lacks. Restore it, or let it go?") and act on the answer.
2. **Add a slide variant next to anything that's already there.** Keep any publishify venue styles and saves, and don't remove their outputs. Build the slide version from the same data and plot object, with:
   - a `style_for_slides()` (plotnine) or `theme_slides()` (ggplot2) function
   - the paper figure's colours for every series: no greying out and no accent series unless the user asks
   - legibility-only changes from `slide_specs.md`: larger fonts, thicker lines, direct labels or a large legend, and splitting panels only when they can't be read at slide size
   - intervals when the paper version shows them (on every series)
   - no in-image title
3. **Save** at the placement size: by default **12.3 × 5.4 in at 300 dpi**, so about 3700 × 1600 px. Save to `<root>/artifacts/slides/figures/<script_stem>_slide.png`, plus `.svg` if asked.
4. **Check.** Run the script with the project's runner (`uv run` or `Rscript`). Look at the PNG and fix crowding or small text, then go through the final checks in `figures.md`. Make sure the publication outputs still get produced.

Data, filtering and statistics stay the same. Grey that is part of the data (for example, people below an inclusion cutoff) stays. Any series dropped for legibility is listed in the report.

## 5. Build the deck
1. Write one manifest to the scratchpad, with the slides in the user's order:
   ```json
   {
     "template": null,
     "slides": [
       {"type": "table", "source": "artifacts/tables/model_results.csv",
        "csv": "artifacts/tables/model_results.csv",
        "title": "Fine-tuned BERT matches the 7B LLM at a fraction of the size",
        "footer": "Accuracy on held-out test set (N = 1,200)",
        "notes": "Full results with F1 and CIs: paper Table 2. ...",
        "spec": {"keep_rows": ["Majority", "GPT-style 7B", "Fine-tuned_BERT"],
                 "highlight_rows": ["Fine-tuned_BERT"],
                 "columns": [{"source": "model", "label": "Model"},
                             {"source": "acc", "label": "Accuracy", "decimals": 2}]}},
       {"type": "image", "source": "analysis/03_fig_accuracy.py",
        "image": "artifacts/slides/figures/03_fig_accuracy_slide.png",
        "title": "Fine-tuned LLM leads at every training size",
        "notes": "Error bars are 95% CIs. BERT and LogReg are also shown in the paper version."}
     ]
   }
   ```
   - `source` identifies the slide. For tables, use the CSV path. For figures, use the **script path**, even when the user wrote `<image> from <script>`, because the slide image is re-rendered from the script. All paths are relative to the project root.
   - When you re-run with the same deck, a slide whose `source` matches is replaced in place. New sources are added at the end, and slides the user made by hand are left alone.
2. Build the deck **from the project root**, so that relative paths in the manifest resolve:
   ```bash
   cd <root> && uv run ~/.claude/skills/presentify/scripts/build_deck.py <manifest.json> artifacts/slides/<deck>.pptx
   ```
3. Preview every slide and look at the PNGs. Check that:
   - titles fit in 2 lines or fewer
   - the table fills a good share of the space
   - the highlight is on the right row
   - nothing overlaps or runs off the slide

   ```bash
   uv run ~/.claude/skills/presentify/scripts/preview_deck.py <deck.pptx> <scratchpad>/preview/
   ```
   It is an approximate render without theme fonts. It shows positions, sizes, bold, fills and alignment, but the user's PowerPoint has the final say.
4. **Report:**
   - the deck path
   - each slide's number, title, what was cut, and what's in its notes
   - any legibility choices (dropped rows, series or panels) the user may want to undo

## Principles
- One artifact per slide; the user decides the message. Don't infer a story or emphasise one result over another unless asked.
- Never change numbers. Only select, round and (when asked) emphasise.
- Batch every question into one round, and don't search the project when the user can just tell you.
