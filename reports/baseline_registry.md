# Baseline reproduction registry

Scope: reproduce or document evidence-backed reproducibility barriers for every system in the supplied registry before any 144-cell search. No new-method search is authorized to bypass unresolved baselines.

| System | Status | Evidence / next step |
|---|---|---|
| BM25 + TimelyRAG auto | Smoke passed; full domains running | Repaired executable pinned at 61059193d176190df4a530805ca5cb328e30cbb8; unchanged scoring; isolated worker independently reviewed |
| BGE-M3 + TimelyRAG auto | Real-model smoke passed; full Company running | Checkpoint 5617a9f61b028005a4858fdac845db406aefb181; 2-query smoke GPU allocation 1.25 GiB; full-domain memory measurement pending |
| TimelyRAG best-alpha | Offline diagnostic only | Evaluate all native alpha rankings offline with true gold; never a deployable baseline |
| TEMPO BM25 / retrievers / DiVeR | Source cloned, not run | Official repo SHA 8731487254e0988eaf2ca4ae3e93ff587fec64d0; audit data and independent environment |
| FRESCO | Source cloned, not run | Official repo SHA 51eadebff0e8ec625d66ace44d44e12020c550a2; data-generation and optimization requirements audit pending |
| Re³ | Paper-linked code unavailable at check | https://github.com/cjwyv/Re3 clone returns Repository not found; no alternative official release located in initial search |
| Q-TIE | Official code unavailable at check | Paper points to https://github.com/ssoy0701/Q-TIE; direct GitHub API and browser checks return 404 on 2026-11-04. Search authors' releases before marking unavailable |

Sources: https://github.com/tempo-bench/Tempo ; https://github.com/facebookresearch/fresco ; https://aclanthology.org/2026.acl-long.1180.pdf ; https://aclanthology.org/2026.emnlp-main.2611.pdf . These statuses describe access and work performed, not verified numeric replication.
