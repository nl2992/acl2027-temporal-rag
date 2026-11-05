# Progress

Updated: 2026-11-04. Research status: SMOKE_PASSED; repaired author-scoring baseline runs in progress. Combinatorial search locked until the full baseline registry is resolved.

| Phase | Status | Completion evidence / next gate |
|---|---|---|
| Preserve protocol and factorial | Complete | Byte-identical copies and SHA256 manifest |
| Factorial preregistration structure | Validated | 144 unique configurations, five factor dimensions |
| Repository and skills | Complete | Private GitHub repository published; ARIS, 12 HKUSTDial skills, Graphify installed; dependency check passed |
| R0 source, paper, license audit | Partial | Upstream frozen; dataset counts/IDs and metric discrepancy checked; licenses and remaining papers unresolved |
| R1 native environment | Native pins conflict; repaired setup verified | Linux/Python 3.11.5/PyTorch 2.3.1 CUDA calculation and pip check pass; disclosed Notebook repair |
| R2 numeric reproduction | Seven full backbone/domain runs complete | All four BM25 and Company/Law/Terms BGE-M3 baselines match nDCG tolerance. Automatic matches Law for both backbones; other completed automatic cells miss. University BGE active |
| C fixed candidates | Not run | Candidate recall, ceiling, immutable cache |
| F factorial development | Not run | Frozen group splits and dev-only selection |
| Final lockbox/external evaluation | Locked / not created | Freeze winner before one-time evaluation |

Dataset path/university filename and metric imports repaired in a separate Git worktree. True labels are inaccessible to the unprivileged prediction worker through a private mount namespace; evaluation and best-alpha diagnostics occur afterwards. The first inherited-working-directory isolation defect was corrected and independently retested. BGE-M3 real smoke passed on 2 queries/20 documents using the pinned local snapshot; those scores are not paper reproduction results. Full-domain results and parity remain pending. Continue all listed baseline reproductions before any factorial search.

TEMPO: independent environment ready after compiler/Java prerequisites, missing InstructorEmbedding addition, and a separate optional-vLLM import repair. Source-function identity and evaluator fixtures reviewed. Full Iota BM25 completed (10 queries/10,372 docs), NDCG@10=0.09736, rounding to the published 9.7%. Other domains and temporal judge metrics remain pending. User elected continued local work with documented hardware limits; no rental started.

## 2026-11-05 verified continuation

All eight P0 backbone/domain runs finished (24,000 query/backbone predictions). All eight base nDCG cells satisfy the prescribed tolerance; automatic TimelyRAG satisfies two Law cells and misses six others. Status is REPRO_PARTIAL, with no scoring changes made to fit published numbers. Full saved-artifact deterministic audit evidence is in P0_EXPERIMENT_AUDIT.md and review_tools/p0_evidence.json. The review agent later hit an account usage limit; its written artifact and completed deterministic evidence are retained, but no additional review completion is inferred.

TEMPO BM25 completed eight of thirteen domains: Iota, Quant, Law, Workplace, Economics, Cardano, Monero and Travel. All eight round to published NDCG@10 values (tempo_parity.md). Bitcoin's first attempt exited 137 after a kernel OOM event; remaining domains are incomplete. Local Linux has 7.6 GiB RAM and initially 2 GiB swap, on a host with about 16 GiB physical RAM. With all workers confirmed stopped, added a temporary 8 GiB swap file without increasing physical-RAM allocation. Bitcoin retry tempo-bitcoin-bm25-20261105T073857Z now runs alone, full original corpus/settings. This is a resource repair, not a method change or successful reproduction yet.

TEMPO BGE smoke tempo-iota-bge-smoke-001 completed unchanged native FP32/batch128 inference on two queries and all 10,372 Iota documents. Offline evaluation completed; NDCG@10 0.37875 is a smoke value, not full-domain reproduction. Measured Torch peak allocation 7,796,289,536 bytes. Source/settings pre-review exists; independent post-execution review remains incomplete after reviewer usage limit. Dense full runs remain pending. The running Linux worker version is preserved in worker provenance; the Windows forward revision includes a document-only cache-key correction not yet deployed.

All listed SOTA methods remain in scope, with hardware/source/data limits documented separately. No paid resources, factorial runs, lockbox access or SOTA claim. CPU/GPU memory-heavy jobs must be serialized.
