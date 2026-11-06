"""DRAFT ONLY: INSTRUCTOR-L isolated run; requires independent review before use."""
raise SystemExit("Draft runner is disabled pending independent review and deployment checks")
import argparse
from pathlib import Path
import subprocess
import datetime
import json
import sys
import hashlib
import shutil
import os

root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser()
p.add_argument('--domain',required=True)
p.add_argument('--run-id')
p.add_argument('--smoke',action='store_true')
p.add_argument('--model',choices=['inst-l'],default='inst-l')
a=p.parse_args()
run=a.run_id or f'tempo-{a.domain}-{a.model}-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=root/'reports/tempo'/run
out.mkdir(parents=True,exist_ok=False)
state={'run_id':run,'status':'running','utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':sys.argv,'project_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()}
state['project_dirty']=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
state['inference_worker_sha256']=hashlib.sha256((root/'scripts/drafts/tempo_instructor_isolated.py').read_bytes()).hexdigest()
state['evaluator_entry_sha256']=hashlib.sha256((root/'scripts/tempo_isolated.py').read_bytes()).hexdigest()
state['launcher_sha256']=hashlib.sha256((root/'scripts/drafts/isolated_tempo_instructor_worker.sh').read_bytes()).hexdigest()
state['evaluator_wrapper_sha256']=hashlib.sha256((root/'scripts/tempo_evaluate_with_provenance.py').read_bytes()).hexdigest()
(out/'source_changes.patch').write_bytes(subprocess.check_output(['git','diff','--','scripts','configs'],cwd=root))
def save():
    staged=out/'launch.json.tmp'
    staged.write_text(json.dumps(state,indent=2)+'\n')
    os.replace(staged,out/'launch.json')
save()
print('TEMPO_RUN_ID',run,flush=True)
py='/home/nigel/miniforge3/envs/tempo-native/bin/python'
scripts='/home/nigel/acl2027/scripts/'
commands=[
 ['wsl','-d','Ubuntu-24.04','-u','nigel','--',py,scripts+'stage_tempo_data.py','--domain',a.domain,'--run-id',run,'--model',a.model]+(['--smoke'] if a.smoke else []),
 ['wsl','-d','Ubuntu-24.04','-u','root','--','unshare','--mount','--fork','bash',scripts+'isolated_tempo_instructor_worker.sh','--run-id',run,'--model',a.model],
 ['wsl','-d','Ubuntu-24.04','-u','nigel','--',py,scripts+'tempo_evaluate_with_provenance.py','--run-id',run]
]
def verify_wrapper(phase):
    raw=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',scripts+'tempo_evaluate_with_provenance.py'])
    digest=hashlib.sha256(raw).hexdigest()
    state.setdefault('evaluation_wrapper_checks',{})[phase]=digest
    save()
    assert digest==state['evaluator_wrapper_sha256'], 'Evaluator wrapper changed after launch'

try:
    for filename,key in [('tempo_instructor_isolated.py','inference_worker_sha256'),
                         ('tempo_isolated.py','evaluator_entry_sha256'),
                         ('isolated_tempo_instructor_worker.sh','launcher_sha256'),
                         ('tempo_evaluate_with_provenance.py','evaluator_wrapper_sha256')]:
        actual=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',scripts+filename])
        actual_sha=hashlib.sha256(actual).hexdigest()
        state.setdefault('deployed_script_sha256',{})[filename]=actual_sha
        assert actual_sha==state[key],f'Deployed script differs: {filename}'
    save()
    for name,cmd in zip(['prepare','inference','evaluation'],commands):
        if name=='evaluation':
            verify_wrapper('immediately_before_evaluation')
        state.setdefault('resources_before_stage',{})[name]={
            'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'host_disk_free_bytes':shutil.disk_usage(root).free,
        }
        save()
        with (out/f'{name}.log').open('wb') as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        if name=='evaluation':
            verify_wrapper('immediately_after_evaluation')
        print(name,'complete',flush=True)
    exported={name:subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',
        f'/home/nigel/acl2027/results/{run}/{name}']) for name in
        ['manifest.json','summary.json','evaluator_runtime.json']}
    manifest=json.loads(exported['manifest.json'])
    runtime=json.loads(exported['evaluator_runtime.json'])
    assert manifest['run_id']==runtime['run_id']==run
    assert manifest['model']==manifest['worker']['model']==a.model
    assert manifest['worker']['worker_script_sha256']==state['inference_worker_sha256']
    assert runtime==manifest['evaluator_runtime']
    assert runtime['wrapper_sha256']==state['evaluator_wrapper_sha256']
    assert runtime['evaluator_entry_point_sha256']==state['evaluator_entry_sha256']
    assert runtime['same_process'] is True
    summary_sha=hashlib.sha256(exported['summary.json']).hexdigest()
    assert summary_sha==runtime['summary_sha256']==manifest['summary_sha256']
    for name in ['evaluator_runtime.json','summary.json','manifest.json']:
        staged=out/(name+'.export.tmp')
        staged.write_bytes(exported[name])
        os.replace(staged,out/name)
    state['status']='complete'
except BaseException as e:
    state.update(status='failed',error=str(e))
    raise
finally:
    state['utc_finish']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
