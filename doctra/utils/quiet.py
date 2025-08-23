from __future__ import annotations
import os
import contextlib

@contextlib.contextmanager
def suppress_output():
    """Temporarily silence stdout/stderr (tqdm + print + noisy libs)."""
    devnull = open(os.devnull, "w")
    try:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield
    finally:
        devnull.close()
