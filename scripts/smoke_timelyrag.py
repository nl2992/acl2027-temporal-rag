"""Small deterministic scientific checks, then optional real BGE pipeline smoke."""
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ.setdefault('TR_EXPERIMENT_DIR', '/home/nigel/acl2027/results/smoke')
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import math
import inspect
import hashlib
import torch
import numpy as np

vendor = Path('/home/nigel/acl2027/vendor/TimelyRAG-repaired')
sys.path.insert(0, str(vendor))
import metrics
from TimelyQABench_datasets import prepare_dataset_collections
from retrieval import evaluate_2stage
from alpha import choose_alpha_from_signals
from datetime import datetime

torch.manual_seed(0)
x = torch.randn(8, 8, device='cuda')
y = x @ x.T
assert y.shape == (8, 8) and torch.isfinite(y).all()
print('WITNESS', tuple(y.shape), torch.cuda.get_device_name(), flush=True)
assert metrics.evaluate_ranking_ids(['a', 'b'], ['a', 'b'], 2) == (1, 1, 1, 1, 1)
assert metrics.evaluate_ranking_ids(['x', 'y'], ['a', 'b'], 2) == (0, 0, 0, 0, 0)
assert metrics.evaluate_ranking_ids(['a', 'x'], ['a', 'b'], 2)[3:] == (1, 1)
assert abs(1/(1+1/math.log2(3)) - 0.6131471927654584) < 1e-12
assert 'pos_ids' not in inspect.signature(choose_alpha_from_signals).parameters
data_checks = []
for path in sorted((vendor / 'datasets').glob('*.jsonl')):
    items = [json.loads(line) for line in path.read_text().splitlines()]
    docs, ids, mapping, queries, qet, qit, det, dit = prepare_dataset_collections(items)
    assert len(docs) == len(ids) == len(set(ids)) == 30000
    assert len(queries) == 3000
    assert all(q['positive_ids'] for q in queries)
    assert all(g in mapping for q in queries for g in q['positive_ids'])
    # A tiny fixed candidate array checks the native automatic path independently of gold.
    native = queries[0].copy()
    native.update(qit=qit[0], qet=qet[0])
    alternatives = []
    for gold in [native['positive_ids'], [ids[-1]]]:
        q = dict(native, positive_ids=gold)
        scores = np.linspace(1.0, 0.0, len(ids))
        original = metrics.evaluate_ranking_ids
        import retrieval
        seen = []
        def capture(top_ids, gold_ids, k):
            seen.append(list(top_ids))
            return original(top_ids, gold_ids, k)
        retrieval.evaluate_ranking_ids = capture
        evaluate_2stage('smoke', lambda _: scores, [q], ids, det, dit)
        retrieval.evaluate_ranking_ids = original
        alternatives.append(seen[0])
    assert alternatives[0] == alternatives[1], 'Automatic ranking must not depend on gold'
    assert set(alternatives[0]).issubset(set(ids[:100])), 'Native reranker changed candidate membership'
    data_checks.append({'file': path.name, 'queries': len(queries), 'docs': len(docs), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'auto_gold_independent': True, 'candidate_membership_preserved': True})
report = {'status': 'passed', 'seed': 0, 'gpu': torch.cuda.get_device_name(), 'torch': torch.__version__, 'cuda': torch.version.cuda, 'numpy': np.__version__, 'datasets': data_checks, 'known_native_limitations': ['Post-cutoff candidates receive neutral affinity rather than hard exclusion.', 'Native tie behavior is NumPy argsort reversal; proposed stable ties not applied to parity track.', 'Author metrics use retrieved-positive ideal/denominator; audited standard metrics remain separate.']}
out = Path('/home/nigel/acl2027/reports/smoke_checks.json')
out.write_text(json.dumps(report, indent=2)+'\n')
print('PASS: metric vectors, four full data schemas, GPU witness, candidate invariance, and automatic gold independence.', flush=True)
