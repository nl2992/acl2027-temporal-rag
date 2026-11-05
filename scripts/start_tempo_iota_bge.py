"""Deploy reviewed cache bookkeeping and start full Iota BGE after the CPU suite."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
expected=set(json.loads((root/'configs/published_tempo_bm25.json').read_text())['domains'])
completed=set()
for path in (root/'reports/tempo').glob('tempo-*-bm25-*/manifest.json'):
    record=json.loads(path.read_text(encoding='utf-8-sig'))
    launch=json.loads((path.parent/'launch.json').read_text(encoding='utf-8-sig'))
    if record.get('status')=='complete' and launch.get('status')=='complete' and not record.get('smoke'):
        assert (path.parent/'summary.json').exists()
        completed.add(record['domain'])
assert completed==expected, f'CPU suite incomplete: {sorted(expected-completed)}'
wsl=['wsl','-d','Ubuntu-24.04']
probe=subprocess.run(wsl+['-u','root','--','pgrep','-f',
    'baseline_isolated.py worker|tempo_isolated.py (worker|evaluate)|stage_tempo_data.py'],capture_output=True)
assert probe.returncode==1, 'A research process is active or its state could not be checked'
gpu=subprocess.check_output(wsl+['-u','root','--','nvidia-smi',
    '--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True)
assert all(int(value.strip())<500 for value in gpu.splitlines()), 'GPU is occupied'
worker=root/'scripts/tempo_isolated.py'
payload=worker.read_bytes()
ast.parse(payload)
new_sha=hashlib.sha256(payload).hexdigest()
assert new_sha=='9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee', new_sha
remote='/home/nigel/acl2027/scripts/tempo_isolated.py'
old=subprocess.check_output(wsl+['-u','nigel','--','cat',remote])
old_sha=hashlib.sha256(old).hexdigest()
assert old_sha=='f098fb069b2fe18c270ea5554be5ccaf8cd9e720fbc20ec860cdb75318214705', old_sha
shell=subprocess.check_output(wsl+['-u','nigel','--','cat','/home/nigel/acl2027/scripts/isolated_tempo_worker.sh'])
assert shell==(root/'scripts/isolated_tempo_worker.sh').read_bytes(), 'Launcher differs'
subprocess.run(wsl+['-u','nigel','--','/home/nigel/miniforge3/envs/tempo-native/bin/python','-c',
    'from pathlib import Path; import sys; Path("/home/nigel/acl2027/scripts/tempo_isolated.py").write_bytes(sys.stdin.buffer.read())'],input=payload,check=True)
observed=subprocess.check_output(wsl+['-u','nigel','--','cat',remote])
assert observed==payload
evidence={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'old_worker_sha256':old_sha,'new_worker_sha256':new_sha,
    'completed_bm25_domains':sorted(completed),'idle_check_returncode':probe.returncode,
    'change':'Reviewed document-only cache key; no model/scoring/settings changes; no old-cache migration',
    'command':sys.argv}
(root/'reports/tempo_dense_deployment.json').write_text(json.dumps(evidence,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'scripts/run_tempo_wsl.py'),'--domain','iota','--model','bge'],check=True)
