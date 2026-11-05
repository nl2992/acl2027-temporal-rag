"""Run one reviewed baseline through gold-free WSL inference and offline evaluation."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--domain',choices=['company','law','terms','university'],required=True)
p.add_argument('--backbone',choices=['bm25','dense'],required=True)
p.add_argument('--smoke',action='store_true')
p.add_argument('--run-id')
a=p.parse_args()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=a.run_id or f'{"smoke" if a.smoke else "baseline"}-{a.domain}-{a.backbone}-{stamp}'
common=['--domain',a.domain,'--backbone',a.backbone,'--run-id',run]+(['--smoke'] if a.smoke else [])
script='/home/nigel/acl2027/scripts/baseline_isolated.py'
python='/home/nigel/miniforge3/envs/timelyrag-repaired/bin/python'
state={'run_id':run,'status':'running','utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project_url':'https://github.com/nl2992/acl2027-temporal-rag','project_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'project_dirty':subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True),'invocation':sys.argv,'worker_script_sha256':hashlib.sha256((root/'scripts/baseline_isolated.py').read_bytes()).hexdigest(),'launcher_sha256':hashlib.sha256((root/'scripts/isolated_worker.sh').read_bytes()).hexdigest()}
folder=root/'reports'/'baselines'/run
folder.mkdir(parents=True,exist_ok=False)
statepath=folder/'launch.json'
statepath.write_text(json.dumps(state,indent=2)+'\n')
print('RUN_ID',run,flush=True)
try:
    commands=[
      ['wsl','-d','Ubuntu-24.04','-u','nigel','--',python,script,'prepare',*common],
      ['wsl','-d','Ubuntu-24.04','-u','root','--','unshare','--mount','--fork','bash','/home/nigel/acl2027/scripts/isolated_worker.sh',*common],
      ['wsl','-d','Ubuntu-24.04','-u','nigel','--',python,script,'evaluate',*common],
    ]
    for name,cmd in zip(['prepare','inference','evaluation'],commands):
        with (folder/f'{name}.log').open('wb') as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        print(name,'complete',flush=True)
    subprocess.run([sys.executable,str(root/'scripts/collect_linux_runs.py'),'--run-id',run],check=True)
    state['status']='complete'
except BaseException as e:
    state.update(status='failed',error_type=type(e).__name__,error=str(e))
    raise
finally:
    state['utc_finish']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    statepath.write_text(json.dumps(state,indent=2)+'\n')
