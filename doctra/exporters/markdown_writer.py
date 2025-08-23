from __future__ import annotations
import os
import re
from typing import List


def write_markdown(md_lines: List[str], out_dir: str, filename: str = "result.md") -> str:
    """
    Convert collected Markdown lines into a single Markdown file and save it.

    Args:
        md_lines: List of markdown strings to join.
        out_dir: Directory where the markdown file will be saved.
        filename: Name of the markdown file (default: "result.md").

    Returns:
        The absolute path of the written markdown file.
    """
    os.makedirs(out_dir, exist_ok=True)

    md = "\n".join(md_lines).strip() + "\n"
    # Collapse excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)

    md_path = os.path.join(out_dir, filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    return os.path.abspath(md_path)