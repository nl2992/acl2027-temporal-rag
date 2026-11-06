"""Build a separate Inst-L draft from frozen worker bytes; never deploy it."""
import ast
import difflib
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
base=(ROOT/'scripts/tempo_isolated.py').read_bytes()
assert hashlib.sha256(base).hexdigest()=='9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee'
source=base.decode()

def replace_once(old,new):
    global source
    assert source.count(old)==1, old
    source=source.replace(old,new)

replace_once("        staged=json.loads(Path('/home/acl-infer/models/tempo_models.json').read_text())",
    "        staged_record=json.loads((ROOT/'reports/instructor_source/staged_snapshot.json').read_text())\n"
    "        staged_digest=hashlib.sha256(json.dumps(staged_record,sort_keys=True,separators=(',',':')).encode()).hexdigest()\n"
    "        assert staged_digest=='622ff71f899545bb9178dc1f379775b1b0392d7b7412d9b09c237722807c4ed9', 'Checkpoint inventory changed'\n"
    "        staged={'inst-l':{k:staged_record[k] for k in ['repo','revision','snapshot','license','files']}}\n"
    "        assert staged['inst-l']['repo']=='hkunlp/instructor-large'\n"
    "        assert staged['inst-l']['revision']=='54e5ffb8d484de506e59443b07dc819fb15c7233'")
replace_once("            profile.update(parameter_dtype=str(next(model.parameters()).dtype),max_seq_length=model.max_seq_length)",
    "            profile.update(parameter_dtype=str(next(model.parameters()).dtype),constructor_max_seq_length=model.max_seq_length)\n"
    "            assert profile['parameter_dtype']=='torch.float32', profile\n"
    "            original_encode=model.encode\n"
    "            def encode(*texts,**encode_kw):\n"
    "                profile['max_seq_length']=model.max_seq_length\n"
    "                flags=[layer.include_prompt for layer in model.modules() if hasattr(layer,'include_prompt')]\n"
    "                assert flags and all(flag is False for flag in flags), flags\n"
    "                assert model.max_seq_length==2048\n"
    "                assert encode_kw.get('batch_size')==4 and encode_kw.get('normalize_embeddings') is True\n"
    "                profile['pooling_include_prompt']=flags\n"
    "                profile.setdefault('encode_calls',[]).append({'texts':len(texts[0]),'batch_size':encode_kw['batch_size'],\n"
    "                    'normalize_embeddings':encode_kw['normalize_embeddings'],'prompt':encode_kw.get('prompt')})\n"
    "                return original_encode(*texts,**encode_kw)\n"
    "            model.encode=encode")
replace_once("{'bge':512,'sbert':384,'contriever':512}[a.model]", "{'inst-l':2048}[a.model]")
replace_once("{'bge':128,'sbert':128,'contriever':1}[a.model]", "{'inst-l':4}[a.model]")
replace_once("        cache=cache/key\n        cache.mkdir(parents=True,exist_ok=True)\n        (cache/'descriptor.json').write_text(json.dumps(descriptor,indent=2)+'\\n')",
    "        # Each run starts with an exclusively created cold cache; never trust a previous run.\n"
    "        run_cache_key=hashlib.sha256(a.run_id.encode('utf-8')).hexdigest()\n"
    "        cache=cache/'instructor-cold'/run_cache_key/key\n"
    "        cache.mkdir(parents=True,exist_ok=False)\n"
    "        (cache/'descriptor.json').write_text(json.dumps(descriptor,indent=2)+'\\n')")
replace_once("def worker(a):", """def validate_instructor_cache(cache, domain, documents):
    import numpy as np
    directory=cache/'doc_emb'/'inst-l'/domain/'long_False'
    vectors=directory/'embeddings.npy'
    mapping_file=directory/'doc_id_mapping.json'
    mapping=json.loads(mapping_file.read_text())
    ids=[d['id'] for d in documents]
    assert len(ids)==len(set(ids)) and set(mapping)==set(ids)
    assert all(type(mapping[doc_id]) is int and mapping[doc_id]==i for i,doc_id in enumerate(ids))
    array=np.load(vectors,mmap_mode='r',allow_pickle=False)
    assert array.dtype==np.float32 and array.ndim==2 and array.shape[0]==len(ids) and array.shape[1]>0
    for offset in range(0,len(ids),1024):
        assert np.isfinite(array[offset:offset+1024]).all()
    return {'embeddings_sha256':sha(vectors),'mapping_sha256':sha(mapping_file),
            'descriptor_sha256':sha(cache/'descriptor.json'),
            'shape':list(array.shape),'dtype':str(array.dtype),'mapping_order':'input document order',
            'cache_policy':'exclusive per-run cold cache; reuse disabled'}

def worker(a):""")
replace_once("        meta['cache_descriptor']=descriptor", "        meta['cache_descriptor']=descriptor\n        meta['cache_receipt']=validate_instructor_cache(cache,data['domain'],data['documents'])")
replace_once("choices=['bm25','bge','sbert','contriever'],default='bm25'", "choices=['inst-l'],default='inst-l'")
ast.parse(source)
destination=ROOT/'scripts/drafts/tempo_instructor_isolated.py'
destination.parent.mkdir(exist_ok=True)
destination.write_bytes(source.encode())
patch=''.join(difflib.unified_diff(base.decode().splitlines(True),source.splitlines(True),
    fromfile='frozen-tempo-isolated-9f0e5555.py',tofile='draft-tempo-instructor-isolated.py'))
(ROOT/'reports/instructor_worker_draft.patch').write_bytes(patch.encode())
print('Built separate draft SHA256',hashlib.sha256(source.encode()).hexdigest())
print('No deployment, model constructor, inference or evaluation was executed.')
