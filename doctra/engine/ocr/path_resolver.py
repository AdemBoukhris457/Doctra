from __future__ import annotations

import os
import platform
import shutil
from typing import Optional

def resolve_tesseract_cmd(tesseract_cmd: Optional[str] = None) -> Optional[str]:
    """
    Best-effort discovery of the Tesseract executable.
    Priority: explicit arg -> TESSERACT_CMD env -> PATH -> common install paths.
    Returns the resolved path or None if not found.
    """
    if tesseract_cmd and os.path.exists(tesseract_cmd):
        return tesseract_cmd

    env_cmd = os.getenv("TESSERACT_CMD")
    if env_cmd and os.path.exists(env_cmd):
        return env_cmd

    which = shutil.which("tesseract")
    if which:
        return which

    system = platform.system()
    candidates = []
    if system == "Windows":
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
    elif system == "Darwin":
        candidates = ["/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"]
    else:  # Linux/Unix
        candidates = ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]

    for c in candidates:
        if os.path.exists(c):
            return c

    return None
