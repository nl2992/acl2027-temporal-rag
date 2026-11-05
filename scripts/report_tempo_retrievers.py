"""Report each pinned TEMPO retriever separately; never count smoke or oracle scores."""
from pathlib import Path
import hashlib
import json

root=Path(__file__).resolve().parents[1]
targets=json.loads((root/'configs/published_tempo_retrievers.json').read_text())
aliases={'bm25':'BM25','bge':'BGE','contriever':'Contriever','diver':'DiVeR',
         'e5':'E5','grit':'GritLM','inst-l':'Inst-L','qwen':'Qwen','rader':'Rader',
         'reasonir':'ReasonIR','sbert':'SBERT','sf':'SFR'}
runs={name:{} for name in targets['models']}
for path in sorted((root/'reports/tempo').glob('*/manifest.json')):
    m=json.loads(path.read_text(encoding='utf-8-sig'))
    if m.get('status')!='complete' or m.get('smoke'):
        continue
    worker=m['worker']
    model=aliases[m.get('model',worker['model'])]
    assert worker['status']=='complete' and m['queries']==m['original_queries']
    assert m['documents']==m['original_documents']
    assert m['run_id']==path.parent.name
    summary=(path.parent/'summary.json').read_bytes()
    assert hashlib.sha256(summary).hexdigest()==m['summary_sha256']
    value=json.loads(summary)['NDCG@10']
    target=targets['models'][model]['domains'][m['domain']]
    runs[model][m['domain']]={'run_id':m['run_id'],'queries':m['queries'],
        'documents':m['documents'],'ndcg10':value,'author_target_percentage':target,
        'within_one_decimal_rounding_interval':abs(value*100-target)<=0.050000001}
report={'source':targets['source'],'metric':targets['metric'],
        'scope':'Ordinary retrieval metrics only; temporal LLM-judge metrics unmeasured. Smoke and oracle excluded.',
        'models':{}}
lines=['# TEMPO retriever coverage','',report['scope'],
       'Targets come from the pinned author README; full-benchmark reproduction remains unverified for every incomplete row.',
       '', '| Retriever | Full domains | Matching target rounding | Full macro nDCG@10 |',
       '|---|---:|---:|---:|']
for model,domains in runs.items():
    expected=set(targets['models'][model]['domains'])
    assert set(domains)<=expected
    full=set(domains)==expected
    macro=sum(r['ndcg10'] for r in domains.values())/len(domains) if full else None
    matched=sum(r['within_one_decimal_rounding_interval'] for r in domains.values())
    report['models'][model]={'completed_domains':len(domains),'expected_domains':len(expected),
        'full_macro_ndcg10':macro,'matching_domain_rounding':matched,'runs':domains}
    shown=f'{macro:.6f}' if macro is not None else 'Pending'
    lines.append(f'| {model} | {len(domains)}/{len(expected)} | {matched}/{len(domains)} | {shown} |')
lines+=['','Hardware, source and dataset barriers remain incomplete work; see baseline_registry.md and compute_limits_and_rental_plan.md.',
        'A complete retrieval row alone does not establish temporal-judge parity or permit combinatorial search.']
(root/'reports/tempo_retriever_coverage.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'reports/tempo_retriever_coverage.md').write_text('\n'.join(lines)+'\n')
print('Verified available full-domain artifacts; reported coverage and missing work for 12 retrievers.')
