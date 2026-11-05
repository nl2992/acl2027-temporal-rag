# Baseline reproduction registry

Scope: reproduce or document evidence-backed reproducibility barriers for every system in the supplied registry before any 144-cell search. No new-method search is authorized to bypass unresolved baselines.

| System | Status | Evidence / next step |
|---|---|---|
| BM25 + TimelyRAG auto | Smoke preparation | Repaired executable pinned at 61059193d176190df4a530805ca5cb328e30cbb8; unchanged scoring; label-isolated worker under review |
| BGE-M3 + TimelyRAG auto | Pending real-model smoke | BGE-M3 checkpoint pinned at 5617a9f61b028005a4858fdac845db406aefb181; GPU feasibility before full data |
| TimelyRAG best-alpha | Offline diagnostic only | Evaluate all native alpha rankings offline with true gold; never a deployable baseline |
| TEMPO BM25 / retrievers / DiVeR | Source cloned, not run | Official repo SHA 8731487254e0988eaf2ca4ae3e93ff587fec64d0; audit data and independent environment |
| FRESCO | Source cloned, not run | Official repo SHA 51eadebff0e8ec625d66ace44d44e12020c550a2; data-generation and optimization requirements audit pending |
| Re³ | Official code identified in paper | https://github.com/cjwyv/Re3; inspect release/checkpoints/data before reproduction |
| Q-TIE | Official code unavailable at check | Paper points to https://github.com/ssoy0701/Q-TIE; direct GitHub API and browser checks return 404 on 2026-11-04. Search authors' releases before marking unavailable |

Sources: https://github.com/tempo-bench/Tempo ; https://github.com/facebookresearch/fresco ; https://aclanthology.org/2026.acl-long.1180.pdf ; https://aclanthology.org/2026.emnlp-main.2611.pdf . These statuses describe access and work performed, not verified numeric replication.
