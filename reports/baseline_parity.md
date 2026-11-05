# Repaired baseline parity audit

Rounded published targets are reference values. All measured runs below use repaired executable/environment and isolated evaluation; none is a verbatim native replication. No tuning to published scores. Standard metrics and oracle diagnostics remain separate.

| Domain | Backbone | Method | Queries | Published nDCG@10 | Measured author nDCG@10 | Difference | Gate |
|---|---|---|---:|---:|---:|---:|---|
| company | bm25 | baseline | 3000 | 0.226 | 0.225781 | -0.000219 | within_tolerance |
| company | bm25 | auto | 3000 | 0.227 | 0.210976 | -0.016024 | mismatch |
| law | bm25 | baseline | 3000 | 0.174 | 0.175206 | +0.001206 | within_tolerance |
| law | bm25 | auto | 3000 | 0.189 | 0.187057 | -0.001943 | within_tolerance |
| terms | bm25 | baseline | 3000 | 0.113 | 0.112873 | -0.000127 | within_tolerance |
| terms | bm25 | auto | 3000 | 0.134 | 0.116438 | -0.017562 | mismatch |

Only completed full-domain runs are included. Missing domains remain pending. Any mismatch requires discrepancy analysis rather than baseline tuning. Full four-metric differences: baseline_parity.json. Raw-category subgroup summaries are saved beside each run summary.
