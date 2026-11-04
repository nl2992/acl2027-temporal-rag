# Reproduction audit

Status: R0_PARTIAL; native execution NOT_STARTED (Linux provisioning blocked).

## Completed source and data checks (2026-11-04)

Pristine upstream checkout: `https://github.com/kaist-dmlab/TimelyRAG`, SHA `5213a0c1743f23fd52a258005c3887aaf7e8cd0f`. Clean state and source/archive hashes are in `manifests/upstream_audit.json`; recent commit metadata in `manifests/timelyrag_git_log.txt`. The ignored checkout is local only; no upstream datasets redistributed.

All four archive JSONL members contain 3,000 queries, 30,000 documents, 30,000 unique IDs, no missing IDs, and no unresolved global gold references. All document insertion times are nonempty; no document has a nonempty `event_time` metadata field. Timestamp validity is not yet audited. Category counts and raw field names are recorded. Category labels contain spelling/language variants; establish a documented mapping before Table 14 comparisons. Do not infer category membership from answers.

No LICENSE/COPYING file was found in the upstream repository root. Redistribution permissions remain unresolved. Dataset local inspection does not establish a redistribution license.

Confirmed code settings: K=10, candidate pool=100, alpha grid 0 to 1 by 0.1, BAAI/bge-m3 FP16, whitespace BM25. Best-alpha explicitly searches using gold nDCG and remains diagnostic only.

## Source defects / discrepancies identified statically

- `config.py` expects `timelyrag_yonsei_dataset_v2.jsonl`; archive provides `timelyrag_university_dataset_v2.jsonl` instead. Archive members are at archive root, while default paths expect `./datasets/`.
- `pipeline.py` has relative `.metrics` imports inside BM25/BGE loops and macro reporting despite the runner invoking top-level `python -m pipeline`. No native exception captured yet; do not describe static findings as observed execution failures.
- Experiment output config is imported before `--exp-dir` sets its environment variable; flag behavior needs a runtime check.
- Granularity IDs passed from retrieval are year=0, month=1, day=2, hour=3; `alpha.py` maps IDs back to hour/day/month/year for GAP_MAX. Preserve native behavior and document before any repair.
- The temporal distance function marks post-cutoff items NaN, then affinity converts NaN to 0.5. That does not constitute hard cutoff exclusion. Audit actual ranking leakage before using this as a known-at baseline.

## Executed metric audit

Read-only author metric import in the separate Windows tooling environment (not the native author environment): ranking `[a,x]`, gold `[a,b]`, k=2 produces author nDCG=1 and AP=1, while standard binary nDCG is approximately 0.613147 and AP with min(gold,k) denominator is 0.5. This is a metric-definition audit, not a retrieval experiment. Author code is unchanged.

## Independently checked publication sources

- TimelyRAG paper and official repository resolve. Table 4 nDCG cells in the supplied protocol match the paper. Table 14 confirms the historical Company figures. Tables 9/10 use @5 and varying candidate pools; do not compare them directly with @10 runs. Source: https://aclanthology.org/2026.findings-emnlp.398.pdf
- ACL 2027 official call lists January 4, 2027 ARR submission deadline at 11:59 PM UTC−12 (AoE): https://2027.aclweb.org/calls/main/
- Other related-work repositories/papers remain unaudited. No numerical baseline parity or SOTA claim is established.

Required evidence: independently verified paper/code URLs; upstream SHA and clean state; source/data licenses; dataset counts and ID integrity; environment and CUDA compatibility; native invocation and exact first failure; separate minimal repair patch if needed; author and standard metric audit; matched paper settings and parity table. Record each with an artifact path before changing status.
