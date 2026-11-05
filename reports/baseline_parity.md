# Repaired baseline parity audit

Rounded published targets are reference values. All measured runs below use repaired executable/environment and isolated evaluation; none is a verbatim native replication. No tuning to published scores. Standard metrics and oracle diagnostics remain separate.

| Domain | Backbone | Method | Queries | Published nDCG@10 | Measured author nDCG@10 | Difference | Gate |
|---|---|---|---:|---:|---:|---:|---|
| company | bm25 | baseline | 3000 | 0.226 | 0.225781 | -0.000219 | within_tolerance |
| company | bm25 | auto | 3000 | 0.227 | 0.210976 | -0.016024 | mismatch |
| company | dense | baseline | 3000 | 0.197 | 0.197649 | +0.000649 | within_tolerance |
| company | dense | auto | 3000 | 0.200 | 0.181524 | -0.018476 | mismatch |
| law | bm25 | baseline | 3000 | 0.174 | 0.175206 | +0.001206 | within_tolerance |
| law | bm25 | auto | 3000 | 0.189 | 0.187057 | -0.001943 | within_tolerance |
| law | dense | baseline | 3000 | 0.172 | 0.170330 | -0.001670 | within_tolerance |
| law | dense | auto | 3000 | 0.179 | 0.177856 | -0.001144 | within_tolerance |
| terms | bm25 | baseline | 3000 | 0.113 | 0.112873 | -0.000127 | within_tolerance |
| terms | bm25 | auto | 3000 | 0.134 | 0.116438 | -0.017562 | mismatch |
| terms | dense | baseline | 3000 | 0.059 | 0.059339 | +0.000339 | within_tolerance |
| terms | dense | auto | 3000 | 0.071 | 0.061173 | -0.009827 | mismatch |
| university | bm25 | baseline | 3000 | 0.197 | 0.198349 | +0.001349 | within_tolerance |
| university | bm25 | auto | 3000 | 0.246 | 0.205424 | -0.040576 | mismatch |

Only completed full-domain runs are included. Missing domains remain pending. Any mismatch requires discrepancy analysis rather than baseline tuning. Full four-metric differences: baseline_parity.json. Raw-category subgroup summaries are saved beside each run summary.
