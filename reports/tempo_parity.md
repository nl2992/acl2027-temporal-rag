# TEMPO BM25 reproduction audit

Repaired optional imports and isolated scoring/offline evaluation preserve the released BM25 and metric function bodies. Published values are percentages rounded to one decimal. Smoke subsets and gold-assisted oracle values are excluded.

| Domain | Queries | Documents | Published NDCG@10 (%) | Measured (%) | Same rounding |
|---|---:|---:|---:|---:|---|
| bitcoin | 100 | 153291 | 6.2 | 6.157 | True |
| cardano | 51 | 87201 | 13.4 | 13.377 | True |
| economics | 83 | 93756 | 5.8 | 5.805 | True |
| genealogy | 115 | 156228 | 13.3 | 13.273 | True |
| history | 801 | 356493 | 9.2 | 9.247 | True |
| hsm | 150 | 213818 | 21.2 | 21.165 | True |
| iota | 10 | 10372 | 9.7 | 9.736 | True |
| law | 35 | 43288 | 12.7 | 12.692 | True |
| monero | 65 | 85093 | 2.8 | 2.755 | True |
| politics | 150 | 183394 | 32.7 | 32.694 | True |
| quant | 34 | 28785 | 2.5 | 2.501 | True |
| travel | 100 | 177677 | 4.6 | 4.610 | True |
| workplace | 36 | 64659 | 6.2 | 6.229 | True |

13/13 domains complete. A whole-benchmark macro result is reported only after all thirteen domains complete. Ordinary metrics are saved with each run. The released oracle has an independently observed tie/pool defect and is diagnostic only. Temporal Coverage/Precision require the separate author judge stage and have not been measured.
