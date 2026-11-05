# Independent TEMPO Iota BM25 smoke review

**Decision.** The repaired BM25 path passed on the first two Iota queries against all 10,372 documents. It is ready for the separate ten-query Iota run, subject to the same completeness and isolation checks. The earlier 30-document smoke failed at the released exclusion step. The official oracle metrics require separate diagnostic reporting.

## Source, data and execution boundary

Pristine TEMPO SHA `8731487254e0988eaf2ca4ae3e93ff587fec64d0`; repaired SHA `4bd4324017810ebede72492a3ed869910d668fa7`. The repaired worktree was clean at inspection. Its diff defers optional vLLM imports. The extracted `retrieval_bm25` function has SHA256 `defa67a4492ca3f4207a7b999bd17c246455d7be72b614bcdb170e38a8e32a08` in both trees. The equal hash for `calculate_retrieval_metrics` is `ee4326476acd1826e1975552e58961629ba33ec793d5a95e44692aae41434668`. The separate TEMPO environment adds missing InstructorEmbedding and uses its own package resolution. This is a repaired replay of released BM25 code. These checks cover the BM25 baseline only.

I matched `stage_tempo_data.py` and `tempo_isolated.py` to the upstream `run.py` calls. The released path uses document `content`, original query text and IDs, explicitly excluded IDs from `negative_ids`, and `long_context=False`. The repaired wrapper calls the same Lucene analyzer, Gensim LuceneBM25Model (`k1=0.9`, `b=0.4`), original tie handling and top-1,000 truncation. Inference receives the official negative exclusion metadata. It receives no positive IDs, answers, or evaluation results. Both private directories were mode 0700. The worker starts at `/` as UID 1001, masks Windows mounts, the TEMPO raw-data cache and the project evaluation results directory, and verifies access probes before loading inputs. The offline evaluator opens gold only after worker exit.

Dataset revision `1dba7027d0afa628993c6dd794e9b68c657a6fac`. Original Iota sizes were 10 queries and 10,372 documents. Parquet SHA256 values are `79eb29454ed69c746eceb508d6f00a0b07fd89d1dce12ee13ade7d86ab26705c` for examples and `ca69f1f551ecf7262ee5bf164504a8fef97b52c96499ba6480bc7a461f8db9c3` for documents. The second smoke’s preflight recorded zero duplicate document IDs, zero missing positive references, and zero missing exclusions. The tested runner hashes were `1d4a9101e00aa2624287da6ae06ae223cd2da43292f1eff72f3508b26470c2d4` (Python) and `7ac1eb7bb08e5dbe5b1febe3d944af5fa53c83f5824b2395f5c759b60e28efb0` (shell). The revised trusted staging script hash was `666bda36d94ea5a10425ff5c3aef10c3f40e1d6b67fd8d1900ab1e8899cc78a2`.

## Recorded runs

The environment was Linux WSL, `/home/nigel/miniforge3/envs/tempo-native/bin/python`, Python 3.10.22, Java 21, Pyserini 1.2.0, Gensim 4.4.0, pytrec-eval 0.5, NumPy 1.26.4, SciPy 1.10.1, Torch 2.14.1, transformers 4.40.0. Retrieval ran on CPU. Each command below ran once.

```text
wsl -d Ubuntu-24.04 -u root -- unshare --mount --fork bash /home/nigel/acl2027/scripts/isolated_tempo_worker.sh --run-id tempo-iota-bm25-smoke-001
wsl -d Ubuntu-24.04 -u root -- unshare --mount --fork bash /home/nigel/acl2027/scripts/isolated_tempo_worker.sh --run-id tempo-iota-bm25-smoke-002
wsl -d Ubuntu-24.04 -u nigel -- /home/nigel/miniforge3/envs/tempo-native/bin/python /home/nigel/acl2027/scripts/tempo_isolated.py evaluate --run-id tempo-iota-bm25-smoke-002
```

1. `001`, two queries and the first 30 documents. Worker exit 1 in 7.44 s. The first query listed 164 distinct non-sentinel exclusions, all absent from this truncated corpus. Upstream called `all_scores[str(query_id)].pop(did)` in `retrieval_bm25` and raised `KeyError: 'iota/2c41700c_0047.txt'`. The worker output directory was empty; the evaluator was skipped.
2. `002`, the same two queries against the complete Iota corpus with all original exclusions. Worker exit 0 after 13.5973 seconds of measured retrieval, finished `2026-11-05T02:26:08.658435+00:00`. Public input SHA256 `031fcf928c428a01343e0f064e050838848c5cdffac21b111c78557e9c42e5aa`; score SHA256 `3214795abd9ca1247cc739490c70e462c0a8ff293360834268a4fbdd6c0518c2`. Each query produced 1,000 distinct, finite scores. Neither ranking contained an excluded ID. The two queries' exclusions and gold references were disjoint.
3. The separate `002` evaluator exited 0. I read back and checked the score, gold and summary hashes, both query IDs, and the 31 output keys: 25 ordinary retrieval metrics and six explicitly named `Oracle NDCG@k` entries for k = 1, 5, 10, 25, 50, 100. These two-query results are smoke evidence only.

## Independent evaluator fixtures

The released evaluator uses pytrec-eval against binary relevance for the ordinary metrics. I tested two synthetic queries: the first returned its only positive at rank 2, and the second returned no positives. It matched handwritten expectations for ordinary nDCG@1 = 0, nDCG@5 = 0.31546, MAP@5 = 0.25, Recall@5 = 0.5, P@5 = 0.1 and MRR = 0.25. Its gold-assisted Oracle nDCG@1 = 0.5. The six oracle metrics were separately labeled.

A second synthetic fixture ranked the only relevant document (`zzzz-outside100`) at position 101 after one hundred higher-scored negatives. Ordinary nDCG@1 and nDCG@100 were zero, but the official `Oracle NDCG@1` returned 1. The implementation gives zero oracle scores to every returned document outside the top 100 and passes them to pytrec-eval; tie ordering can bring that document into the oracle top ranks. This diagnostic therefore cannot establish a strictly top-100-constrained ceiling. Keep its released value for source comparability and label it oracle-only. Any actual candidate ceiling requires a separate metric over the fixed pool.

The ten-query run and all-domain comparisons were outside this review. No model was downloaded and no other active job was modified.
