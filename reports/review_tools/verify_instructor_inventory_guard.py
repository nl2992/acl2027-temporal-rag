"""Test the worker's pinned checkpoint inventory guard without opening weights."""
import ast
import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

source = Path('scripts/drafts/tempo_instructor_isolated.py')
tree = ast.parse(source.read_text(encoding='utf-8'))
worker = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'worker')
branch = next(n for n in worker.body if isinstance(n, ast.If) and "a.model != 'bm25'" in ast.unparse(n.test))
start = next(i for i, n in enumerate(branch.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'staged_record' for t in n.targets))
block = ast.Module(body=branch.body[start:start+3], type_ignores=[])
code = compile(ast.fix_missing_locations(block), str(source), 'exec')
raw = subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u','nigel','--','cat','/home/nigel/acl2027/reports/instructor_source/staged_snapshot.json'])
original = json.loads(raw)
assert len(original['files']) == 12
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    target = root/'reports'/'instructor_source'/'staged_snapshot.json'
    target.parent.mkdir(parents=True)
    def check(value):
        target.write_text(json.dumps(value), encoding='utf-8')
        exec(code, {'ROOT': root, 'json': json, 'hashlib': hashlib})
    check(original)
    for field, replacement in [('snapshot', '/tmp/untrusted'), ('files', {})]:
        changed = copy.deepcopy(original)
        changed[field] = replacement
        try:
            check(changed)
        except AssertionError:
            continue
        raise AssertionError('Modified checkpoint metadata accepted: ' + field)
print('PASS: pinned inventory accepted, altered path and empty inventory rejected; no weights loaded')
