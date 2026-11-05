# Local limits and later rental readiness

User direction (2026-11-04): continue locally, document limits, and consider renting a GPU later. No paid resource has been started or reserved.

## What the local machine has demonstrated

- RTX 4060 Laptop GPU: 8,188 MiB. WSL has approximately 7.6 GiB system RAM and 2 GiB initial swap, plus an 8 GiB temporary swap file when activated.
- All eight full P0 backbone/domain runs completed. Base retrieval matches the prescribed nDCG tolerance; six automatic TimelyRAG cells miss. This is partial repaired reproduction.
- TEMPO BM25 completed all thirteen domains with ordinary nDCG matching published rounding. BGE Iota/Quant completed; Law and the remaining dense domains run sequentially. Temporal judge metrics remain unmeasured.

## Remaining method requirements

Official model metadata inspected on 2026-11-04:

| Method component | Pinned checkpoint revision | Weight-file bytes | Local implication |
|---|---|---:|---|
| TEMPO DiVeR 4B (`AQ-MedAI/Diver-Retriever-4B`) | ff7f8bc8d1827734dcf2bbfab99f065be618069a | 8,043,594,472 | Native vLLM reserves 90% of this GPU; weights alone exceed that reservation, before cache/activations |
| FRESCO default reranker (`Qwen/Qwen3-Reranker-8B`) | 77d193c791ed757ca307ee72715aa132723da912 | 16,377,142,272 | Weight files exceed local VRAM |
| FRESCO default gradient model (`meta-llama/Llama-3.3-70B-Instruct`) | 6f6073b423013f6a7d4d9f39144961bfbfbc386b | 141,107,497,872 | Exceeds local GPU memory, RAM and currently free disk |

These are weight-size/implementation preflight constraints, not measured OOM traces. For the vLLM defaults above, adding CPU offload, quantization, smaller checkpoints or changed memory fractions would alter the released setup. Other TEMPO backends already request automatic placement; their native policy must be assessed separately below.

Sources: official model metadata at https://huggingface.co/AQ-MedAI/Diver-Retriever-4B , https://huggingface.co/Qwen/Qwen3-Reranker-8B , https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct ; code in the pinned TEMPO/FRESCO checkouts. No gated model authorization has been assumed.

## Native placement policies needing a local pilot

Source inspection at TEMPO SHA `8731487254e0988eaf2ca4ae3e93ff587fec64d0` shows E5, SFR and Qwen use `device_map="auto"` with BF16, and RaDeR uses it with FP16. The released functions do not force the complete model onto CUDA afterwards. Automatic placement can span GPU and CPU, with disk dispatch depending on the loader and storage conditions. [Official Accelerate documentation](https://huggingface.co/docs/accelerate/usage_guides/big_modeling)

These methods remain **conditional native local pilots**, not measured failures or verified local successes. Weight size exceeding VRAM alone is insufficient to decide their feasibility. Preserve the original dtype, model, batch/length defaults and automatic map; record the actual resulting map, host RAM/swap, GPU peak, output-file needs and measured throughput. A pilot must also assess the full-corpus embedding/scoring buffers; a successful model load does not prove all thirteen domains fit. No large checkpoint or pilot was started by this source audit.

ReasonIR explicitly moves its model to the source-selected device (CUDA on this host). The installed GritLM 1.0.2 wrapper also defaults to CUDA and moves the model there when no map/quantization override is supplied; TEMPO supplies neither. Those policies are distinct from the automatic-map branches. See `manifests/tempo_placement_source_audit.json`, author `retrievers.py:86–107,1443–1455,1510–1516`, and the installed GritLM source observed at SHA256 `f0a8cd72e7f4566158b92af5950a4d0249f1eb9a6703e5bf710eec3003e8f9ac`.

## Prerequisites before spending on a rental

1. Finish the available local baseline suite and establish numerical discrepancies before renting hardware to repeat a non-reproducible pipeline.
2. Resolve official Re³ and Q-TIE source/checkpoint availability; larger hardware does not repair 404 repositories.
3. Obtain a frozen, licensed FRESCO evaluation dataset and correct its broken orchestration references. Check Llama model access independently.
4. Prepare each independent environment and a small CPU/data validation before a GPU instance is started. Freeze source/data/model hashes and exact commands.
5. Calculate model/cache/activation capacity from the actual selected run. FRESCO's default code launches both models and sets each memory fraction to 0.45; sizing only one checkpoint would understate the requirement.
6. On a candidate host, run a small pilot, measure throughput and peak memory, then estimate duration and cost. No speculative hourly-price or total-cost claim is supplied before choosing a provider and measuring a pilot.
7. Start a paid instance only after the user requests that concrete rental. Save output paths and a shutdown plan before launching experiments.

## Observed local system-memory limit (2026-11-05)

Bitcoin BM25's first full attempt was killed137 by Linux OOM while a native BGE smoke also ran. This is a measured system-memory failure, distinct from the larger-model VRAM preflight limits above. Host physical memory is approximately16GiB; WSL sees7.6GiB with2GiB initial swap. After workers finished, added8GiB temporary file swap (/swap-research; chmod600; mkswap; swapon), leaving physical-RAM allocation unchanged. No WSL shutdown or persistent configuration edit was needed. Native BGE smoke completed FP32/batch128, peak Torch allocation7,796,289,536bytes; its close VRAM fit does not establish larger-corpus system-memory feasibility. Retry Bitcoin runs alone; remaining large BM25 corpora are queued sequentially. Swapping can substantially slow runs; timings must describe the resource repair and cannot be compared as algorithm-only speed measurements. Temporary swap must be revalidated after a WSL restart.
