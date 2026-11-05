# Independent review of the repaired TimelyRAG smoke run

The configured command passed on the local RTX 4060 Laptop GPU. It exercised the repaired environment, author metrics, dataset loader and automatic reranking of four fixed-score examples. R2 numerical reproduction remains pending.

## Observed invocation

One invocation from the Windows project root on 2026-11-04 local time, exactly as recorded in `configs/environment_linux.json` at review time. The command returned exit code 0 after 9.52 seconds. The Linux report was written at 2026-11-05 01:25:44.919551690 UTC. The harness did not record a separate UTC start timestamp.

```text
wsl -d Ubuntu-24.04 -u nigel -- /home/nigel/miniforge3/envs/timelyrag-repaired/bin/python /home/nigel/acl2027/scripts/smoke_timelyrag.py
```

The output included eight completed one-query progress bars and these two lines:

```text
WITNESS (8, 8) NVIDIA GeForce RTX 4060 Laptop GPU
PASS: metric vectors, four full data schemas, GPU witness, candidate invariance, and automatic gold independence.
```

WSL output `/home/nigel/acl2027/reports/smoke_checks.json` has SHA256 `f02b8dfcd394f7ec93cd666702a2f0b6847c659fdcece78936c7ad6f7da06e83`. The executed smoke script and Windows source both hashed to `f59536d9dd6c678a15167c41bd4fce297de9f7a323efad2f0fb1439b7b568ea2`. The witness ran on PyTorch 2.3.1+cu121, CUDA 12.1 and NumPy 1.26.4. The report lists four JSONL files, each with 3,000 queries and 30,000 unique document IDs. All four SHA256 values match the individual archive members in `manifests/upstream_audit.json`.

## Repair integrity and records

The pristine Linux vendor HEAD was `5213a0c1743f23fd52a258005c3887aaf7e8cd0f`. Its tracked diff was empty. The repaired HEAD was `61059193d176190df4a530805ca5cb328e30cbb8`. Its status listed only the untracked extracted `datasets/` directory. The complete base-to-repaired diff has five one-line replacements across three files: Notebook 7.2.1 → 7.3.1, the University filename, and three top-level metric imports in `pipeline.py`. The upstream retrieval, alpha, temporal-scoring and metric implementations match the base commit. The full WSL patch at `/home/nigel/acl2027/reports/repair.patch` hashed to `5f47fc5c85355e8ec8858979cb3788bbd44438ae3ffcc8bc18393f20540a33a6`. The workspace’s earlier `reports/setup/repair.patch` documents only the Notebook change.

At inspection, `reports/setup_status.md` and `reports/progress.md` still listed dataset placement, imports and smoke as next work. The verified repairs and this successful invocation supersede those entries. Historical failures remain valid: exact pip resolution first failed on `mkl-service`, then on the author-pinned Notebook/JupyterLab conflict after the conda prerequisite. Under the repaired environment, the unchanged runner failed at the first dataset open. The relative imports were identified by inspection. This command calls `evaluate_2stage` directly, so it does not demonstrate a successful call to the repaired `pipeline.py` entry point.

The repair script accepts any descendant of upstream, stages whole files, and skips existing extracted targets. Its success message alone cannot establish the actual diff or byte identity. Both checks succeeded independently for this checkout. A reusable repair command also needs the patched Notebook requirement as an input or prior step: the script stages `requirements.txt` but never makes that edit itself.

## What the tests establish

- The GPU completed a finite 8×8 matrix product. The script initializes neither BM25 nor BGE-M3. It provides no checkpoint verification, encoder precision check, throughput for real data, or peak VRAM measurement.
- The metric checks covered perfect, zero-overlap, and one partially retrieved gold set. They demonstrate the author nDCG/AP behavior on those examples. The standard nDCG assertion compares a formula for one vector to a constant; there is no separate standard metric implementation under test here.
- The data assertions operate on the loader’s normalized IDs. The loader can synthesize missing IDs or skip invalid gold references. The prior independent archive audit is the evidence for original ID integrity. The loop has no assertion that all four expected filenames exist or match frozen hashes. An empty glob could print PASS on a later run. The four observed names and matching hashes establish coverage for this invocation.
- One first query from each domain received descending synthetic base scores across all 30,000 IDs. The smoke compares the first metric call’s auto-ranked IDs before and after replacing `positive_ids`. Both lists matched within each domain. That check establishes observed invariance to those label substitutions. The loader also carries the original labeled `raw_item`, and `evaluate_2stage` reads gold and evaluates the diagnostic best-alpha oracle in the same process. Inference-side label isolation requires a separate label-free interface and evaluation process.
- The candidate check establishes that the observed auto output is a subset of the first hundred IDs for each synthetic fixture. It does not assert ten unique output IDs, check full candidate identity and order, freeze either retriever’s real top-100, or measure candidate recall. The reported cutoff and tie behaviors are source-inspection statements; this invocation had no targeted cutoff or tied-score fixture.

## Before full baselines

Keep R1 classified as exact dependency resolution failed, repaired smoke passed. Before R2, pin the accessible model snapshot and verify the actual encoder on representative lengths with measured elapsed time and peak VRAM. The local GPU has 8,188 MiB. Separate label-free automatic rankings from evaluation and oracle diagnosis. Capture per-query rankings, scores, runtime, input/model hashes and exact matched settings. Keep author metrics distinct from standard metrics and freeze a category mapping for the historical Company comparison. Full per-domain runs and discrepancy analysis against published cells still determine numerical parity. This review executed no full retrieval, downloaded no models and produced no research score.

## Pre-deployment code review of the proposed real-BGE runner

Read-only review of `scripts/run_timelyrag_baseline.py` against the pinned provider source. The first revision (`ae54ec98627d6a1724edd7ce6c719ea081dcbe2600ba2db74aa865a779966378`) would emit the oracle winner twice, once under its proper label and again as an automatic prediction: `evaluate_2stage` scores its final best ranking after the grid returns. The summary would reject the duplicate automatic rows after GPU execution. This was a finding from the code paths, not an observed failed GPU run.

The revised file (`babb50dfede95a29af692436f639549c1900bbbf7be04b17c3d818f6bccaff03`) checks the identity of `reranked_auto_gids` inside the pinned upstream evaluator. Inspection confirms that a baseline is emitted in `run_pipeline`, auto is emitted from that precise evaluator call, and only the oracle wrapper emits `oracle_best`. It now enforces all six expected methods and unique method/query pairs, repeated candidate ID/score identity, top-k length and uniqueness, candidate-pool membership, GPU capacity, interpreter path and actual K/pool settings. Query association follows the pinned runner’s sequential iteration order and checks the query text against that ordinal. The separate binary nDCG and AP formulas use all unique positives up to k; they are appropriate for validated unique predictions. Check `[a,x]` vs `[a,b]` and a zero-overlap example before using these implementations for reported results.

The selected BGE-M3 commit resolves on the publisher’s host. The filters include the main checkpoint, both projection heads, tokenizer artifacts and configuration. The installed M3 implementation loads tokenizer and model weights from the supplied directory. The proposed runner records file hashes after downloading. This review checked model metadata only. [Pinned model file list](https://huggingface.co/BAAI/bge-m3/tree/5617a9f61b028005a4858fdac845db406aefb181)

**Decision for this revision: hold execution against true labeled inputs.** `--smoke` copies two complete records, including their answers and gold fields. Upstream passes both `positive_ids` and the entire labeled `raw_item` to `evaluate_2stage`; its oracle reads those labels in the same process as the retrievers. Replaying the author evaluator this way can demonstrate how its code behaves on released benchmark labels. Project rules also require gold labels to be inaccessible to inference, and protocol §2 applies that invariant to each run. Disclosure and the fixture’s observational auto independence do not implement that boundary. This is an execution gate even if the results are only feasibility measurements.

A compatible design can keep the pinned author scoring formulas and reranking intact. Stage sanitized inputs and keep both raw JSONL and its archive unreadable by the inference worker. Capture baseline and automatic rankings before a separate evaluator sees real labels. For an optional faithful diagnostic, capture the ordered grid rankings without real labels and use the offline evaluator to select the first strict maximum under the author nDCG, as in the pinned oracle. Record the input projection, access checks, and separation as repaired/instrumented replay. A label-free encoder feasibility smoke can proceed independently.

Remaining full-run manifest checks include verifying the exact repaired SHA and input hash against the preregistered artifacts before model work, finalizing the manifest on preamble failures (`pip freeze` sits outside `try`), and distinguishing the score-wrapper’s base scoring time from total automatic per-query latency. The smoke and full corpus also require explicit expected query/document counts. Keep ground-truth, raw prediction, and model artifacts local. No real-BGE runner was executed as part of this review.
