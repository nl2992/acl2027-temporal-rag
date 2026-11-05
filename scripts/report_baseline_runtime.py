"""Summarize measured per-query timing; never relabel grid timing as auto-only."""
from pathlib import Path
import json
import statistics
import subprocess

root=Path(__file__).resolve().parents[1]
records=[]
for manifest in sorted((root/'reports/baselines').glob('baseline-*/manifest.json')):
    m=json.loads(manifest.read_text())
    if m.get('status')!='complete' or m.get('smoke'):
        continue
    raw=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat',f'/home/acl-infer/runs/{m["run_id"]}/predictions.jsonl'])
    rows=[json.loads(line) for line in raw.decode().splitlines()]
    def describe(key):
        vals=sorted(r[key] for r in rows)
        return {'mean_seconds':statistics.mean(vals),'median_seconds':statistics.median(vals),'p95_seconds':vals[min(len(vals)-1,int(0.95*len(vals)))],'queries':len(vals)}
    records.append({'run_id':m['run_id'],'domain':m['domain'],'backbone':m['backbone'],'base_scoring':describe('score_seconds'),'native_rerank_plus_all_11_grid_trials':describe('instrumented_rerank_with_all_grid_seconds'),'worker_elapsed_seconds':m['worker']['elapsed_seconds'],'peak_torch_allocated_bytes':m['worker']['peak_torch_vram_bytes'],'interpretation':'Grid timing includes oracle-ranking enumeration with sentinel labels and in-memory metric/capture instrumentation; excludes prediction write/flush; not automatic-only latency and not matched to paper Table9 @5/N50.'})
(root/'reports/baseline_runtime.json').write_text(json.dumps(records,indent=2)+'\n')
print(f'Summarized measured timing for {len(records)} completed runs.')
