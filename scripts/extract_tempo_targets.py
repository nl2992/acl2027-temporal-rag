"""Freeze the pinned author README's retrieval targets without treating them as results."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root=Path(__file__).resolve().parents[1]
source=root/'vendor/Tempo/README.md'
revision=subprocess.check_output(['git','-C',str(source.parent),'rev-parse','HEAD'],text=True).strip()
assert revision=='8731487254e0988eaf2ca4ae3e93ff587fec64d0'
blob=subprocess.check_output(['git','-C',str(source.parent),'show',f'{revision}:README.md'])
assert source.read_text(encoding='utf-8').splitlines()==blob.decode('utf-8').splitlines()
lines=blob.decode('utf-8').splitlines()
header=next(i for i,line in enumerate(lines) if line.startswith('| Domain') and 'DiVeR' in line)
columns=[v.strip() for v in lines[header].strip('|').split('|')][1:]
models={column:{'domains':{}} for column in columns}
for line in lines[header+2:]:
    if not line.startswith('|'):
        break
    values=[re.sub(r'<[^>]+>|\*','',v).strip() for v in line.strip('|').split('|')]
    assert len(values)==len(columns)+1
    domain=values[0].lower()
    domain={'political':'politics'}.get(domain,domain)
    for model,value in zip(columns,values[1:]):
        if domain=='avg.':
            models[model]['macro_average_percentage']=float(value)
        else:
            models[model]['domains'][domain]=float(value)
assert all(len(m['domains'])==13 for m in models.values())
previous=json.loads((root/'configs/published_tempo_bm25.json').read_text())
assert models['BM25']['domains']==previous['domains']
assert models['BM25']['macro_average_percentage']==previous['macro_average']
result={'source':f'https://github.com/tempo-bench/Tempo/blob/{revision}/README.md',
        'source_sha':revision,'readme_blob_sha256':hashlib.sha256(blob).hexdigest(),
        'metric':'ordinary NDCG@10, percentage rounded to one decimal',
        'verification':'Extracted from pinned author README; not a new independent PDF cross-check. These are targets, not measured results.',
        'domain_aliases':{'Political':'politics'},'models':models}
(root/'configs/published_tempo_retrievers.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'Frozen {len(models)} models x 13 author-domain targets; BM25 cross-check passed.')
