"""Download and hash exact local-feasible TEMPO model snapshots before inference."""
from pathlib import Path
import json
import hashlib
from huggingface_hub import HfApi, snapshot_download

revisions={
 'bge':('BAAI/bge-large-en-v1.5','d4aa6901d3a41ba39fb536a557fa166f842b0e09'),
 'sbert':('sentence-transformers/all-mpnet-base-v2','e8c3b32edf5434bc2275fc9bab85f82640a19130'),
 'contriever':('facebook/contriever-msmarco','abe8c1493371369031bcb1e02acb754cf4e162fa')
}
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()
report={}
for model,(repo,revision) in revisions.items():
    info=HfApi().model_info(repo,revision=revision)
    names=[s.rfilename for s in info.siblings]
    safe={str(Path(n).parent) for n in names if n.endswith('.safetensors') and not n.startswith(('onnx/','openvino/'))}
    wanted=[n for n in names if not n.startswith(('onnx/','openvino/')) and (n.endswith(('.json','.txt','.model','.py','.safetensors')) or (Path(n).name.startswith('pytorch_model') and n.endswith('.bin') and str(Path(n).parent) not in safe))]
    snapshot=Path(snapshot_download(repo,revision=revision,cache_dir='/home/acl-infer/models',allow_patterns=wanted,max_workers=2))
    report[model]={'repo':repo,'revision':revision,'snapshot':str(snapshot),'license':info.card_data.get('license') if info.card_data else None,'files':{str(p.relative_to(snapshot)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in snapshot.rglob('*') if p.is_file()}}
    print('Staged',model,revision,flush=True)
Path('/home/acl-infer/models/tempo_models.json').write_text(json.dumps(report,indent=2)+'\n')
Path('/home/nigel/acl2027/reports/tempo_models.json').write_text(json.dumps(report,indent=2)+'\n')
