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
references=[]
for path in (root/'reports/tempo').glob(f'tempo-{a.domain}-bm25-*/manifest.json'):
    candidate=json.loads(path.read_bytes())
    if candidate.get('status')=='complete' and candidate.get('smoke') is False:
        references.append(candidate)
assert len(references)==1, 'Missing or ambiguous full-domain BM25 reference'
reference=references[0]
assert reference['benchmark']=='TEMPO' and reference['domain']==a.domain
assert reference['worker']['model']=='bm25'
assert reference['dataset_revision']=='1dba7027d0afa628993c6dd794e9b68c657a6fac'
assert reference['source_sha']=='8731487254e0988eaf2ca4ae3e93ff587fec64d0'
retriever_sha='b207b0d61130b01a9b3c31215c6a5d66cdb8f4b8b83b579898979850639310e4'
assert reference['worker']['source_sha256']==retriever_sha
run=a.run_id or f'tempo-{a.domain}-{a.model}-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=root/'reports/tempo'/run
out.mkdir(parents=True,exist_ok=False)
state={'run_id':run,'status':'running','utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':sys.argv,'project_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()}
state['project_dirty']=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
state['inference_worker_sha256']=hashlib.sha256((root/'scripts/drafts/tempo_instructor_isolated.py').read_bytes()).hexdigest()
state['evaluator_entry_sha256']=hashlib.sha256((root/'scripts/tempo_isolated.py').read_bytes()).hexdigest()
state['launcher_sha256']=hashlib.sha256((root/'scripts/drafts/isolated_tempo_instructor_worker.sh').read_bytes()).hexdigest()
state['evaluator_wrapper_sha256']=hashlib.sha256((root/'scripts/tempo_evaluate_with_provenance.py').read_bytes()).hexdigest()
state['stager_sha256']=hashlib.sha256((root/'scripts/stage_tempo_data.py').read_bytes()).hexdigest()
assert state['stager_sha256']=='bdc5b59b63134ec125c48117537c289727da00b7cefb2d1248a31d1f73857f3d', 'Stager changed'
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

def check_resources():
    """Admission only; does not serialize non-cooperating launchers."""
    wsl=['wsl','-d','Ubuntu-24.04','-u','root','--']
    active=subprocess.run(wsl+['pgrep','-f',
        'baseline_isolated.py (prepare|worker|evaluate)|tempo_isolated.py (worker|evaluate)|tempo_instructor_isolated.py (worker|evaluate)|tempo_evaluate_with_provenance.py|stage_tempo_data.py'],capture_output=True)
    assert active.returncode==1, 'Research process active or process state unavailable'
    values=subprocess.check_output(wsl+['nvidia-smi','--query-gpu=memory.used',
        '--format=csv,noheader,nounits'],text=True).split()
    assert len(values)==1 and values[0].isdigit() and int(values[0])<500, 'GPU unavailable'
    meminfo=subprocess.check_output(wsl+['cat','/proc/meminfo'],text=True)
    memory={line.split(':')[0]:int(line.split()[1]) for line in meminfo.splitlines()}
    assert memory['SwapTotal']>=9*1024**2
    assert memory['SwapFree']>=4*1024**2 and memory['MemAvailable']>=2*1024**2
    filesystem=subprocess.check_output(wsl+['df','-PB1','/home/acl-infer'],text=True).splitlines()
    assert len(filesystem)==2 and int(filesystem[1].split()[3])>=4*1024**3
    assert shutil.disk_usage(root).free>=12*1024**3

def check_private_evaluation_boundary():
    """Check existing owner-only permissions; namespace masking is checked separately."""
    wsl=['wsl','-d','Ubuntu-24.04','-u','root','--']
    path='/home/nigel/acl2027/eval-private'
    identity=subprocess.check_output(wsl+['stat','-c','%U %a %F',path],text=True).strip()
    assert identity=='nigel 700 directory', 'Private evaluation directory is not owner-only'
    for flag in ['-r','-x']:
        result=subprocess.run(wsl+['runuser','-u','acl-infer','--','test',flag,path],capture_output=True)
        assert result.returncode==1, 'Inference-user access check failed or was inconclusive'

try:
    check_resources()
    check_private_evaluation_boundary()
    for filename,key in [('tempo_instructor_isolated.py','inference_worker_sha256'),
                         ('tempo_isolated.py','evaluator_entry_sha256'),
                         ('isolated_tempo_instructor_worker.sh','launcher_sha256'),
                         ('stage_tempo_data.py','stager_sha256'),
                         ('tempo_evaluate_with_provenance.py','evaluator_wrapper_sha256')]:
        actual=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',scripts+filename])
        actual_sha=hashlib.sha256(actual).hexdigest()
        state.setdefault('deployed_script_sha256',{})[filename]=actual_sha
        assert actual_sha==state[key],f'Deployed script differs: {filename}'
    retrieval=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',
        '/home/nigel/acl2027/vendor/Tempo-repaired/retrievers.py'])
    assert hashlib.sha256(retrieval).hexdigest()==retriever_sha, 'Retrieval source changed'
    save()
    for name,cmd in zip(['prepare','inference','evaluation'],commands):
        if name=='inference':
            check_private_evaluation_boundary()
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
    assert manifest['status']=='complete' and manifest['benchmark']=='TEMPO'
    assert manifest['domain']==a.domain and manifest['smoke'] is a.smoke
    assert manifest['dataset_revision']==reference['dataset_revision']
    assert manifest['source_sha']==reference['source_sha']
    assert manifest['repaired_sha']=='4bd4324017810ebede72492a3ed869910d668fa7'
    assert manifest['preparation_script_sha256']==state['stager_sha256']
    assert manifest['raw_file_sha256']==reference['raw_file_sha256']
    assert manifest['original_queries']==reference['queries']>0
    assert manifest['documents']==manifest['original_documents']==reference['documents']>0
    assert manifest['queries']==(min(2,reference['queries']) if a.smoke else reference['queries'])
    assert manifest['worker']['status']=='complete'
    assert manifest['worker']['queries']==manifest['queries']
    assert manifest['worker']['documents']==manifest['documents']
    assert manifest['worker']['input_sha256']==manifest['input_sha256']
    assert manifest['worker']['source_sha256']==retriever_sha
    if not a.smoke:
        assert manifest['input_sha256']==reference['input_sha256']
        assert manifest['gold_sha256']==reference['gold_sha256']
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
