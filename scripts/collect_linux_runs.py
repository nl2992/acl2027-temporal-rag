"""Copy only run summaries/manifests and scientific logs back to the Git workspace."""
import argparse
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--run-id',action='append',default=[])
a=p.parse_args()
def fetch(source,destination,user='nigel'):
    content=subprocess.check_output(['wsl','-d','Ubuntu-24.04','-u',user,'--','cat',source])
    target=root/destination
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(content)
for run in a.run_id:
    for filename in ['manifest.json','summary.json']:
        fetch(f'/home/nigel/acl2027/results/{run}/{filename}',f'reports/baselines/{run}/{filename}')
for name in ['smoke_checks.json','repair.patch']:
    fetch('/home/nigel/acl2027/reports/'+name,'reports/setup/'+name)
print('Collected summaries and evidence; raw labels, input projections, rankings and embeddings remain local.')
