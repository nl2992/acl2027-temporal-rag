"""Preserve a transcoded aggregate export and restore its authoritative Linux bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parents[1]
run='tempo-iota-bge-smoke-001'
backup=root/'reports/artifact_export_repairs'/run
backup.mkdir(parents=True,exist_ok=False)
records=[]
for name in ['manifest.json','summary.json']:
    path=root/'reports/tempo'/run/name
    old=path.read_bytes()
    new=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',
        f'/home/nigel/acl2027/results/{run}/{name}'])
    assert json.loads(old)==json.loads(new), 'Numeric or metadata changes are not permitted'
    assert old.replace(b'\r\n',b'\n')==new, 'Difference is not solely line endings'
    (backup/name).write_bytes(old)
    path.write_bytes(new)
    assert path.read_bytes()==new
    records.append({'file':name,'preserved_export_sha256':hashlib.sha256(old).hexdigest(),
        'authoritative_and_restored_sha256':hashlib.sha256(new).hexdigest()})
manifest=json.loads((root/'reports/tempo'/run/'manifest.json').read_bytes())
assert hashlib.sha256((root/'reports/tempo'/run/'summary.json').read_bytes()).hexdigest()==manifest['summary_sha256']
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':run,
    'repair':'Restore LF from authoritative Linux exports; preserve original CRLF bytes; JSON values unchanged.',
    'files':records,'numeric_values_changed':False}
(backup/'repair.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
