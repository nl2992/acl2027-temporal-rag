# Annotation guide (pilot, ~40 cases)

Files: `queries_to_rewrite.csv` (for annotators), `GOLD_KEY_do_not_share_with_annotators.json` (kept by the method owner; annotators must NOT open it).

For each row:
1. Read `intended_semantics`: **valid_at** = what legally applied at t (later publications/corrections allowed); **known_at** = latest rule published by h, even if not yet effective; **valid_known** = rule in force at t using only what was published by h; **current** = in force today.
2. Rewrite `draft_query_1/2` in your own words into `your_rewrite`. Do not copy the drafts' phrasing, and do not mention document numbers or the words "valid time" / "publication time".
3. Open each candidate URL and read the rule's DATES section. Put the single best answer in `annotator_best_document` (document number). Use `annotator_notes` for ties, ambiguity, or a rule that does not belong to the topic.
4. Second judges: see ASSIGNMENTS.md (10 blind rows each; no rewrite needed).

After both pass, the method owner compares annotator picks with the metadata-derived key, resolves disagreements by reading the rule text, and reports agreement. Queries should be re-run through the router unchanged; do not edit the router afterwards.
