"""Run the draft's read-only evaluation-directory boundary probe, without inference."""
import ast
import subprocess
from pathlib import Path

path = Path('scripts/drafts/run_tempo_instructor_wsl.py')
node = next(n for n in ast.parse(path.read_text(encoding='utf-8')).body
            if isinstance(n, ast.FunctionDef) and n.name == 'check_private_evaluation_boundary')
env = {'subprocess': subprocess}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), 'exec'), env)
env['check_private_evaluation_boundary']()
print('PASS: eval-private is owner-only and inference user cannot read or traverse; no namespace or inference launched')
