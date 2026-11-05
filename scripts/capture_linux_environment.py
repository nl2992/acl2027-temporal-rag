"""Capture Linux provisioning evidence from Windows without exposing credentials."""
from pathlib import Path
import datetime
import json
import subprocess

root = Path(__file__).resolve().parents[1]
def run(args):
    p = subprocess.run(args, capture_output=True)
    def decode(b):
        return b.decode('utf-16-le' if b'\0' in b[:100] else 'utf-8', errors='replace')
    return {'command': args, 'exit_code': p.returncode, 'stdout': decode(p.stdout), 'stderr': decode(p.stderr)}
commands = [
    ['wsl', '--version'],
    ['wsl', '--list', '--verbose'],
    ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', 'uname', '-a'],
    ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', 'cat', '/etc/os-release'],
    ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', 'nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv'],
    ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', '/home/nigel/miniforge3/envs/timelyrag-native/bin/python', '--version'],
    ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', 'git', '-C', '/home/nigel/acl2027/vendor/TimelyRAG', 'status', '--porcelain'],
]
report = {'captured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'observations': [run(c) for c in commands]}
(root / 'manifests/linux_environment.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print('Captured WSL, Linux, GPU, Python and pristine source status.')
