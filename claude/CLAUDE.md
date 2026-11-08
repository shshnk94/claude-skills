# Global Preferences

## About me
- Researcher at the intersection of AI and Psychology.
- My code is read by both ML/AI people and psychologists who may not be strong programmers. Write code, comments, and explanations both groups can follow.
- Briefly explain a statistical or ML concept only when it's non-obvious.
- I work in R and Python, mostly data analysis, statistical modeling, and ML experiments, often starting as quick POCs.
- I'm comfortable with the terminal.

## Communication
- Be concise. Lead with the answer, then the reasoning if needed.
- Give a recommendation, not a survey of options.
- If something is ambiguous and the choice matters, ask. Otherwise pick a sensible default and say what you chose.
- After code changes, briefly explain in chat what changed and why.

## Code modes
- POC / exploratory (default for scratch work): get it working quickly. Readability is nice but not required.
- Shared / published (when I say so, or the repo will be shared): follow the readability rules below strictly.
- If unsure which mode applies, ask once.

## Coding style
- Clean, readable code that is also reasonably efficient. Don't sacrifice one entirely for the other.
- Simple list comprehensions are good. Avoid complicated ones (nested, multiple conditions); use a plain loop instead.
- Avoid dense one-liners, chained ternaries, and heavy use of lambdas, decorators, or metaprogramming.
- Use descriptive names (`average_response_time`, not `art`). Keep functions short and single-purpose.
- Choose a less readable approach for speed only when it matters, and mention it in one sentence.
- Match the existing style of the project.

## Comments and docstrings
- Docstrings: yes, but simple, one or two plain sentences.
- Inline comments: only where the "why" isn't obvious. One short line, everyday words. Don't narrate what the code does.
- When code changes, update the existing comment to match. Don't append new comment lines on top of old ones.
- Don't add comments or docstrings to code I didn't ask you to change.
- No comments about the edit itself ("added", "fixed", "updated").

## Languages
Use the project's existing language. For a new project, follow my request or ask.

### Python
- Packages: `uv` (`uv add`, `uv sync`, `uv run`). Don't use `pip install` directly.
- Style: PEP 8. Format and lint with `ruff`.
- Analysis: `numpy`, `pandas`, `scipy`, `statsmodels` (regression, mixed models), `sklearn` (ML).
- Plotting: `plotnine` by default (mirrors `ggplot2`). Use `plotly` when I want interactive plots.
- Use `pathlib`, type hints on public functions, and `pytest` for tests.

### R
- Packages: `renv`. Run `renv::init()` in new projects and `renv::snapshot()` after adding packages.
- Style: tidyverse style guide (`snake_case`, `<-`, 2-space indents, lines under 80 characters). Format with `styler`, lint with `lintr`.
- Use the tidyverse (`dplyr`, `tidyr`, `readr`, `purrr`, `stringr`) over base R equivalents; tibbles, not data.frames.
- Plotting: `ggplot2`.
- Pipe: `%>%`, one step per line. Break long pipelines into named intermediate objects.
- Analysis: `lm`, and `lme4` for mixed-effects models.

## Project structure
For new projects, set up this layout (adapt if the project already has one):

    project/
    ├── data/
    │   ├── raw/          # original data, never edited
    │   └── processed/    # cleaned data produced by code
    ├── analysis/         # scripts/notebooks, numbered in run order (01_clean.R, 02_model.py)
    ├── results/
    │   ├── figures/
    │   └── tables/
    ├── artifacts/        # publication/presentation artifacts (/publishify, /presentify)
    │   ├── tables/
    │   ├── figures/
    │   └── slides/       # decks (.pptx) and slide figures
    ├── docs/             # notes, codebooks, drafts
    ├── README.md         # what the project is and how to run it
    └── .gitignore

- Add `data/` to `.gitignore` by default (data may be sensitive). Also ignore `.venv/`, `__pycache__/`, `renv/library/`, and `.Rproj.user/`.
- Set up the environment: `uv init` for Python, `renv::init()` for R. Set up git and GitHub as described in Version control.
- Put reusable functions in one module/file, not copied across scripts.
- Keep results reproducible: set random seeds and write outputs to `results/` from code.

## Workflow
- Read relevant files before editing. Make minimal, targeted changes.
- Run the code or tests to verify when possible; report failures honestly.
- Put throwaway files in a scratch/`tmp` folder, not the project root.
- For statistical analyses, state the model and key assumptions in plain language.

## Version control
- New projects: run `git init -b main`, make an initial commit (README.md, .gitignore, folder layout), then create a private GitHub repo with `gh repo create <folder-name> --private --source . --push`. Confirm the repo name with me first.
- After finishing a plan, or a self-contained piece of work, ask me whether to commit and push. Never commit or push on your own.
- When asking, show `git status` and a proposed commit message. If the changes cover unrelated things, propose splitting them into separate commits.
- Don't commit half-finished or broken work, throwaway files, or anything git-ignored (data, secrets, `.env`).
- Stage files by name; review `git diff --staged` before committing. Avoid `git add -A`.
- Push to `origin main` after committing, unless I say otherwise. Never force-push.

### Commit messages
- One line only, no body. Under 72 characters, no trailing period.
- Imperative mood, capitalised: "Add mixed model for reaction times", not "Added..." or "adding...".
- Say what changed and, if it fits, why: "Drop participants with <80% accuracy", not "Update script" or "Fix stuff".
- One logical change per commit.

## Parallel subagents
<!--
How to use (for human readers):
1. Explore and plan first (plan mode works well). Ask Claude to end the plan with an explicit task list.
2. Check that the tasks are independent. That's your job. If one task needs another's output, mark it as a dependency.
3. Say "run this task" or "run these tasks in parallel". Claude then runs one subagent per task.
A task can be anything: test a hypothesis, clean a dataframe, make a figure.
-->
Use only when I say "run this task" or "run these tasks in parallel".

### Planning
- When a plan has several independent pieces, end it with a numbered task list. For each task give: goal, type (`investigate` or `build`), the files or outputs it owns, and what it depends on.

### Coordinate
- The main conversation is the coordinator. Run the tasks from the list. Ask only if something is ambiguous enough to change the work.
- One subagent per task, at most 3 at a time. Run a task after the one it depends on, and run tasks that share files or other resources one after another.
- Subagents can't see our chat. Give each one its goal, the relevant findings from planning, file paths, constraints, and the files or outputs it owns.
- Every subagent follows the coding rules in this file.
- When a subagent runs a skill, don't override the skill's output paths or file handling in its brief.

### Investigate tasks (for example, test a hypothesis)
- Test it, don't assume it's true. State what evidence would support or contradict it.
- Prefer a small test that separates the competing explanations. Run it if feasible, and say clearly what was run versus only proposed.
- Record commands, parameters, seeds, and results. Keep observations separate from interpretation, in plain language.
- Report: supported, contradicted, or inconclusive, plus limitations. A failed run is inconclusive, not a disconfirmation.
- Don't change the main analysis code or implement a fix.

### Build tasks (for example, clean data, make a figure)
- Edit only the files the task owns. Two agents never edit the same file.
- Run the code to check it works. Report what changed, how you ran it, and any problems.
- Don't expand beyond the assigned task.

### Avoid interference
- Prefer read-only work for investigations. If source edits are needed in parallel, use a git worktree per agent (or a separate copy if there's no git).
- Each agent writes outputs only to its own folder, `results/<task_name>/`. Never overwrite existing results.
- Check for shared files, databases, or services before running in parallel.
- The Safety rules below still apply.

### Report back
- Give a short table: task, what was done or tested, evidence or files changed, result.
- For hypotheses, note whether more than one could be true, any conflicting evidence, and tests that don't discriminate. Recommend the next most informative test.
- For build tasks, check the outputs fit together (for example, the figure uses the cleaned data).
- Don't implement further changes unless I ask.

## Safety
- Ask before destructive or hard-to-reverse actions (deleting files, force-push, overwriting data).
- Never commit or push without my explicit OK (see Version control).
- Treat `data/raw/` as read-only.
