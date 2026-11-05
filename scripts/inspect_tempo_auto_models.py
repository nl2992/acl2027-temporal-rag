"""Freeze small official metadata for native auto-placement candidates, not weights."""
from pathlib import Path
import datetime
import hashlib
import json
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import HfHubHTTPError

ROOT=Path('/home/nigel/acl2027/reports/tempo_auto_models')
ROOT.mkdir(parents=True,exist_ok=True)
REPOS={'e5':'intfloat/e5-mistral-7b-instruct',
       'sf':'salesforce/sfr-embedding-mistral',
       'qwen':'alibaba-nlp/gte-qwen1.5-7b-instruct',
       'rader':'Raderspace/RaDeR_Qwen_25_7B_instruct_MATH_LLMq_CoT_lexical'}
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'models':{},
    'weights_downloaded':False,'model_instantiated':False,'gpu_used':False,
    'status':'Official metadata only; native auto-placement, remote-code safety, memory and parity remain unverified.'}
for model,repo in REPOS.items():
    try:
        info=HfApi().model_info(repo,files_metadata=True)
    except HfHubHTTPError as error:
        report['models'][model]={'author_repo_name':repo,'metadata_http_status':error.response.status_code if error.response is not None else None}
        (ROOT/'source_candidates.json').write_text(json.dumps(report,indent=2)+'\n')
        continue
    names={item.rfilename:item for item in info.siblings}
    configs={}
    for name in ['config.json','adapter_config.json']:
        if name in names:
            try:
                path=Path(hf_hub_download(repo,name,revision=info.sha,cache_dir=ROOT/'hf_metadata_cache'))
                raw=path.read_bytes()
                configs[name]={'sha256':hashlib.sha256(raw).hexdigest(),'json':json.loads(raw)}
            except HfHubHTTPError as error:
                configs[name]={'fetch_error_type':type(error).__name__,
                    'http_status':error.response.status_code if error.response is not None else None}
    weights={name:{'bytes':item.size,'advertised_lfs_sha256':getattr(item.lfs,'sha256',None)}
        for name,item in names.items() if '/' not in name and name.endswith(('.bin','.safetensors'))}
    report['models'][model]={'author_repo_name':repo,'returned_repo_id':info.id,
        'revision':info.sha,'gated':info.gated,
        'license':info.card_data.get('license') if info.card_data else None,
        'configs':configs,'root_weight_inventory_only':weights,
        'repository_python_files':[name for name in names if name.endswith('.py')]}
    (ROOT/'source_candidates.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Inspected metadata:',model,info.sha,flush=True)
(ROOT/'source_candidates.json').write_text(json.dumps(report,indent=2)+'\n')
