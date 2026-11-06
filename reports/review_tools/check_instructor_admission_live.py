"""Exercise disabled draft admission check against the currently live Linux worker."""
import ast
import shutil
import subprocess
from pathlib import Path

path = Path('scripts/drafts/run_tempo_instructor_wsl.py')
tree = ast.parse(path.read_text(encoding='utf-8'))
fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'check_resources')
env = {'subprocess': subprocess, 'shutil': shutil, 'root': Path.cwd()}
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(path), 'exec'), env)
try:
    env['check_resources']()
except AssertionError as exc:
    assert str(exc) == 'Research process active or process state unavailable', str(exc)
    print('PASS: admission refused while research process is active; no job launched')
else:
    raise SystemExit('FAIL: expected the currently active research process to block admission')
