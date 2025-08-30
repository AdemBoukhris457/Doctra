from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any
from tqdm import tqdm
from tqdm.auto import tqdm as tqdm_auto


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
    if "ipykernel" in sys.modules:
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
    
    # Add emoji icons to descriptions
    emoji_map = {
        "loading": "🔄",
        "charts": "📊",
        "tables": "📋",
        "figures": "🖼️",
        "ocr": "🔍",
        "vlm": "🤖",
        "processing": "⚙️",
    }
    
    # Add appropriate emoji to description
    for key, emoji in emoji_map.items():
        if key in desc_lower:
            desc = f"{emoji} {desc}"
            break
    else:
        desc = f"⚙️ {desc}"
    
    # Enhanced tqdm configuration
    tqdm_config = {
        "total": total,
        "desc": desc,
        "leave": leave,
        "bar_format": bar_format,
        "ncols": color_scheme["ncols"],
        "ascii": False,  # Use Unicode characters for better appearance
        "dynamic_ncols": True,  # Responsive width
        "smoothing": 0.3,  # Smooth progress updates
        "mininterval": 0.1,  # Minimum update interval
        "maxinterval": 1.0,  # Maximum update interval
        "position": position,
        **kwargs
    }
    
    # Enhanced environment detection
    is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
    is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    # Add color only for terminal environments (not notebooks)
    if not is_notebook and is_terminal:
        tqdm_config["colour"] = color_scheme["colour"]
    
    # Use auto tqdm for better Jupyter notebook support
    if is_notebook:
        # In notebooks, don't use color to avoid ANSI code issues
        tqdm_config.pop("colour", None)  # Remove color in notebooks
        return tqdm_auto(**tqdm_config)
    else:
        # In terminal/cmd/powershell, we can use colors
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
    Create a notebook-friendly progress bar with minimal formatting.
    
    This function creates progress bars specifically optimized for Jupyter notebooks
    to avoid display issues and ANSI code problems.
    
    :param total: Total number of items to process
    :param desc: Description text for the progress bar
    :param kwargs: Additional tqdm parameters
    :return: Configured notebook-friendly progress bar
    """
    # Force notebook mode
    kwargs["disable"] = False
    kwargs["ascii"] = True  # Use ASCII characters for better notebook compatibility
    
    # Add emoji icons to descriptions (same as beautiful bars)
    emoji_map = {
        "loading": "🔄",
        "charts": "📊",
        "tables": "📋",
        "figures": "🖼️",
        "ocr": "🔍",
        "vlm": "🤖",
        "processing": "⚙️",
    }
    
    # Add appropriate emoji to description
    desc_lower = desc.lower()
    for key, emoji in emoji_map.items():
        if key in desc_lower:
            desc = f"{emoji} {desc}"
            break
    else:
        desc = f"⚙️ {desc}"
    
    # Simple format for notebooks
    bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"
    
    tqdm_config = {
        "total": total,
        "desc": desc,
        "leave": True,
        "bar_format": bar_format,
        "ncols": 80,
        "ascii": True,
        "dynamic_ncols": False,  # Fixed width for notebooks
        "smoothing": 0.1,  # Faster updates
        "mininterval": 0.05,
        "maxinterval": 0.5,
        **kwargs
    }
    
    return tqdm_auto(**tqdm_config)
