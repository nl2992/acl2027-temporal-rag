# TEMPO evaluator provenance preflight

**PASS for the forward component at the reviewed hashes, 2026-11-05 18:27 UTC.** A valid synthetic evaluation preserved the exact summary bytes. Both parity reporters excluded failed exports, including synthetic leftovers with an otherwise complete manifest and summary. The prior revision admitted these leftovers and was held until repaired. The historical integrity audit retains its WARN. This review supplies component-level evidence only. Each future benchmark run requires its own recorded witness.

The fresh review used the experiment-bridge/run-experiment route supplied by the coordinator, Codex native, requested GPT-6-Astra at xhigh effort, agent `/root/evaluator_preflight`. No independent runtime model string was supplied. Semantic acceptance is same-family provisional. The review included inspection of the project rules, original protocol, prior audit, local source and byte hashes, and a synthetic CPU regression. The reviewer ran no Linux evaluation, benchmark, encoder, model download, or installation.

## Accepted source bytes

Observed from the Windows working tree, project HEAD `13a200d8a937834e6372133a3aed7f93004b0a72`. Hashes below identify the actual bytes, including changes outside HEAD.

| File | SHA256 |
|---|---|
| `scripts/tempo_evaluate_with_provenance.py` | `414345f385faab91f48b1a7ae631458047bfe9d757cc7947b991df8800f1b0a3` |
| `scripts/run_tempo_wsl.py` | `634604d86d4865495fa3ba9f3f145961801fcc841ee928e049d1525927eaa2b9` |
| `scripts/report_tempo_retrievers.py` | `77b5fbd8c10942198b0f1d254d089c330edc4e5406a613434b088fd873526bfe` |
| `scripts/report_tempo_parity.py` | `42ee5a86bf29756975988afc87293953227764855af9a1376baecf5623551404` |
| Frozen `scripts/tempo_isolated.py` | `9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee` |
| `scripts/isolated_tempo_worker.sh` | `aac2b9e76cfb6b925aa0be3fee4ab81d02a97144863a3c3baedf3f536d35187a` |
| `reports/review_tools/verify_tempo_provenance_wrapper.py` | `9aa83c867ac51e98ab323fe5e4afdb007c59f2d287bddee357c657bfb7d9fc8f` |

The historical audit identifies upstream TEMPO `8731487254e0988eaf2ca4ae3e93ff587fec64d0` and repaired revision `4bd4324017810ebede72492a3ed869910d668fa7`. The BGE queue separately checks the deployed repaired retrieval file's bytes before inference (`scripts/run_tempo_bge_suite.py`, `RETRIEVER_SHA` and `preflight`). This component review did not change either source.

## What passed

- **Metric path and CLI.** The wrapper selects exactly one of a run ID and describe-only mode. In evaluation mode it executes the frozen file in the same interpreter with `evaluate --run-id <id>`. The frozen evaluator authenticates the staged score/label files, forms binary qrels, calls the released routine and writes the ordinary/diagnostic summary. The wrapper reads that summary and checks its digest before and after attaching metadata. In a synthetic run the output equaled the expected bytes and both copies of the witness agreed. The stub checked the exact forwarded argument list. See `scripts/tempo_evaluate_with_provenance.py:53–88`, `scripts/tempo_isolated.py:97–123`, `vendor/Tempo/retrievers.py:1084–1173`.
- **Provider identity.** The witness records the full resolved paths and SHA256s of the loaded `pytrec_eval*` modules, candidate distribution versions, each applicable RECORD entry's algorithm/value and byte match, and the evaluator class MRO. The same-process observations bracket the real evaluator entry point. In a synthetic import with two overlapping distributions, both imported files matched precisely the designated provider and both failed the other provider's RECORD comparison. Describe-only succeeded before the fixture result directory existed. Absolute paths, import digests and matching records are the evidence for future attribution. A describe-only sample describes its own process. See `scripts/tempo_evaluate_with_provenance.py:24–70`.
- **Source and failure checks.** The runner compares all three deployed scripts with the starting hashes and checks the wrapper again immediately before and after the evaluation stage. The wrapper checks its evaluator entry and own source at the run boundary. Mutating a synthetic entry, wrapper or imported module caused failure. The runner rejected deployment mismatch before preparation, a change before the evaluator, and a change after it. Independent bad entry SHA, wrapper SHA, run ID, same-process flag, summary bytes, unequal witnesses and absent witness all produced a failed launch. See `scripts/run_tempo_wsl.py:24–26,41–81`.
- **Export and completion.** All three source byte strings are fetched before publication. Run ID, runtime object equality, expected wrapper and entry-point digests, same-process flag and summary digest must agree. The runner publishes via same-directory replacements, with the manifest last and the completed launch status after that. Both reporters require a matching successful launch. Git treats the binary-sensitive runtime export as `-text`. See `scripts/run_tempo_wsl.py:28–32,70–92`, `scripts/report_tempo_parity.py:8–19`, `scripts/report_tempo_retrievers.py:12–28`, and `.gitattributes`.
- **Duplicate IDs and interruption.** A repeated successful run ID was rejected with the original synthetic outputs intact. The frozen evaluator exclusively creates its result directory. If a real evaluator stops after that creation, the Linux directory can contain partial files and the same ID cannot be used for an in-place retry. The Windows launcher also reserves the report directory exclusively and requires successful stage exits. Preserve failed attempts and investigate before starting any new run ID. See `scripts/tempo_isolated.py:111–115`, `scripts/run_tempo_wsl.py:19–21,65–92`. The wrapper atomically replaces the augmented manifest. Its separate Linux runtime file and original evaluator output become accepted together through the runner's checks.
- **Gold boundary.** Describe-only does module inspection. Only the trusted post-inference Linux stage executes the wrapper. The worker still enters the mount namespace as `acl-infer` and checks the public input schema. The trusted evaluator opens private labels only after the worker is complete. This review examined the code paths and historical audit evidence. The synthetic tests had no benchmark labels or predictions. See `scripts/run_tempo_wsl.py:36–39`, `scripts/isolated_tempo_worker.sh:3–15`, `scripts/tempo_isolated.py:22–37,97–110`, historical audit sections A/B.

## Failure reproduced and repaired

The first reviewed runner (`6f8158a36f2c259f17970eb5d02fb10452734903ca9483a5820cc4a66ed46ad8`, lines 67–78) exported a completed manifest and summary before authenticating the witness. For a divergent witness or failed witness copy, launch status became failed, but the initial BM25 and retriever reporters admitted the synthetic run. Each reported one cell. The coordinator changed the runner and both reporter admission gates. The identical two injected failures now expose no manifest. Deliberately restoring a synthetic stale manifest and summary next to each failed launch also resulted in zero cells in both reports.

The earlier real `tempo-law-bge-20261105T170234Z` failure is separate. Its saved launch records a missing deployed wrapper command before preparation. It supplies neither scores nor evaluator evidence.

## Replay and limits

Windows PowerShell, CPython 3.13.1 (MSC v.1942 64-bit), normal unoptimized mode. Fixture files lived in a new Windows TEMP directory for each execution. The fixture loads the actual wrapper with a synthetic evaluator, and executes local copies of the runner and reporters with Git/WSL subprocess calls replaced by controlled synthetic responses. A valid run preserved each exported byte array. Failure injections exercised both reporter loops. No Linux upstream function, installed Linux provider, or operational resource preflight was exercised by these fixtures.

```powershell
python -VV
python -B reports/review_tools/verify_tempo_provenance_wrapper.py
git check-attr text -- reports/tempo/fixture/evaluator_runtime.json
```

The regression command returned 0. The comparison command below returned 1 on the preserved earlier script copies. The folder is a reviewer-local temporary copy. The successful regression command above uses only checked-in path conventions and fixture resources.

```powershell
python -B reports/review_tools/verify_tempo_provenance_wrapper.py --source (Join-Path ([System.IO.Path]::GetTempPath()) 'acl2027-provenance-preflight-source-6f8158a3')
```

Historical evaluator processes have no import-file witnesses. The prior audit independently recalculated 400 ordinary and 96 diagnostic values in its frozen snapshot and identified Terrier 0.5.11's matching files in the environment it inspected. Quant finished after the snapshot. This forward preflight adds no historical provider attribution, score verification for Quant, new result, judge measurement or promotion approval.
