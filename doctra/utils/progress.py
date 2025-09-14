from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, Iterable, Iterator, Tuple
from tqdm import tqdm
from tqdm.auto import tqdm as tqdm_auto


class ProgressConfig:
    """
    Central configuration for progress behavior, overridable via environment.

    Env vars:
    - DOCTRA_PROGRESS_DISABLE: "1" to disable progress entirely
    - DOCTRA_PROGRESS_ASCII: "1" to force ASCII bars
    - DOCTRA_PROGRESS_EMOJI: "0" to disable emoji prefixing
    - DOCTRA_PROGRESS_NCOLS: integer width for bars
    - DOCTRA_PROGRESS_EMOJI_MODE: one of {default, safe, ascii, none}
    """

    def __init__(self) -> None:
        self.disable: bool = os.getenv("DOCTRA_PROGRESS_DISABLE", "0") == "1"
        self.force_ascii: bool = os.getenv("DOCTRA_PROGRESS_ASCII", "0") == "1"
        self.use_emoji: bool = os.getenv("DOCTRA_PROGRESS_EMOJI", "1") == "1"
        self.ncols_env: Optional[int] = None
        self.emoji_mode: str = os.getenv("DOCTRA_PROGRESS_EMOJI_MODE", "default").lower()
        try:
            ncols_val = os.getenv("DOCTRA_PROGRESS_NCOLS")
            self.ncols_env = int(ncols_val) if ncols_val else None
        except Exception:
            self.ncols_env = None


_PROGRESS_CONFIG = ProgressConfig()


def _detect_environment() -> Tuple[bool, bool, bool]:
    """
    Returns (is_notebook, is_tty, is_windows).
    """
    is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
    if "google.colab" in sys.modules:
        is_notebook = True
    if "kaggle_secrets" in sys.modules or "kaggle_web_client" in sys.modules:
        is_notebook = True
    is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    is_windows = sys.platform.startswith("win")
    return is_notebook, is_tty, is_windows


def _select_emoji(key: str) -> str:
    """
    Choose an emoji/symbol for a given key according to env and config.
    Modes:
      - default: rich emoji
      - safe: single-codepoint symbols with stable width
      - ascii: ASCII text tokens
      - none: empty prefix
    """
    default_map = {
        "loading": "🔄",
        "charts": "📊",
        "tables": "📋",
        "figures": "🖼️",
        "ocr": "🔍",
        "vlm": "🤖",
        "processing": "⚙️",
    }
    safe_map = {
        "loading": "⏳",
        "charts": "▦",
        "tables": "▤",
        "figures": "▧",
        "ocr": "🔎",
        "vlm": "★",
        "processing": "⚙",
    }
    ascii_map = {
        "loading": "[loading]",
        "charts": "[charts]",
        "tables": "[tables]",
        "figures": "[figures]",
        "ocr": "[ocr]",
        "vlm": "[vlm]",
        "processing": "[processing]",
    }

    mode = _PROGRESS_CONFIG.emoji_mode
    is_notebook, _, is_windows = _detect_environment()
    if not _PROGRESS_CONFIG.use_emoji:
        mode = "none"
    elif mode == "default":
        if is_windows or "google.colab" in sys.modules or "kaggle_secrets" in sys.modules:
            mode = "safe"

    if mode == "none":
        return ""
    if mode == "ascii":
        return ascii_map.get(key, "")
    if mode == "safe":
        return safe_map.get(key, safe_map["processing"])
    return default_map.get(key, default_map["processing"])


def _supports_unicode_output() -> bool:
    """Best-effort detection whether stdout likely supports Unicode/emoji."""
    try:
        enc = getattr(sys.stdout, "encoding", None) or ""
        enc_lower = enc.lower()
        if "utf" in enc_lower:
            return True
    except Exception:
        pass

    env = os.environ
    if any(k in env for k in ("COLAB_GPU", "GCE_METADATA_HOST", "KAGGLE_KERNEL_RUN_TYPE", "JPY_PARENT_PID")):
        return True

    if sys.platform.startswith("win"):
        if _PROGRESS_CONFIG.force_ascii:
            return False
        if any(k in env for k in ("WT_SESSION", "TERM_PROGRAM", "VSCODE_PID")):
            return True

    return False


def create_beautiful_progress_bar(
    total: int,
    desc: str,
    leave: bool = True,
    position: Optional[int] = None,
    **kwargs
) -> tqdm:
    """
    Create a beautiful and interactive tqdm progress bar with enhanced styling.
    
    Features:
    - Colorful progress bars with gradients
    - Emoji icons for different operations
    - Better formatting and spacing
    - Interactive features
    - Responsive design
    
    :param total: Total number of items to process
    :param desc: Description text for the progress bar
    :param leave: Whether to leave the progress bar after completion
    :param position: Position of the progress bar (for multiple bars)
    :param kwargs: Additional tqdm parameters
    :return: Configured tqdm progress bar instance
    """
    
    is_notebook, is_tty, is_windows = _detect_environment()
    if is_notebook:
        bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    else:
        bar_format = (
            "{l_bar}{bar:30}| {n_fmt}/{total_fmt} "
            "[{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        )
    
    color_schemes = {
        "loading": {"colour": "cyan", "ncols": 100},
        "charts": {"colour": "green", "ncols": 100},
        "tables": {"colour": "blue", "ncols": 100},
        "figures": {"colour": "magenta", "ncols": 100},
        "ocr": {"colour": "yellow", "ncols": 100},
        "vlm": {"colour": "red", "ncols": 100},
        "processing": {"colour": "white", "ncols": 100},
    }
    
    desc_lower = desc.lower()
    if "loading" in desc_lower or "model" in desc_lower:
        color_scheme = color_schemes["loading"]
    elif "chart" in desc_lower:
        color_scheme = color_schemes["charts"]
    elif "table" in desc_lower:
        color_scheme = color_schemes["tables"]
    elif "figure" in desc_lower:
        color_scheme = color_schemes["figures"]
    elif "ocr" in desc_lower:
        color_scheme = color_schemes["ocr"]
    elif "vlm" in desc_lower:
        color_scheme = color_schemes["vlm"]
    else:
        color_scheme = color_schemes["processing"]
    
    emoji_categories = {"loading", "charts", "tables", "figures", "ocr", "vlm", "processing"}
    
    if _PROGRESS_CONFIG.use_emoji:
        prefix_key = next((k for k in emoji_categories if k in desc_lower), "processing")
        prefix = _select_emoji(prefix_key)
        if prefix:
            desc = f"{prefix} {desc}"
    
    tqdm_config = {
        "total": total,
        "desc": desc,
        "leave": leave,
        "bar_format": bar_format,
        "ncols": _PROGRESS_CONFIG.ncols_env or color_scheme["ncols"],
        "ascii": _PROGRESS_CONFIG.force_ascii or not _supports_unicode_output(),
        "dynamic_ncols": True,
        "smoothing": 0.3,
        "mininterval": 0.1,
        "maxinterval": 1.0,
        "position": position,
        **kwargs
    }
    
    is_notebook, is_terminal, is_windows = _detect_environment()
    
    if not is_notebook and is_terminal:
        tqdm_config["colour"] = color_scheme["colour"]
    
    if _PROGRESS_CONFIG.disable:
        tqdm_config["disable"] = True

    if is_notebook:
        tqdm_config.pop("colour", None)
        try:
            return tqdm_auto(**tqdm_config)
        except Exception:
            tqdm_config["ascii"] = True
            return tqdm_auto(**tqdm_config)
    else:
        try:
            return tqdm(**tqdm_config)
        except Exception:
            tqdm_config["ascii"] = True
            return tqdm(**tqdm_config)


def create_multi_progress_bars(
    descriptions: list[str],
    totals: list[int],
    positions: Optional[list[int]] = None
) -> list[tqdm]:
    """
    Create multiple beautiful progress bars for concurrent operations.
    
    :param descriptions: List of descriptions for each progress bar
    :param totals: List of totals for each progress bar
    :param positions: Optional list of positions for each bar
    :return: List of configured tqdm progress bar instances
    """
    if positions is None:
        positions = list(range(len(descriptions)))
    
    bars = []
    for desc, total, pos in zip(descriptions, totals, positions):
        bar = create_beautiful_progress_bar(
            total=total,
            desc=desc,
            position=pos,
            leave=True
        )
        bars.append(bar)
    
    return bars


def update_progress_with_info(
    bar: tqdm,
    increment: int = 1,
    info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Update progress bar with additional information.
    
    :param bar: tqdm progress bar instance
    :param increment: Number to increment the progress
    :param info: Optional dictionary of information to display
    """
    if info:
        postfix_parts = []
        for key, value in info.items():
            if isinstance(value, float):
                postfix_parts.append(f"{key}: {value:.2f}")
            else:
                postfix_parts.append(f"{key}: {value}")
        
        bar.set_postfix_str(", ".join(postfix_parts))
    
    bar.update(increment)


def create_loading_bar(desc: str = "Loading", **kwargs) -> tqdm:
    """
    Create a special loading progress bar for model initialization.
    
    :param desc: Description for the loading operation
    :param kwargs: Additional tqdm parameters
    :return: Configured loading progress bar
    """
    return create_beautiful_progress_bar(
        total=1,
        desc=desc,
        leave=True,
        **kwargs
    )


def create_processing_bar(
    total: int,
    operation: str,
    **kwargs
) -> tqdm:
    """
    Create a processing progress bar for data operations.
    
    :param total: Total number of items to process
    :param operation: Type of operation (charts, tables, figures, etc.)
    :param kwargs: Additional tqdm parameters
    :return: Configured processing progress bar
    """
    desc = f"{operation.title()} (processing)"
    return create_beautiful_progress_bar(
        total=total,
        desc=desc,
        leave=True,
        **kwargs
    )


def create_notebook_friendly_bar(
    total: int,
    desc: str,
    **kwargs
) -> tqdm:
    """
    Create a notebook-friendly progress bar with consistent sizing.
    
    This function creates progress bars that match the main progress bar
    styling and behavior in notebook environments.
    
    :param total: Total number of items to process
    :param desc: Description text for the progress bar
    :param kwargs: Additional tqdm parameters
    :return: Configured notebook-friendly progress bar
    """
    return create_beautiful_progress_bar(
        total=total,
        desc=desc,
        leave=True,
        **kwargs
    )


def progress_for(iterable: Iterable[Any], desc: str, total: Optional[int] = None, leave: bool = True, **kwargs) -> Iterator[Any]:
    """
    Wrap an iterable with a configured progress bar.
    Respects env config and auto-detects notebook vs terminal.
    """
    if _PROGRESS_CONFIG.disable:
        for item in iterable:
            yield item
        return

    is_notebook, _, _ = _detect_environment()
    bar_factory = create_notebook_friendly_bar if is_notebook else create_beautiful_progress_bar
    with bar_factory(total=total if total is not None else 0, desc=desc, leave=leave, **kwargs) as bar:
        if total is None:
            # Unknown total: manual increments
            for item in iterable:
                yield item
                bar.update(1)
        else:
            for item in iterable:
                yield item
                bar.update(1)
