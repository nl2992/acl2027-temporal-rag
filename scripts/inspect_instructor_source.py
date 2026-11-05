"""Freeze official INSTRUCTOR-L metadata/configs without loading or downloading weights."""
from pathlib import Path
import datetime
import hashlib
import json
from huggingface_hub import HfApi, hf_hub_download

ROOT=Path('/home/nigel/acl2027')
REPO='hkunlp/instructor-large'
info=HfApi().model_info(REPO,files_metadata=True)
revision=info.sha
output=ROOT/'reports/instructor_source'
output.mkdir(parents=True,exist_ok=True)
files={item.rfilename:item for item in info.siblings}
names=['modules.json','config.json','sentence_bert_config.json',
       'config_sentence_transformers.json','1_Pooling/config.json','2_Dense/config.json']
configs={}
for name in names:
    if name not in files:
        continue
    path=Path(hf_hub_download(REPO,name,revision=revision,cache_dir=output/'hf_metadata_cache'))
    raw=path.read_bytes()
    configs[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'json':json.loads(raw)}
weights={}
for name,item in files.items():
    if name.endswith(('.bin','.safetensors')):
        lfs=item.lfs
        weights[name]={'bytes':item.size,'advertised_lfs_sha256':getattr(lfs,'sha256',None)}
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':REPO,
    'revision':revision,'source':f'https://huggingface.co/{REPO}/tree/{revision}',
    'license':info.card_data.get('license') if info.card_data else None,
    'configs':configs,'weight_inventory':weights,'weights_downloaded':False,
    'model_instantiated':False,'gpu_used':False,
    'status':'Source-only candidate preflight; loader compatibility and native smoke remain unverified.'}
(output/'source_preflight.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
