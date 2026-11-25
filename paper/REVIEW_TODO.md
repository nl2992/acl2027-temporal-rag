# Paper review state (updated 2026-11-24 evening)

Done: humanizer pass; paper-polish pass (hedged "as we read them" for Q-TIE/Re3, "often share most of their text", conclusion scoped to our experiments); two review passes. Added: running example (Reg Z rules 2019-16300 and 2018-18209, verified via the Federal Register API), vector TikZ Figure 1, equations (1)-(2), ablation Table 2 (`src/pilot/ablation_test3.py`), Conclusion, BM25-only limitation, metadata-derived-labels wording in the abstract. Fixed bibliography authors; corrected "150+ CFR parts" to 84 parts + 28 titles and the improvement range to +0.35..+0.40. Compiles cleanly, 4 pages, no overfull boxes. Line numbers overlapping text is the review-mode artifact also seen in the official ACL template on this TeX install.

Remaining (cannot be fixed by editing):
- MAJOR: no human-annotated queries or relevance judgments; labels are metadata-derived (annotation sheets out, none returned).
- DONE: related work read and integrated (A9b); Re3 is the closest prior art, a real Re3/Re2Bench comparison is still missing.
- MAJOR: BM25 only; Q-TIE and Re3 only approximated.
- MINOR: bibliography notes ("bibliographic details to be verified" for Jensen and Snodgrass; Re3 v1 withdrawn note) to resolve; the paper is 4 pages against an 8-page limit, so room exists for the missing material.

## Update 2026-11-25
Paper rewritten around valid-to semantics with test5 as the clean batch, dense replication, ablation on test5 and a blind-judge section. Open: human annotation, a real Re3/Q-TIE comparison (no public Re3 code found), parser misses and withdrawn/delayed/confirmation notices, larger dense models.
