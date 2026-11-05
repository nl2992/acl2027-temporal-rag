"""Apply only documented executable repairs in the Linux repaired worktree."""
from pathlib import Path
import json
import subprocess
import zipfile

root = Path('/home/nigel/acl2027')
vendor = root / 'vendor/TimelyRAG-repaired'
assert subprocess.check_output(['git', '-C', str(vendor), 'merge-base', 'HEAD', '5213a0c1743f23fd52a258005c3887aaf7e8cd0f'], text=True).strip() == '5213a0c1743f23fd52a258005c3887aaf7e8cd0f'
config = vendor / 'config.py'
config.write_text(config.read_text().replace('timelyrag_yonsei_dataset_v2.jsonl', 'timelyrag_university_dataset_v2.jsonl'))
pipeline = vendor / 'pipeline.py'
pipeline.write_text(pipeline.read_text().replace('from .metrics import ', 'from metrics import '))
with zipfile.ZipFile(vendor / 'datasets.zip') as archive:
    for name in archive.namelist():
        if '/' not in name and name.endswith('.jsonl'):
            target = vendor / 'datasets' / name
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                target.write_bytes(archive.read(name))
for name in ['config.py', 'pipeline.py', 'requirements.txt']:
    subprocess.run(['git', '-C', str(vendor), 'add', name], check=True)
if subprocess.run(['git', '-C', str(vendor), 'diff', '--cached', '--quiet']).returncode:
    subprocess.run(['git', '-C', str(vendor), '-c', 'user.name=ACL Research Setup', '-c', 'user.email=research@localhost', 'commit', '-m', 'Repair Notebook dependency, university filename and top-level metric imports'], check=True)
patch = subprocess.check_output(['git', '-C', str(vendor), 'diff', '5213a0c1743f23fd52a258005c3887aaf7e8cd0f', 'HEAD'])
(root / 'reports/repair.patch').write_bytes(patch)
print('Applied executable repairs; extracted byte-identical datasets; scoring code untouched.')
