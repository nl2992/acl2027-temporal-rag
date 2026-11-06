"""Exercise the draft's cache receipt against synthetic valid and corrupt files."""
import ast
import hashlib
import json
import tempfile
from pathlib import Path
import numpy as np

source = Path('scripts/drafts/tempo_instructor_isolated.py').read_text(encoding='utf-8')
tree = ast.parse(source)
func = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'validate_instructor_cache')
env = {'json': json, 'sha': lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()}
exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])), '<draft-cache-check>', 'exec'), env)
validate = env['validate_instructor_cache']
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    target = root / 'doc_emb' / 'inst-l' / 'fixture' / 'long_False'
    target.mkdir(parents=True)
    (root / 'descriptor.json').write_text('{}')
    mapping = target / 'doc_id_mapping.json'
    vectors = target / 'embeddings.npy'
    docs = [{'id': 'a'}, {'id': 'b'}]
    def save(array, index):
        np.save(vectors, array)
        mapping.write_text(json.dumps(index))
    valid = np.array([[1, 0], [0, 1]], dtype=np.float32)
    save(valid, {'a': 0, 'b': 1})
    receipt = validate(root, 'fixture', docs)
    assert receipt['shape'] == [2, 2] and receipt['dtype'] == 'float32'
    for array, index in [(valid.astype(np.float16), {'a': 0, 'b': 1}),
                         (np.array([[float('nan'), 0], [0, 1]], dtype=np.float32), {'a': 0, 'b': 1}),
                         (valid, {'a': 1, 'b': 0}), (valid[:1], {'a': 0, 'b': 1})]:
        save(array, index)
        try:
            validate(root, 'fixture', docs)
        except AssertionError:
            pass
        else:
            raise AssertionError('Malformed synthetic cache was accepted')
print('PASS: valid receipt and four malformed cache cases; no model loaded')
