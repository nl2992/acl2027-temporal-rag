"""Summarize completed repaired runs against frozen rounded author targets."""
from pathlib import Path
import json
import subprocess

root=Path(__file__).resolve().parents[1]
targets=json.loads((root/'configs/published_timelyrag_table4.json').read_text())
rows=[]
for path in sorted((root/'reports/baselines').glob('baseline-*/manifest.json')):
    m=json.loads(path.read_text())
    if m.get('status')!='complete' or m.get('smoke'):
        continue
    s=json.loads((path.parent/'summary.json').read_text())
    domain,backbone=m['domain'],m['backbone']
    for method in ['baseline','auto']:
        expected=targets['domains'][domain][backbone][method]
        measured=s[method]
        delta={k:measured[k]-v for k,v in expected.items()}
        rows.append({'run':m['run_id'],'domain':domain,'backbone':backbone,'method':method,'queries':m['queries'],'published':expected,'measured':{k:measured[k] for k in expected},'delta':delta,'ndcg_gate':'within_tolerance' if abs(delta['ndcg'])<=targets['ndcg_absolute_tolerance'] else 'mismatch','candidate_recall100':s['candidate_recall100']})
    # Category labels remain unmerged; historical Company comparison uses its exact released string.
    cmd=['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',f'/home/nigel/acl2027/results/{m["run_id"]}/per_query_metrics.jsonl']
    pq=[json.loads(line) for line in subprocess.check_output(cmd).decode().splitlines()]
    groups={}
    for item in pq:
        key=(item['method'],item['category'])
        groups.setdefault(key,[]).append(item)
    subgroups=[{'method':method,'raw_category':category,'queries':len(items),'author_ndcg':sum(i['author']['ndcg'] for i in items)/len(items),'standard_ndcg':sum(i['standard']['ndcg'] for i in items)/len(items)} for (method,category),items in groups.items()]
    (path.parent/'subgroups_raw.json').write_text(json.dumps(subgroups,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
out=root/'reports/baseline_parity.json'
out.write_text(json.dumps({'targets':targets['source'],'status':'partial' if len(rows)<16 else ('all_ndcg_cells_within_tolerance' if all(r['ndcg_gate']=='within_tolerance' for r in rows) else 'REPRO_PARTIAL'),'cells':rows},indent=2)+'\n')
lines=['# Repaired baseline parity audit','', 'Rounded published targets are reference values. All measured runs below use repaired executable/environment and isolated evaluation; none is a verbatim native replication. No tuning to published scores. Standard metrics and oracle diagnostics remain separate.','', '| Domain | Backbone | Method | Queries | Published nDCG@10 | Measured author nDCG@10 | Difference | Gate |','|---|---|---|---:|---:|---:|---:|---|']
for r in rows:
    lines.append(f'| {r["domain"]} | {r["backbone"]} | {r["method"]} | {r["queries"]} | {r["published"]["ndcg"]:.3f} | {r["measured"]["ndcg"]:.6f} | {r["delta"]["ndcg"]:+.6f} | {r["ndcg_gate"]} |')
lines+=['','Only completed full-domain runs are included. Missing domains remain pending. Any mismatch requires discrepancy analysis rather than baseline tuning. Full four-metric differences: baseline_parity.json. Raw-category subgroup summaries are saved beside each run summary.']
(root/'reports/baseline_parity.md').write_text('\n'.join(lines)+'\n')
print(f'Summarized {len(rows)} completed published-cell comparisons.')
