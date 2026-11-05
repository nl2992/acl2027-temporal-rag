"""Deploy only the reviewed metadata witness, then describe imports without evaluating."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='414345f385faab91f48b1a7ae631458047bfe9d757cc7947b991df8800f1b0a3'
payload=(ROOT/'scripts/tempo_evaluate_with_provenance.py').read_bytes()
assert hashlib.sha256(payload).hexdigest()==EXPECTED
WSL=['wsl','-d','Ubuntu-24.04','-u','nigel','--']
PY='/home/nigel/miniforge3/envs/tempo-native/bin/python'
remote='/home/nigel/acl2027/scripts/tempo_evaluate_with_provenance.py'
probe=subprocess.run(['wsl','-d','Ubuntu-24.04','-u','root','--','pgrep','-f',
    'baseline_isolated.py (prepare|worker|evaluate)|tempo_isolated.py (worker|evaluate)|tempo_evaluate_with_provenance.py|stage_tempo_data.py'],capture_output=True)
assert probe.returncode==1, 'Research process active or observation failed'
code='''from pathlib import Path
import hashlib, os, sys, tempfile
target=Path("/home/nigel/acl2027/scripts/tempo_evaluate_with_provenance.py")
payload=sys.stdin.buffer.read()
assert hashlib.sha256(payload).hexdigest()=="414345f385faab91f48b1a7ae631458047bfe9d757cc7947b991df8800f1b0a3"
if target.exists():
    assert target.read_bytes()==payload, "Unknown deployed witness"
else:
    fd,name=tempfile.mkstemp(prefix=".evaluator-witness-",dir=target.parent)
    try:
        with os.fdopen(fd,"wb") as out:
            out.write(payload)
            out.flush()
            os.fsync(out.fileno())
        Path(name).chmod(0o644)
        os.replace(name,target)
    finally:
        Path(name).unlink(missing_ok=True)
assert target.read_bytes()==payload
'''
subprocess.run(WSL+[PY,'-c',code],input=payload,check=True)
actual=subprocess.check_output(WSL+['cat',remote])
assert actual==payload
description=subprocess.check_output(WSL+[PY,remote,'--describe-only'])
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'wrapper_sha256':EXPECTED,'deployed_byte_identity':True,'describe_only':True,
    'evaluation_or_model_run':False,'current_imports':json.loads(description)}
(ROOT/'reports/tempo_evaluator_witness_deployment.json').write_text(json.dumps(record,indent=2)+'\n')
print('Reviewed witness deployed byte-identically; import-only description saved; no evaluation run.')
