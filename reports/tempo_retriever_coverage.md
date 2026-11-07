# TEMPO retriever coverage

Ordinary retrieval metrics only; temporal LLM-judge metrics unmeasured. Smoke and oracle excluded.
Targets come from the pinned author README; full-benchmark reproduction remains unverified for every incomplete row.

| Retriever | Full domains | Matching target rounding | Full macro nDCG@10 |
|---|---:|---:|---:|
| BM25 | 13/13 | 13/13 | 0.107878 |
| BGE | 11/13 | 11/11 | Pending |
| Contriever | 0/13 | 0/0 | Pending |
| DiVeR | 0/13 | 0/0 | Pending |
| E5 | 0/13 | 0/0 | Pending |
| GritLM | 0/13 | 0/0 | Pending |
| Inst-L | 7/13 | 6/7 | Pending |
| Qwen | 0/13 | 0/0 | Pending |
| Rader | 0/13 | 0/0 | Pending |
| ReasonIR | 0/13 | 0/0 | Pending |
| SBERT | 0/13 | 0/0 | Pending |
| SFR | 0/13 | 0/0 | Pending |

Hardware, source and dataset barriers remain incomplete work; see baseline_registry.md and compute_limits_and_rental_plan.md.
A complete retrieval row alone does not establish temporal-judge parity or permit combinatorial search.
