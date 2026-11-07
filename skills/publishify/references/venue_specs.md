# Venue specs for figures

Set the figure's physical size to its final print size, and set font sizes for that size. Then nothing gets scaled in the manuscript, and the text in the figure matches the paper.

## ACL (two-column A4 template)
| Placement | LaTeX | Width | Typical height |
|---|---|---|---|
| One column | `figure` + `\includegraphics[width=\columnwidth]` | **3.03 in** (7.7 cm) | 2.0–2.5 in |
| Both columns | `figure*` + `\includegraphics[width=\textwidth]` | **6.3 in** (16 cm) | 2.0–3.0 in |

- **Format:** vector PDF. Add a PNG at 300 dpi only if the plot has more than about 10k points; in that case rasterize only the points layer if the library allows it.
- **Font:** Times, to match the paper. Use 8–9 pt for tick labels and 9 pt for axis titles. Never go below 7 pt.
  - Name the font explicitly. Generic `"serif"` often resolves to DejaVu Serif, not Times.
  - In plotnine, `theme(text=element_text(family="Times New Roman", size=8))`. Check that it resolves with `matplotlib.font_manager.findfont("Times New Roman")`.
  - In ggplot2, `theme_classic(base_size = 8, base_family = "Times New Roman")` and save with `device = cairo_pdf`, which embeds system fonts. If the font isn't found, try `"Times"`.
- **Captions** go in LaTeX, below the figure. Print a suggested `\begin{figure}...\end{figure}` snippet with `\caption{}` and `\label{fig:<stem>}` for the user.
- Prefer one column unless the figure needs the width. Space in ACL papers is scarce, and an 8-page limit is typical.

## APA 7th edition (Word or Google Docs manuscript)
- **Size:**
  - Use **6.5 × 3.5 in**, the full text width on Letter paper with 1 in margins, for multi-panel figures or more than about 3 series.
  - Use **4.5 × 3 in** for a single simple panel, where a full-width figure would look sparse.
  - Many journals reformat figures anyway, so the goal is clean and readable.
- **Format:** **PNG at 600 dpi** to insert into Word or Google Docs. Google Docs can't embed PDFs, and Word treats them poorly. Also export a **PDF** (vector) for journal submission systems.
- **Font:** sans-serif (Arial, Helvetica, or Calibri), 8–14 pt at print size. Use about 10 pt for axis titles and 9 pt for tick labels.
  - Name the font explicitly. Generic `"sans-serif"` often resolves to DejaVu Sans.
  - In plotnine, use `family="Arial"`.
  - In ggplot2, use `base_family = "Arial"` with `device = cairo_pdf` for the PDF.
- **Inside the image there's no figure number and no title.** APA puts "**Figure 1**" in bold and the title in italic Title Case **above** the figure, in the manuscript text. A "*Note.*" goes below it. Print these lines for the user to paste.
- Keep any legend inside the image, but direct labels are still preferred. Use the same font in all figures in the paper.
- Many psychology journals print in greyscale, and colour alone won't survive that. Okabe–Ito orange, sky blue and grey turn into nearly the same grey. Encode every series redundantly: colour plus shape or linetype, or a direct label.

## File naming
Save to `artifacts/figures/<script_stem>_<venue>.<ext>`, relative to the project root, for example `artifacts/figures/03_fig_accuracy_acl.pdf`. Create the folder if it's missing.
