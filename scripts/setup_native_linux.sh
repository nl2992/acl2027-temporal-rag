#!/usr/bin/env bash
# Run inside Linux with conda already installed. Stops before changing author pins.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$PROJECT_ROOT/reports/setup"
exec > >(tee -a "$PROJECT_ROOT/reports/setup/native_environment.log") 2>&1
date -u +%FT%TZ
uname -a
test "$(uname -s)" = Linux || { echo 'Linux is required'; exit 1; }
nvidia-smi
command -v conda >/dev/null || { echo 'Install Miniconda/Anaconda in Linux first (official author prerequisite); conda was not found.'; exit 1; }
available_kb=$(df -Pk "$HOME" | awk 'NR==2 {print $4}')
test "$available_kb" -ge 31457280 || { echo 'Need at least 30 GiB free for the initial environment; measure again before model download.'; exit 1; }
eval "$(conda shell.bash hook)"
conda create -n timelyrag-native python=3.11.5 -y
conda activate timelyrag-native
python --version
# Observed pip availability failure: provide the identical author version via conda.
conda install -n timelyrag-native mkl-service=2.4.0 -y
python -m pip install -r "$PROJECT_ROOT/vendor/TimelyRAG/requirements.txt"
python -m pip freeze > "$PROJECT_ROOT/manifests/native_environment.txt"
python -c 'import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available()); assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))'
echo 'Environment installation passed. Audit dataset placement and run manifest before native execution.'
