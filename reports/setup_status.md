# Linux/CUDA setup status — 2026-11-04

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
