"""Draft cooperative Windows GPU ownership for future research launchers.

Both callers must acquire the same path for the whole child-process lifetime.
This does not cover the already-running queue or any non-cooperating process.
"""
from contextlib import contextmanager
from pathlib import Path
import msvcrt


@contextmanager
def exclusive_owner(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        if handle.seek(0, 2) == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError('Another cooperating research launcher owns the GPU') from exc
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
