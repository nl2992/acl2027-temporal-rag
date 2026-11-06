# Progress

Current verified state (2026-11-06): TEMPO BM25 has 13/13 domains matching author-rounded ordinary nDCG@10, macro 0.107878. BGE has 8/13 domains complete, all matching rounded targets; Bitcoin is running. The historical integrity audit remains WARN for earlier provenance gaps. INSTRUCTOR-L is staged but not tested with a real model; Qwen access is deferred. Full dense coverage, temporal judge metrics, FRESCO/Re3/Q-TIE and the stronger-baseline gate remain incomplete. Combinatorial search stays locked. See tempo_retriever_coverage.md and the dated entries below.

Updated: 2026-11-05. Research status: P0 REPRO_PARTIAL; TEMPO reproduction in progress. Combinatorial search locked until the full baseline registry is resolved.

| Phase | Status | Completion evidence / next gate |
|---|---|---|
| Preserve protocol and factorial | Complete | Byte-identical copies and SHA256 manifest |
| Factorial preregistration structure | Validated | 144 unique configurations, five factor dimensions |
| Repository and skills | Complete | Private GitHub repository published; ARIS, 12 HKUSTDial skills, Graphify installed; dependency check passed |
| R0 source, paper, license audit | Partial | Upstream frozen; dataset counts/IDs and metric discrepancy checked; licenses and remaining papers unresolved |
| R1 native environment | Native pins conflict; repaired setup verified | Linux/Python 3.11.5/PyTorch 2.3.1 CUDA calculation and pip check pass; disclosed Notebook repair |
| R2 numeric reproduction | Eight full backbone/domain runs complete | All eight base nDCG cells match tolerance; automatic matches both Law cells and misses six other cells. See baseline_parity.md |
| C fixed candidates | Not run | Candidate recall, ceiling, immutable cache |
| F factorial development | Not run | Frozen group splits and dev-only selection |
| Final lockbox/external evaluation | Locked / not created | Freeze winner before one-time evaluation |

Dataset path/university filename and metric imports repaired in a separate Git worktree. True labels are inaccessible to the unprivileged prediction worker through a private mount namespace; evaluation and best-alpha diagnostics occur afterwards. The first inherited-working-directory isolation defect was corrected and independently retested. BGE-M3 real smoke passed on 2 queries/20 documents using the pinned local snapshot; those scores are not paper reproduction results. Full-domain results and parity are saved in baseline_parity.md. Continue all listed baseline reproductions before any factorial search.

TEMPO: independent environment ready after compiler/Java prerequisites, missing InstructorEmbedding addition, and a separate optional-vLLM import repair. Source-function identity and evaluator fixtures reviewed. Eight full BM25 domains completed with rounded published parity; five domains and temporal judge metrics remain pending. User elected continued local work with documented hardware limits; no rental started.

## 2026-11-05 verified continuation

All eight P0 backbone/domain runs finished (24,000 query/backbone predictions). All eight base nDCG cells satisfy the prescribed tolerance; automatic TimelyRAG satisfies two Law cells and misses six others. Status is REPRO_PARTIAL, with no scoring changes made to fit published numbers. Full saved-artifact deterministic audit evidence is in P0_EXPERIMENT_AUDIT.md and review_tools/p0_evidence.json. The review agent later hit an account usage limit; its written artifact and completed deterministic evidence are retained, but no additional review completion is inferred.

TEMPO BM25 completed eight of thirteen domains: Iota, Quant, Law, Workplace, Economics, Cardano, Monero and Travel. All eight round to published NDCG@10 values (tempo_parity.md). Bitcoin's first attempt exited 137 after a kernel OOM event; remaining domains are incomplete. Local Linux has 7.6 GiB RAM and initially 2 GiB swap, on a host with about 16 GiB physical RAM. With all workers confirmed stopped, added a temporary 8 GiB swap file without increasing physical-RAM allocation. Bitcoin retry tempo-bitcoin-bm25-20261105T073857Z now runs alone, full original corpus/settings. This is a resource repair, not a method change or successful reproduction yet.

TEMPO BGE smoke tempo-iota-bge-smoke-001 completed unchanged native FP32/batch128 inference on two queries and all 10,372 Iota documents. Offline evaluation completed; NDCG@10 0.37875 is a smoke value, not full-domain reproduction. Measured Torch peak allocation 7,796,289,536 bytes. Source/settings pre-review exists; independent post-execution review remains incomplete after reviewer usage limit. Dense full runs remain pending. The running Linux worker version is preserved in worker provenance; the Windows forward revision includes a document-only cache-key correction not yet deployed.

All listed SOTA methods remain in scope, with hardware/source/data limits documented separately. No paid resources, factorial runs, lockbox access or SOTA claim. CPU/GPU memory-heavy jobs must be serialized.

2026-11-05 update: Bitcoin retry completed, 100 queries/153,291 documents, ordinary NDCG@10=0.06157 (published6.2% after rounding). TEMPO BM25 now9/13 domains complete. Genealogy has started; Politics/HSM/History remain queued. Resumed independent BGE smoke review passed saved ranking/cache and all31 metric checks; see tempo_dense_smoke_review.md. Full Iota BGE is cleared on the repaired track after the CPU queue; no cross-domain feasibility assumed.

2026-11-05 update: Genealogy completed115queries/156,228docs, NDCG@10=.13273 (published13.3% rounded), retrieval284.767322seconds. TEMPOBM25 now10/13 domains completed with matching rounded author targets. Politics run tempo-politics-bm25-20261105T074747Z started; HSM/History queued. Host diskfree47,760,523,264bytes atboundary. No whole-benchmark macro claim before remaining domains finish.

2026-11-05 update: Politics complete150queries/183,394docs, NDCG@10=.32694, matching published32.7% rounded. TEMPOBM25 now11/13 completed. HSM run tempo-hsm-bm25-20261105T075235Z active, History last; hostdiskfree46,755,729,408bytes atboundary. FullIotaBGE waits behind the CPUqueue plus fullscope/hash/idle gates.

Current update (2026-11-05): QuantBGE completed34queries/28,785docs, ordinary nDCG@10 .11737 (11.7%rounded), soBGE2/13domains. Historical16-runaudit completedWARN withverifiednumericparityandexplicitprovenancegaps; seereportandtrace. Futureevaluatorloggingwrapperdeployedandimport-onlychecked, no metricimplementationchanged. Law's onepreflightfailureispreservedandreviewedforno-computationrecovery. RemainingBGEqueue can nowresume under source/resource guards. AllotherSOTAscope andfactoriallockunchanged.

2026-11-05 — User answered gated-Qwen access question: continue othermethods; userwillarrangeaccesslater. Qwenremainsincomplete/pendingauthorizedaccess, notremovedfromfullSOTAobjective. No repeatedauthprompt, tokenrequest, gateacceptance or gatedweightdownload scheduled. Otherlocalbaselinescontinue; factoriallockunchanged.

2026-11-06 — TEMPO BGE full-domain coverage advanced to 8/13, all eight matching the author's rounded nDCG@10 targets. Workplace, Economics, Cardano, Monero and Travel completed; Bitcoin tempo-bitcoin-bge-20261106T011741Z is active in queue handle70715. The INSTRUCTOR-L isolated worker draft passed CPU-only source and cold/warm-cache fixtures, including rejection of a wrong-dtype cache write. It has not been deployed, loaded a real model, or completed a native smoke; separate launcher and evaluator identity integration remain pending. Full SOTA objective and factorial lock remain unchanged.

2026-11-06 — Bitcoin BGE is still running in the existing sequential queue. A separate INSTRUCTOR-L namespace launcher draft has been prepared; deployment and real smoke remain pending.

2026-11-06 — INSTRUCTOR-L draft launcher syntax and synthetic CPU fixture passed. Real model loading and native smoke remain pending while Bitcoin BGE continues.

2026-11-06 — Corrected the stale opening progress snapshot against tempo_retriever_coverage.md: eight of 13 BGE domains are complete and match author-rounded targets. Bitcoin remains in progress; no new result is claimed.

2026-11-06 — Prepared a disabled INSTRUCTOR-L runner draft that separately records and checks the inference worker and trusted evaluator entry-point hashes. It is not reviewed or deployed; end-to-end integration, isolation, fixtures and real model smoke remain pending.

2026-11-06 — A synthetic fixture executed the draft's actual export assertions and rejected six identity or digest mismatches. This is a narrow local check, not a review or end-to-end run; deployment remains blocked on the remaining checks.

2026-11-06 — Fresh reviewer identified missing source/stager pins and cross-run resource exclusion, incomplete scope checks and warm-cache validation gaps in the disabled INSTRUCTOR runner. Interim findings are recorded in instructor_runner_review_checkpoint.md; no deployment approval or completed independent review is claimed.

2026-11-06 — The fresh reviewer completed its read-only assessment and confirmed the four findings; review is same-family provisional with backend identity not independently attested. The draft remains disabled pending repairs and re-review.

2026-11-06 — Partially repaired the disabled INSTRUCTOR runner: added stager and retriever hash checks and run-scope checks against the corresponding completed BM25 reference. Synthetic export tests reject eleven identity, scope and digest mismatches. Concurrency, cache integrity, deployed namespace, real-model checks and re-review remain pending.
