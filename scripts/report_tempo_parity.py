"""Compare completed TEMPO domain metrics, without mixing smoke or oracle scores."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
t=json.loads((root/'configs/published_tempo_bm25.json').read_text())
rows=[]
for path in sorted((root/'reports/tempo').glob('*/manifest.json')):
    m=json.loads(path.read_text())
    if m.get('status')!='complete' or m.get('smoke'):
        continue
    if m.get('model',m['worker']['model'])!='bm25':
        continue
    result=json.loads((path.parent/'summary.json').read_text())
    score=result['NDCG@10']*100
    target=t['domains'][m['domain']]
    rows.append({'run_id':m['run_id'],'domain':m['domain'],'queries':m['queries'],'documents':m['documents'],'ndcg10':result['NDCG@10'],'ndcg10_percentage':score,'published_percentage':target,'matches_published_rounding':abs(score-target)<=0.050000001,'metric_roles':m.get('metric_roles',{})})
latest={r['domain']:r for r in rows}
complete=set(latest)==set(t['domains'])
macro=sum(r['ndcg10'] for r in latest.values())/len(latest) if latest else None
report={'status':'all_domains_measured' if complete else 'partial','metric':'ordinary NDCG@10, not Oracle NDCG','completed_domains':len(latest),'expected_domains':13,'macro_of_available_domains':macro,'full_macro_ndcg10':macro if complete else None,'published_macro_percentage':t['macro_average'],'runs':rows}
(root/'reports/tempo_parity.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# TEMPO BM25 reproduction audit','','Repaired optional imports and isolated scoring/offline evaluation preserve the released BM25 and metric function bodies. Published values are percentages rounded to one decimal. Smoke subsets and gold-assisted oracle values are excluded.','','| Domain | Queries | Documents | Published NDCG@10 (%) | Measured (%) | Same rounding |','|---|---:|---:|---:|---:|---|']
for domain,r in sorted(latest.items()):
    lines.append(f'| {domain} | {r["queries"]} | {r["documents"]} | {r["published_percentage"]:.1f} | {r["ndcg10_percentage"]:.3f} | {r["matches_published_rounding"]} |')
lines+=['',f'{len(latest)}/13 domains complete. A whole-benchmark macro result is reported only after all thirteen domains complete. Ordinary metrics are saved with each run. The released oracle has an independently observed tie/pool defect and is diagnostic only. Temporal Coverage/Precision require the separate author judge stage and have not been measured.']
(root/'reports/tempo_parity.md').write_text('\n'.join(lines)+'\n')
print(f'TEMPO: {len(latest)}/13 completed domains; whole-benchmark macro available={complete}.')
