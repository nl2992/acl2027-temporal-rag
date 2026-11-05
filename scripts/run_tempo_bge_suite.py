"""Continue the reviewed BGE track sequentially after full Iota and Quant finish."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
WSL=['wsl','-d','Ubuntu-24.04','-u','root','--']
WORKER_SHA='9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee'
SHELL_SHA='aac2b9e76cfb6b925aa0be3fee4ab81d02a97144863a3c3baedf3f536d35187a'
RETRIEVER_SHA='b207b0d61130b01a9b3c31215c6a5d66cdb8f4b8b83b579898979850639310e4'
DOMAINS=['law','workplace','economics','cardano','monero','travel','bitcoin',
         'genealogy','politics','hsm','history']
HANDOFF={'iota':'tempo-iota-bge-20261105T122024Z','quant':'tempo-quant-bge-20261105T163915Z'}
MODEL=json.loads((ROOT/'manifests/tempo_models.json').read_text(encoding='utf-8-sig'))['bge']

def reference(domain):
    records=[]
    for path in (ROOT/'reports/tempo').glob(f'tempo-{domain}-bm25-*/manifest.json'):
        m=json.loads(path.read_text(encoding='utf-8-sig'))
        if m.get('status')=='complete' and not m.get('smoke'):
            assert m['worker']['model']=='bm25'
            records.append(m)
    assert len(records)==1, f'BM25 reference ambiguous or missing: {domain}'
    return records[0]

def completed(domain):
    found=[]
    base=reference(domain)
    for directory in sorted((ROOT/'reports/tempo').glob(f'tempo-{domain}-bge-*')):
        path=directory/'manifest.json'
        m=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
        if m.get('smoke'):
            continue
        assert path.exists(), f'Unresolved attempt (missing manifest): {directory.name}'
        launch=json.loads((path.parent/'launch.json').read_text(encoding='utf-8-sig'))
        assert m.get('status')==launch.get('status')=='complete', f'Unresolved attempt: {directory.name}'
        assert m['run_id']==launch['run_id']==path.parent.name
        if domain in HANDOFF:
            assert m['run_id']==HANDOFF[domain], f'Unexpected handoff run: {domain}'
        assert m['benchmark']=='TEMPO' and m['model']==m['worker']['model']=='bge'
        assert m['domain']==domain
        assert m['queries']==m['original_queries']>0
        assert m['documents']==m['original_documents']>0
        assert m['worker']['status']=='complete'
        assert m['worker']['queries']==m['queries'] and m['worker']['documents']==m['documents']
        assert m['worker']['input_sha256']==m['input_sha256']
        assert m['dataset_revision']==base['dataset_revision']=='1dba7027d0afa628993c6dd794e9b68c657a6fac'
        assert m['source_sha']==base['source_sha']=='8731487254e0988eaf2ca4ae3e93ff587fec64d0'
        assert m['repaired_sha']=='4bd4324017810ebede72492a3ed869910d668fa7'
        if 'repaired_sha' in base:  # Early BM25 manifests retain the file hash instead.
            assert base['repaired_sha']==m['repaired_sha']
        assert m['worker']['source_sha256']==base['worker']['source_sha256']==RETRIEVER_SHA
        for field in ['input_sha256','raw_file_sha256','gold_sha256','queries','documents']:
            assert m[field]==base[field], f'BGE/BM25 input mismatch: {domain}/{field}'
        assert m['worker']['worker_script_sha256']==launch['worker_script_sha256']==WORKER_SHA
        assert launch['launcher_sha256']==SHELL_SHA
        assert m['worker']['model_snapshot']==MODEL
        assert m['worker']['observed_profile']['parameter_dtype']=='torch.float32'
        assert hashlib.sha256((path.parent/'summary.json').read_bytes()).hexdigest()==m['summary_sha256']
        found.append(path.parent.name)
    assert len(found)<=1, f'Ambiguous completed attempts: {domain}'
    return found

def preflight():
    probe=subprocess.run(WSL+['pgrep','-f',
        'baseline_isolated.py (prepare|worker|evaluate)|tempo_isolated.py (worker|evaluate)|stage_tempo_data.py'],capture_output=True)
    assert probe.returncode==1, 'Research process active or process state unavailable; queue stops'
    values=subprocess.check_output(WSL+['nvidia-smi','--query-gpu=memory.used',
        '--format=csv,noheader,nounits'],text=True).split()
    assert len(values)==1 and values[0].isdigit() and int(values[0])<500, 'GPU unavailable'
    meminfo=subprocess.check_output(WSL+['cat','/proc/meminfo'],text=True)
    memory={line.split(':')[0]:int(line.split()[1]) for line in meminfo.splitlines()}
    assert memory['SwapTotal']>=9*1024**2, 'Temporary swap reserve is inactive; queue stops'
    assert memory['SwapFree']>=4*1024**2 and memory['MemAvailable']>=2*1024**2, 'Memory reserve unavailable'
    filesystem=subprocess.check_output(WSL+['df','-PB1','/home/acl-infer'],text=True).splitlines()
    assert len(filesystem)==2 and int(filesystem[1].split()[3])>=4*1024**3, 'Linux output filesystem reserve unavailable'
    for name,expected in [('tempo_isolated.py',WORKER_SHA),('isolated_tempo_worker.sh',SHELL_SHA)]:
        local=(ROOT/'scripts'/name).read_bytes()
        deployed=subprocess.check_output(WSL+['cat',f'/home/nigel/acl2027/scripts/{name}'])
        assert hashlib.sha256(local).hexdigest()==expected
        assert deployed==local, f'Deployed source differs: {name}'
    retrieval=subprocess.check_output(WSL+['cat','/home/nigel/acl2027/vendor/Tempo-repaired/retrievers.py'])
    assert hashlib.sha256(retrieval).hexdigest()==RETRIEVER_SHA, 'Retrieval source changed'
    assert shutil.disk_usage(ROOT).free>=12*1024**3, 'Less than 12GiB free on host; queue stops'

assert completed('iota'), 'Full Iota BGE is not complete'
assert completed('quant'), 'Full Quant BGE is not complete; no automatic retry'
for domain in DOMAINS:
    done=completed(domain)
    if done:
        print('Already complete:',domain,done,flush=True)
        continue
    preflight()
    print('Starting full BGE domain:',domain,flush=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/run_tempo_wsl.py'),
        '--domain',domain,'--model','bge'],check=True)
    assert completed(domain), f'Child exited without verified full artifacts: {domain}'
print('All full BGE domains completed.',flush=True)
