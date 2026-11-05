"""Run the remaining TEMPO BM25 domains, one CPU corpus at a time."""
from pathlib import Path
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[1]
domains=['quant','law','workplace','economics','cardano','monero','travel','bitcoin','genealogy','politics','hsm','history']
for domain in domains:
    if domain in ['bitcoin','genealogy','politics','hsm','history']:
        # Large whole-corpus tokenization must not compete with the live P0 encoder.
        while True:
            probe=subprocess.run(['wsl','-d','Ubuntu-24.04','-u','root','--','pgrep','-u','acl-infer','-f','baseline_isolated.py worker'],capture_output=True)
            if probe.returncode==1:
                break
            if probe.returncode!=0:
                raise RuntimeError('Could not verify P0 process state; not starting large corpus')
            time.sleep(5)
    print('Starting TEMPO BM25 domain:',domain,flush=True)
    subprocess.run([sys.executable,str(root/'scripts/run_tempo_wsl.py'),'--domain',domain],check=True)
print('All remaining TEMPO BM25 domains completed.',flush=True)
