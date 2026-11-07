# Turning a result into a slide

A paper table answers "what are all the numbers?". A slide answers "what should I remember?". Start from the second question.

## Takeaway titles (assertion–evidence)
- The title is a full sentence stating the finding. The table or figure is the evidence for it.
  - Topic label: "Results on SST-2" → Takeaway: "Fine-tuning beats prompting by 9 points on SST-2"
  - Topic label: "Response times by condition" → Takeaway: "Incongruent trials slow responses by ~80 ms"
- Keep it to **about 90 characters** (2 lines at 30 pt; one line holds about 50 characters). Put a concrete number in it if one exists.
- Don't overclaim. If the effect is small or uncertain, say so ("Small, consistent gain from …").

## What to cut (it goes into the speaker notes, not the bin)
| Paper detail | On the slide |
|---|---|
| All models or conditions | The baseline, the winner, and the one comparison the story needs (4–6 rows or series at most) |
| All metrics | The one metric the story is about, two at most |
| *SD*, *SE*, CI columns, *p*-values | Drop them. Mention significance in the footer if it matters ("all differences p < .01") |
| 2–3 decimals | Fewest decimals that still show the difference (81.2 → 81, or 0.81) |
| Variable names and abbreviations | Plain words ("Accuracy", "Response time (ms)") |
| Table notes, model details, seeds | Speaker notes |
| Many facets or panels | 1–2 panels. Suggest extra slides for the rest |

Everything cut goes into the slide's speaker notes, so the presenter has it for Q&A: full numbers, CIs, *N*, seeds, caveats, and where the full result lives ("paper Table 2").

## Emphasis
- One accent colour for the thing the story is about: the highlighted row, or the key series.
- Everything else is neutral (dark grey text, grey lines). If everything is emphasised, nothing is.
- If the claim is about two things (a tie, or "A beats B"), emphasise both, for example A in the accent colour and B in a second accent or dark grey. Don't leave half of the claim in the background.
- For a comparison over time or conditions, show the baseline in grey and the key series in the accent colour, then label both directly.

## When to split
If one artifact supports two separate claims, such as "model A wins" and "gains flatten with data", propose two slides with the same source and different emphasis. Give them distinct `source` tags in the manifest, such as `…csv#accuracy` and `…csv#scaling`.
