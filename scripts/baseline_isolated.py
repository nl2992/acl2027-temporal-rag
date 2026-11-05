"""Gold-free prediction worker, followed by independent offline author-metric evaluation."""
import argparse
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import datetime
import subprocess

ROOT = Path('/home/nigel/acl2027')
VENDOR = ROOT / 'vendor/TimelyRAG-repaired'
sys.dont_write_bytecode = True
sys.path.insert(0, str(VENDOR))
os.environ.setdefault('TR_EXPERIMENT_DIR', '/tmp/acl-config')
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('MKL_NUM_THREADS','4')
REVISION = '5617a9f61b028005a4858fdac845db406aefb181'
DOMAINS = {'company':'company_policies','law':'law','terms':'terms_of_service','university':'university'}

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def prepare(args):
    from TimelyQABench_datasets import prepare_dataset_collections
    source = VENDOR / 'datasets' / f'timelyrag_{DOMAINS[args.domain]}_dataset_v2.jsonl'
    items = [json.loads(line) for line in source.read_text().splitlines()]
    if args.smoke:
        items=items[:2]
    docs,ids,mapping,queries,qet,qit,det,dit = prepare_dataset_collections(items)
    base=Path('/home/acl-infer') / 'inputs' / args.run_id
    base.mkdir(parents=True,exist_ok=False)
    private=ROOT / 'eval-private' / args.run_id
    private.mkdir(parents=True,exist_ok=False)
    def stamp(x):
        return x.isoformat() if x is not None else None
    public={'domain':args.domain,'smoke':args.smoke,'ids':ids,'docs':docs,'dit':[stamp(x) for x in dit],'det':[stamp(x) for x in det], 'queries':[{'query_id':f'{args.domain}:{i}','query':q['query'],'qit':stamp(qit[i]),'qet':stamp(qet[i])} for i,q in enumerate(queries)]}
    labels={f'{args.domain}:{i}':{'gold':q['positive_ids'],'category':q['raw_item'].get('category')} for i,q in enumerate(queries)}
    (base/'input.json').write_text(json.dumps(public,ensure_ascii=False))
    (private/'labels.json').write_text(json.dumps(labels,ensure_ascii=False))
    manifest={'run_id':args.run_id,'domain':args.domain,'smoke':args.smoke,'purpose':'author-scoring-replay-with-isolated-evaluation','source_sha256':sha(source),'input_sha256':sha(base/'input.json'),'gold_sha256':sha(private/'labels.json'),'upstream_sha':'5213a0c1743f23fd52a258005c3887aaf7e8cd0f','repaired_sha':subprocess.check_output(['git','-C',str(VENDOR),'rev-parse','HEAD'],text=True).strip(),'script_sha256':sha(Path(__file__)),'queries':len(queries),'documents':len(docs),'backbone':args.backbone,'metric_k':10,'candidate_pool':100,'model_revision':REVISION,'gold_policy':'Gold-free input projection; separate unprivileged mount-isolated worker. Sentinel-positive evaluator calls capture author rankings; true labels opened only after worker exits. Oracle selected offline by author strict-first-max nDCG.'}
    (private/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    os.chmod(ROOT/'eval-private',0o700)
    print(json.dumps(manifest,indent=2),flush=True)

def worker(args):
    import numpy as np
    import torch
    from datetime import datetime
    from rank_bm25 import BM25Okapi
    import retrieval
    import metrics
    from config import K, STAGE1_TOPN, ALPHA_GRID
    assert (K,STAGE1_TOPN)==(10,100)
    assert os.getcwd() == '/', 'Worker must not retain an open Windows working directory'
    # These paths must be genuinely inaccessible, not merely omitted from arguments.
    protected=[ROOT/'eval-private'/args.run_id/'labels.json',ROOT/'vendor/TimelyRAG/datasets.zip',VENDOR/'datasets.zip',Path('/mnt/c/Users/nigel/Downloads/ACL2027_Temporal_RAG_Replication_Protocol.md'),Path('vendor/TimelyRAG/datasets.zip'),ROOT/'vendor/TimelyRAG/timelyrag_company_policies_dataset_v2.jsonl',VENDOR/'datasets/timelyrag_company_policies_dataset_v2.jsonl']
    for path in protected:
        try:
            with open(path,'rb') as f:
                accessible=f.read(1)
        except (PermissionError,FileNotFoundError,IsADirectoryError):
            continue
        if accessible:
            raise AssertionError(f'Inference can access protected bytes: {path}')
    input_path=Path('/home/acl-infer/inputs')/args.run_id/'input.json'
    data=json.loads(input_path.read_text())
    assert all(set(q)=={'query_id','query','qit','qet'} for q in data['queries'])
    output=Path('/home/acl-infer/runs')/args.run_id
    output.mkdir(parents=True,exist_ok=False)
    start=time.time()
    meta={'status':'running','utc_start':datetime.now().astimezone().isoformat(),'input_sha256':sha(input_path),'label_access_probes':'passed','python':sys.version,'uid':os.getuid(),'torch':torch.__version__,'cuda':torch.version.cuda,'numpy':np.__version__,'backbone':args.backbone,'scoring_source_sha256':{n:sha(VENDOR/n) for n in ['retrieval.py','alpha.py','time_scores.py','time_utils.py','metrics.py']}}
    (output/'worker.json').write_text(json.dumps(meta,indent=2))
    snapshot=None
    if args.backbone=='dense':
        from huggingface_hub import snapshot_download
        snapshot=snapshot_download('BAAI/bge-m3',revision=REVISION,cache_dir='/home/acl-infer/models',local_files_only=True)
        meta.update(model_revision=REVISION,model_file_sha256={str(p.relative_to(snapshot)):sha(p) for p in Path(snapshot).rglob('*') if p.is_file()},gpu=torch.cuda.get_device_name(),gpu_total_bytes=torch.cuda.get_device_properties(0).total_memory)
        original=retrieval.BGEM3FlagModel
        retrieval.BGEM3FlagModel=lambda name,*a,**kw:original(snapshot,*a,**kw)
        torch.cuda.reset_peak_memory_stats()
        print('Building author BGE-M3 document embeddings',flush=True)
        bundle=retrieval.RetrieverBundle(data['docs'],device='cuda')
        score_fn=bundle.dense_scores
        np.save(output/'document_embeddings.npy',bundle.doc_embeddings)
    else:
        # Identical constructor/tokenization to RetrieverBundle, without loading unused BGE.
        bm25=BM25Okapi([d.split() for d in data['docs']])
        score_fn=lambda q:bm25.get_scores(q.split())
    (output/'worker.json').write_text(json.dumps(meta,indent=2))
    def parse(x):
        return datetime.fromisoformat(x) if x else None
    det=np.array([parse(x) for x in data['det']],dtype=object)
    dit=np.array([parse(x) for x in data['dit']],dtype=object)
    retrieval.tqdm=lambda seq,*a,**kw:seq
    original_eval=metrics.evaluate_ranking_ids
    current={}
    def capture(top,gold,k):
        frame=sys._getframe(1)
        if frame.f_code.co_name=='rerank_with_alpha_grid':
            current['grid'].append({'alpha':float(frame.f_locals['a']),'top_ids':list(top)})
        elif frame.f_code.co_name=='evaluate_2stage' and top is frame.f_locals.get('reranked_auto_gids'):
            current['auto']=list(top)
        # Native evaluator sees only an impossible sentinel, never true relevance.
        assert gold==['__NO_TRUE_GOLD__']
        return original_eval(top,gold,k)
    retrieval.evaluate_ranking_ids=capture
    with (output/'predictions.jsonl').open('w') as stream:
        for i,q in enumerate(data['queries']):
            t=time.perf_counter()
            scores=score_fn(q['query'])
            score_seconds=time.perf_counter()-t
            assert np.isfinite(scores).all()
            cand=np.argsort(scores)[::-1][:min(100,len(scores))]
            candidate_ids=[data['ids'][j] for j in cand]
            current.clear()
            current['grid']=[]
            native={'query':q['query'],'qit':parse(q['qit']),'qet':parse(q['qet']),'positive_ids':['__NO_TRUE_GOLD__']}
            t=time.perf_counter()
            a,b,auto_hist,best_hist=retrieval.evaluate_2stage('isolated_replay',lambda _:scores,[native],data['ids'],det,dit)
            rerank_seconds=time.perf_counter()-t
            assert len(current['grid'])==len(ALPHA_GRID)==11
            assert [r['alpha'] for r in current['grid']]==ALPHA_GRID
            assert len(set(candidate_ids))==len(candidate_ids)
            rankings=[candidate_ids[:10],current['auto']]+[r['top_ids'] for r in current['grid']]
            assert all(len(r)==min(10,len(data['ids'])) and len(set(r))==len(r) and set(r).issubset(set(candidate_ids)) for r in rankings)
            record={'query_id':q['query_id'],'candidate_ids':candidate_ids,'candidate_scores':[float(scores[j]) for j in cand],'baseline':candidate_ids[:10],'auto':current['auto'],'grid':current['grid'],'auto_alpha':next(float(k) for k,v in auto_hist.items() if v),'score_seconds':score_seconds,'instrumented_rerank_with_all_grid_seconds':rerank_seconds}
            stream.write(json.dumps(record)+'\n')
            stream.flush()
            if i%100==0:
                print(f'{args.run_id}: {i+1}/{len(data["queries"])} queries',flush=True)
    meta.update(status='complete',queries=len(data['queries']),documents=len(data['docs']),elapsed_seconds=time.time()-start,utc_finish=datetime.now().astimezone().isoformat(),peak_torch_vram_bytes=torch.cuda.max_memory_allocated() if args.backbone=='dense' else 0,predictions_sha256=sha(output/'predictions.jsonl'))
    (output/'worker.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2),flush=True)

def evaluate(args):
    import numpy as np
    import metrics
    private=ROOT/'eval-private'/args.run_id
    output=Path('/home/acl-infer/runs')/args.run_id
    worker_meta=json.loads((output/'worker.json').read_text())
    assert worker_meta['status']=='complete'
    manifest=json.loads((private/'manifest.json').read_text())
    assert worker_meta['input_sha256']==manifest['input_sha256']
    assert sha(output/'predictions.jsonl')==worker_meta['predictions_sha256']
    assert sha(private/'labels.json')==manifest['gold_sha256']
    assert worker_meta['queries']==manifest['queries'] and worker_meta['documents']==manifest['documents']
    assert args.backbone==manifest['backbone']==worker_meta['backbone']
    manifest['evaluator_script_sha256']=sha(Path(__file__))
    labels=json.loads((private/'labels.json').read_text())
    rows=[json.loads(line) for line in (output/'predictions.jsonl').read_text().splitlines()]
    assert len(rows)==len(labels)==len({r['query_id'] for r in rows})
    summaries={m:[] for m in ['baseline','auto','oracle_best']}
    per_query=[]
    for row in rows:
        gold=labels[row['query_id']]['gold']
        best=None
        best_ndcg=-1
        for entry in row['grid']:
            score=metrics.evaluate_ranking_ids(entry['top_ids'],gold,10)[3]
            if score>best_ndcg:
                best_ndcg=score
                best=entry
        for method,top in [('baseline',row['baseline']),('auto',row['auto']),('oracle_best',best['top_ids'])]:
            vals=list(map(float,metrics.evaluate_ranking_ids(top,gold,10)))
            rel=[int(g in set(gold)) for g in top]
            dcg=sum(v/np.log2(i+2) for i,v in enumerate(rel))
            ideal=sum(1/np.log2(i+2) for i in range(min(10,len(set(gold)))))
            standard_ndcg=float(dcg/ideal) if ideal else 0.0
            standard_map=float(sum(sum(rel[:i+1])/(i+1) for i,v in enumerate(rel) if v)/max(1,min(10,len(set(gold)))))
            summaries[method].append(vals+[standard_ndcg,standard_map])
            per_query.append({'query_id':row['query_id'],'method':method,'oracle':method=='oracle_best','category':labels[row['query_id']]['category'],'author':dict(zip(['hit','recall','precision','ndcg','map'],vals)),'standard':{'ndcg':standard_ndcg,'map':standard_map}})
    keys=['hit','recall','precision','ndcg','map','standard_ndcg','standard_map']
    summary={m:dict(zip(keys,map(float,np.mean(vals,axis=0)))) for m,vals in summaries.items()}
    summary['candidate_recall100']=float(np.mean([len(set(r['candidate_ids'])&set(labels[r['query_id']]['gold']))/len(set(labels[r['query_id']]['gold'])) for r in rows]))
    summary['oracle_recall10_ceiling']=float(np.mean([min(10,len(set(r['candidate_ids'])&set(labels[r['query_id']]['gold'])))/len(set(labels[r['query_id']]['gold'])) for r in rows]))
    destination=ROOT/'results'/args.run_id
    destination.mkdir(parents=True,exist_ok=False)
    (destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (destination/'per_query_metrics.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in per_query))
    manifest.update(status='complete',worker=worker_meta,summary_sha256=sha(destination/'summary.json'),per_query_metrics_sha256=sha(destination/'per_query_metrics.jsonl'),deviations=['Repaired executable/environment; not verbatim native replication','Gold-free projection and offline oracle evaluation','BM25 path skips unused BGE initialization; same BM25 constructor and defaults','Base scores computed once then passed unchanged to author reranker','Native alpha/scoring/NumPy ties preserved; no proposed reranker components'])
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['prepare','worker','evaluate'])
    p.add_argument('--domain',choices=list(DOMAINS),required=True)
    p.add_argument('--backbone',choices=['bm25','dense'],required=True)
    p.add_argument('--run-id',required=True)
    p.add_argument('--smoke',action='store_true')
    a=p.parse_args()
    globals()[a.mode](a)
