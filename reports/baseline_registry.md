# Baseline reproduction registry

Scope: reproduce or document evidence-backed reproducibility barriers for every system in the supplied registry before any 144-cell search. No new-method search is authorized to bypass unresolved baselines.

| System | Status | Evidence / next step |
|---|---|---|
| BM25 + TimelyRAG auto | Three full domains completed; University running | BM25 baseline matches Company/Law/Terms nDCG targets within 0.005; auto matches Law, misses Company/Terms; see baseline_parity.md |
| BGE-M3 + TimelyRAG auto | Real-model smoke passed; full Company running | Checkpoint 5617a9f61b028005a4858fdac845db406aefb181; 2-query smoke GPU allocation 1.25 GiB; full-domain memory measurement pending |
| TimelyRAG best-alpha | Offline diagnostic only | Evaluate all native alpha rankings offline with true gold; never a deployable baseline |
| TEMPO BM25 / retrievers / DiVeR | Independent environment setup active | Repo SHA 8731487254e0988eaf2ca4ae3e93ff587fec64d0; requirements dry-run succeeded; native requirements install in separate Python 3.10 environment. HF data revision 1dba7027d0afa628993c6dd794e9b68c657a6fac. DiVeR 4B weight size alone is 8,043,594,472 bytes, leaving insufficient runtime room on 8 GB |
| FRESCO | Source audited; full optimizer hardware blocked | Repo SHA 51eadebff0e8ec625d66ace44d44e12020c550a2; defaults Qwen3-Reranker-8B + Llama-3.3-70B (16.38 GB + 141.11 GB weight files). No fixed evaluation data found in checkout. README data-generation command points to a subdirectory script, which references missing collect_neg_pssgs.py; inspect its provided rankify variant before repairs |
| Re³ | Paper-linked code unavailable at check | https://github.com/cjwyv/Re3 clone returns Repository not found; no alternative official release located in initial search |
| Q-TIE | Official code unavailable at check | Paper points to https://github.com/ssoy0701/Q-TIE; direct GitHub API and browser checks return 404 on 2026-11-04. Search authors' releases before marking unavailable |

Sources: https://github.com/tempo-bench/Tempo ; https://github.com/facebookresearch/fresco ; https://aclanthology.org/2026.acl-long.1180.pdf ; https://aclanthology.org/2026.emnlp-main.2611.pdf . These statuses describe access and work performed, not verified numeric replication.
