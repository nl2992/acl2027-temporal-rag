"""Audit placement arguments in pinned author source without importing model libraries."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SHA='8731487254e0988eaf2ca4ae3e93ff587fec64d0'
raw=subprocess.check_output(['git','-C',str(ROOT/'vendor/Tempo'),'show',f'{SHA}:retrievers.py'])
tree=ast.parse(raw)
selected={'retrieval_sf_qwen_e5','retrieval_rader','retrieval_reasonir','retrieval_grit'}
records={}
for fn in tree.body:
    if not isinstance(fn,ast.FunctionDef) or fn.name not in selected:
        continue
    calls=[]
    for node in ast.walk(fn):
        if not isinstance(node,ast.Call):
            continue
        if isinstance(node.func,ast.Attribute) and node.func.attr=='from_pretrained':
            maps={k.arg:ast.unparse(k.value) for k in node.keywords if k.arg in
                  {'device_map','torch_dtype','trust_remote_code'}}
            if maps:
                calls.append({'line':node.lineno,'constructor':ast.unparse(node.func),
                    'checkpoint_expression':ast.unparse(node.args[0]) if node.args else None,'arguments':maps})
        if isinstance(node.func,ast.Attribute) and node.func.attr=='to' and ast.unparse(node.func.value)=='model':
            calls.append({'line':node.lineno,'explicit_model_move':ast.unparse(node)})
        if isinstance(node.func,ast.Name) and node.func.id=='GritLM':
            calls.append({'line':node.lineno,'constructor':ast.unparse(node)})
    records[fn.name]={'start_line':fn.lineno,'calls':calls}
assert set(records)==selected
report={'source_sha':SHA,'retrievers_blob_sha256':hashlib.sha256(raw).hexdigest(),
    'method':'AST inspection only; no imports, model construction, placement or inference executed.',
    'functions':records,
    'classification':{'e5/sf/qwen/rader':'Native automatic placement; measured local feasibility pending.',
        'reasonir':'Explicit model move to source-selected device; CUDA selected on current GPU host.',
        'grit':'Author constructor has no device_map override; inspect installed GritLM default device move.',
        'diver':'Separate vLLM source path and VRAM preflight; automatic Transformers placement does not apply.'}}
(ROOT/'manifests/tempo_placement_source_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Recorded source-only placement policies; no feasibility or completed-run claim.')
