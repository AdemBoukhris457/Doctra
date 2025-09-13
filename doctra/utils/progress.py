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
    # Colab/Kaggle specifics
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
    # Maps
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
        # Use BMP or geometric shapes likely to render everywhere
        "loading": "⏳",
        "charts": "▦",
        "tables": "▤",
        "figures": "▧",
        "ocr": "🔎",
        "vlm": "★",
        "processing": "⚙",  # no variation selector
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

    # Determine effective mode
    mode = _PROGRESS_CONFIG.emoji_mode
    is_notebook, _, is_windows = _detect_environment()
    if not _PROGRESS_CONFIG.use_emoji:
        mode = "none"
    elif mode == "default":
        # Heuristics: prefer safe in Colab/Kaggle notebooks and Windows terminals
        if is_windows or "google.colab" in sys.modules or "kaggle_secrets" in sys.modules:
            mode = "safe"

    if mode == "none":
        return ""
    if mode == "ascii":
        return ascii_map.get(key, "")
    if mode == "safe":
        return safe_map.get(key, safe_map["processing"])
    # default
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

    # Heuristics for common notebook environments that support emoji
    env = os.environ
    if any(k in env for k in ("COLAB_GPU", "GCE_METADATA_HOST", "KAGGLE_KERNEL_RUN_TYPE", "JPY_PARENT_PID")):
        return True

    # On modern Windows terminals with UTF-8 code page, assume yes
    if sys.platform.startswith("win"):
        # If user opted-in to force ASCII, respect it
        if _PROGRESS_CONFIG.force_ascii:
            return False
        # Try to detect WT/Terminal/VSCode which usually handle Unicode
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
    
    # Enhanced styling parameters - notebook-friendly format
    is_notebook, is_tty, is_windows = _detect_environment()
    if is_notebook:
        # Simpler format for notebooks to avoid display issues
        bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    else:
        # Full format for terminal
        bar_format = (
            "{l_bar}{bar:30}| {n_fmt}/{total_fmt} "
            "[{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        )
    
    # Color schemes based on operation type
    color_schemes = {
        "loading": {"colour": "cyan", "ncols": 100},
        "charts": {"colour": "green", "ncols": 100},
        "tables": {"colour": "blue", "ncols": 100},
        "figures": {"colour": "magenta", "ncols": 100},
        "ocr": {"colour": "yellow", "ncols": 100},
        "vlm": {"colour": "red", "ncols": 100},
        "processing": {"colour": "white", "ncols": 100},
    }
    
    # Determine color scheme based on description
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
    
    # Emoji categories
    emoji_categories = {"loading", "charts", "tables", "figures", "ocr", "vlm", "processing"}
    
    # Add appropriate emoji to description (can be disabled)
    if _PROGRESS_CONFIG.use_emoji:
        prefix_key = next((k for k in emoji_categories if k in desc_lower), "processing")
        prefix = _select_emoji(prefix_key)
        if prefix:
            desc = f"{prefix} {desc}"
    
    # Enhanced tqdm configuration
    tqdm_config = {
        "total": total,
        "desc": desc,
        "leave": leave,
        "bar_format": bar_format,
        "ncols": _PROGRESS_CONFIG.ncols_env or color_scheme["ncols"],
        # Prefer Unicode unless user forces ASCII or environment lacks Unicode support
        "ascii": _PROGRESS_CONFIG.force_ascii or not _supports_unicode_output(),
        "dynamic_ncols": True,  # Responsive width
        "smoothing": 0.3,  # Smooth progress updates
        "mininterval": 0.1,  # Minimum update interval
        "maxinterval": 1.0,  # Maximum update interval
        "position": position,
        **kwargs
    }
    
    # Enhanced environment detection
    is_notebook, is_terminal, is_windows = _detect_environment()
    
    # Add color only for terminal environments (not notebooks)
    if not is_notebook and is_terminal:
        tqdm_config["colour"] = color_scheme["colour"]
    
    # Respect global disable
    if _PROGRESS_CONFIG.disable:
        tqdm_config["disable"] = True

    # Try creating the progress bar with Unicode, fallback to ASCII on failure (e.g., Windows code page)
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
        # Format info as postfix
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
    Create a notebook-friendly progress bar with consistent sizing and static display.
    
    This function creates progress bars specifically optimized for Jupyter notebooks
    to avoid display issues and ANSI code problems while maintaining consistency
    with the main progress bar styling.
    
    :param total: Total number of items to process
    :param desc: Description text for the progress bar
    :param kwargs: Additional tqdm parameters
    :return: Configured notebook-friendly progress bar
    """
    # Force notebook mode
    if _PROGRESS_CONFIG.disable:
        kwargs["disable"] = True
    else:
        kwargs["disable"] = False
    # Prefer Unicode in notebooks if supported
    if "ascii" not in kwargs:
        kwargs["ascii"] = _PROGRESS_CONFIG.force_ascii or not _supports_unicode_output()
    
    # Emoji categories
    emoji_categories = {"loading", "charts", "tables", "figures", "ocr", "vlm", "processing"}
    
    # Add appropriate emoji to description
    desc_lower = desc.lower()
    if _PROGRESS_CONFIG.use_emoji:
        prefix_key = next((k for k in emoji_categories if k in desc_lower), "processing")
        prefix = _select_emoji(prefix_key)
        if prefix:
            desc = f"{prefix} {desc}"
    
    # Use same format as main progress bar for consistency
    bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    
    # Color schemes based on operation type (same as main progress bar)
    color_schemes = {
        "loading": {"colour": "cyan", "ncols": 100},
        "charts": {"colour": "green", "ncols": 100},
        "tables": {"colour": "blue", "ncols": 100},
        "figures": {"colour": "magenta", "ncols": 100},
        "ocr": {"colour": "yellow", "ncols": 100},
        "vlm": {"colour": "red", "ncols": 100},
        "processing": {"colour": "white", "ncols": 100},
    }
    
    # Determine color scheme based on description
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
    
    tqdm_config = {
        "total": total,
        "desc": desc,
        "leave": True,
        "bar_format": bar_format,
        "ncols": _PROGRESS_CONFIG.ncols_env or color_scheme["ncols"],  # Use same width as main progress bar
        "ascii": kwargs.get("ascii", False),
        "dynamic_ncols": True,  # Enable responsive width like main progress bar
        "smoothing": 0.3,  # Use same smoothing as main progress bar
        "mininterval": 0.1,  # Use same intervals as main progress bar
        "maxinterval": 1.0,
        **kwargs
    }
    
    # Use same approach as main progress bar for consistency
    is_notebook, is_tty, is_windows = _detect_environment()
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
