"""Archive the caller-visible reviewer dispatch/return without inventing host identity."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parents[1]
trace=root/'.aris/traces/experiment-audit/2026-11-05_tempo_resume'
prior=root/'.aris/traces/experiment-audit/2026-11-05_tempo_usage_limited'
trace.mkdir(parents=True,exist_ok=True)
prior.mkdir(parents=True,exist_ok=True)
route=json.loads((root/'reports/tempo_audit_route.json').read_bytes())
verdict=json.loads((root/'reports/TEMPO_EXPERIMENT_AUDIT.json').read_bytes())
assert verdict['agent_id']=='/root/tempo_audit_resume' and verdict['review_completed'] is True
snapshots={}
for name,expected in verdict['audited_input_hashes'].items():
    if name.startswith('git:'):
        _,revision,path=name.split(':',2)
        raw=subprocess.check_output(['git','show',f'{revision}:{path}'],cwd=root)
        destination=trace/'git_snapshots'/revision/path
    else:
        raw=(root/name).read_bytes()
        destination=trace/'input_snapshots'/name
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==expected.removeprefix('sha256:'), f'Audit input changed before archiving: {name}'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(raw)
    snapshots[name]={'snapshot':destination.relative_to(trace).as_posix(),'sha256':digest}
(trace/'input_snapshot_index.json').write_text(json.dumps(snapshots,indent=2)+'\n')
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'tool':'collaboration.spawn_agent','request_fields':{'task_name':'tempo_audit_resume',
        'fork_turns':'none','model':'gpt-6-astra','reasoning_effort':'ultra'},
    'returned_tool_metadata':{'task_name':'/root/tempo_audit_resume'},
    'route':route,'caller_visible_final_status':'completed',
    'returned_verdict':verdict['verdict'],'reported_runtime_model_id':None,
    'identity_limitation':'Requested model/effort were accepted by host; no independent runtime model ID or opaque session ID was returned.',
    'review_independence':'same-family','acceptance_status':'provisional',
    'trace_scope':'Caller-visible dispatch fields, returned canonical task and saved final artifacts; not a provider-side transcript.',
    'artifact_hashes':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in
        ['reports/TEMPO_EXPERIMENT_AUDIT.md','reports/TEMPO_EXPERIMENT_AUDIT.json',
         'reports/review_tools/tempo_evidence.jsonl','reports/review_tools/tempo_snapshot_evidence.json']}}
(trace/'caller_trace.json').write_text(json.dumps(record,indent=2)+'\n')
(prior/'interruption.json').write_text(json.dumps({'task_name':'/root/tempo_integrity_audit',
    'status':'interrupted_usage_limit','completed_verdict':False,
    'observation':'Host final notification reported account usage limit; later live-agent inventory had no prior canonical reviewer.',
    'replacement_task':'/root/tempo_audit_resume','recorded_at':record['recorded_at']},indent=2)+'\n')
route.update(status='completed_warn',review_completed=True,verdict=verdict['verdict'],
    trace_path='.aris/traces/experiment-audit/2026-11-05_tempo_resume/')
(root/'reports/tempo_audit_route.json').write_text(json.dumps(route,indent=2)+'\n')
print('Saved caller-visible audit trace; historical interruption remains separate.')
