# TEMPO Law preflight recovery review

**PASS, 2026-11-05 18:32 UTC.** The BGE queue may skip the single recorded pre-preparation failure `tempo-law-bge-20261105T170234Z` when admitting a new attempt under the established single-owner resource gates. The failed attempt still has no measured cell. The fresh component reviewer was `/root/evaluator_preflight`, Codex native, requested GPT-6-Astra xhigh, same-family provisional. This review started no queue, evaluator, or model.

| Reviewed component | SHA256 of observed Windows bytes |
|---|---|
| `scripts/run_tempo_bge_suite.py` | `b408ef89f2ed80cb08636d3ebc823f07639ba495b64d532650f078d8de2c2a08` |
| `scripts/record_tempo_preflight_recovery.py` | `8e47e5f7fc9e3cdc088732dd5a0ccb752b9106200ea2b7e2ccb3884b6f1df294` |
| `reports/tempo_preflight_recoveries.json` | `80d1df2afa16798ab1cfc94d780a14eb1e8b96ba0279a5e7f83b5c0d9e386795` |
| `reports/tempo_evaluator_witness_deployment.json` | `e345fa942c634a3d7503db50c5fcb1a10e0e26696b3649ef53a7a898f9d11a75` |

The receipt generator pins the Law ID, runner and wrapper, checks the original failed launch, sees exactly two local files and refuses to replace an existing receipt. The saved receipt has exactly one entry. The queue rechecks both original file hashes, the reviewed Windows runner, the deployed Linux wrapper and all four per-run directory absences. It skips only an entry without a manifest. Complete-run admission, duplicate rejection and the existing domain/resource gates still apply. See `scripts/record_tempo_preflight_recovery.py:8–38` and `scripts/run_tempo_bge_suite.py:18–41,53–91,115–126`.

**Executed admission checks.** Windows CPython 3.13.1, normal unoptimized mode, PowerShell `python -B -`. To avoid dispatch, the reviewer parsed the queue with Python's AST and loaded only import, assignment and function-definition nodes. Calling `resolved_without_computation` on the actual failed directory returned true. The four real `wsl -d Ubuntu-24.04 -u root -- test -e <receipt path>` calls returned 1, and the deployed wrapper rehash matched. Calling `completed('law')` returned an empty list. Calling `completed('iota')` and `completed('quant')` returned exactly their respective registered handoff IDs.

With copies of the failed launch and patch in Windows TEMP, the check rejected an altered launch, altered source patch, extra inference log, unknown ID and bad deployment digest. For each of the four paths, both a reported existing path and a non-1 probe error caused rejection. Mutating each run-ID, stage-start flag, script digest, file digest or checked-path list in the in-memory receipt also prevented admission.

**Idle probe repaired.** The initial reviewed queue `b1c257d026248fd320d5d92c435e3c8316c049501814417aba11d77b3c496e4e` omitted the new wrapper process from its idle check. The final queue's `pgrep -f` pattern now includes `tempo_evaluate_with_provenance.py`. Source-extracted regex checks matched the actual wrapper invocation format for BGE, BM25, the Iota handoff and wrapper deployment. The earlier single-owner condition still applies. This exception adds no historical provenance, author-metric evidence or queue completion claim.
