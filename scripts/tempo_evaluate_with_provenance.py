"""Run the unchanged offline TEMPO evaluator and witness its actual imported provider."""
import argparse
import base64
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import sys

ROOT=Path('/home/nigel/acl2027')
SCRIPT=ROOT/'scripts/tempo_isolated.py'
EXPECTED='9f0e5555495972ea6cb076d46fe11b2b4052cf1295cb066e2093b53bf601c3ee'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda:source.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def witness():
    import pytrec_eval
    files={}
    for name,module in list(sys.modules.items()):
        if name.startswith('pytrec_eval') and getattr(module,'__file__',None):
            path=Path(module.__file__).resolve()
            files[name]={'path':str(path),'sha256':sha(path)}
    providers={}
    for name in ['pytrec-eval','pytrec-eval-terrier']:
        try:
            dist=importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            continue
        matches=[]
        for entry in dist.files or []:
            actual=Path(dist.locate_file(entry)).resolve()
            for module,info in files.items():
                if str(actual)==info['path']:
                    expected=entry.hash
                    digest=base64.urlsafe_b64encode(bytes.fromhex(info['sha256'])).decode().rstrip('=')
                    matches.append({'module':module,'record_path':str(entry),
                        'record_hash_algorithm':expected.mode if expected else None,
                        'record_hash_value':expected.value if expected else None,
                        'matches_imported_bytes':bool(expected and expected.mode=='sha256' and expected.value==digest)})
        providers[name]={'distribution_version':dist.version,'record_entries':matches}
    return {'module_files':files,'installed_distribution_metadata':providers,
        'evaluator_class_mro':[f'{cls.__module__}.{cls.__name__}' for cls in pytrec_eval.RelevanceEvaluator.__mro__],
        'interpretation':'Module bytes observed in this evaluation process; distribution version alone does not identify an overwritten import.'}

def main():
    p=argparse.ArgumentParser()
    selection=p.add_mutually_exclusive_group(required=True)
    selection.add_argument('--run-id')
    selection.add_argument('--describe-only',action='store_true')
    args=p.parse_args()
    if args.describe_only:
        print(json.dumps(witness(),indent=2))
        return
    assert sha(SCRIPT)==EXPECTED, 'Evaluator entry point changed'
    wrapper_sha=sha(Path(__file__))
    before=witness()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    sys.argv=[str(SCRIPT),'evaluate','--run-id',args.run_id]
    runpy.run_path(str(SCRIPT),run_name='__main__')
    after=witness()
    assert before==after and sha(SCRIPT)==EXPECTED, 'Evaluator files changed during the run'
    assert sha(Path(__file__))==wrapper_sha, 'Provenance wrapper changed during the run'
    destination=ROOT/'results'/args.run_id
    manifest=destination/'manifest.json'
    m=json.loads(manifest.read_bytes())
    summary_sha=sha(destination/'summary.json')
    assert m['run_id']==args.run_id and m['summary_sha256']==summary_sha
    record={'run_id':args.run_id,'utc_start':started,'utc_finish':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':sys.version,'python_executable':sys.executable,'evaluator_entry_point_sha256':EXPECTED,
        'wrapper_sha256':wrapper_sha,'same_process':True,'summary_sha256':summary_sha,**after}
    (destination/'evaluator_runtime.json').write_text(json.dumps(record,indent=2)+'\n')
    m['evaluator_runtime']=record
    temporary=manifest.with_suffix('.json.runtime.tmp')
    try:
        temporary.write_text(json.dumps(m,indent=2)+'\n')
        assert json.loads(temporary.read_bytes())==m
        os.replace(temporary,manifest)
    finally:
        temporary.unlink(missing_ok=True)
    assert sha(destination/'summary.json')==summary_sha

if __name__=='__main__':
    main()
