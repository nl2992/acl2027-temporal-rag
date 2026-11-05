"""Stage the official Inst-L snapshot separately; never alter active TEMPO models."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
from huggingface_hub import HfApi, snapshot_download

REPO='hkunlp/instructor-large'
REVISION='54e5ffb8d484de506e59443b07dc819fb15c7233'
CACHE=Path('/home/acl-infer/models/instructor-only')
OUTPUT=Path('/home/nigel/acl2027/reports/instructor_source')
assert CACHE.is_dir() and shutil.disk_usage(CACHE).free>=8*1024**3
info=HfApi().model_info(REPO,revision=REVISION,files_metadata=True)
assert info.sha==REVISION and info.card_data.get('license')=='apache-2.0'
items={item.rfilename:item for item in info.siblings}
wanted=[name for name in items if name.endswith(('.json','.txt','.model')) or
        (Path(name).name.startswith('pytorch_model') and name.endswith('.bin'))]
snapshot=Path(snapshot_download(REPO,revision=REVISION,cache_dir=CACHE,
                               allow_patterns=wanted,max_workers=1))
files={}
for name in wanted:
    path=snapshot/name
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):
            h.update(block)
    digest=h.hexdigest()
    advertised=getattr(items[name].lfs,'sha256',None)
    if advertised:
        assert digest==advertised, f'Official LFS hash mismatch: {name}'
    assert items[name].size is None or path.stat().st_size==items[name].size
    files[name]={'sha256':digest,'bytes':path.stat().st_size,'advertised_lfs_sha256':advertised}
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':'inst-l',
    'repo':REPO,'revision':REVISION,'snapshot':str(snapshot),'license':'apache-2.0',
    'files':files,'weights_downloaded':True,'model_instantiated':False,'gpu_used':False,
    'active_tempo_registry_changed':False,
    'status':'Checkpoint staged and hashed; loader compatibility and native smoke still pending.'}
OUTPUT.mkdir(parents=True,exist_ok=True)
(OUTPUT/'staged_snapshot.json').write_text(json.dumps(record,indent=2)+'\n')
print(f'Staged {REPO}@{REVISION}; {len(files)} files verified; no model run.',flush=True)
