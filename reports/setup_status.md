# Linux/CUDA setup status — 2026-11-04

## Latest continuation

Disk recheck: C: had 77.56 GiB free; the initial storage blocker is resolved. Installed WSL 2.7.14 through elevated Windows PowerShell, then Ubuntu 24.04.5. Verified Linux kernel 6.18.33.2-microsoft-standard-WSL2 and GPU visibility with Linux `nvidia-smi`; no reboot needed. Created Linux user `nigel` and configured it as the WSL default user.

Installed Miniforge 26.9.4-1 at `/home/nigel/miniforge3`, verifying the installer SHA256 against the official GitHub release asset digest (`571b410272cc434f28bc6c5c49ca8ffd4a4d1bcba9f57f1b6baccdb46446cfcc`). Created `timelyrag-native` with verified Python 3.11.5. A separate pristine Linux vendor checkout is at `/home/nigel/acl2027/vendor/TimelyRAG`, pinned to the same SHA as the Windows audit.

First exact pip requirements attempt failed because `mkl-service==2.4.0` was unavailable from pip for this environment. Saved the full pip output in `reports/setup/native_failure.log`. Conda-forge does provide a compatible build: installed the exact 2.4.0 version via conda without changing author pins. The unchanged pip requirements are being retried after that environment prerequisite. Linux PyTorch CUDA is not yet verified.

That retry failed with a genuine pinned dependency conflict: Notebook 7.2.1 requires JupyterLab <4.3, whereas upstream pins JupyterLab 4.3.3. Full resolver output: `reports/setup/native_dependency_conflict.log`. A separate `timelyrag-repaired` conda environment and `vendor-repaired` Git worktree test the minimal requirements change Notebook 7.2.1 → 7.3.1. Installation in progress; no author scoring code changed. The native exact requirements are not installable by this observed pip resolution, so subsequent repaired runs must be labeled accordingly.

Final result of continuation: repaired requirements installation **succeeded**. `pip check` reports no broken requirements. Verified PyTorch 2.3.1+cu121, NumPy 1.26.4, CUDA runtime 12.1, `torch.cuda.is_available() == True`, correct RTX 4060 Laptop device, GPU tensor calculation `[2,2,2,2]`, and tensor-to-NumPy conversion. `python -m pipeline --help` passes with imports intact. Frozen packages: `manifests/linux_repaired_environment.txt`; installation output: `reports/setup/repaired_install.log`; one-line requirements patch: `reports/setup/repair.patch`.

Executed unchanged upstream runner under the **repaired dependency environment**, after extracting the author archive at checkout root as instructed. It fails before model initialization with `FileNotFoundError` for `./datasets/timelyrag_company_policies_dataset_v2.jsonl`. Exact output: `reports/setup/runner_repaired_environment_failure.log`. This confirms the archive-placement issue; no retrieval results were produced. It is not a verbatim native reproduction because the environment includes the disclosed Notebook repair. Extraction creates untracked dataset files in the Linux vendor worktree; tracked source files remain unchanged.

Next research step: repair dataset paths/placement in the separate repaired track, resolve the known relative imports, run tiny data/metric smoke tests, then measure BGE-M3 feasibility on 8 GB before full baselines. Linux setup is complete; exact native dependency parity failed and is documented.

Setup-script correction: WSL 2.7.14 rejects `--no-reboot`; removed that unsupported option after capturing `Wsl/E_INVALIDARG`. Ubuntu installation succeeded using `wsl --install --distribution Ubuntu-24.04 --no-launch`. Historical failure observations below are retained for traceability and no longer describe the current Linux installation state.

## Observed hardware and installation failures

Windows driver 592.82 reports CUDA capability 13.1. GPU: RTX 4060 Laptop GPU, 8188 MiB. This is below the protocol assumption of 24–32 GB; feasibility must be measured. A Windows driver report does not prove Linux PyTorch works.

Only C: is available; approximately 7.0 GB decimal free at inspection. No large model or CUDA environment installation attempted. A 30 GiB free-space check is an initial operational minimum, not a measured final storage budget.

Session is not elevated. `wsl --status`, `wsl --list --verbose`, and `wsl --install` all returned the WSL-not-installed message. The distribution-specific install attempt also returned that message.

`winget install --id Microsoft.WSL --exact --accept-source-agreements --accept-package-agreements --silent --disable-interactivity` found Microsoft.WSL 2.7.14 and verified its installer hash, but failed:

```text
Installer failed with exit code: 0x80073d28 : The package installation failed because administrator privileges are required. Please contact an administrator to install this package.
```

No Linux distribution, conda environment, or native benchmark was installed/executed. This is an environment provisioning failure, not an upstream benchmark failure. No `native_failure.log` is fabricated for a native run that never occurred.

## Prepared continuation

1. Free disk space or identify a larger drive for Linux storage; do not delete unrelated files automatically.
2. Run `scripts/install_linux.ps1` in Administrator PowerShell. It checks space, installs WSL and Ubuntu 24.04 without an automatic reboot. Ubuntu 24.04 is a proposed WSL host; the author README lists Ubuntu 18.04.6, so host-version differences must be recorded.
3. If Windows requests a restart, restart at a suitable time. Launch Ubuntu to finish the Linux user setup.
4. Verify `nvidia-smi` inside Ubuntu. Install Linux Miniconda/Anaconda from its official distribution. Keep the Windows GPU driver; follow NVIDIA's WSL instructions before installing any Linux CUDA packages.
5. Place a pristine checkout at the recorded upstream SHA on the Linux filesystem and run `scripts/setup_native_linux.sh`. It creates Python 3.11.5 and attempts the exact author requirements, logging failures without changing pins. Script is prepared, not executed or Linux-tested.
6. Before native execution, freeze a run manifest and preserve the unmodified runner's first exception. Dataset filename/import corrections belong in a separate repaired checkout after the native attempt.

Official installation reference: https://learn.microsoft.com/en-us/windows/wsl/install
