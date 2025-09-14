from __future__ import annotations
from typing import Any, Dict, Optional
import json

try:
    from pydantic import BaseModel  # type: ignore
except Exception:
    class BaseModel:
        pass

def to_structured_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """
    Accepts a VLM result that might be:
      - JSON string
      - dict
      - Pydantic BaseModel (v1 .dict() or v2 .model_dump())
    Returns a normalized dict with keys: title, headers, rows — or None.
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
        headers = obj.get("headers") or []
        rows = obj.get("rows") or []
        if not isinstance(headers, list) or not isinstance(rows, list):
            return None
        return {"title": title, "headers": headers, "rows": rows}

    return None
