"""Trusted download stage; never runs retrieval or opens benchmark labels."""
from pathlib import Path
import hashlib
import json
from huggingface_hub import snapshot_download

revision='5617a9f61b028005a4858fdac845db406aefb181'
snapshot=Path(snapshot_download('BAAI/bge-m3',revision=revision,cache_dir='/home/acl-infer/models',allow_patterns=['*.json','*.model','*.pt','pytorch_model.bin'],ignore_patterns=['onnx/*'],max_workers=2))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()
report={'model':'BAAI/bge-m3','revision':revision,'snapshot':str(snapshot),'files':{str(p.relative_to(snapshot)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in snapshot.rglob('*') if p.is_file()}}
Path('/home/nigel/acl2027/reports/bge_checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
