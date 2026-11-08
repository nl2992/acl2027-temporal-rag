"""Sequential local continuation; stop on any unresolved attempt or error."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ('bitcoin', 'genealogy', 'politics', 'hsm', 'history')
LOG = ROOT / 'reports' / 'durable_instructor_queue.log'

def note(message):
    with LOG.open('a', encoding='utf-8') as f:
        f.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} {message}\n')

def main():
    for domain in DOMAINS:
        attempts = list((ROOT / 'reports' / 'tempo').glob(f'tempo-{domain}-inst-l-durable-*'))
        # This specific failed admission created no staged input or inference.
        attempts = [p for p in attempts if not (p.name == 'tempo-bitcoin-inst-l-durable-20261108T203712Z'
                    and set(x.name for x in p.iterdir()) == {'launch.json', 'source_changes.patch'}
                    and json.loads((p / 'launch.json').read_text(encoding='utf-8')).get('status') == 'failed')]
        # The scheduler and WSL worker were verified stopped after this interrupted run.
        attempts = [p for p in attempts if not (p.name == 'tempo-bitcoin-inst-l-durable-20261108T203801Z'
                    and hashlib.sha256((p / 'launch.json').read_bytes()).hexdigest() == 'c56ef1df57a72570dc118d00288d82f300524eb5aec14689f2f8a72c1c7f017f'
                    and not (p / 'manifest.json').exists())]
        if attempts:
            if len(attempts) != 1:
                raise RuntimeError(f'{domain}: ambiguous attempts')
            attempt = attempts[0]
            launch = json.loads((attempt / 'launch.json').read_text(encoding='utf-8'))
            manifest = json.loads((attempt / 'manifest.json').read_text(encoding='utf-8'))
            if launch['status'] != 'complete' or manifest['status'] != 'complete' or manifest['run_id'] != attempt.name:
                raise RuntimeError(f'{domain}: incomplete attempt requires review')
            continue
        # Restore only the existing, project-created swap files; fail closed if missing.
        for swap in ('/swap-research', '/swap-research-extra'):
            command = ['wsl', '-d', 'Ubuntu-24.04', '-u', 'root', '--']
            active = subprocess.check_output(command + ['swapon', '--noheadings', '--raw', '--show=NAME'], text=True).split()
            if swap not in active:
                subprocess.run(command + ['swapon', swap], check=True)
        run = f'tempo-{domain}-inst-l-durable-{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%SZ}'
        note(f'START {run}')
        with (ROOT / 'reports' / f'{run}-supervisor.log').open('ab') as output:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/drafts/run_tempo_instructor_enabled.py'),
                                     '--domain', domain, '--run-id', run], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f'{run}: runner exited {result.returncode}')
        subprocess.run([sys.executable, str(ROOT / 'scripts/report_tempo_retrievers.py')], cwd=ROOT, check=True)
        note(f'COMPLETE {run}')
    note('QUEUE COMPLETE; other baselines and temporal judge remain pending')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        note(f'STOP {type(exc).__name__}: {exc}')
        raise
