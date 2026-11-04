# ACL 2027: Retrospective-Aware Temporal Retrieval — Preregistered Reproduction and Factorial Protocol

**Version:** 2026-11-04 (research plan, not executed). **Lead constraint:** one 24–32 GB GPU. **Target:** January 4, 2027 ACL Rolling Review deadline. **Status:** code/papers inspected remotely; no experiments have yet been run or scores reproduced.

## 0. Falsifiable thesis

The primary observed failure is TimelyRAG's degradation on **Historical, Retrospective Fact** queries in TimelyQABench–Company: BM25 nDCG@10 0.186 versus BM25+TimelyRAG 0.157; BGE-M3 0.133 versus BGE-M3+TimelyRAG 0.130 (published Table 14; figures rounded). Test whether a query-intent-aware, uncertainty-aware, conflict-aware reranker resolves this failure without material regression elsewhere.

Two tasks must be separated: **valid-at** (what rule was effective at event time) versus **known-at** (what information was available by the knowledge cutoff). TimelyRAG already uses insertion time, event time, effective intervals and a causal availability rule; those are NOT novel contributions. Our potential novelty is handling retrospective query intent, ambiguous and retroactive revisions, and evidence supersession while retaining retrieval quality.

Primary source: https://aclanthology.org/2026.findings-emnlp.398.pdf ; repository: https://github.com/kaist-dmlab/TimelyRAG .

## 1. Baseline reproduction registry

| Priority | System | Official source | Reproduction status/role |
|---|---|---|---|
| P0 | BM25; BGE-M3; TimelyRAG (auto-alpha) | https://github.com/kaist-dmlab/TimelyRAG | Code publicly visible; numerical reproduction NOT YET VERIFIED; required primary controls |
| P0 diagnostic only | TimelyRAG (best-alpha) | Same | Uses each query's gold relevant IDs to maximize nDCG; **oracle upper bound, never test-time baseline** |
| P1 | TEMPO BM25 and available retrievers/DiVeR | https://github.com/tempo-bench/Tempo | Public evaluation scripts; independent benchmark, not necessarily identical TimelyQABench protocol |
| P1 | FRESCO | https://github.com/facebookresearch/fresco | Public data-generation/optimization scripts; licensing is mostly CC-BY-NC; check model and dataset access |
| P1 | Re³ | https://aclanthology.org/2026.acl-long.1180/ | Published method; official reproducibility/code availability must be audited before claiming exact replication |
| P1 | Q-TIE | https://aclanthology.org/2026.emnlp-main.2611/ | Paper identifies https://github.com/ssoy0701/Q-TIE but link returned 404 on 2026-11-04; exact code currently unverified |

**DO NOT** call gains against TimelyRAG automatic equal to gains against every 2026 SOTA system. Cite model- and dataset-matched results separately. Track inability to reproduce stronger systems as a limitation, not an excuse to claim SOTA.

## 2. Immutable run manifest and no-leakage invariants

Each run MUST persist:

- Run ID, UTC start/finish, purpose (`native-replication`, `controlled-baseline`, `factorial-dev`, `frozen-test`), Git repository URL plus complete Git SHA, clean/dirty state and patch diff.
- Input SHA256 for every dataset file and query/group split; source corpus file IDs and count; deduplication and version-family rules; query gold-label hash (not readable by inference processes).
- Python, PyTorch/CUDA, FlagEmbedding, rank-bm25, NumPy, transformers, model-name and checkpoint revision/hash; GPU type/VRAM; exact invocation; environment lock.
- Dataset domain, number of queries, full candidate-pool size, top-k, output ranking for *every* query, eligible document features, scores, runtime, peak GPU memory and all metrics.

**Frozen within controlled comparisons:** full document corpus, gold labels, query wording, query timestamps, data preprocessing, tokenizer, base retrieval and embeddings, initial top-100 IDs and scores, inference checkpoints, top-10 output cutoff, timestamps, gold-label interpretation, and metric implementation. Change one factor only in one-at-a-time ablations; factorial combinations intentionally change several independently defined reranker factors.

`positive_ids`, oracle time annotations derived from gold relevance, downstream correctness judgments and test metric feedback may NOT feed the production reranker. Additional generated features must use only available document/query text and metadata, pretrained frozen models, and parameters fitted on training data.

## 3. Phase R — Native reproduction, no proposed algorithm

### R0: Source audit and freezing (before running)

```bash
# Commands below are a PROPOSED orchestration wrapper; clone/requirements/run script are author-documented.
mkdir -p acl-temporal/{vendor,manifests,results,reports,cache}
cd acl-temporal/vendor
git clone https://github.com/kaist-dmlab/TimelyRAG.git
cd TimelyRAG
git rev-parse HEAD > ../../manifests/timelyrag_sha.txt
git status --porcelain > ../../manifests/timelyrag_dirty.txt
sha256sum datasets.zip > ../../manifests/timelyrag_datasets_zip.sha256
```

Inspect `git log`, paper Table 4/Table 9/Table 14, `config.py`, `requirements.txt`, `retrieval.py`, `pipeline.py`, `metrics.py`, `alpha.py`, `TimelyQABench_datasets.py`, and data files. Do not modify the vendor checkout for R0.

**Verified from current upstream code:** `K=10`, `STAGE1_TOPN=100`, alpha grid `[0,.1,...,1]`, `BAAI/bge-m3`, `BGEM3FlagModel(..., use_fp16=True)`, BM25 using whitespace-split text, four JSONL datasets. The source contains `from .metrics import ...` in `pipeline.py` despite invoking `python -m pipeline`, which is potentially incompatible. Capture the first resulting exception verbatim if encountered. Source also implements query-wise gold-label-based `best-alpha`: report it as oracle only.

### R1: Faithful environment and attempt

```bash
# Only run in Linux with a suitable CUDA GPU; source the author env and inspect failures before changing pins.
conda create -n timelyrag-native python=3.11.5 -y
conda activate timelyrag-native
cd /path/to/acl-temporal/vendor/TimelyRAG  # replace /path/to with your actual checkout path
pip install -r requirements.txt
unzip -n datasets.zip
bash run_pipeline.sh
```

Author environment specifies Python 3.11.5; repository `requirements.txt` pins `torch==2.3.1` and `transformers==4.46.3` at inspection time. Log actual resolution and driver compatibility. Do not replace versions or alter code silently. If installation/execution fails, save `native_failure.log`, classify root cause, and create a separate `vendor-repaired` tracked patch with the minimal correction. Retest that correction on a tiny input and on full data. Never call repaired execution a verbatim replication.

### R2: Reproduce identifiable published cells

Published Table 4 nDCG@10 expected baseline / plus TimelyRAG for BM25 and BGE-M3:

| Domain | BM25 / +TimelyRAG | BGE-M3 / +TimelyRAG |
|---|---|---|
| Law | 0.174 / 0.189 | 0.172 / 0.179 |
| University | 0.197 / 0.246 | 0.173 / 0.213 |
| Company | 0.226 / 0.227 | 0.197 / 0.200 |
| Terms of Service | 0.113 / 0.134 | 0.059 / 0.071 |

These are rounded author results, **not reproduced scores**. Match all four metrics (nDCG@10, MAP@10, Recall@10 and Hit@10) per domain, and compare Table 14 historical-subcategory values separately. Check whether the released data exposes the published category labels; if not, mark Table 14 as not yet independently reproducible rather than reverse-engineering categories from the answers.

**Proposed parity gate:** exact file counts 30,000 docs/3,000 queries per domain as published, all expected IDs valid, no missing gold documents, score agreement within 0.005 absolute for each nDCG@10 published cell when matching code/data/experiment settings. Investigate larger mismatches; report them, do not tune the baseline to paper figures. Include author table settings such as 50-versus-100 candidate-pool selection. The paper Table 9/10 employs candidate pool values that differ from current config `100`; explicitly match each claimed figure.

Also run an independent metric unit test with known binary relevance vectors. The current `metrics.py` calculates ideal DCG by sorting only the returned top-k relevances; this may not equal every standard nDCG implementation. Preserve *author metric* for paper parity; report a separate standard metric audit, never mix the two.

**Stop condition for native parity:** If the original executable cannot run or the 0.005 parity gate remains unmet after transparent minimal repairs and documented discrepancy analysis, continue only as a **controlled reimplementation**. Do not report exact SOTA replication.

## 4. Phase C — One controlled baseline and fixed retrieval cache

Freeze two experimental backbones separately: (i) BM25 and (ii) BGE-M3, exactly as constructed by the fixed author implementation. Each has 100 retrieved candidates per query, their canonical IDs, original rank and original scores, model embedding revision, metadata and gold IDs for evaluation only. Verify that proposed feature extraction never modifies candidate membership.

Canonical record schema:

```json
{
  "query_id":"...", "family_id":"...", "domain":"law|university|company|terms",
  "query":"...", "query_intent":"valid_at|known_at|unspecified",
  "query_event_time":null, "query_knowledge_cutoff":null,
  "candidate_ids":["..."], "base_scores":[0.0],
  "candidate_features_path":"...", "gold_ids_eval_only":["..."]
}
```

Schema is **proposed**, not upstream. Make `query_intent` labels manually audited for the new extension; do not infer them from model answer correctness. Preserve the upstream exact fields separately in raw artifacts.

Before reranking report candidate recall@100, the oracle achievable Recall@10 constrained to that candidate pool, duplicate ID checks and availability of document insertion dates. This explicitly separates reranker ceiling from first-stage retrieval failures.

## 5. Phase F — Pre-registered 144-cell factorial

Factors (3 × 4 × 3 × 2 × 2 = **144 configurations**):

| Factor | Levels | Fixed implementation contract |
|---|---|---|
| T: temporal scoring (3) | TimelyRAG reference distance; interval-overlap with knowledge cutoff; asymmetric past/future distance | All return calibrated [0,1] scalar per candidate. Reference method must preserve upstream precisely. |
| C: conflict management (4) | No conflict signal; latest eligible revision; frozen NLI contradiction; supersession graph | Never use an ineligible post-cutoff document as evidence for known-at queries. Precompute once. |
| F: score fusion (3) | Static normalized linear sum; reciprocal-rank fusion; train-only-fitted query gate | Gate trained and cross-fitted only within training data. Equal feature/inference budget reported. |
| U: missing/uncertain time (2) | Conservative neutral fallback; uncertainty-aware penalty/abstain | Distinguish missing metadata from true historical uncertainty. |
| G: granularity (2) | Whole document; independently extracted clause/claim features | Both retain exactly the same document IDs and candidate set; clauses are intermediate features, not new candidates. |

Guard against invalid/duplicated cells: identical predictions across factor levels where no relevant metadata exists must be collapsed/reported; the algorithm cannot access gold labels to break ties. Pre-register default tie-breaking (original rank, then stable doc ID). Make the factorial code emit all 144 config IDs even if some are aliased.

Candidate scoring (illustrative, *not* the authors' formula):

`S(q,d) = Fuse_F(S_base(q,d), T_T(q,d), C_C(q,d), U_U(q,d), G_G(q,d); theta_fit_on_train)`

Required ablations on finalist: no event time, no knowledge cutoff, no conflict management, no uncertainty modelling, document-only representation, reference TimelyRAG score. Include an explicit `TimelyRAG-auto` baseline **not necessarily one of the 144 cells** to avoid a wrongly recreated reference.

## 6. Splits, model selection and independent evaluation

Published TimelyQABench is a **reproduction benchmark**, not a genuinely unseen final test once used throughout development. The repository paper and README do not establish an author-sanctioned train/dev/test partition in the inspected pages. Audit this before creating one.

**Proposed query-group split:** 60% train / 20% development / 20% lockbox across evolving-document policy families, preserving domain and historical query strata. Build groups using provenance/family IDs before splitting. Do **not** randomly split near-identical revised clauses or queries; audit overlap after splitting. The full original corpus remains constant for retrieval; only queries/labels are partitioned. Freeze exact group IDs and SHA256 in a signed manifest before tuning.

- Stage F1: run all 144 combinations on a fixed representative development subset. Rank using dev nDCG@10 with a pre-registered minimum retrospective performance constraint. Do not use final holdout.
- Stage F2: promote 24 configurations; evaluate full development partition, run 3 training seeds where stochastic models appear, log runtime and variance.
- Stage F3: promote six; validate using held-out family-group validation or nested group folds. One winner only before true external test. Frozen thresholds and weights.
- Stage F4: **one-time** lockbox evaluation on group-disjoint TimelyQABench split and a completely independent newer benchmark assembled from audited real version histories. Report all 144 results only as development results, not 144 independent test hypotheses.

**Independent test extension:** collect 300–600 candidate cases from timestamped policies, Wikipedia revision histories or regulation amendments. Curate both *valid-at* and *known-at* questions, and explicitly include retroactive corrections; each case requires independently verifiable version archive, publication date, applicability date, supersession link, gold evidence document and whether the answer is answerable as of the cutoff. Do not claim a novel benchmark until licensing, provenance, independent manual review, strata counts, inter-annotator agreement, and locked annotation guidelines are complete. Keep some families unseen in training and development. Synthetic examples may be used to test parser properties, but cannot be the sole external validation.

FRESCO assesses evolving/current recency and TEMPO spans reasoning-intensive temporal retrieval. Neither automatically provides gold labels for historical **known-at**; use original task metrics as published, and evaluate known-at only on an appropriately annotated extension. Never silently relabel an existing benchmark.

## 7. Metrics, tests and decision rules

Primary *matched-retrieval* metric: per-query nDCG@10 using the original metric code for paper-parity and a separately audited standard nDCG implementation as robustness. Also report Hit@10, Recall@10, MAP@10, candidate recall@100, per-query latency and peak VRAM.

Primary *new-failure-mode* metrics on the independent set: point-in-time evidence accuracy, future-information leakage rate among top-k, applicable-but-not-yet-known error rate, and performance split by valid-at/known-at/retroactive and conflict types. Declare whether the scored label is evidence retrieval or end-to-end answer correctness. Downstream QA uses a fixed generator, prompt, token budget, temperature and context serialization for all methods.

Analysis: family-clustered paired bootstrap 10,000 iterations for difference versus strongest compatible baseline; report 95% CIs, point estimates, effect sizes and raw denominators. Handle multiplicity for simultaneous confirmatory contrasts; Holm adjustment or a single pre-registered primary comparison, not 144 uncorrected p-values. Report per-domain, per-query-type and rare-group results, plus regression counts. For any learned models, run 3 fixed training seeds and test all seeds on the same locked data.

**Proposed advancement gates (not literature-established):**
1. **Reproduce:** absolute deviation <= 0.005 for paper Table 4 nDCG@10 cells if matching settings, otherwise status `REPRO_PARTIAL`/`REPRO_FAILED` with discrepancy report.
2. **Candidate feasibility:** at least 90% of target positives remain retrievable from 100-candidate pool (aspirational threshold; report if not met rather than misrepresenting ceiling).
3. **Dev promotion:** mean nDCG improvement and retrospective benefit, with no >0.005 absolute deterioration in any ordinary domain; no tuning on held-out test.
4. **Confirmed improvement:** final frozen method has positive cluster-bootstrap CI against best reproduced *deployable* baseline on a pre-registered primary metric; report overall and historical effects, corrected multiple comparisons and latency.
5. **ACL-worthiness:** nontrivial mechanism demonstrated by ablations and a clean, independently grounded failure-mode benchmark. If it only wins by data cleanup, test leakage, unverifiable labels or larger inference budget, classify as not sufficient for the intended SOTA claim.

A small positive gain alone **cannot guarantee acceptance**.

## 8. Compute plan and cache discipline

Each TimelyQABench domain has 3,000 queries and 30,000 documents in upstream README; four domains = 12,000 queries and 120,000 *domain entries* (audit unique IDs across data). A top-100 pool yields up to **1,200,000 query–candidate rows across both backbones separately** (per backbone 12k × 100 = 1.2M). A claim-aware NLI pass on all pairs could dominate GPU time; prefer clustering/version-family comparisons and cache logits rather than invoking the same network 144 times.

Cache key must include dataset SHA, model SHA/revision, tokenizer, input serialization, cutoff policy, embedding dtype, max length and feature extraction version. Build base embedding index once per dataset/backbone; compute semantic scores once; extract timestamps once; precompute claim features and contradiction pairs once per frozen model; store float16 or float32 scores plus a precision audit. GPU-heavy extraction can be batched with autocast/quantization where valid, but *do not* alter the published baseline’s precision on the native reproduction track.

Estimate total time only after one pilot measures: `estimated_GPU_hours = (number_of_uncached_model_pairs / measured_pairs_per_second) / 3600 + training_GPU_hours`; separately benchmark CPU graph/reranker time. Record full elapsed time and hardware. Avoid speculative runtime or cloud-dollar claims before measurement.

## 9. Minimal proposed project tree

```text
acl-temporal/
  vendor/TimelyRAG/              # pristine upstream submodule or vendored SHA
  vendor/Tempo/                  # external evaluation, independent environment
  vendor/fresco/                 # external benchmark, independent environment
  configs/native.yaml
  configs/factorial.yaml
  data/raw/ data/splits/ data/processed/
  cache/retrieval/ cache/temporal/ cache/claims/
  src/adapters/ src/features/ src/rerank/ src/eval/ src/stats/
  tests/test_metric_parity.py
  tests/test_cutoff_nonleakage.py
  tests/test_candidate_invariance.py
  tests/test_deterministic_tiebreak.py
  scripts/audit_upstream.py
  scripts/run_native.sh
  scripts/export_fixed_candidates.py
  scripts/precompute_features.py
  scripts/run_factorial.py
  scripts/select_finalist.py
  scripts/evaluate_lockbox.py
  manifests/ results/native/ results/dev/ results/locked/
  reports/reproduction_audit.md reports/experiment_log.md
```

All `src/` and `scripts/` files above are **proposed**, not created or tested by this document. The reproduction shell commands in §3 are orchestrator instructions to check/execute, not a guarantee the upstream code presently runs.

## 10. Day-by-day first ten working days (proposed)

| Day | Executable task | Acceptance artifact |
|---|---|---|
| 1 | Pin upstream SHAs; audit source, README, paper tables, environment | manifest, code-audit checklist |
| 2 | Create author env; unpack original files; execute unchanged runner | native.log or exact failure trace |
| 3 | Minimal repair branch if necessary; document diff; rerun smoke tests | repair.patch, passing data/metric smoke tests |
| 4 | Run four-domain BM25 and BGE-M3 native benchmark; capture all metrics | per-domain baseline JSON, paired table vs paper |
| 5 | Resolve paper/code discrepancies; mark replication pass/partial/fail | signed replication audit and fixed versions |
| 6 | Export deterministic top-100 candidate caches and SHA hashes; check gold exposure | first-stage recall/ceiling report |
| 7 | Define historical/retroactive label rubric, group disjoint splits and lockbox | immutable split manifests |
| 8 | Implement original-score adapter and 3 temporal scoring choices; parity tests | `TimelyRAG-auto` adapter score identity test |
| 9 | Add conflict and uncertainty cached feature extraction, run two pilot domains | candidate coverage, NLI costs, latency pilot |
| 10 | Freeze 144-cell factorial manifest; run first development subset and generate a result matrix | `dev_results.csv`, seed/score logs, invalid config report |

If native reproduction or dataset audit fails by day 5, do not bury the issue; decide whether the project can proceed honestly as a matched reimplementation rather than an exact reproduction.

## 11. Source and publication protocol

- TimelyRAG publication: https://aclanthology.org/2026.findings-emnlp.398/
- Original repository: https://github.com/kaist-dmlab/TimelyRAG
- Re³ 2026 ACL: https://aclanthology.org/2026.acl-long.1180/
- Q-TIE 2026 EMNLP: https://aclanthology.org/2026.emnlp-main.2611/
- TEMPO benchmark: https://github.com/tempo-bench/Tempo
- FRESCO 2026 EMNLP Findings: https://aclanthology.org/2026.findings-emnlp.54/ and https://github.com/facebookresearch/fresco
- ACL 2027 submission rules: https://2027.aclweb.org/calls/main/

The paper must disclose author-code patches, non-replicable claimed baselines, use of synthetic/LLM-labeled examples, compare costs and candidate pools fairly, preserve original baseline metrics, include comprehensive related work and a dedicated Limitations section. Source and data licenses must be audited before any redistribution. **No claimed SOTA success exists at the time of writing.**
