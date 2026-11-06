"""Exercise the disabled runner's real export checks with synthetic artifacts only."""
import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

path = Path('scripts/drafts/run_tempo_instructor_wsl.py')
tree = ast.parse(path.read_text(encoding='utf-8'))
outer_try = next(node for node in tree.body if isinstance(node, ast.Try))
start = next(i for i, node in enumerate(outer_try.body) if isinstance(node, ast.Assert))
end = next(i for i, node in enumerate(outer_try.body[start:], start) if isinstance(node, ast.For))
checks = compile(ast.fix_missing_locations(ast.Module(body=outer_try.body[start:end], type_ignores=[])), str(path), 'exec')
summary = b'{"synthetic": true}'
summary_sha = hashlib.sha256(summary).hexdigest()
runtime = {'run_id': 'fixture', 'wrapper_sha256': 'wrapper', 'evaluator_entry_point_sha256': 'eval', 'same_process': True, 'summary_sha256': summary_sha}
manifest = {'run_id': 'fixture', 'model': 'inst-l', 'worker': {'model': 'inst-l', 'worker_script_sha256': 'worker'}, 'evaluator_runtime': copy.deepcopy(runtime), 'summary_sha256': summary_sha}
base = {'manifest': manifest, 'runtime': runtime, 'run': 'fixture', 'a': SimpleNamespace(model='inst-l'), 'state': {'inference_worker_sha256': 'worker', 'evaluator_entry_sha256': 'eval', 'evaluator_wrapper_sha256': 'wrapper'}, 'exported': {'summary.json': summary}}
context = copy.deepcopy(base)
context['hashlib'] = hashlib
exec(checks, context)
for label, change in [
    ('worker hash', lambda x: x['manifest']['worker'].__setitem__('worker_script_sha256', 'wrong')),
    ('model identity', lambda x: x['manifest']['worker'].__setitem__('model', 'bge')),
    ('evaluator hash', lambda x: x['state'].__setitem__('evaluator_entry_sha256', 'worker')),
    ('wrapper hash', lambda x: x['state'].__setitem__('evaluator_wrapper_sha256', 'wrong')),
    ('same process', lambda x: (x['runtime'].__setitem__('same_process', False), x['manifest']['evaluator_runtime'].__setitem__('same_process', False))),
    ('summary bytes', lambda x: x['exported'].__setitem__('summary.json', b'tampered')),
]:
    context = copy.deepcopy(base)
    context['hashlib'] = hashlib
    change(context)
    try:
        exec(checks, context)
    except AssertionError:
        continue
    raise SystemExit(f'FAIL: accepted {label}')
print('PASS: synthetic export identity and digest checks reject six mismatches; no inference executed')
