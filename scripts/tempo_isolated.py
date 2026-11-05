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
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
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
    scores=retrievers.retrieval_bm25(queries=[q['query'] for q in data['queries']],query_ids=[q['id'] for q in data['queries']],documents=[d['content'] for d in data['documents']],doc_ids=[d['id'] for d in data['documents']],excluded_ids={q['id']:q['excluded_ids'] for q in data['queries']},long_context=False)
    elapsed=time.perf_counter()-start
    assert set(scores)=={str(q['id']) for q in data['queries']}
    valid={d['id'] for d in data['documents']}
    for q in data['queries']:
        result=scores[str(q['id'])]
        assert len(result)==min(1000,len(valid-set(q['excluded_ids'])))
        assert set(result).issubset(valid-set(q['excluded_ids']))
    (out/'scores.json').write_text(json.dumps(scores))
    meta={'status':'complete','benchmark':'TEMPO','model':'bm25','queries':len(data['queries']),'documents':len(data['documents']),'input_sha256':sha(path),'scores_sha256':sha(out/'scores.json'),'elapsed_retrieval_seconds':elapsed,'utc_finish':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uid':os.getuid(),'source_sha256':sha(VENDOR/'retrievers.py'),'versions':{p:importlib.metadata.version(p) for p in ['pyserini','gensim','pytrec-eval','torch','transformers','numpy','scipy']},'algorithm':'Unchanged released retrieval_bm25: Lucene analyzer + gensim LuceneBM25Model k1=0.9,b=0.4, top1000, author exclusions'}
    (out/'worker.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2),flush=True)
def evaluate(a):
    import retrievers
    private=ROOT/'eval-private'/a.run_id
    out=Path('/home/acl-infer/runs')/a.run_id
    m=json.loads((private/'manifest.json').read_text())
    w=json.loads((out/'worker.json').read_text())
    assert w['status']=='complete' and w['input_sha256']==m['input_sha256']
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
    a=p.parse_args()
    globals()[a.mode](a)
