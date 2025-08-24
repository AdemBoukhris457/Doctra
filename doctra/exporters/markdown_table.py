from __future__ import annotations
from typing import List, Optional

def _esc(cell: object) -> str:
    """
    Escape and clean a cell value for Markdown table formatting.
    
    Handles None values, escapes pipe characters, and collapses newlines
    to ensure proper Markdown table formatting.

    :param cell: Cell value to escape (can be any object)
    :return: Escaped string safe for Markdown table cells
    """
    s = "" if cell is None else str(cell)
    # Escape pipes and collapse newlines for MD
    return s.replace("|", r"\|").replace("\n", " ").strip()

def render_markdown_table(
    headers: List[str] | None,
    rows: List[List[str]] | None,
    title: Optional[str] = None,
) -> str:
    """
    Render a Markdown table from headers, rows, and optional title.
    
    Creates a properly formatted Markdown table with headers, separator row,
    and data rows. Handles missing headers by generating column names and
    ensures all rows have consistent width.

    :param headers: List of column headers (optional, will be auto-generated if None)
    :param rows: List of data rows, where each row is a list of cell values
    :param title: Optional title to display above the table
    :return: Formatted Markdown table string
    """
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