# Improving a figure with Tufte's principles

The core idea (Tufte, *The Visual Display of Quantitative Information*): every drop of ink should show data or help read data. Remove what doesn't, and make the comparison the reader needs as easy as possible. Work through the checklist below in order. Not every item applies to every plot. Skip what doesn't fit, and don't add decoration to "use" a principle.

## Checklist

1. **What is the one comparison?** Before editing, write down in one sentence what the figure should let the reader see (for example, "fine-tuned models beat zero-shot ones on every dataset"). Each later choice serves that comparison.
2. **Right chart type.**
   - No pie or donut charts: use a sorted bar chart or dot plot instead.
   - No 3D.
   - No dual y-axes: use two aligned panels instead.
   - Bars only for counts or quantities that start at zero. For means with CIs, a dot with an error bar is usually cleaner than a bar.
3. **Maximize data-ink, erase non-data ink.**
   - Remove the panel border, the grey background, the minor gridlines, and the axis tick marks if the labels alone are clear.
   - Keep only faint major gridlines, and only if readers need to read off values. Otherwise drop them.
   - A range frame (axis lines that span only the data range) is a nice touch. It's easy in matplotlib (`spines[...].set_bounds`) and in R (`ggh4x::guide_axis_truncated()` if installed). plotnine has no simple recipe, so skip it there.
4. **Label directly, drop the legend.** Put series names at the end of lines or next to point clusters, in the series colour. A legend makes the reader look back and forth.
5. **Order meaningfully.** Sort categories by value, or in a logical order such as condition or model size. Avoid alphabetical order unless it is the logical order.
6. **Small multiples over clutter.** If more than about 4 series overlap, facet them with shared axes. Keep scales fixed across facets unless the comparison is within each facet.
7. **Show variability honestly.** Show CIs or SEs when the data has them, and state which one it is in the caption, not the plot. Start bar axes at zero. Don't truncate axes to exaggerate differences.
8. **Colour with purpose.**
   - Use grey for context and one or two accent colours for the comparison.
   - Use a colourblind-safe palette: Okabe–Ito for categories, viridis for continuous values.
   - The figure must still work in greyscale, and colour alone won't do it: several Okabe–Ito colours turn into the same grey. Always pair colour with shape or linetype, or label directly.
9. **Words.**
   - Axis titles are plain words with units, for example "Response time (ms)" not "rt_ms".
   - Tick labels are readable and not rotated 90°. If labels are long, flip the axes instead.
   - No in-image title: the caption goes in the manuscript.
10. **Readable at print size.** See `venue_specs.md` for width and font size. Check by viewing the exported file at 100%.

## Library cues

### plotnine (Python) and ggplot2 (R)
- Start from `theme_classic()` (or `theme_minimal()` with grid tweaks), then:
  - `panel_grid_minor=element_blank()`
  - `panel_grid_major_x=element_blank()` for vertical-category plots
  - `axis_ticks=element_blank()` if not needed
  - `legend_position="none"` when labelling directly
- Direct labels: add a `geom_text` with `data=` filtered to the last x per series, plus `ha="left"` and some nudge. In R, `ggrepel::geom_text_repel()` is helpful if it's installed. Expand the x scale so labels aren't clipped.
- Okabe–Ito palette: `["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]`. For one accent plus context, use `"#0072B2"` with `"#B0B0B0"`.
- Means with CIs: `geom_pointrange` (plotnine and ggplot2) rather than `geom_bar` + `geom_errorbar`.
- Sorting: in plotnine, use `pd.Categorical(..., categories=order, ordered=True)`. In R, use `forcats::fct_reorder()`.
- Name the font explicitly ("Times New Roman" or "Arial"), not a generic family. See `venue_specs.md`.
- plotnine renders with matplotlib, so set `matplotlib.rcParams["pdf.fonttype"] = 42` before saving. Otherwise PDFs get Type 3 fonts, which some ACL checks reject.
- Size and export: in plotnine, use `plot.save(path, width=w, height=h, units="in", dpi=600)`. In ggplot2, use `ggsave(path, plot, width = w, height = h, units = "in", dpi = 600)`. Set `base_size` in the theme so fonts match `venue_specs.md` at that physical size.

### matplotlib / seaborn
- Remove spines: `ax.spines[["top", "right"]].set_visible(False)`. For range frames, use `ax.spines["left"].set_bounds(ymin, ymax)`.
- Direct labels: `ax.annotate(...)` at each line's last point, and drop `ax.legend()`.
- Export: `fig.set_size_inches(w, h)`, then `fig.savefig(path, bbox_inches="tight", dpi=600)`. Set `rcParams["pdf.fonttype"] = 42` so the fonts embed as editable text. Some ACL and APA checks want TrueType or Type 42 fonts, not Type 3.

## What not to do
- Don't change the data, the statistics, or which subset is plotted. Only change the presentation. If the analysis looks wrong, say so and leave it alone.
- Don't switch plotting libraries: stay in the script's library so it fits the project.
- Don't add annotations that state conclusions in the figure, such as "Model X is best!". That belongs in the text.
