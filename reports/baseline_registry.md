# Baseline reproduction registry

Scope: replicate every system in the supplied registry before any 144-cell search. Evidence-backed access and hardware barriers must be documented as incomplete work; they are not substitutes for replication or grounds to declare the full goal achieved. No new-method search is authorized to bypass unresolved baselines.

| System | Status | Evidence / next step |
|---|---|---|
| BM25 + TimelyRAG auto | All four full domains complete | All four BM25 baseline nDCG cells match within 0.005; auto matches Law, misses Company/Terms/University; see baseline_parity.md |
| BGE-M3 + TimelyRAG auto | Company/Law/Terms complete; University active | All three completed BGE baseline nDCG cells match tolerance; auto matches Law, misses Company/Terms. Checkpoint 5617a9f61b028005a4858fdac845db406aefb181 |
| TimelyRAG best-alpha | Offline diagnostic only | Evaluate all native alpha rankings offline with true gold; never a deployable baseline |
| TEMPO BM25 / retrievers / DiVeR | Iota full BM25 complete; remaining domains pending | Iota NDCG@10=0.09736 (10 queries,10,372 docs) rounds to published 9.7%. Source8731487; repaired optional-import SHA4bd4324; HF data1dba7027. Independent environment and smoke reviewed. DiVeR 4B weights alone exceed native 90% VRAM reservation on local GPU |
| FRESCO | Source audited; full optimizer hardware blocked | Repo SHA 51eadebff0e8ec625d66ace44d44e12020c550a2; defaults Qwen3-Reranker-8B + Llama-3.3-70B (16.38 GB + 141.11 GB weight files). No fixed evaluation data found in checkout. README data-generation command points to a subdirectory script, which references missing collect_neg_pssgs.py; inspect its provided rankify variant before repairs |
| Re³ | Paper-linked code unavailable at check | https://github.com/cjwyv/Re3 clone returns Repository not found; no alternative official release located in initial search |
| Q-TIE | Official code unavailable at check | Paper points to https://github.com/ssoy0701/Q-TIE; direct GitHub API and browser checks return 404 on 2026-11-04. Search authors' releases before marking unavailable |

Sources: https://github.com/tempo-bench/Tempo ; https://github.com/facebookresearch/fresco ; https://aclanthology.org/2026.acl-long.1180.pdf ; https://aclanthology.org/2026.emnlp-main.2611.pdf . These statuses describe access and work performed, not verified numeric replication.
