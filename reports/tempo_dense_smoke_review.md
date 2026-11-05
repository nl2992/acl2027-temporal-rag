# TEMPO dense smoke review

## Pre-deployment review

The reviewed smoke run is `tempo-iota-bge-smoke-001`: the first two Iota queries, all 10,372 original documents, and the released exclusion lists. Preparation recorded no duplicate document IDs, missing positives or missing exclusions. Input SHA256 `031fcf928c428a01343e0f064e050838848c5cdffac21b111c78557e9c42e5aa`; dataset revision `1dba7027d0afa628993c6dd794e9b68c657a6fac`. Trusted staging leaves positive IDs, answers and the raw dataset behind the access boundary. UID 1001 starts at `/`. The launcher masks Windows mounts, raw data and evaluator results. Both Hugging Face and Transformers are offline inside the worker.

The TEMPO source was frozen at `8731487254e0988eaf2ca4ae3e93ff587fec64d0` and the separate repaired worktree was clean at `4bd4324017810ebede72492a3ed869910d668fa7`. Extracted source text has identical SHA256 in both trees for `retrieval_sbert_bge` (`854ecd924e7f8f25aa57db24ebc1dc32c6ce437f4c78f74b60bbbe23e8f79405`), `retrieval_contriever` (`f517e6214c79172507e185fde9a664992f3fd276d243c2079ed7b6b27cd084a9`), `get_scores` (`e4030154f3d68f89dd0fdb16bd8e3d1a907f851c90cd09ec3fd6aa1b58880ff4`), `add_instruct_concatenate` (`2dfce11c7201c3bb7cf5d3de01fd20caba2a0dafe15dd4880c9bc05b4686b2c7`) and `calculate_retrieval_metrics` (`ee4326476acd1826e1975552e58961629ba33ec793d5a95e44692aae41434668`). Worker script SHA256 `f098fb069b2fe18c270ea5554be5ccaf8cd9e720fbc20ec860cdb75318214705`; shell SHA256 `aac2b9e76cfb6b925aa0be3fee4ab81d02a97144863a3c3baedf3f536d35187a`.

`run.py` uses its fallback `Represent this query for retrieving relevant documents: ` including one trailing space, plus an empty document instruction. Both checkouts lack model instruction config files. BGE prepends that string to queries; SBERT and Contriever use plain queries. The two SentenceTransformer branches encode at the author default batch size 128 with normalized embeddings and cosine scoring. The staged BGE checkpoint specifies CLS pooling and 512 tokens; staged SBERT specifies mean pooling and 384 tokens. Contriever uses the author’s mask-weighted mean pooling and L2 normalization, batch size one, explicit CUDA placement and tokenizer truncation (staged tokenizer limit 512). All paths remove official exclusions, retain descending original scores and return up to 1,000 documents. Only BGE execution belongs to this review. SBERT and Contriever have source/settings checks only.

The staged revisions are BGE `d4aa6901d3a41ba39fb536a557fa166f842b0e09`, SBERT `e8c3b32edf5434bc2275fc9bab85f82640a19130`, and Contriever `abe8c1493371369031bcb1e02acb754cf4e162fa`. The worker verifies every active model file’s recorded SHA256, then routes the author constructor to that local snapshot. The original precision, pooling, batch and normalization settings are passed through. The model registry SHA256 is `49fd9c91d3c921c1194ca23f3dac2754f199d34e6fe2a1f3a9aa7460ddf91951`.

## Execution

The RTX 4060 Laptop GPU was idle at 10 of 8,188 MiB immediately before launch. The only listed retrieval worker then was a CPU BM25 job. No change was made to that job. The exact BGE smoke invocation was:

```text
wsl -d Ubuntu-24.04 -u root -- unshare --mount --fork bash /home/nigel/acl2027/scripts/isolated_tempo_worker.sh --run-id tempo-iota-bge-smoke-001 --model bge
```

The worker reported a cold cache and started 82 document encoding batches. A live device sample during early batches showed 7,820 of 8,188 MiB in use and 100% utilization. That sample is a device-wide observation, separate from the process’s PyTorch peak allocation.

## Cache scope

The cache descriptor includes the projected dataset hash, model and tokenizer pins, repaired retrieval source hash, prompt, cutoffs, native batch/sequence/precision defaults and key software versions. It also includes the query list and smoke flag through the full input hash. Taking all ten Iota queries would change the key even though it would reuse these same 10,372 documents. This can cause a second full encoding. A document-only reuse key would require a hash of the ordered document IDs and contents with the existing model/configuration constraints, preserving the separate full-input hash for run provenance.

## Execution outcome recorded by root (2026-11-05)

Saved worker status is complete, 2 queries/10,372 documents, elapsed retrieval677.136964 seconds, Torch peak7,796,289,536 bytes. Root ran the trusted offline evaluator after confirming worker exit; NDCG@10=0.37875 (smoke only). Aggregate manifest/summary exported under reports/tempo/tempo-iota-bge-smoke-001. The reviewer hit an account usage limit before post-execution review; this addition is an executor observation, not independent approval. Full dense deployment still needs that gate.
