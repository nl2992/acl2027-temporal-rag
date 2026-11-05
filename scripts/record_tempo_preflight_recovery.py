"""Record the one no-computation Law failure after the missing witness was repaired."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
RUN='tempo-law-bge-20261105T170234Z'
WRAPPER='414345f385faab91f48b1a7ae631458047bfe9d757cc7947b991df8800f1b0a3'
RUNNER='634604d86d4865495fa3ba9f3f145961801fcc841ee928e049d1525927eaa2b9'
directory=ROOT/'reports/tempo'/RUN
assert set(p.name for p in directory.iterdir())=={'launch.json','source_changes.patch'}
launch=json.loads((directory/'launch.json').read_bytes())
assert launch['run_id']==RUN and launch['status']=='failed'
assert 'tempo_evaluate_with_provenance.py' in launch['error']
assert 'resources_before_stage' not in launch
assert hashlib.sha256((ROOT/'scripts/run_tempo_wsl.py').read_bytes()).hexdigest()==RUNNER
deployment=json.loads((ROOT/'reports/tempo_evaluator_witness_deployment.json').read_bytes())
assert deployment['deployed_byte_identity'] and deployment['describe_only']
assert deployment['wrapper_sha256']==WRAPPER
WSL=['wsl','-d','Ubuntu-24.04','-u','root','--']
paths=[f'/home/acl-infer/inputs/{RUN}',f'/home/acl-infer/runs/{RUN}',
       f'/home/nigel/acl2027/eval-private/{RUN}',f'/home/nigel/acl2027/results/{RUN}']
for path in paths:
    assert subprocess.run(WSL+['test','-e',path]).returncode==1, f'Artifact exists or state unavailable: {path}'
wrapper=subprocess.check_output(WSL+['cat','/home/nigel/acl2027/scripts/tempo_evaluate_with_provenance.py'])
assert hashlib.sha256(wrapper).hexdigest()==WRAPPER
entry={'run_id':RUN,'reason':'Missing evaluator witness before preparation began',
    'preparation_started':False,'inference_started':False,'evaluation_started':False,
    'launch_sha256':hashlib.sha256((directory/'launch.json').read_bytes()).hexdigest(),
    'source_patch_sha256':hashlib.sha256((directory/'source_changes.patch').read_bytes()).hexdigest(),
    'repaired_wrapper_sha256':WRAPPER,'reviewed_runner_sha256':RUNNER,
    'absence_checked_paths':paths,'review':'reports/tempo_evaluator_provenance_review.md',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
output=ROOT/'reports/tempo_preflight_recoveries.json'
assert not output.exists(), 'Preserve existing recovery records; review before appending'
output.write_text(json.dumps({'preflight_failures':{RUN:entry}},indent=2)+'\n')
print('Recorded repaired pre-preparation failure; original files preserved; no benchmark was run.')
