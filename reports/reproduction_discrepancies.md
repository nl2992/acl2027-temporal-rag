# Reproduction discrepancies — in progress

These are repaired author-scoring replays, not exact native replication. No proposed temporal method or factorial cell has been evaluated.

## Completed observations

The Company BM25 baseline returns author nDCG@10 0.225781, MAP@10 0.181750, Recall@10 0.217750, and Hit@10 0.344000 (3,000 queries), consistent with the rounded Table 4 baseline. Its automatic scorer returns nDCG 0.210976 rather than 0.227. Terms baseline likewise agrees with its published nDCG, while automatic scoring returns 0.116438 rather than 0.134. Law baseline 0.175206 and automatic 0.187057 both fall inside the preregistered 0.005 nDCG tolerance. Full deltas and remaining runs: baseline_parity.json.

Company's exact released category `Historical, retrospective fact` has 469 queries: BM25 author nDCG 0.181037, automatic 0.145930, compared with published Table 14 values 0.186 and 0.157. No answer-based category inference or alias merging was applied.

Company candidate recall@100 is 0.376325, below the aspirational 0.90 threshold. The protocol requires reporting this retrieval limitation, not claiming a reranker can recover missing positives. Author and standard metrics differ materially: Company baseline author nDCG is 0.225781 versus separately audited standard nDCG 0.163641. This is a metric-definition difference, not two alternative reproduction targets.

## Established differences; causal attribution still pending

- The inspected release has no nonempty document `event_time` metadata fields. Its loader reads that field and otherwise falls back to insertion times; it does not extract clause validity intervals from document text. The paper describes broader event-time handling. The release has insertion times for every document.
- Paper §3.3.3 Eq. 7 describes a sigmoid of event-time presence and granularity. Released `alpha.py` uses a clipped weighted combination of gap, granularity, variance and availability signals, followed by a grid mapping. Released final scoring also includes a gate and per-candidate margin weights. These are substantive paper/code differences; no equation coefficients have been invented or fitted to the paper scores.
- Retrieval maps year/month/day/hour to 0/1/2/3; `alpha.py` maps those IDs to hour/day/month/year for its gap normalization. This was preserved in reference replay, not silently corrected.
- Paper causality permits insertion time equal to query time; released code flags equal-or-later dates missing, then gives unknown affinity a neutral value instead of excluding the candidate. This is not a hard known-at guarantee.
- Current released candidate pool is 100. Paper Tables 9/10 use @5 and settings including 50; these cannot be mixed with Table 4 @10. Candidate-pool sensitivity is a separately declared settings audit, not a search over weights to hit a target.

Primary source: https://aclanthology.org/2026.findings-emnlp.398.pdf . These observations can explain why exact reproduction is uncertain, but their individual effects have not yet been established by controlled discrepancy tests.

## Instrumentation validation and limitations

The source scoring functions are unchanged. A fresh reviewer replayed recorded dense-smoke scores through pristine upstream code across 42 synthetic-label cases, covering tied/all-zero/non-initial oracle choices. Baseline/auto/grid/oracle ranks and metrics matched. True labels remain private during production scoring; an impossible sentinel triggers reference logging of all alpha rankings, and actual oracle selection occurs offline after predictions finish.

The initial small isolation check inherited a Windows cwd; it was superseded by a clean-cwd rerun before full runs. Review later found completed smoke metric feedback was readable despite true label protection. The worker source never reads the feedback directory; it was mount-hidden in the three then-running prediction namespaces and is hidden from launch for later runs. The Company BM25 run finished before that extra feedback mask. No inference weights or thresholds were changed from observed results. This limitation is disclosed rather than claiming that all feedback files were inaccessible from the first instant of every earlier run.
