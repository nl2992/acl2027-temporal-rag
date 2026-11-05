"""Continue the single-GPU baseline queue after the already-running Company job."""
from pathlib import Path
import json
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[1]
dependency=root/'reports/baselines/baseline-company-dense-20261105T013616Z/launch.json'
while True:
    state=json.loads(dependency.read_text())
    if state['status']=='complete':
        break
    if state['status']=='failed':
        raise RuntimeError('Company dense failed; inspect logs before continuing GPU jobs')
    time.sleep(2)
for domain in ['law','terms','university']:
    print('Starting next dense domain:',domain,flush=True)
    subprocess.run([sys.executable,str(root/'scripts/run_baseline_wsl.py'),'--domain',domain,'--backbone','dense'],check=True)
print('All four dense domain jobs completed.',flush=True)
