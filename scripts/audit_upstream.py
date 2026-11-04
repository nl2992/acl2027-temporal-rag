"""Read-only upstream/data audit; no model downloads or vendor modifications."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True

root = Path(__file__).resolve().parents[1]
vendor = root / 'vendor/TimelyRAG'
def git(*args):
    return subprocess.check_output(['git', '-C', str(vendor), *args], text=True).strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'upstream': 'https://github.com/kaist-dmlab/TimelyRAG', 'sha': git('rev-parse', 'HEAD'), 'dirty': git('status', '--porcelain'), 'python': sys.version, 'platform': platform.platform(), 'files': {}, 'datasets': []}
for name in ['config.py', 'requirements.txt', 'pipeline.py', 'retrieval.py', 'metrics.py', 'alpha.py', 'TimelyQABench_datasets.py', 'datasets.zip', 'TimelyRAG_paper.pdf']:
    report['files'][name] = sha(vendor / name)
report['license_files'] = [p.name for p in vendor.iterdir() if 'license' in p.name.lower() or 'copying' in p.name.lower()]
with zipfile.ZipFile(vendor / 'datasets.zip') as archive:
    for name in archive.namelist():
        if not name.endswith('.jsonl') or name.startswith('__MACOSX/'):
            continue
        raw = archive.read(name)
        items = [json.loads(line) for line in raw.decode('utf-8-sig').splitlines() if line.strip()]
        docs = [d for item in items for d in item.get('docs_ko', item.get('docs', []))]
        ids = [d.get('global_doc_id') for d in docs]
        idset = set(ids)
        gold = [g for item in items for g in item.get('gold_docs_final_global', [])]
        report['datasets'].append({'archive_member': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'records': len(items), 'queries': sum(bool(i.get('query_ko', i.get('query'))) for i in items), 'documents': len(docs), 'unique_ids': len(idset), 'missing_ids': ids.count(None), 'duplicate_ids': len(ids)-len(idset), 'global_gold_references': len(gold), 'unresolved_global_gold_references': sum(g not in idset and str(g) not in idset for g in gold), 'document_insert_time_present': sum(bool(d.get('doc_insert_time')) for d in docs), 'event_time_present': sum(bool(d.get('event_time')) for d in docs), 'categories': dict(Counter(str(i.get('category')) for i in items)), 'query_fields': sorted(set().union(*(i.keys() for i in items))), 'document_fields': sorted(set().union(*(d.keys() for d in docs)))})
spec = importlib.util.spec_from_file_location('author_metrics', vendor / 'metrics.py')
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
author = metrics.evaluate_ranking_ids(['a', 'x'], ['a', 'b'], 2)
import math
standard_ndcg = 1 / (1 + 1/math.log2(3))
report['metric_audit'] = {'ranking': ['a', 'x'], 'gold': ['a', 'b'], 'k': 2, 'author_hit_recall_precision_ndcg_ap': [float(x) for x in author], 'standard_binary_ndcg': standard_ndcg, 'standard_ap_denominator_min_gold_k': 0.5, 'conclusion': 'Author nDCG and AP condition ideal/denominator on retrieved positives; keep separate from standard metrics.'}
assert author[3] == 1 and author[4] == 1 and standard_ndcg < 1
out = root / 'manifests/upstream_audit.json'
out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'sha': report['sha'], 'dirty': report['dirty'], 'datasets': [{k:d[k] for k in ['archive_member','queries','documents','unique_ids','unresolved_global_gold_references','event_time_present']} for d in report['datasets']], 'metric_audit': report['metric_audit']}, indent=2))
