"""Validate the immutable guides and complete factorial without ML dependencies."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
for item in json.loads((root / 'manifests/input_documents.json').read_text()):
    assert hashlib.sha256((root / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
original = root / 'docs/guides/ACL2027_Temporal_RAG_Factorial_144.jsonl'
assert original.read_bytes() == (root / 'configs/factorial_144.jsonl').read_bytes()
rows = [json.loads(line) for line in original.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
assert len(rows) == len({r['config_id'] for r in rows}) == 144
assert len({json.dumps(r['factors'], sort_keys=True) for r in rows}) == 144
assert sorted(len({r['factors'][k] for r in rows}) for k in rows[0]['factors']) == [2, 2, 3, 3, 4]
assert all(r['status'] == 'proposed_not_run' and r['metric_k'] == 10 and r['fixed_candidates'] == 100 for r in rows)
print('PASS: guide hashes, working copy, 144 unique configurations, factor levels, and not-run status')
