"""Trusted TEMPO data preparation, keeping relevance/answer fields private."""
import argparse
from pathlib import Path
import os
import json
import hashlib
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq

p=argparse.ArgumentParser()
p.add_argument('--domain',required=True)
p.add_argument('--run-id',required=True)
p.add_argument('--smoke',action='store_true')
p.add_argument('--model',default='bm25')
a=p.parse_args()
root=Path('/home/nigel/acl2027')
private=root/'tempo-private'
private.mkdir(exist_ok=True,mode=0o700)
os.chmod(private,0o700)
revision='1dba7027d0afa628993c6dd794e9b68c657a6fac'
paths={kind:Path(hf_hub_download('tempo26/Tempo',f'{kind}/{a.domain}.parquet',repo_type='dataset',revision=revision,cache_dir=private/'hf_cache')) for kind in ['examples','documents']}
examples=pq.read_table(paths['examples']).to_pylist()
docs=pq.read_table(paths['documents']).to_pylist()
original_queries=len(examples)
original_docs=len(docs)
if a.smoke:
    examples=examples[:2]
    # Keep the full corpus: released exclusion IDs refer to this complete universe.
public={'domain':a.domain,'smoke':a.smoke,'documents':[{'id':d['id'],'content':d['content']} for d in docs],'queries':[{'id':e['id'],'query':e['query'],'excluded_ids':e.get('negative_ids',[])} for e in examples]}
labels={e['id']:{'gold_ids':e['gold_ids']} for e in examples}
out=Path('/home/acl-infer/inputs')/a.run_id
out.mkdir(exist_ok=False)
(out/'input.json').write_text(json.dumps(public,ensure_ascii=False))
evaluation=root/'eval-private'/a.run_id
evaluation.mkdir(exist_ok=False)
(evaluation/'labels.json').write_text(json.dumps(labels))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest={'run_id':a.run_id,'benchmark':'TEMPO','domain':a.domain,'smoke':a.smoke,'dataset_revision':revision,'raw_file_sha256':{k:sha(v) for k,v in paths.items()},'input_sha256':sha(out/'input.json'),'gold_sha256':sha(evaluation/'labels.json'),'queries':len(examples),'documents':len(docs),'original_queries':original_queries,'original_documents':original_docs,'source_sha':'8731487254e0988eaf2ca4ae3e93ff587fec64d0','excluded_id_policy':'Released negative_ids passed unchanged as author exclusion metadata; true positive IDs and answers removed from worker input.'}
import subprocess
manifest['model']=a.model
manifest['repaired_sha']=subprocess.check_output(['git','-C',str(root/'vendor/Tempo-repaired'),'rev-parse','HEAD'],text=True).strip()
manifest['preparation_script_sha256']=sha(Path(__file__))
docids={d['id'] for d in docs}
manifest['duplicate_document_ids']=len(docs)-len(docids)
manifest['missing_gold_references']=sum(g not in docids for e in examples for g in e['gold_ids'])
manifest['missing_exclusion_references']=sum(g not in docids for e in examples for g in e.get('negative_ids',[]) if g!='N/A')
(evaluation/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2),flush=True)
