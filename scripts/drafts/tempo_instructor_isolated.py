"""Run the unchanged TEMPO BM25 function without access to evaluation labels."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path('/home/nigel/acl2027')
VENDOR=ROOT/'vendor/Tempo-repaired'
sys.dont_write_bytecode=True
sys.path.insert(0,str(VENDOR))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()
def validate_instructor_cache(cache, domain, documents):
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

def worker(a):
    assert os.getuid()!=0 and os.getcwd()=='/'
    for protected in [ROOT/'eval-private'/a.run_id/'labels.json',ROOT/'tempo-private/hf_cache',ROOT/'results']:
        try:
            if protected.is_dir():
                assert not list(protected.iterdir()),str(protected)
            else:
                with protected.open('rb') as f:
                    assert not f.read(1),str(protected)
        except (FileNotFoundError,PermissionError):
            pass
    import retrievers
    path=Path('/home/acl-infer/inputs')/a.run_id/'input.json'
    data=json.loads(path.read_text())
    assert all(set(q)=={'id','query','excluded_ids'} for q in data['queries'])
    assert all(set(d)=={'id','content'} for d in data['documents'])
    out=Path('/home/acl-infer/runs')/a.run_id
    out.mkdir(exist_ok=False)
    start=time.perf_counter()
    instructions={'query':'Represent this query for retrieving relevant documents: ','document':''}
    model_manifest=None
    cache=Path('/home/acl-infer/model-cache')
    profile={}
    if a.model!='bm25':
        import torch
        staged_record=json.loads((ROOT/'reports/instructor_source/staged_snapshot.json').read_text())
        staged={'inst-l':{k:staged_record[k] for k in ['repo','revision','snapshot','license','files']}}
        assert staged['inst-l']['repo']=='hkunlp/instructor-large'
        assert staged['inst-l']['revision']=='54e5ffb8d484de506e59443b07dc819fb15c7233'
        model_manifest=staged[a.model]
        for name,item in model_manifest['files'].items():
            assert sha(Path(model_manifest['snapshot'])/name)==item['sha256'],name
        mapped={row['repo']:row['snapshot'] for row in staged.values()}
        def local(name):
            return mapped.get(str(name),name)
        original_st=retrievers.SentenceTransformer
        def sentence_transformer(name,*args,**kw):
            model=original_st(local(name),*args,**kw)
            profile.update(parameter_dtype=str(next(model.parameters()).dtype),constructor_max_seq_length=model.max_seq_length)
            assert profile['parameter_dtype']=='torch.float32', profile
            original_encode=model.encode
            def encode(*texts,**encode_kw):
                profile['max_seq_length']=model.max_seq_length
                flags=[layer.include_prompt for layer in model.modules() if hasattr(layer,'include_prompt')]
                assert flags and all(flag is False for flag in flags), flags
                assert model.max_seq_length==2048
                assert encode_kw.get('batch_size')==4 and encode_kw.get('normalize_embeddings') is True
                profile['pooling_include_prompt']=flags
                profile.setdefault('encode_calls',[]).append({'texts':len(texts[0]),'batch_size':encode_kw['batch_size'],
                    'normalize_embeddings':encode_kw['normalize_embeddings'],'prompt':encode_kw.get('prompt')})
                return original_encode(*texts,**encode_kw)
            model.encode=encode
            return model
        retrievers.SentenceTransformer=sentence_transformer
        original_tokenizer=retrievers.AutoTokenizer.from_pretrained
        original_model=retrievers.AutoModel.from_pretrained
        def tokenizer(name,*args,**kw):
            tok=original_tokenizer(local(name),*args,**kw)
            profile['tokenizer_max_length']=tok.model_max_length
            return tok
        retrievers.AutoTokenizer.from_pretrained=staticmethod(tokenizer)
        def auto_model(name,*args,**kw):
            model=original_model(local(name),*args,**kw)
            profile['parameter_dtype']=str(next(model.parameters()).dtype)
            return model
        retrievers.AutoModel.from_pretrained=staticmethod(auto_model)
        ordered_docs_sha256=hashlib.sha256(json.dumps(data['documents'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        descriptor={'ordered_documents_sha256':ordered_docs_sha256,'domain':data['domain'],'model_revision':model_manifest['revision'],'tokenizer_revision':model_manifest['revision'],'retrieval_source_sha256':sha(VENDOR/'retrievers.py'),'input_serialization':instructions,'embedding_dtype':'native FP32; actual parameter dtype recorded by hook','max_length':{'inst-l':2048}[a.model],'batch_size':{'inst-l':4}[a.model],'encode_parameters':'unchanged author defaults','normalization':'unchanged author normalization','cutoff_policy':'TEMPO original exclusion metadata, no added known-at filter','versions':{p:importlib.metadata.version(p) for p in ['torch','transformers','sentence-transformers','numpy']}}
        key=hashlib.sha256(json.dumps(descriptor,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        # Each run starts with an exclusively created cold cache; never trust a previous run.
        run_cache_key=hashlib.sha256(a.run_id.encode('utf-8')).hexdigest()
        cache=cache/'instructor-cold'/run_cache_key/key
        cache.mkdir(parents=True,exist_ok=False)
        (cache/'descriptor.json').write_text(json.dumps(descriptor,indent=2)+'\n')
        torch.cuda.reset_peak_memory_stats()
    scores=retrievers.RETRIEVAL_FUNCS[a.model](queries=[q['query'] for q in data['queries']],query_ids=[q['id'] for q in data['queries']],documents=[d['content'] for d in data['documents']],doc_ids=[d['id'] for d in data['documents']],excluded_ids={q['id']:q['excluded_ids'] for q in data['queries']},long_context=False,task=data['domain'],model_id=a.model,instructions=instructions,cache_dir=str(cache))
    elapsed=time.perf_counter()-start
    assert set(scores)=={str(q['id']) for q in data['queries']}
    valid={d['id'] for d in data['documents']}
    for q in data['queries']:
        result=scores[str(q['id'])]
        assert len(result)==min(1000,len(valid-set(q['excluded_ids'])))
        assert set(result).issubset(valid-set(q['excluded_ids']))
    (out/'scores.json').write_text(json.dumps(scores))
    meta={'status':'complete','benchmark':'TEMPO','model':a.model,'queries':len(data['queries']),'documents':len(data['documents']),'input_sha256':sha(path),'scores_sha256':sha(out/'scores.json'),'elapsed_retrieval_seconds':elapsed,'utc_finish':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uid':os.getuid(),'source_sha256':sha(VENDOR/'retrievers.py'),'worker_script_sha256':sha(Path(__file__)),'python':sys.version,'versions':{p:importlib.metadata.version(p) for p in ['pyserini','gensim','pytrec-eval','torch','transformers','numpy','scipy']},'algorithm':'Unchanged released retrieval function, pooling/normalization/defaults, top1000 and author exclusions','instructions':instructions,'model_snapshot':model_manifest,'observed_profile':profile}
    if a.model!='bm25':
        assert profile['parameter_dtype']=='torch.float32',profile
        assert profile.get('max_seq_length',profile.get('tokenizer_max_length'))==descriptor['max_length'],profile
        meta['cache_descriptor']=descriptor
        meta['cache_receipt']=validate_instructor_cache(cache,data['domain'],data['documents'])
        meta['peak_torch_allocated_bytes']=torch.cuda.max_memory_allocated()
        meta['gpu']=torch.cuda.get_device_name()
    (out/'worker.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2),flush=True)
def evaluate(a):
    import retrievers
    private=ROOT/'eval-private'/a.run_id
    out=Path('/home/acl-infer/runs')/a.run_id
    m=json.loads((private/'manifest.json').read_text())
    w=json.loads((out/'worker.json').read_text())
    assert w['status']=='complete' and w['input_sha256']==m['input_sha256']
    assert w['model']==m.get('model','bm25')
    assert sha(out/'scores.json')==w['scores_sha256'] and sha(private/'labels.json')==m['gold_sha256']
    labels=json.loads((private/'labels.json').read_text())
    scores=json.loads((out/'scores.json').read_text())
    assert set(scores)==set(labels)
    qrels={qid:{gid:1 for gid in row['gold_ids']} for qid,row in labels.items()}
    result=retrievers.calculate_retrieval_metrics(scores,qrels)
    destination=ROOT/'results'/a.run_id
    destination.mkdir(exist_ok=False)
    (destination/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    m.update(status='complete',worker=w,summary_sha256=sha(destination/'summary.json'),metric_roles={'Oracle NDCG@*':'Gold-assisted released diagnostic only; not a candidate-constrained ceiling (independent fixture found out-of-top100 tie leakage).','NDCG/MAP/Recall/P/MRR':'Released relevance metrics; original definitions retained.'},deviations=['Missing InstructorEmbedding added to independent environment','Optional unused vLLM imports deferred; BM25/metric functions unchanged','True relevance/answer fields projected out; isolated inference and offline evaluation','Dataset/model inputs pinned; current unpinned package resolution differs from unspecified author environment'])
    (destination/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['worker','evaluate'])
    p.add_argument('--run-id',required=True)
    p.add_argument('--model',choices=['inst-l'],default='inst-l')
    a=p.parse_args()
    globals()[a.mode](a)
