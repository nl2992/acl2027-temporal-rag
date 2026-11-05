# TEMPO BM25 Bitcoin memory rescue

Reviewed 2026-11-05, 07:44 UTC. Full-domain Bitcoin completed under the repaired local environment after the overlapping dense job ended. Its released BM25 run scored **0.06157 nDCG@10** on 100 queries over 153,291 documents. This rounds to the 6.2% value in the pinned upstream README. The remaining domains need their own completed inference and offline evaluation.

## Failure and retry

| Run | Evidence | Outcome |
|---|---|---|
| `tempo-bitcoin-bm25-20261105T024849Z` | Full preparation completed. Inference ended with `Killed` and exit 137 at 02:54:46 UTC. The original session recovered a global kernel OOM kill of Python PID 7222, UID 1001, with 6,156,896 KiB of anonymous resident memory (5.87 GiB). The previous boot's kernel journal was unavailable for independent replay. | Failed during inference with 7.60 GiB guest RAM and 2 GiB swap. No ranking or evaluation established. |
| `tempo-bitcoin-bm25-20261105T073857Z` | Inference ran alone on the same published corpus. Launch, worker, and evaluation manifests report completion, with the aggregate summary checksum verified. The staged input hash matches the failed attempt. | Finished 07:42:09 UTC. Reported retrieval time was 138.12 s. Full-domain nDCG@10 = 0.06157. |

The original run overlapped the Iota BGE smoke. Its manifest records 677.14 s of retrieval ending at 02:59:16 UTC with FP32 parameters and batch size 128. Torch's 7,796,289,536-byte GPU allocation measures device use. The host-memory diagnosis comes from the Linux kernel. The exact line of Python at the kill and combined peak resident memory were unmeasured.

The release loads analyzed tokens for every document, constructs the dictionary and bag-of-words corpus, then builds a sparse index before scoring queries. The isolated worker also retains the input documents. Bitcoin's projected JSON alone occupied 404,310,197 bytes. Token counts, term diversity, and Python objects affect working memory, so document counts or compressed input sizes cannot forecast an exact peak. Comparing upstream commit `8731487254e0988eaf2ca4ae3e93ff587fec64d0` with repaired commit `4bd4324017810ebede72492a3ed869910d668fa7` showed only the existing optional-vLLM import repair in `retrievers.py`. The retry used Python 3.10.22, Pyserini 1.2.0 and Gensim 4.4.0. Its manifest records the remaining versions and hashes.

## What the resource measurements establish

- Windows has two 8 GiB memory modules and 15.70 GiB visible to the OS. At 02:59:39 UTC the host reported 0.66 GiB free. At 07:42:07 UTC it reported 1.44 GiB free. These are snapshots after Bitcoin inference in each attempt.
- The retry had 7.60 GiB of guest RAM, 2 GiB of original swap, and an additional temporary 8 GiB Linux swap file. At 07:42:06 UTC the original swap used 483,328 bytes and the extra file used zero. Linux booted at 07:37:58 UTC, before the retry. By 07:43:37 UTC, after it finished, the guest had swapped out 118 pages of 4,096 bytes (0.46 MiB) and swapped in zero. Bitcoin therefore completed with minimal paging. Both scheduling and available swap changed between attempts, so the retry does not isolate the cause of success.
- At 07:42 UTC C: had 45.44 GiB free. Ubuntu's virtual disk is on C:. Its filesystem advertised 918.24 GiB available internally, but additional virtual-disk growth consumes host storage shared with datasets, staged JSON inputs, models, outputs, and Windows. The 8 GiB swap file had already been allocated at the time of this measurement.

## Local continuation

Continue the single active queue for Genealogy, Politics, HSM, and History. At review time the Genealogy worker was processing its original 156,228 documents and 115 queries. Keep one preparation, retrieval, or evaluation workload active at a time during the large runs. The revised suite checks for heavy worker processes and stops on a failed domain. Avoid starting an independent heavy job while the queue is active.

Keep the current allocation for this queue. Check the host drive's free space and guest swap use at domain boundaries. If a domain fails again or paging stalls progress, capture the failing stage, kernel record, elapsed time, guest memory/swap, and host free disk before deciding on a further attempt. After all jobs have exited, recheck Windows memory and disk headroom before considering any WSL allocation change. No `.wslconfig` existed during this review. A domain that exceeds the measured local capacity stays pending for a machine with more memory.

## Verification record

Read the two Bitcoin runs' `prepare.log`, `launch.json`, and `inference.log`, plus the retry's `evaluation.log`, `summary.json`, and `manifest.json`. Compared the two input digests and verified the summary with PowerShell `Get-FileHash -Algorithm SHA256`. The score comparison used the Bitcoin BM25 column of the pinned `vendor/Tempo/README.md`. Reviewed `scripts/tempo_isolated.py`, `scripts/run_tempo_bm25_suite.py`, and the upstream `retrieval_bm25` implementation.

Resource checks used `Get-CimInstance Win32_PhysicalMemory`, `Get-CimInstance Win32_OperatingSystem`, `Get-CimInstance Win32_ComputerSystem`, `Get-PSDrive C`, and `Test-Path "$env:USERPROFILE/.wslconfig"`. In Ubuntu 24.04 the read-only checks included `free -b`, `swapon --show --bytes`, `df -B1 / /mnt/c`, `cat /proc/vmstat`, `cat /proc/stat`, `getconf PAGESIZE`, and `journalctl -k -b -1`. The coordinator recorded the swap setup and retry command in `reports/experiment_log.md`. This review launched no benchmark or resource change.
