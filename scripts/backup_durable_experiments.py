"""Snapshot allowed experiment records to a separate Git branch, without touching the working index."""
import datetime
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BRANCH = 'codex/experiment-backup'
REF = 'refs/heads/' + BRANCH
FILES = {'launch.json', 'source_changes.patch', 'prepare.log', 'inference.log',
         'evaluation.log', 'manifest.json', 'summary.json', 'evaluator_runtime.json'}

def git(*args, env=None, check=True):
    return subprocess.run(['git', *args], cwd=ROOT, env=env, check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def main():
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    # A remote advance that is not in our local history must never be overwritten.
    remote = git('ls-remote', '--heads', 'origin', REF, env=env).stdout.strip().split()
    local = git('rev-parse', '--verify', REF, env=env, check=False)
    if local.returncode:
        if remote:
            raise RuntimeError('Backup branch exists remotely but not locally; review before continuing')
        parent = git('rev-parse', 'HEAD', env=env).stdout.strip()
    else:
        parent = local.stdout.strip()
        if remote and remote[0] != parent:
            # A prior push may have failed; retry only if it remains fast-forward.
            if git('merge-base', '--is-ancestor', remote[0], parent, env=env, check=False).returncode:
                raise RuntimeError('Backup branch diverged from remote; review before continuing')
    paths = []
    for p in (ROOT / 'reports' / 'tempo').glob('tempo-*-inst-l-durable-*'):
        if p.is_dir():
            paths.extend(str(x.relative_to(ROOT)) for x in p.iterdir() if x.is_file() and x.name in FILES)
    for domain in ('hsm', 'history'):
        for p in (ROOT / 'reports' / 'tempo').glob(f'tempo-{domain}-bge-*'):
            if p.is_dir():
                paths.extend(str(x.relative_to(ROOT)) for x in p.iterdir() if x.is_file() and x.name in FILES)
    paths.extend(str(p.relative_to(ROOT)) for p in (ROOT / 'reports').glob('tempo-*-inst-l-durable-*-supervisor.log'))
    for name in ('durable_instructor_queue.log', 'bge_handoff_status.txt', 'bge_handoff.log', 'tempo_retriever_coverage.json', 'tempo_retriever_coverage.md'):
        p = ROOT / 'reports' / name
        if p.is_file():
            paths.append(str(p.relative_to(ROOT)))
    if not paths:
        raise RuntimeError('No eligible experiment records found')
    with tempfile.TemporaryDirectory(prefix='acl2027-backup-') as temp:
        env['GIT_INDEX_FILE'] = str(Path(temp) / 'index')
        git('read-tree', parent, env=env)
        git('add', '--', *paths, env=env)
        tree = git('write-tree', env=env).stdout.strip()
        parent_tree = git('rev-parse', parent + '^{tree}', env=env).stdout.strip()
        if tree != parent_tree:
            stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            commit = git('commit-tree', tree, '-p', parent, '-m', 'Experiment records snapshot ' + stamp, env=env).stdout.strip()
            git('update-ref', REF, commit, parent if local.returncode == 0 else '0' * 40, env=env)
        git('push', 'origin', REF + ':' + REF, env=env)
    print('Saved eligible records to ' + BRANCH)

if __name__ == '__main__':
    log = ROOT / 'cache' / 'durable-backup-status.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        main()
    except Exception as exc:
        with log.open('a', encoding='utf-8') as output:
            output.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} FAILED {type(exc).__name__}: {exc}\n')
        raise
    else:
        with log.open('a', encoding='utf-8') as output:
            output.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} OK\n')
