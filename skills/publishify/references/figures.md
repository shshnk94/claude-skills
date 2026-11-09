# Research figures

Create figures that make the intended comparison easy to see, and that people enjoy looking at. Use Kieran Healy's *Data Visualization* (https://socviz.co/) as the main design reference, together with Tufte's principle that every drop of ink should show data or help read it.

Minimalism is not the goal. Tufte cares about beauty too: *The Visual Display of Quantitative Information*, ch. 9 ("Aesthetics and Technique"), and *Envisioning Information*, ch. 5 ("Color and Information": muted fields with small spots of intense colour). Stripping colour and structure until a figure is grey and flat is a failure, just as clutter is. Studies find that moderate embellishment and colour make charts more memorable without hurting accuracy (Bateman et al. 2010; Borkin et al. 2013).

Use the examples below as design precedents, not templates to copy blindly. Apply them in the user's plotting library. Do not switch languages or libraries just to match the book.

## Workflow

1. **Identify the question the figure should answer.** Write it down in one sentence (for example, "fine-tuned models beat zero-shot ones on every dataset"). Every later choice serves that comparison.
2. **Identify the data.** List the variables, units, groups, and any paired or repeated observations.
3. **Choose a plot that makes the comparison clear.**
   - Never use pie or donut charts; a sorted bar chart or dot plot works better. Never use 3D.
   - Use bars only for quantities anchored at zero, such as counts or correlations.
   - For comparing categories with short labels, vertical (grouped) bars are the default: they are the most familiar reading. Go horizontal only for long labels or many categories.
   - Dots with intervals suit means on an arbitrary scale. Don't switch to them, or to horizontal bars, just to remove a legend.
   - If the user has said which chart type they prefer, use it.
   - Order categories meaningfully: by value, or in a logical order such as condition or model size. Avoid alphabetical order unless it is the logical order.
   - If more than about 4 series overlap, use small multiples (facets).
   - When readers compare the same categories across many panels, put the categories on an axis rather than in a legend.
4. **Apply the design and colour rules below.** Give the figure a visual hierarchy: one clear entry point, emphasis where the story is, and context that recedes (light grey, thin lines).
   - Remove ink that carries no data: the panel border, the grey background, minor gridlines.
   - Keep faint major gridlines only if readers need to read off values.
   - Keep short, outward tick marks on axes that have a numeric scale.
   - Centre facet (strip) titles, set them in plain text, and drop the strip background.
5. **Render and inspect the figure** when tools are available.
6. **Deliver** the figure or the reproducible code the user asked for.

Use the available context. Ask a question only if missing information would materially change the plot or its interpretation.

Follow explicit user and venue requirements. Explain any requirement that would make the figure misleading.

## Design rules and worked examples

### Crowded trajectories
When many lines overlap:
- Split them into panels using a meaningful grouping variable.
- Use the same scales when readers need to compare magnitudes. Free scales only when the comparison is within each panel.
- Draw individual trajectories in light grey.
- Add a stronger group trend only when it answers the question.
- State the smoothing method if a smoother is used.

Example: country GDP trajectories, Chapter 4, Figures 4.2–4.4. https://socviz.co/groupfacettx.html

### Dual-axis comparisons
Do not overlay unrelated quantities using independently scaled y-axes. Instead:
- Use aligned panels to preserve the original units.
- Or, if relative change is the question, index both series to the same baseline and state the baseline.
- Add a separate difference panel when the difference is meaningful.
- Do not subtract quantities with incompatible units.

Example: S&P 500 and Monetary Base, Chapter 8, Figures 8.18–8.20. https://socviz.co/refineplots.html

### Summaries that hide variation
When distribution shape matters:
- Show the distribution instead of only a mean.
- Add reference lines for relevant summary values.
- Label those values beside the reference lines.
- Use comparable scales across panels.
- State any normalization that changes how heights are interpreted.

Example: GSS age distributions, Chapter 8, Figure 8.16. https://socviz.co/refineplots.html

### Redundant legends and direct labels
- Remove a colour or fill legend when axis labels already identify the same categories unambiguously.
- Prefer direct labels: put series names at the end of lines or next to point clusters, in the series colour. A legend makes the reader look back and forth.
- Keep a legend when it adds information not shown elsewhere, for example when colour identifies a category across several panels or groups. Place it where it doesn't crowd other text: in one row below the plot, or in empty panel space, never stacked directly on top of facet titles.
- A reference value that applies to each group (a baseline, a ceiling) can be a dashed line across the group rather than another bar. Give it a legend entry or a label.

Example: religious-preference bars, Chapter 4. https://socviz.co/groupfacettx.html

### Highlighting a subset
When a subset is the focus:
- Draw the remaining observations in subdued grey.
- Draw the focal observations above the background layer.
- Use stronger colours for the focal observations.
- Label only observations relevant to the question.
- Explain what the grey observations represent.
- Avoid overlapping labels.

Example: flipped counties, Chapter 8, Figures 8.10–8.13. https://socviz.co/refineplots.html

## Colour rules

Follow the colour guidance in Chapter 8: https://socviz.co/refineplots.html

- **Unordered categories:** start with an established qualitative palette that is rich but calm.
  - The default is **Paul Tol's "muted"** palette. It is colourblind-safe, and works for both bars and lines.
  - Alternatives: ColorBrewer Dark2 (more saturated), and Set2 (pale, best for large filled areas with few categories).
  - Okabe–Ito is a fallback. Its fills are loud, so reserve its strongest colours for highlights.
- **Use colour when it carries identity.** If colour lets the reader follow the same category across panels or groups, keep it, even if the axis also names the categories. Flattening every category to one colour removes that, and the figure goes flat.
- **Ordered magnitudes:** use a sequential palette, such as viridis or a ColorBrewer sequential palette.
- **Values around a meaningful midpoint:** use a diverging palette, and set the midpoint explicitly.
- **Highlighting:** use subdued grey for context, and for the reference or baseline condition, with stronger colours for the focal observations.
- **Consistency:** keep each category's colour the same across related figures, and across the paper and slide versions of a figure.
- **Purpose:**
  - Do not assign different colours merely to decorate marks.
  - Do not use more categories than the palette supports.
  - If categories become hard to distinguish, use panels, direct labels, shapes or line styles instead of adding more colours.
- **Check the colours:**
  - Simulate colour-vision deficiency and greyscale on the actual palette with `uv run ~/.claude/skills/publishify/scripts/check_palette.py <hex> <hex> ...`.
  - A figure that must work in greyscale, such as one for a journal printed in black and white, also needs shape, linetype or a direct label for each series.
  - Do not assume that a named palette guarantees distinguishability.
  - If colour checking is unavailable, say it was not checked.

## Statistical clarity

- Do not invent observations, sample sizes or uncertainty intervals.
- Label axes with plain-word variable names and units where applicable, for example "Response time (ms)" not "rt_ms".
- Keep tick labels readable and not rotated 90°. If labels are long, flip the axes.
- Define intervals precisely, such as "95% confidence intervals" or "±1 SE across 5 runs". Say this in the caption, not in the plot.
- **Show uncertainty consistently.**
  - If some series have intervals and others don't, an interval on only some of them looks like a difference in precision that isn't there.
  - Show intervals for all series or for none, and say in the caption or notes where the missing ones come from or why there are none.
- Preserve pairing and repeated-measure structure.
- State transformations, normalization and aggregation.
- Start quantitative bar-chart axes at zero.
- Do not change scales or omit observations to exaggerate a result.
- Don't change the data, the statistics, or which subset is plotted. If the analysis looks wrong, say so and leave it alone.
- Don't put conclusions in the figure, such as "Model X is best!". They belong in the text.

## Paper and presentation versions

For papers:
- Keep the detail needed to evaluate the result.
- Explain samples, transformations and intervals in the caption. No in-image title: the caption goes in the manuscript.
- Check readability at the intended publication size. See `venue_specs.md` for width and font size.

For presentations (see presentify's `slide_specs.md`):
- Emphasize one main comparison per figure.
- Split dense multipanel figures when needed.
- Increase label sizes for the intended display.
- Keep essential uncertainty and qualifications.

## Final checks

Before delivering, check:
- Does the figure answer the intended question?
- Are scales, units, transformations and intervals clear?
- Are comparable panels actually comparable?
- Are colours consistent and distinguishable?
- Are legends necessary and labels readable?
- Is any text clipped or overlapping?
- Does visual emphasis match the evidence?

Inspect the rendered figure when tools are available. Do not claim to have rendered, inspected or tested anything unless you actually did.

Provide the requested figure or code. Briefly explain consequential design choices and unresolved assumptions. Do not repeat this checklist in the response.

## Library cues

### Palettes
- **Tol muted** (default): `["#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499"]`. Pair light and deep members (for example `#88CCEE` and `#332288`) when two series must also separate in greyscale.
- **Set2** (fills): `["#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3", "#A6D854", "#FFD92F", "#E5C494", "#B3B3B3"]`
- **Dark2** (points and lines): `["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D", "#666666"]`
- **Okabe–Ito** (fallback): `["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]`
- **Grey** for context or a reference: `"#B0B0B0"` for fills and lines, `"#8C8C8C"` where it must read as a category.
- Set2 yellow (`#FFD92F`) and Set2 grey (`#B3B3B3`) are weak on white. Skip them unless you need 7 or more categories, and don't use Set2 grey for a category when grey already means context.

### plotnine (Python) and ggplot2 (R)
- **Theme:** start from `theme_classic()`, then:
  - `panel_grid_minor=element_blank()`
  - `panel_grid_major_x=element_blank()` for vertical-category plots
  - `strip_background=element_blank()`, with the strip text centred (the default `ha="center"`, so don't override it)
  - `legend_position="none"` when labelling directly
  - keep `axis_ticks` on numeric axes. On a categorical axis whose labels sit right at each group, ticks are optional.
- **Direct labels:**
  - Add a `geom_text` with `data=` filtered to the last x per series, plus `ha="left"` and some nudge. In R, `ggrepel::geom_text_repel()` is helpful if it's installed.
  - Expand the x scale so labels aren't clipped.
- **Vertical grouped bars:** `geom_col(position=position_dodge(width=w), width=w, color="white", size=0.15)`. The thin white outline keeps neighbouring bars apart. Add `geom_hline(yintercept=0)` when values can go below zero.
- **Intervals on bars:** `geom_errorbar(position=<the same dodge>, width=0.25)`, only when every series has one.
- **Reference line per group:** `geom_errorbar(aes(ymin="r", ymax="r", linetype="series"), data=reference, width=w + 0.1, linetype dashed)` draws a dashed segment across each group, and the linetype mapping gives it a legend entry.
- **Legend below the panels:** `theme(legend_position="bottom")` with `guides(fill=guide_legend(nrow=1))`.
- **Means on an arbitrary scale:** `geom_pointrange` is cleaner than `geom_bar` + `geom_errorbar`.
- **Sorting:** in plotnine, use `pd.Categorical(..., categories=order, ordered=True)`. In R, use `forcats::fct_reorder()`.
- **Font:** name it explicitly ("Times New Roman" or "Arial"), not a generic family. See `venue_specs.md`.
- **PDF fonts:** plotnine renders with matplotlib, so set `matplotlib.rcParams["pdf.fonttype"] = 42` before saving. Otherwise PDFs get Type 3 fonts, which some ACL checks reject.
- **Size and export:**
  - plotnine: `plot.save(path, width=w, height=h, units="in", dpi=600)`
  - ggplot2: `ggsave(path, plot, width = w, height = h, units = "in", dpi = 600)`
  - Set `base_size` in the theme so fonts match `venue_specs.md` at that physical size.

### matplotlib / seaborn
- **Spines:** remove them with `ax.spines[["top", "right"]].set_visible(False)`.
- **Range frames:** axis lines that span only the data range are a nice touch: `ax.spines["left"].set_bounds(ymin, ymax)`.
- **Direct labels:** use `ax.annotate(...)` at each line's last point, and drop `ax.legend()`.
- **Export:** `fig.set_size_inches(w, h)`, then `fig.savefig(path, bbox_inches="tight", dpi=600)`. Set `rcParams["pdf.fonttype"] = 42` so the fonts embed as editable text.
