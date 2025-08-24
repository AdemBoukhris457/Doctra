"""
CLI utilities for the Doctra command line interface.

This module contains shared utilities and helper functions used across
different CLI commands.
"""

import click
import sys
from typing import Optional, Dict, Any
from pathlib import Path


def validate_vlm_config(use_vlm: bool, vlm_api_key: Optional[str]) -> None:
    """
    Validate VLM configuration and exit with error if invalid.

    Args:
        use_vlm: Whether VLM is enabled
        vlm_api_key: The VLM API key (can be None)
    """
    if use_vlm and not vlm_api_key:
        click.echo("❌ Error: VLM API key is required when using --use-vlm", err=True)
        click.echo("   Set the VLM_API_KEY environment variable or use --vlm-api-key", err=True)
        click.echo("   Example: export VLM_API_KEY=your_api_key", err=True)
        sys.exit(1)


def handle_keyboard_interrupt() -> None:
    """Handle keyboard interrupt (Ctrl+C) gracefully."""
    click.echo("\n⚠️  Operation interrupted by user", err=True)
    sys.exit(130)


def handle_exception(e: Exception, verbose: bool = False) -> None:
    """
    Handle exceptions with appropriate error messages.

    Args:
        e: The exception that occurred
        verbose: Whether to show full traceback
    """
    click.echo(f"❌ Error: {e}", err=True)
    if verbose:
        import traceback
        click.echo(traceback.format_exc(), err=True)
    sys.exit(1)


def validate_pdf_path(pdf_path: Path) -> None:
    """
    Validate that the PDF path exists and is a valid PDF file.

    Args:
        pdf_path: Path to the PDF file
    """
    if not pdf_path.exists():
        click.echo(f"❌ Error: PDF file not found: {pdf_path}", err=True)
        sys.exit(1)

    if not pdf_path.is_file():
        click.echo(f"❌ Error: Path is not a file: {pdf_path}", err=True)
        sys.exit(1)

    if pdf_path.suffix.lower() != '.pdf':
        click.echo(f"⚠️  Warning: File does not have .pdf extension: {pdf_path}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get basic file information.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    if not file_path.exists():
        return {}

    stat = file_path.stat()
    return {
        'name': file_path.name,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': stat.st_mtime,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
        'extension': file_path.suffix.lower()
    }


def print_processing_summary(
        input_file: Path,
        output_dir: Path,
        processing_time: Optional[float] = None,
        elements_processed: Optional[int] = None,
        use_vlm: bool = False
) -> None:
    """
    Print a summary of processing results.

    Args:
        input_file: Input PDF file path
        output_dir: Output directory path
        processing_time: Time taken for processing in seconds
        elements_processed: Number of elements processed
        use_vlm: Whether VLM was used
    """
    click.echo("\n" + "=" * 50)
    click.echo("📊 Processing Summary")
    click.echo("=" * 50)

    # Input file info
    file_info = get_file_info(input_file)
    if file_info:
        click.echo(f"Input file: {file_info['name']}")
        click.echo(f"File size:  {file_info['size_formatted']}")

    # Output info
    if output_dir.exists():
        click.echo(f"Output:     {output_dir}")

    # Processing details
    if elements_processed is not None:
        click.echo(f"Elements:   {elements_processed} processed")

    if processing_time is not None:
        click.echo(f"Time:       {processing_time:.1f} seconds")

    if use_vlm:
        click.echo("VLM:        ✅ Enabled")
    else:
        click.echo("VLM:        ❌ Disabled")


def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are available.

    Returns:
        Dictionary mapping dependency names to availability status
    """
    dependencies = {
        'PIL': False,
        'paddle': False,
        'pytesseract': False,
        'tqdm': False,
        'click': False,
        'google.generativeai': False,
        'openai': False,
    }

    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False

    return dependencies


def estimate_processing_time(
        num_pages: int,
        num_charts: int = 0,
        num_tables: int = 0,
        use_vlm: bool = False
) -> int:
    """
    Estimate processing time based on document characteristics.

    Args:
        num_pages: Number of pages in document
        num_charts: Number of charts detected
        num_tables: Number of tables detected
        use_vlm: Whether VLM processing will be used

    Returns:
        Estimated processing time in seconds
    """
    # Base time per page (layout detection + OCR)
    base_time = num_pages * 2

    # Additional time for charts and tables
    visual_elements_time = (num_charts + num_tables) * 1

    # VLM processing time
    vlm_time = 0
    if use_vlm:
        vlm_time = (num_charts + num_tables) * 3

    return base_time + visual_elements_time + vlm_time


def create_progress_callback(description: str, total: int):
    """
    Create a progress callback function for use with processing operations.

    Args:
        description: Description for the progress bar
        total: Total number of items to process

    Returns:
        Callable progress callback function
    """
    from tqdm import tqdm

    pbar = tqdm(total=total, desc=description, leave=True)

    def callback(completed: int):
        pbar.n = completed
        pbar.refresh()
        if completed >= total:
            pbar.close()

    return callback


def safe_create_directory(path: Path, parents: bool = True) -> bool:
    """
    Safely create a directory with error handling.

    Args:
        path: Directory path to create
        parents: Whether to create parent directories

    Returns:
        True if successful, False otherwise
    """
    try:
        path.mkdir(parents=parents, exist_ok=True)
        return True
    except PermissionError:
        click.echo(f"❌ Permission denied creating directory: {path}", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ Error creating directory {path}: {e}", err=True)
        return False


def get_output_recommendations(element_counts: Dict[str, int]) -> str:
    """
    Generate command recommendations based on detected elements.

    Args:
        element_counts: Dictionary of element type counts

    Returns:
        Recommendation string
    """
    charts = element_counts.get('chart', 0)
    tables = element_counts.get('table', 0)
    text = element_counts.get('text', 0)
    figures = element_counts.get('figure', 0)

    recommendations = []

    if charts > 0 and tables > 0:
        recommendations.append(f"📊📋 doctra extract both document.pdf  # {charts} charts, {tables} tables")
    elif charts > 0:
        recommendations.append(f"📊 doctra extract charts document.pdf  # {charts} charts")
    elif tables > 0:
        recommendations.append(f"📋 doctra extract tables document.pdf  # {tables} tables")

    if text > 0 or figures > 0:
        recommendations.append(f"📄 doctra parse document.pdf  # Full document with text")

    if charts > 0 or tables > 0:
        recommendations.append("💡 Add --use-vlm for structured data extraction")

    return "\n     ".join(recommendations) if recommendations else "No specific recommendations"