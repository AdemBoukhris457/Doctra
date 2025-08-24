from __future__ import annotations

import os
import platform
import shutil
from typing import Optional

def resolve_tesseract_cmd(tesseract_cmd: Optional[str] = None) -> Optional[str]:
    """
    Best-effort discovery of the Tesseract executable.
    
    Searches for the Tesseract executable using a priority-based approach:
    1. Explicitly provided path
    2. TESSERACT_CMD environment variable
    3. System PATH
    4. Common installation paths for the current platform

    :param tesseract_cmd: Optional explicit path to tesseract executable
    :return: Resolved path to tesseract executable, or None if not found
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
