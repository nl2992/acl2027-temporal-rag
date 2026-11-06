"""Check the draft worker's cold-cache allocation without loading a model."""
import ast
import hashlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

source = Path('scripts/drafts/tempo_instructor_isolated.py').read_text(encoding='utf-8')
worker = next(x for x in ast.parse(source).body if isinstance(x, ast.FunctionDef) and x.name == 'worker')
branch = next(x for x in worker.body if isinstance(x, ast.If) and "a.model != 'bm25'" in ast.unparse(x.test))
start = next(i for i, x in enumerate(branch.body) if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'run_cache_key' for t in x.targets))
statements = branch.body[start:start+4]
code = compile(ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[])), '<draft-cache>', 'exec')
with tempfile.TemporaryDirectory() as tmp:
    def allocate(run):
        env = {'cache': Path(tmp), 'a': SimpleNamespace(run_id=run), 'key': 'descriptor-key', 'descriptor': {'fixture': True}, 'hashlib': hashlib, 'json': json}
        exec(code, env)
        return env['cache']
    one = allocate('run-1')
    (one / 'untrusted.bin').write_bytes(b'test')
    two = allocate('run-2')
    assert one != two and sorted(p.name for p in two.iterdir()) == ['descriptor.json']
    try:
        allocate('run-1')
    except FileExistsError:
        pass
    else:
        raise AssertionError('Previously allocated cache was accepted')
    assert (one / 'untrusted.bin').read_bytes() == b'test'
print('PASS: per-run cold cache rejects reuse and preserves existing files; synthetic filesystem only')
