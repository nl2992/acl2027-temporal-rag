# Annotation assignments (replace "Researcher N" with names)

Roles from the plan: Researcher 1 = method/implementation, 2 = data/evaluation, 3 = literature/paper.
**Researcher 1 must not annotate**: they hold `GOLD_KEY_do_not_share_with_annotators.json` and run the scoring. Nobody else opens that file.

| Sheet | Who | Task | Rows | Est. time |
|---|---|---|---|---|
| `R2_primary_Q001-Q021.csv` | Researcher 2 | rewrite query in own words + pick best document from rule text | 21 | ~2.5 h |
| `R3_primary_Q022-Q042.csv` | Researcher 3 | same | 21 | ~2.5 h |
| `R3_second_judge_Q001-Q010.csv` | Researcher 3 | independent best-document pick only (use `draft_query_1`; no rewrite) | 10 | ~1 h |
| `R2_second_judge_Q022-Q031.csv` | Researcher 2 | same | 10 | ~1 h |

Rules: fill the second-judge sheet **before** looking at the other person's primary sheet for those rows. Do not discuss picks until both are returned. Use `annotator_notes` for ties, a rule that does not fit the topic, or if the stated semantics (`intended_semantics`, t, h) feel ambiguous; those notes are data.

Deadline suggestion: primary sheets by 2026-11-27, second-judge sheets by 2026-11-28 (leaves the weeks 3-4 window for expansion and Q-TIE). Return files as CSV in `annotation/returned/` (create it; do not edit these sheets in place).

After return, Researcher 1 will (1) compare picks with the metadata key and report agreement and Cohen's kappa on the 20 double-judged rows, (2) score the router and the full pipeline once on the rewritten queries, router frozen, (3) log disagreements as findings, not edits to the key.
