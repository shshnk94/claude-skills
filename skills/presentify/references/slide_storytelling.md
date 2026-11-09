# Telling a story on a slide (only when the user supplies it)

**The default is neutral.** Don't infer which result is the headline. Make each slide a clear, legible version of the artifact. Use a descriptive title, show every series in its paper colours, and highlight no rows. The user decides the story and adds emphasis later, or tells you the story in the request.

Use this file only when the user gives a story, a claim or titles in the request, such as "slide 3 should show that BERT matches the 7B LLM" or "highlight recursive summary".

## Titles
- **Default (no story given):** a descriptive title naming what is shown, for example "Assessment accuracy by memory mechanism and outcome" or "Response times by condition". It states no finding.
- **Story given:** a takeaway title, which is a full sentence stating the user's claim, for example "Fine-tuning beats prompting by 9 points on SST-2".
  - Keep it to **about 90 characters** (2 lines at 30 pt; one line holds about 50 characters). Put a concrete number in it if one exists.
  - Don't overclaim. If the effect is small or uncertain, say so ("Small, consistent gain from …").

## What to cut (it goes into the speaker notes, not the bin)
Cut for legibility, not for a story. List every cut in the report so the user can restore it.

| Paper detail | On the slide |
|---|---|
| Many rows or series | About 4–6. If more are needed to keep the comparison whole, keep them and split across slides instead |
| Many metrics | The main metric, two at most |
| *SD*, *SE*, CI, *p*-value columns in tables | Drop them, and give the values in the notes |
| 2–3 decimals | The fewest decimals that still show the differences honestly |
| Variable names and abbreviations | Plain words ("Accuracy", "Response time (ms)") |
| Table notes, model details, seeds | Speaker notes |
| Many facets or panels | Split across slides only when the panels can't be read at slide size |

Everything cut goes into the slide's speaker notes, so the presenter has it for Q&A: full numbers, CIs, *N*, seeds, caveats, and where the full result lives ("paper Table 2").

## Emphasis (only on request)
When the user names what to emphasise:
- Use one accent colour for it: the highlighted row, or the key series. Keep that series in its paper colour where possible.
- Make everything else neutral (dark grey text, grey lines or bars). If everything is emphasised, nothing is.
- If the claim is about two things (a tie, or "A beats B"), emphasise both. Don't leave half of the claim in the background.

## When to split
If the user wants two separate claims from one artifact, such as "model A wins" and "gains flatten with data", make two slides with the same source and different emphasis. Give them distinct `source` tags in the manifest, such as `…csv#accuracy` and `…csv#scaling`.
