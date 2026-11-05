# Local limits and later rental readiness

User direction (2026-11-04): continue locally, document limits, and consider renting a GPU later. No paid resource has been started or reserved.

## What the local machine has demonstrated

- RTX 4060 Laptop GPU: 8,188 MiB. WSL has approximately 7.6 GiB system RAM and 2 GiB swap.
- Pinned FP16 BGE-M3 passed a real two-query smoke. Full Company document encoding completed without a changed batch-size or model-precision setting. Full-run query evaluation remains in progress.
- Four full BM25 domains completed on CPU. Full dense domains are queued one at a time on the single GPU.

## Remaining method requirements

Official model metadata inspected on 2026-11-04:

| Method component | Pinned checkpoint revision | Weight-file bytes | Local implication |
|---|---|---:|---|
| TEMPO DiVeR 4B (`AQ-MedAI/Diver-Retriever-4B`) | ff7f8bc8d1827734dcf2bbfab99f065be618069a | 8,043,594,472 | Native vLLM reserves 90% of this GPU; weights alone exceed that reservation, before cache/activations |
| FRESCO default reranker (`Qwen/Qwen3-Reranker-8B`) | 77d193c791ed757ca307ee72715aa132723da912 | 16,377,142,272 | Weight files exceed local VRAM |
| FRESCO default gradient model (`meta-llama/Llama-3.3-70B-Instruct`) | 6f6073b423013f6a7d4d9f39144961bfbfbc386b | 141,107,497,872 | Exceeds local GPU memory, RAM and currently free disk |

These are weight-size/implementation preflight constraints, not measured OOM traces. Quantization, CPU offload, smaller-model substitution, or changed memory fractions would be separate experimental tracks and cannot be called an exact default reproduction.

Sources: official model metadata at https://huggingface.co/AQ-MedAI/Diver-Retriever-4B , https://huggingface.co/Qwen/Qwen3-Reranker-8B , https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct ; code in the pinned TEMPO/FRESCO checkouts. No gated model authorization has been assumed.

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
