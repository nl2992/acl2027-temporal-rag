"""Start the reviewed BGE suite once the INSTRUCTOR queue completes cleanly."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
QUEUE_LOG = ROOT / 'reports/durable_instructor_queue.log'
RECORD = ROOT / 'reports/bge_handoff_status.txt'
OUTPUT = ROOT / 'reports/bge_handoff.log'

def main():
    if RECORD.exists():
        return  # Manual review is required after any prior launch, including interruption.
    if not QUEUE_LOG.exists() or not QUEUE_LOG.read_text(encoding='utf-8').rstrip().endswith('QUEUE COMPLETE; other baselines and temporal judge remain pending'):
        return
    # The reviewed BGE runner checks the GPU and its own provenance gates before launch.
    with RECORD.open('x', encoding='utf-8') as status:
        status.write('STARTED; no automatic retry after interruption or failure\n')
    with OUTPUT.open('ab') as output:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/run_tempo_bge_suite.py')],
                                cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        with RECORD.open('a', encoding='utf-8') as status:
            status.write(f'FAILED exit={result.returncode}\n')
        raise SystemExit(result.returncode)
    subprocess.run([sys.executable, str(ROOT / 'scripts/report_tempo_retrievers.py')], cwd=ROOT, check=True)
    with RECORD.open('a', encoding='utf-8') as status:
        status.write('COMPLETED after BGE suite verification\n')

if __name__ == '__main__':
    main()
