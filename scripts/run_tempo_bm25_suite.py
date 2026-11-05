"""Run the remaining TEMPO BM25 domains, one CPU corpus at a time."""
from pathlib import Path
import subprocess
import sys
import time
import json
import argparse

root=Path(__file__).resolve().parents[1]
domains=['quant','law','workplace','economics','cardano','monero','travel','bitcoin','genealogy','politics','hsm','history']
parser=argparse.ArgumentParser()
parser.add_argument('--domains',nargs='+',choices=domains,default=domains)
domains=parser.parse_args().domains
for domain in domains:
    completed=[]
    for path in (root/'reports/tempo').glob(f'tempo-{domain}-bm25-*/launch.json'):
        state=json.loads(path.read_text(encoding='utf-8-sig'))
        manifest=path.parent/'manifest.json'
        if state.get('status')=='complete' and manifest.exists() and (path.parent/'summary.json').exists():
            record=json.loads(manifest.read_text(encoding='utf-8-sig'))
            if record.get('status')=='complete' and not record.get('smoke'):
                completed.append(path.parent.name)
    if completed:
        print('Already completed:',domain,completed,flush=True)
        continue
    if domain in ['bitcoin','genealogy','politics','hsm','history']:
        # Serialize all heavy retrieval workers, including TEMPO dense encoders.
        while True:
            probe=subprocess.run(['wsl','-d','Ubuntu-24.04','-u','root','--','pgrep','-f','baseline_isolated.py worker|tempo_isolated.py (worker|evaluate)|stage_tempo_data.py'],capture_output=True)
            if probe.returncode==1:
                break
            if probe.returncode!=0:
                raise RuntimeError('Could not verify retrieval process state; not starting large corpus')
            time.sleep(5)
    print('Starting TEMPO BM25 domain:',domain,flush=True)
    subprocess.run([sys.executable,str(root/'scripts/run_tempo_wsl.py'),'--domain',domain],check=True)
print('All remaining TEMPO BM25 domains completed.',flush=True)
