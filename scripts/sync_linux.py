"""Copy tracked project scripts into WSL; never copy datasets or credentials."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for source in sorted(p for p in (root / 'scripts').iterdir() if p.suffix in ['.py','.sh']):
    target = '/home/nigel/acl2027/scripts/' + source.name
    program = 'import sys; from pathlib import Path; p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(sys.stdin.buffer.read())'
    subprocess.run(['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--', 'python3', '-c', program, target], input=source.read_bytes(), check=True)
print('Synced project Python scripts into Linux.')
