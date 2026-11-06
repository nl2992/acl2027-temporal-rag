"""Run the draft launcher's mount setup in its own namespace, but no model worker."""
from pathlib import Path
import subprocess

source = Path('scripts/drafts/isolated_tempo_instructor_worker.sh').read_text(encoding='utf-8')
lines = source.splitlines()
assert len([line for line in lines if line.startswith('exec runuser ')]) == 1
assert lines[-1].startswith('exec runuser ')
probe = '\n'.join(lines[:-1]) + '''
runuser -u acl-infer -- bash -c '
  set -eu
  test "$(id -un)" = acl-infer
  test "$PWD" = /
  test ! -r /home/nigel/acl2027/eval-private
  test ! -x /home/nigel/acl2027/eval-private
  test -z "$(ls -A /mnt)"
  test -z "$(ls -A /home/nigel/acl2027/results)"
  test -z "$(ls -A /home/nigel/acl2027/tempo-private)"
'
printf '%s\\n' 'PASS: namespace masks checked paths; inference user denied private evaluation directory'
'''
result = subprocess.run(['wsl','-d','Ubuntu-24.04','-u','root','--','unshare','--mount','--fork','bash','-s'], input=probe.encode(), capture_output=True)
if result.returncode:
    print(result.stderr.decode(errors='replace'))
    raise SystemExit(result.returncode)
print(result.stdout.decode(errors='replace').strip())
