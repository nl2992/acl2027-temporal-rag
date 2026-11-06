"""Exercise Windows byte-range lock across processes, using only temporary files."""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path('scripts/drafts/research_gpu_owner.py').resolve()
spec = importlib.util.spec_from_file_location('research_gpu_owner', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
child = """import importlib.util,sys
s=importlib.util.spec_from_file_location('owner',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
try:
    with m.exclusive_owner(sys.argv[2]): pass
except RuntimeError: sys.exit(23)
"""
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'owner.lock'
    with module.exclusive_owner(path):
        busy = subprocess.run([sys.executable, '-c', child, str(source), str(path)])
        assert busy.returncode == 23, busy.returncode
    free = subprocess.run([sys.executable, '-c', child, str(source), str(path)])
    assert free.returncode == 0, free.returncode
    crashing = """import importlib.util,os,sys
s=importlib.util.spec_from_file_location('owner',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with m.exclusive_owner(sys.argv[2]): os._exit(17)
"""
    assert subprocess.run([sys.executable, '-c', crashing, str(source), str(path)]).returncode == 17
    assert subprocess.run([sys.executable, '-c', child, str(source), str(path)]).returncode == 0
print('PASS: lock excludes concurrent owner and releases after exit or crash; no GPU accessed')
