# Paper review state (updated 2026-11-24 evening)

Done: humanizer pass; paper-polish pass (hedged "as we read them" for Q-TIE/Re3, "often share most of their text", conclusion scoped to our experiments); two review passes. Added: running example (Reg Z rules 2019-16300 and 2018-18209, verified via the Federal Register API), vector TikZ Figure 1, equations (1)-(2), ablation Table 2 (`src/pilot/ablation_test3.py`), Conclusion, BM25-only limitation, metadata-derived-labels wording in the abstract. Fixed bibliography authors; corrected "150+ CFR parts" to 84 parts + 28 titles and the improvement range to +0.35..+0.40. Compiles cleanly, 4 pages, no overfull boxes. Line numbers overlapping text is the review-mode artifact also seen in the official ACL template on this TeX install.

Remaining (cannot be fixed by editing):
- MAJOR: no human-annotated queries or relevance judgments; labels are metadata-derived (annotation sheets out, none returned).
- DONE: related work read and integrated (A9b); Re3 is the closest prior art, a real Re3/Re2Bench comparison is still missing.
- MAJOR: BM25 only; Q-TIE and Re3 only approximated.
- MINOR: bibliography notes ("bibliographic details to be verified" for Jensen and Snodgrass; Re3 v1 withdrawn note) to resolve; the paper is 4 pages against an 8-page limit, so room exists for the missing material.

## Update 2026-11-25
Paper rewritten around valid-to semantics with test5 as the clean batch, dense replication, ablation on test5 and a blind-judge section. Open: human annotation, a real Re3/Q-TIE comparison (no public Re3 code found), parser misses and withdrawn/delayed/confirmation notices, larger dense models.

## Update 2026-11-26
Paper numbers moved to level-2 validity (VALID_TO=2). The ablation table now shows level-2 numbers (src/pilot/ablation_test5.py with VALID_TO=2). Judgments are LLM-agent judgments, not human; human annotation files have not been returned.

## Update 2026-11-25 (audit and correction)
Main results now use the described router and parser; gated baselines, a no-router control, gold-family and truncated-title diagnostics added; Table 2 replaced by Figure 4; Figure 1 redrawn so bars show when a rule is in force; Figures 2-3 added (figure style after ChenLiu-1996/figures4papers, code written here). 6 pages. Open: red TODOs, "to be verified" bibliography notes, corrections/missing-date/ordinary-query analyses still in the earlier setting, no LLM re-ranker baseline, v2 does not beat gated single-clock baselines on their own intents. The line-number ruler overlaps text; `acl.sty` is identical to the copy in `acl-style-files/`, cause not diagnosed.
