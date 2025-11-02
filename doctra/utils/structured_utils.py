from __future__ import annotations
from typing import Any, Dict, Optional, List
import json

try:
    from pydantic import BaseModel  # type: ignore
except Exception:
    class BaseModel:
        pass

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

def to_structured_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """
    Accepts a VLM result that might be:
      - JSON string
      - dict
      - Pydantic BaseModel (v1 .dict() or v2 .model_dump())
    Returns a normalized dict with keys: title, description, headers, rows, page, type — or None.
    """
    if obj is None:
        return None

    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except Exception:
            return None

    if isinstance(obj, BaseModel):
        try:
            return obj.model_dump()
        except Exception:
            try:
                return obj.dict()
            except Exception:
                return None

    if isinstance(obj, dict):
        title = obj.get("title") or "Untitled"
        description = obj.get("description") or ""
        headers = obj.get("headers") or []
        rows = obj.get("rows") or []
        page = obj.get("page", "Unknown")
        item_type = obj.get("type", "Table")
        if not isinstance(headers, list) or not isinstance(rows, list):
            return None
        return {"title": title, "description": description, "headers": headers, "rows": rows, "page": page, "type": item_type}

    return None


def html_table_to_structured_dict(html_content: str, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convert an HTML table string to structured dict format.
    
    Args:
        html_content: HTML string containing a table
        title: Optional title for the table
        
    Returns:
        Dictionary with keys: title, description, headers, rows, page, type — or None if parsing fails
    """
    if not BS4_AVAILABLE:
        return None
        
    if not html_content:
        return None
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return None
        
        headers: List[str] = []
        rows: List[List[str]] = []
        
        # Check for thead (header section)
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Check for tbody (body section)
        tbody = table.find('tbody')
        table_rows = tbody.find_all('tr') if tbody else table.find_all('tr')
        
        # If no thead was found, use first row as headers
        if not headers and table_rows:
            first_row = table_rows[0]
            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            table_rows = table_rows[1:]  # Skip first row if used as headers
        
        # Extract data rows
        for row in table_rows:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if cells:  # Only add non-empty rows
                rows.append(cells)
        
        # Ensure headers match column count of rows
        if rows:
            max_cols = max(len(row) for row in rows) if rows else 0
            if not headers:
                headers = [f"Column {i+1}" for i in range(max_cols)]
            elif len(headers) < max_cols:
                # Extend headers if rows have more columns
                headers.extend([f"Column {i+1}" for i in range(len(headers), max_cols)])
        
        if not rows:
            return None
        
        return {
            "title": title or "Untitled Table",
            "description": "",
            "headers": headers,
            "rows": rows,
            "page": "Unknown",
            "type": "Table"
        }
    except Exception:
        return None
