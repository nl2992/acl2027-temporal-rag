# Run from an Administrator PowerShell after making sufficient disk space available.
$ErrorActionPreference = 'Stop'
$admin = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $admin.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Windows requires Administrator PowerShell to install WSL.'
}
if ((Get-PSDrive C).Free -lt 30GB) {
    throw 'At least 30 GB free on C: is required by this setup preflight. Free space or choose another Linux storage location first.'
}
winget install --id Microsoft.WSL --exact --accept-source-agreements --accept-package-agreements
if ($LASTEXITCODE -ne 0) { throw 'WSL package installation failed; inspect the installer output.' }
wsl --install --distribution Ubuntu-24.04 --no-launch --no-reboot
if ($LASTEXITCODE -ne 0) { throw 'Ubuntu installation failed; inspect output before retrying.' }
Write-Output 'Installation requested without automatic reboot. After any required restart, launch Ubuntu to finish user setup, then run nvidia-smi inside Linux.'
