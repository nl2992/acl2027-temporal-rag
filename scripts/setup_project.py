"""Preserve supplied guides and initialize auditable project scaffolding."""
from pathlib import Path
import hashlib
import itertools
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
for folder in ['docs/guides', 'configs', 'manifests', 'reports', 'data/raw', 'data/splits', 'data/processed', 'cache/retrieval', 'cache/temporal', 'cache/claims', 'results/native', 'results/dev', 'results/locked', 'src/adapters', 'src/features', 'src/rerank', 'src/eval', 'src/stats', 'tests', 'vendor']:
    p = ROOT / folder
    p.mkdir(parents=True, exist_ok=True)
    if not any(p.iterdir()):
        (p / '.gitkeep').touch()
records = []
for name in ['ACL2027_Temporal_RAG_Replication_Protocol.md', 'ACL2027_Temporal_RAG_Factorial_144.jsonl']:
    source = Path.home() / 'Downloads' / name
    target = ROOT / 'docs/guides' / name
    shutil.copy2(source, target)
    records.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'source': 'user-supplied; preserved byte-for-byte'})
(ROOT / 'manifests/input_documents.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
shutil.copy2(ROOT / records[1]['path'], ROOT / 'configs/factorial_144.jsonl')
rows = [json.loads(line) for line in (ROOT / records[1]['path']).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
assert len(rows) == 144
assert len({r['config_id'] for r in rows}) == 144
assert len({json.dumps(r['factors'], sort_keys=True) for r in rows}) == 144
assert all(r['status'] == 'proposed_not_run' and r['fixed_candidates'] == 100 and r['metric_k'] == 10 for r in rows)
assert sorted(len({r['factors'][k] for r in rows}) for k in rows[0]['factors']) == [2, 2, 3, 3, 4]
print('Preserved both documents; validated 144 unique factorial cells (3 x 4 x 3 x 2 x 2).')
