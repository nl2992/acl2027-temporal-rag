"""Hide evaluator feedback from already-running private prediction namespaces."""
from pathlib import Path
import datetime
import json
import subprocess

p=subprocess.run(['pgrep','-u','acl-infer','-f','baseline_isolated.py worker'],capture_output=True,text=True)
observations=[]
for pid in p.stdout.split():
    command=['nsenter','--target',pid,'--mount','--','mount','-t','tmpfs','tmpfs','/home/nigel/acl2027/results']
    result=subprocess.run(command,capture_output=True,text=True)
    observations.append({'pid':pid,'command':command,'exit_code':result.returncode,'stderr':result.stderr})
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Close observed read access to completed-smoke feedback; scoring worker does not read this directory. New launches mask it from start.','workers':observations}
Path('/home/nigel/acl2027/reports/feedback_boundary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
