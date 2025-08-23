from __future__ import annotations
from typing import List, Optional

def _esc(cell: object) -> str:
    s = "" if cell is None else str(cell)
    # Escape pipes and collapse newlines for MD
    return s.replace("|", r"\|").replace("\n", " ").strip()

def render_markdown_table(
    headers: List[str] | None,
    rows: List[List[str]] | None,
    title: Optional[str] = None,
) -> str:
    headers = headers or []
    rows = rows or []

    lines: List[str] = []
    if title:
        lines.append(f"**{title}**")
    # determine width
    width = len(headers) if headers else (max((len(r) for r in rows), default=1))

    # header row
    if not headers:
        headers = [f"col{i+1}" for i in range(width)]
    lines.append("| " + " | ".join(_esc(h) for h in headers[:width]) + " |")
    lines.append("| " + " | ".join(["---"] * width) + " |")

    # data rows (pad/truncate to width)
    for r in rows:
        row = (r + [""] * width)[:width]
        lines.append("| " + " | ".join(_esc(c) for c in row) + " |")

    lines.append("")  # blank line after table block
    return "\n".join(lines)