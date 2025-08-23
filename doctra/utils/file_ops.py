from __future__ import annotations

import os
import re
from typing import Dict

def ensure_output_dirs(base_out: str, image_subdirs: Dict[str, str]) -> Dict[str, str]:
    """
    Create base output dir and image subfolders if missing.
    Returns a dict with base paths (for convenience).
    """
    img_base = os.path.join(base_out, "images")
    os.makedirs(img_base, exist_ok=True)
    paths = {}
    for lbl, sub in image_subdirs.items():
        p = os.path.join(img_base, sub)
        os.makedirs(p, exist_ok=True)
        paths[lbl] = p
    return {"base": base_out, "images": img_base, **paths}

def sanitize_filename(name: str) -> str:
    """
    Replace unsafe filename characters with underscores.
    """
    name = re.sub(r"[^\w\-.]+", "_", name)
    return name.strip("_")