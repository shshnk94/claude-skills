# claude-skills

My Claude Code skills for turning research results into publication and presentation artifacts, plus my global `CLAUDE.md` (coding and communication preferences).

## Skills

**publishify**: makes publication-ready tables and figures for APA 7th edition (psychology; Word or Google Docs) or ACL (NLP; LaTeX).
- A CSV becomes an APA `.docx` table or an ACL booktabs `.tex` table.
- A plotting script (Python or R) is edited in place following a design guide based on Healy's [*Data Visualization*](https://socviz.co/) and Tufte (`references/figures.md`), plus the venue's size, font and format specs. The previous version is kept as one comment block at the end of the file.
- `scripts/check_palette.py` checks a palette under simulated colour-vision deficiency and greyscale.
- Outputs go to `artifacts/tables/` and `artifacts/figures/`.

```
/publishify apa results/tables/model_fit.csv
/publishify acl analysis/03_fig_accuracy.py
```

**presentify**: turns tables and figures into slides for a talk, all in one 16:9 `.pptx` deck.
- Each slide gets a takeaway title and only the detail the story needs. Everything cut goes into the speaker notes.
- Tables become native, editable PowerPoint tables. Figures are re-rendered from their script as 300 dpi PNGs at slide size.
- Re-running with the same deck updates those slides in place and leaves hand-made slides alone.

```
/presentify deck=lab_meeting artifacts/tables/results.csv artifacts/figures/fig.png from analysis/03_fig.py
```
presentify imports publishify's `scripts/table_format.py`, so install both.

## Install on a machine
```bash
git clone https://github.com/<user>/claude-skills ~/claude-skills
~/claude-skills/install.sh
```
`install.sh` symlinks `skills/*` into `~/.claude/skills/` and `claude/CLAUDE.md` to `~/.claude/CLAUDE.md`. If a real file or folder is already in the way, it is renamed to `*.bak-YYYYMMDD`, not deleted. Re-running the script is harmless.

Requirements:
- [`uv`](https://docs.astral.sh/uv/). Each script declares its own Python dependencies, so you don't install any yourself.
- `pandoc` and `latexmk`, which are only used for checking outputs.
- Whatever your figure scripts use: plotnine, or R with ggplot2.

## Update and improve
Because `~/.claude` points into this repo, any edit to a skill, by you or by Claude, is an edit here.
```bash
cd ~/claude-skills && git add -A && git commit -m "..." && git push   # publish changes
cd ~/claude-skills && git pull                                       # get changes on another machine
```
New skills go in `skills/<name>/`. Run `install.sh` again to link them.
