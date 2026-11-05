"""Execute a TEMPO domain with source-faithful isolated BM25 and offline metrics."""
import argparse
from pathlib import Path
import subprocess
import datetime
import json
import sys

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--domain',required=True)
p.add_argument('--run-id')
p.add_argument('--smoke',action='store_true')
a=p.parse_args()
run=a.run_id or f'tempo-{a.domain}-bm25-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=root/'reports/tempo'/run
out.mkdir(parents=True,exist_ok=False)
state={'run_id':run,'status':'running','utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':sys.argv,'project_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()}
def save():
    (out/'launch.json').write_text(json.dumps(state,indent=2)+'\n')
save()
print('TEMPO_RUN_ID',run,flush=True)
py='/home/nigel/miniforge3/envs/tempo-native/bin/python'
scripts='/home/nigel/acl2027/scripts/'
commands=[
 ['wsl','-d','Ubuntu-24.04','-u','nigel','--',py,scripts+'stage_tempo_data.py','--domain',a.domain,'--run-id',run]+(['--smoke'] if a.smoke else []),
 ['wsl','-d','Ubuntu-24.04','-u','root','--','unshare','--mount','--fork','bash',scripts+'isolated_tempo_worker.sh','--run-id',run],
 ['wsl','-d','Ubuntu-24.04','-u','nigel','--',py,scripts+'tempo_isolated.py','evaluate','--run-id',run]
]
try:
    for name,cmd in zip(['prepare','inference','evaluation'],commands):
        with (out/f'{name}.log').open('wb') as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        print(name,'complete',flush=True)
    for name in ['manifest.json','summary.json']:
        raw=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',f'/home/nigel/acl2027/results/{run}/{name}'])
        (out/name).write_bytes(raw)
    state['status']='complete'
except BaseException as e:
    state.update(status='failed',error=str(e))
    raise
finally:
    state['utc_finish']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
