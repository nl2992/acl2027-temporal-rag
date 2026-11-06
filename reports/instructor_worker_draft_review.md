# TEMPO INSTRUCTOR-L worker source review

**The corrected draft passes the CPU source preflight. Its Linux launcher, real model load, two-query/full-corpus smoke and offline evaluation are pending.** A fresh Codex reviewer performed this review on 2026-11-05 under the experiment-bridge/run-experiment preflight workflow. The semantic review is same-family provisional. The fixture results below apply to the identified source bytes.

## Evidence and repair

The reviewer compared the generated draft with the frozen worker, reproduced the builder output in a temporary directory and ran the fixture from the repository root with `python -IB reports/review_tools/verify_instructor_draft.py`. The final invocation exited 0 on Windows with Python 3.13.1, NumPy 2.4.2 and scikit-learn 1.6.1. The helper checked that Torch, Transformers and SentenceTransformers were absent from its imported modules. Its temporary caches contain only synthetic vectors and IDs.

| Artifact | SHA256 |
| --- | --- |
| Frozen worker and trusted evaluation entry point | `9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee` |
| Initial draft with late precision check | `974207548ab0d7fd1675f41594db0f64267c6a1077e8c0f3afa0aedb7db4ddfc` |
| Corrected draft | `88e1a336534abd8abdf91cf06eace91d4fc25661a9911d86de3c7fb1976b16cd` |
| Corrected builder | `391a48e6427946acacc00a0177e12a534ada99ca94346794ab11f297756f1f30` |
| Corrected unified patch | `9818ed3f672748cef182778f93890a2e5d5360b98b4b3f263585acafbe8639f0` |
| CPU fixture | `61fa647f00c3e0774e823115f8c2ce9bb1b32b594db99a15816cf259b8297d3c` |

The initial draft's FP32 check came after native retrieval had persisted document embeddings. A fake FP16 encoder reproduced the failure and left an FP16 `embeddings.npy` in the nominal FP32 cache. The correction checks the model's observed parameter dtype immediately after construction. On the same fixture it rejected the model before any embedding file was written. The helper also reconstructs the initial candidate in memory, verifies its SHA and reproduces the original failure. Git attributes now pin draft scripts to LF and preserve the patch bytes on this autocrlf-enabled Windows checkout.

## What the fixture verified

- It extracted `retrieval_instructor` and `get_scores` directly from the Git blob at TEMPO commit `8731487254e0988eaf2ca4ae3e93ff587fec64d0`. It used the draft's actual `local` and `sentence_transformer` functions, a fake encoder, a no-op stand-in for the no-grad decorator, and scikit-learn's cosine similarity. Separate plain and observed runs each started with empty caches. The unwrapped constructor received the upstream repo ID and the observed constructor received its staged snapshot path.
- Two synthetic queries scored 1,004 synthetic documents, including ties at the top-1,000 cutoff, real exclusion-shaped IDs and the upstream `N/A` sentinel. On both cold and warm paths, the exact ordered ID/score pairs matched the plain native path and the independently derived synthetic expectation. Both queries returned 1,000 IDs. The document embedding array and ID mapping were byte-identical across the two paths.
- The fake constructor reported a 512-token limit. At every encode the observed limit was 2,048, batch size was 4, normalization was enabled, progress enabled and pooling excluded prompt tokens. The fake encoder received the same texts and arguments with and without the hook. Cold call sizes were 1,004 documents then two queries. Warm reuse called the encoder for the two queries only. The document prompt was empty. The query prompt was the released fallback including its trailing space. A warm query profile witnesses the query encode. The original cold run is the evidence for how cached documents were encoded.
- The draft's actual cache descriptor expressions used the Inst-L model/tokenizer revision, 2,048-token limit, batch 4, prompts, ordered ID/content fingerprint, backend versions, source hash and exclusion policy. With fixed package/source inputs, changing only queries retained the key. Reordering documents or changing content changed it. The fixture supplies synthetic source/version values to these expressions. It never inspects production embeddings.

## Linux source and checkpoint

A read-only standard-library probe under WSL `acl-infer` (UID 1001) read the staged metadata and checked read permission on all 12 selected snapshot paths. Its sorted compact JSON digest was `622ff71f899545bb9178dc1f379775b1b0392d7b7412d9b09c237722807c4ed9`, identical to the archived checkpoint manifest. The worker pins `hkunlp/instructor-large@54e5ffb8d484de506e59443b07dc819fb15c7233` and hashes the listed files before real use. This review observed staging metadata and permissions. File-content verification was performed by the earlier stager and remains a required worker check. The author's historical weight revision is unspecified.

Linux native `retrievers.py` had SHA256 `90169e77aec737c238df9d682833379404d2e4381b074d43495c22bebaae27e4`. The clean repaired checkout at `4bd4324017810ebede72492a3ed869910d668fa7` had file SHA256 `b207b0d61130b01a9b3c31215c6a5d66cdb8f4b8b83b579898979850639310e4`. Python 3.10.22 gave identical full function ASTs in the two files, including the decorator. The AST SHA256 values were `f878a87115783e3b8d26dfe99e0cd14829d52a53123cb0c5065f6f1829e4a776` for `retrieval_instructor` and `ebb30a444f6d0725dcac6bb42ed3e519d3149946b25f49f4899004fd7d950c02` for `get_scores`.

The installed distribution metadata reported Torch 2.14.1, Transformers 4.40.0, SentenceTransformers 3.1.1 and NumPy 1.26.4. Inspection of the installed SentenceTransformers source confirmed the sequence-limit setter updates the first module, and the pooling setter updates the first Pooling module. The exact-repo-name constructor shortcut for INSTRUCTOR can differ when loading a local pathname. Native TEMPO explicitly calls the pooling setter after construction, before either encode. The staged model declares one Pooling module. Real tokenization, encoding and peak memory require a runtime witness.

The following PowerShell command rechecks the supplementary Linux hashes and access using the existing environment and source files.

```powershell
@'
import ast, hashlib, json, os
from pathlib import Path
from importlib.metadata import version
root = Path("/home/nigel/acl2027")
staged = json.loads((root / "reports/instructor_source/staged_snapshot.json").read_bytes())
print(os.getuid(), staged["repo"], staged["revision"], len(staged["files"]))
print(hashlib.sha256(json.dumps(staged, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
assert all(os.access(Path(staged["snapshot"]) / n, os.R_OK) for n in staged["files"])
for folder in ["Tempo", "Tempo-repaired"]:
    source = (root / "vendor" / folder / "retrievers.py").read_bytes()
    print(folder, hashlib.sha256(source).hexdigest())
    for f in ast.parse(source).body:
        if isinstance(f, ast.FunctionDef) and f.name in ("get_scores", "retrieval_instructor"):
            print(f.name, hashlib.sha256(ast.dump(f).encode()).hexdigest())
for p in ["torch", "transformers", "sentence-transformers", "numpy"]:
    print(p, version(p))
'@ | wsl -d Ubuntu-24.04 -u acl-infer -- /home/nigel/miniforge3/envs/tempo-native/bin/python -IB -
```

## Gates for a real smoke

1. Integrate a separate launch path and verify deployed bytes under the actual namespace. The present BGE launcher selects its frozen worker and checks a shared worker/evaluator identity. The future caller must verify the draft against the inference SHA and the trusted evaluator against `9f0e…` separately, and include the new process name when testing for active jobs.
2. The draft inherits the frozen projection checks for `{id,query,excluded_ids}` and `{id,content}`, denied-path probes, and the unchanged offline evaluation function. The existing trusted stager projects upstream `negative_ids` as author exclusions and keeps gold IDs outside the inference input. Recheck non-root UID, cwd, denied paths, fresh run IDs, offline environment and pinned model/source inside the future isolated launch. Linux snapshot readability above was checked outside that namespace.
3. After the active GPU queue releases the device, use a fresh cold Inst-L cache for two Iota queries and the full original corpus. Capture constructor, encode-time settings, prompts, dtype, cache membership, rank coverage, runtime and peak allocation before considering bigger runs. If initialization or encoding fails, retain its log and inspect any partial cache before reuse.
4. Run the separate trusted evaluation through same-process witness `414345f385faab91f48b1a7ae631458047bfe9d757cc7947b991df8800f1b0a3` around frozen evaluator `9f0e…`. Verify exported manifest, summary, runtime/source identity and provider evidence before recording a measured result. This draft review added no benchmark metric, feasibility measurement or reproduction credit.
