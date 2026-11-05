"""CPU-only synthetic preflight. Never invokes WSL, a benchmark, or an encoder."""
import argparse
import base64
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[2]
WRAPPER = 'tempo_evaluate_with_provenance.py'
RUNNER = 'run_tempo_wsl.py'
REPORTERS = ['report_tempo_retrievers.py', 'report_tempo_parity.py']
WORKER = 'tempo_isolated.py'
LAUNCHER = 'isolated_tempo_worker.sh'
FIXTURE_ID = 'synthetic-only'
SUMMARY = b'{"NDCG@10": 0.125, "fixture_only": true}\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def synthetic_providers(folder):
    providers = {
        'pytrec_eval.py': 'from pytrec_eval_ext import Base\nclass RelevanceEvaluator(Base): pass\n',
        'pytrec_eval_ext.py': 'class Base: pass\n',
    }
    for name, source in providers.items():
        (folder / name).write_bytes(source.encode())
    for name, version, matched in [('pytrec_eval', '0.5', False), ('pytrec_eval_terrier', '0.5.11', True)]:
        info = folder / f'{name}-{version}.dist-info'
        info.mkdir()
        (info / 'METADATA').write_text(f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n')
        entries = []
        for filename in providers:
            content = (folder / filename).read_bytes() if matched else b'synthetic shadowed module'
            encoded = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().rstrip('=')
            entries.append(f'{filename},sha256={encoded},{len(content)}\n')
        (info / 'RECORD').write_text(''.join(entries))


EVALUATOR = '''from pathlib import Path
import hashlib, json, sys
assert sys.argv[1:3] == ["evaluate", "--run-id"] and len(sys.argv) == 4
root = Path(__file__).parent
mode = (root / "mode").read_text()
run = sys.argv[3]
folder = root / "results" / run
folder.mkdir(exist_ok=False)
payload = {summary!r}
(folder / "summary.json").write_bytes(payload)
manifest = dict(run_id="other" if mode == "wrong-run" else run,
                summary_sha256="bad" if mode == "wrong-summary" else hashlib.sha256(payload).hexdigest())
(folder / "manifest.json").write_text(json.dumps(manifest))
if mode == "mutate-entry": Path(__file__).write_bytes(b"# synthetic change")
if mode == "mutate-wrapper": (root / "{wrapper}").write_bytes(b"# synthetic change")
if mode == "mutate-import": (root / "pytrec_eval_ext.py").write_bytes(b"# synthetic change")
'''


def check_wrapper(root, source):
    shutil.copyfile(source / WRAPPER, root / WRAPPER)
    spec = importlib.util.spec_from_file_location('provenance_fixture', root / WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    module.SCRIPT = root / 'synthetic_evaluator.py'
    entry = EVALUATOR.format(summary=SUMMARY, wrapper=WRAPPER).encode()
    module.SCRIPT.write_bytes(entry)
    module.EXPECTED = digest(entry)
    synthetic_providers(root)
    original_wrapper = (root / WRAPPER).read_bytes()
    original_import = (root / 'pytrec_eval_ext.py').read_bytes()
    with patch.object(sys, 'path', [str(root), *sys.path]):
        with patch.object(sys, 'argv', [WRAPPER, '--describe-only']), redirect_stdout(io.StringIO()) as out:
            module.main()
        assert not (root / 'results').exists()
        witness = json.loads(out.getvalue())
        assert set(witness['module_files']) == {'pytrec_eval', 'pytrec_eval_ext'}
        distributions = witness['installed_distribution_metadata']
        for provider, expected in [('pytrec-eval', False), ('pytrec-eval-terrier', True)]:
            records = distributions[provider]['record_entries']
            assert len(records) == 2 and all(r['matches_imported_bytes'] is expected for r in records)
        assert witness['evaluator_class_mro'][:2] == ['pytrec_eval.RelevanceEvaluator', 'pytrec_eval_ext.Base']
        (root / 'results').mkdir()
        for mode in ['normal', 'wrong-run', 'wrong-summary', 'mutate-entry', 'mutate-wrapper', 'mutate-import']:
            (root / 'mode').write_text(mode)
            module.SCRIPT.write_bytes(entry)
            (root / WRAPPER).write_bytes(original_wrapper)
            (root / 'pytrec_eval_ext.py').write_bytes(original_import)
            with patch.object(sys, 'argv', [WRAPPER, '--run-id', mode]):
                try:
                    module.main()
                except AssertionError:
                    assert mode != 'normal'
                else:
                    assert mode == 'normal'
            folder = root / 'results' / mode
            assert (folder / 'summary.json').read_bytes() == SUMMARY
            assert (folder / 'evaluator_runtime.json').exists() == (mode == 'normal')
        folder = root / 'results' / 'normal'
        manifest = json.loads((folder / 'manifest.json').read_bytes())
        runtime = json.loads((folder / 'evaluator_runtime.json').read_bytes())
        assert manifest['evaluator_runtime'] == runtime and runtime['same_process'] is True
        assert runtime['module_files'] == witness['module_files'] and runtime['summary_sha256'] == digest(SUMMARY)
        assert runtime['wrapper_sha256'] == digest(original_wrapper) and runtime['evaluator_entry_point_sha256'] == digest(entry)
        before = {p.name: p.read_bytes() for p in folder.iterdir()}
        (root / 'pytrec_eval_ext.py').write_bytes(original_import)
        (root / 'mode').write_text('normal')
        with patch.object(sys, 'argv', [WRAPPER, '--run-id', 'normal']):
            try:
                module.main()
            except FileExistsError:
                pass
            else:
                raise AssertionError('Duplicate fixture run was not rejected')
        assert before == {p.name: p.read_bytes() for p in folder.iterdir()}
    print('wrapper: describe-only, synthetic matching and overwritten RECORDs, exact CLI, intact bytes,'
          ' duplicate refusal and five injected failures passed')


def check_runner(root, source, mode):
    scripts = root / 'scripts'
    scripts.mkdir(parents=True)
    for name in [WRAPPER, RUNNER, *REPORTERS]:
        shutil.copyfile(source / name, scripts / name)
    for name in [WORKER, LAUNCHER]:
        shutil.copyfile(PROJECT / 'scripts' / name, scripts / name)
    (root / 'configs').mkdir()
    for name in ['published_tempo_bm25.json', 'published_tempo_retrievers.json']:
        shutil.copyfile(PROJECT / 'configs' / name, root / 'configs' / name)
    runtime = {'run_id': FIXTURE_ID, 'wrapper_sha256': digest((scripts / WRAPPER).read_bytes()),
               'evaluator_entry_point_sha256': digest((scripts / WORKER).read_bytes()),
               'same_process': True, 'summary_sha256': digest(SUMMARY)}
    if mode == 'wrong-wrapper':
        runtime['wrapper_sha256'] = 'wrong'
    if mode == 'wrong-entry':
        runtime['evaluator_entry_point_sha256'] = 'wrong'
    if mode == 'separate-process':
        runtime['same_process'] = False
    if mode == 'wrong-run':
        runtime['run_id'] = 'wrong'
    manifest = dict(status='complete', run_id=FIXTURE_ID, summary_sha256=digest(SUMMARY),
                    evaluator_runtime=runtime.copy(), model='bm25', domain='law', queries=1, documents=1,
                    original_queries=1, original_documents=1, worker={'model': 'bm25', 'status': 'complete'})
    exports = {'manifest.json': json.dumps(manifest).encode(), 'summary.json': SUMMARY,
               'evaluator_runtime.json': json.dumps(runtime).encode()}
    if mode == 'bad-summary':
        exports['summary.json'] = b'{"fixture_only":false}\n'
    if mode == 'bad-witness':
        exports['evaluator_runtime.json'] = json.dumps(dict(runtime, extra='synthetic change')).encode()
    stages = []

    def read(cmd, **kwargs):
        if cmd[0] == 'git':
            return 'fixture' if kwargs.get('text') else b''
        assert cmd[0:6] == ['wsl', '-d', 'Ubuntu-24.04', '-u', 'nigel', '--']
        assert cmd[-2] == 'cat'
        name = cmd[-1].split('/')[-1]
        if name == 'evaluator_runtime.json' and mode == 'missing-export':
            raise subprocess.CalledProcessError(1, cmd)
        if name == WRAPPER and (mode, len(stages)) in {('change-before', 2), ('change-after', 3), ('undeployed', 0)}:
            return b'# different synthetic deployment'
        return exports[name] if name in exports else (scripts / name).read_bytes()

    def stage(cmd, **kwargs):
        assert kwargs['check'] is True
        expected = ['stage_tempo_data.py', 'isolated_tempo_worker.sh', WRAPPER][len(stages)]
        assert any(arg.endswith('/' + expected) for arg in cmd)
        assert cmd[cmd.index('--run-id') + 1] == FIXTURE_ID
        assert cmd[4] == ('root' if len(stages) == 1 else 'nigel')
        stages.append(expected)
        return subprocess.CompletedProcess(cmd, 0)

    with patch.object(sys, 'argv', [str(scripts / RUNNER), '--domain', 'law', '--run-id', FIXTURE_ID]), \
         patch.object(subprocess, 'check_output', read), patch.object(subprocess, 'run', stage), redirect_stdout(io.StringIO()):
        try:
            runpy.run_path(str(scripts / RUNNER), run_name='__main__')
        except (AssertionError, subprocess.CalledProcessError):
            assert mode != 'normal'
        else:
            assert mode == 'normal'
    folder = root / 'reports/tempo' / FIXTURE_ID
    launch = json.loads((folder / 'launch.json').read_bytes())
    assert launch['status'] == ('complete' if mode == 'normal' else 'failed')
    assert len(stages) == {'undeployed': 0, 'change-before': 2}.get(mode, 3)
    if mode == 'normal':
        assert all((folder / name).read_bytes() == raw for name, raw in exports.items())
    elif mode in {'missing-export', 'bad-witness'}:
        exposed = (folder / 'manifest.json').exists()
        # Emulate the leftover final files of the old exporter too. A failed launch
        # must stay out of both reports even if its other files look complete.
        for name in ('summary.json', 'manifest.json'):
            (folder / name).write_bytes(exports[name])
        with redirect_stdout(io.StringIO()):
            for name in REPORTERS:
                runpy.run_path(str(scripts / name), run_name='__main__')
        parity = json.loads((root / 'reports/tempo_parity.json').read_bytes())
        coverage = json.loads((root / 'reports/tempo_retriever_coverage.json').read_bytes())
        counts = [parity['completed_domains'], coverage['models']['BM25']['completed_domains']]
        print(f'runner {mode}: failed launch; manifest exposed={exposed}; stale-export report counts {counts}')
        return counts
    print(f'runner {mode}: {launch["status"]}; {len(stages)} synthetic stages')
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=PROJECT / 'scripts')
    args = parser.parse_args()
    assert sys.flags.optimize == 0
    with tempfile.TemporaryDirectory(prefix='acl2027-synthetic-evaluator-') as temporary:
        base = Path(temporary)
        check_wrapper(base, args.source)
        report_counts = []
        for scenario in ['normal', 'undeployed', 'change-before', 'change-after', 'bad-summary', 'wrong-wrapper',
                         'wrong-entry', 'separate-process', 'wrong-run', 'bad-witness', 'missing-export']:
            report_counts += check_runner(base / scenario, args.source, scenario)
        if any(report_counts):
            raise SystemExit('HOLD: a reporter admitted a synthetic failed launch')
        print('PASS: failed synthetic exports contribute zero reported cells')
