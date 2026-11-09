# Slide figure specs

## Size and format
- The deck is 16:9 (13.333 × 7.5 in). The content area under the title is about **12.3 × 5.4 in**.
- Render the figure **at the size it will occupy**, so text sizes are true and nothing gets rescaled.
  - Full content area: 12.3 × 5.4 in.
  - Half-width figure, for a figure next to text: 6 × 5.4 in.
- **PNG at 300 dpi** is the default (about 3700 × 1600 px for full width). It looks the same in PowerPoint, Google Slides and Keynote, and stays sharp on 4K projectors. Never upscale an existing image: re-render from the script.
- **SVG** only when asked. Insert it in PowerPoint if you want to recolour it later. Google Slides can't import SVG, Keynote handles it poorly, and text may switch font on machines without that font.

## Text
Text must be readable from the back of the room. These sizes are at print size:
- Tick labels **16 pt** or more, axis titles **18 pt**, direct labels **18–20 pt**.
- Use a sans-serif font, named explicitly ("Arial" or "Helvetica"). Generic "sans-serif" may resolve to DejaVu Sans.
- No in-image title, because the slide title goes above the figure. Keep axis titles short, with units.
- No legend box. Label series directly at the line end or next to the point cluster, or put the categories on an axis. When bars are grouped and direct labels would crowd them, a borderless legend under the plot at 18 pt is fine (two rows if one doesn't fit).

## Ink and colour
- Use a thick line (**1.5–2 pt**, plotnine `size=1.5` or ggplot2 `linewidth = 1.2`) and big points (about 3–4).
- **Use the paper figure's colours for every series.** Don't grey out series or add accents to tell a story: the user decides the story and adds emphasis later (see `slide_storytelling.md`, which applies only when the user gives one).
- Grey is for context that is part of the data, such as people below an inclusion cutoff, not for series the story is less about.
- Section strip titles are bold, as in the paper version. Reference lines are mid-grey (`#8C8C8C`) and dashed, about 1.2 pt, so they guide the eye without outranking the bars.
- A category keeps one colour across the paper and every slide. Don't recolour a series per slide: if blue means one model on one slide, it can't mean another model on the next. Projectors wash out pale colours, so if a paper colour is very light, use a deeper member of the same palette for that category everywhere (see `figures.md`).
- If the figure has no paper version yet, pick colours with the colour rules in `figures.md` and check them with `check_palette.py`.
- Remove gridlines, or keep only very light major ones if the audience needs to read values. Remove the panel border.
- Show CIs or error bars when the paper version does, and give the values in the speaker notes. If shown, show them on every series (see "Show uncertainty consistently" in `figures.md`) and make them light (alpha ~0.25 ribbons) so the means stand out.
- Projectors wash out pale colours. Avoid yellow (`#F0E442`) and light pastels for anything important.

## Code cues
- **plotnine:**
  - Theme: `theme_classic(base_size=18, base_family="Arial")`, then `theme(legend_position="none", axis_line=element_line(size=0.8))`.
  - Save: `plot.save(path, width=12.3, height=5.4, units="in", dpi=300)`.
  - If you also save an SVG, set `matplotlib.rcParams["svg.fonttype"] = "none"` so the text stays editable.
- **ggplot2:**
  - Theme: `theme_classic(base_size = 18, base_family = "Arial") + theme(legend.position = "none")`.
  - Save: `ggsave(path, plot, width = 12.3, height = 5.4, units = "in", dpi = 300)`. For SVG, use `device = svglite::svglite` if it's installed.
- **Direct labels:** add a text layer on the last x value per series, coloured to match its series. Expand the right side of the x-axis by about 0.15–0.25 of the data range at 12.3 in wide, so labels aren't clipped and no big empty strip is left. Check the PNG and trim it if there is one.
- **Emphasis (only when the user asks for it):** map colour through a manual scale, where context series get grey and the named series keep their paper colours. Don't create new data columns that change values; a helper column like `is_key_series` is fine.
