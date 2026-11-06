"""Exercise the disabled runner's actual lock/failure try block without launching commands."""
import ast
import datetime
import importlib.util
import tempfile
from pathlib import Path

runner = Path('scripts/drafts/run_tempo_instructor_wsl.py')
tree = ast.parse(runner.read_text(encoding='utf-8'))
block = next(n for n in tree.body if isinstance(n, ast.Try))
code = compile(ast.fix_missing_locations(ast.Module(body=[block], type_ignores=[])), str(runner), 'exec')
spec = importlib.util.spec_from_file_location('owner', Path('scripts/drafts/research_gpu_owner.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    lock = Path(tmp) / 'lock'
    records = []
    def denied():
        raise AssertionError('simulated admission refusal')
    env = {'owner': module.exclusive_owner(lock), 'acquired': False, 'check_resources': denied,
           'state': {'status': 'running'}, 'datetime': datetime, 'save': lambda: records.append('saved')}
    try:
        exec(code, env)
    except AssertionError as exc:
        assert str(exc) == 'simulated admission refusal'
    else:
        raise AssertionError('Expected admission failure')
    assert env['state']['status'] == 'failed' and 'simulated admission refusal' in env['state']['error']
    assert len(records) == 1 and 'utc_finish' in env['state']
    with module.exclusive_owner(lock):
        pass
    def broken_save():
        raise OSError('simulated save failure')
    env = {'owner': module.exclusive_owner(lock), 'acquired': False, 'check_resources': denied,
           'state': {'status': 'running'}, 'datetime': datetime, 'save': broken_save}
    try:
        exec(code, env)
    except OSError as exc:
        assert str(exc) == 'simulated save failure'
    else:
        raise AssertionError('Expected save failure')
    with module.exclusive_owner(lock):
        pass
print('PASS: admission and save failure both release lock; no subprocesses or jobs')
