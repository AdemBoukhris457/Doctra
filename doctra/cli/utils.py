"""
CLI utilities for the Doctra command line interface.

This module contains shared utilities and helper functions used across
different CLI commands.
"""

import click
import sys
import traceback
from typing import Optional, Dict, Any
from pathlib import Path
from doctra.utils.progress import create_beautiful_progress_bar, create_notebook_friendly_bar


def validate_vlm_config(use_vlm: bool, vlm_api_key: Optional[str], vlm_provider: str = "gemini") -> None:
    """
    Validate VLM configuration and exit with error if invalid.
    
    Checks if VLM is enabled but no API key is provided (except for Ollama), and exits
    with an appropriate error message if the configuration is invalid.

    :param use_vlm: Whether VLM processing is enabled
    :param vlm_api_key: The VLM API key (can be None if VLM is disabled or using Ollama)
    :param vlm_provider: VLM provider name (default: "gemini")
    :return: None
    :raises SystemExit: If VLM is enabled but no API key is provided (except for Ollama)
    """
    if use_vlm and vlm_provider != "ollama" and not vlm_api_key:
        click.echo("❌ Error: VLM API key is required when using --use-vlm (except for Ollama)", err=True)
        click.echo("   Set the VLM_API_KEY environment variable or use --vlm-api-key", err=True)
        click.echo("   Example: export VLM_API_KEY=your_api_key", err=True)
        sys.exit(1)


def handle_keyboard_interrupt() -> None:
    """
    Handle keyboard interrupt (Ctrl+C) gracefully.
    
    Displays a user-friendly message and exits with the standard
    interrupt exit code (130).

    :return: None
    :raises SystemExit: Always exits with code 130
    """
    click.echo("\n⚠️  Operation interrupted by user", err=True)
    sys.exit(130)


def handle_exception(e: Exception, verbose: bool = False) -> None:
    """
    Handle exceptions with appropriate error messages.
    
    Displays the exception message and optionally the full traceback
    if verbose mode is enabled.

    :param e: The exception that occurred
    :param verbose: Whether to show full traceback
    :return: None
    :raises SystemExit: Always exits with code 1
    """
    click.echo(f"❌ Error: {e}", err=True)
    if verbose:
        click.echo(traceback.format_exc(), err=True)
    sys.exit(1)


def validate_pdf_path(pdf_path: Path) -> None:
    """
    Validate that the PDF path exists and is a valid PDF file.
    
    Checks if the file exists, is actually a file (not directory),
    and optionally warns if the file extension is not .pdf.

    :param pdf_path: Path to the PDF file to validate
    :return: None
    :raises SystemExit: If file doesn't exist or is not a file
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
    
    Converts bytes to the most appropriate unit (B, KB, MB, GB)
    with one decimal place precision.

    :param size_bytes: Size in bytes to format
    :return: Formatted size string (e.g., "1.5 MB", "2.3 GB")
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
    
    Retrieves file metadata including name, size, modification time,
    and file type information.

    :param file_path: Path to the file to get information for
    :return: Dictionary containing file information with keys:
             - name: File name
             - size: Size in bytes
             - size_formatted: Human-readable size
             - modified: Modification timestamp
             - is_file: Whether it's a file
             - is_dir: Whether it's a directory
             - extension: File extension (lowercase)
             Returns empty dict if file doesn't exist
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
    
    Displays a formatted summary including input file information,
    output directory, processing time, number of elements processed,
    and VLM usage status.

    :param input_file: Input PDF file path
    :param output_dir: Output directory path
    :param processing_time: Time taken for processing in seconds
    :param elements_processed: Number of elements processed
    :param use_vlm: Whether VLM was used during processing
    :return: None
    """
    click.echo("\n" + "=" * 50)
    click.echo("📊 Processing Summary")
    click.echo("=" * 50)

    file_info = get_file_info(input_file)
    if file_info:
        click.echo(f"Input file: {file_info['name']}")
        click.echo(f"File size:  {file_info['size_formatted']}")

    if output_dir.exists():
        click.echo(f"Output:     {output_dir}")

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
    
    Tests import availability for core and optional dependencies
    used by the Doctra library.

    :return: Dictionary mapping dependency names to availability status:
             - PIL: Pillow for image processing
             - paddle: PaddlePaddle for layout detection
             - pytesseract: Tesseract OCR wrapper
             - tqdm: Progress bar library
             - click: CLI framework
             - google.generativeai: Gemini VLM support
             - openai: OpenAI VLM support
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
    
    Provides a rough estimate of processing time based on the number
    of pages, charts, tables, and whether VLM processing is enabled.

    :param num_pages: Number of pages in the document
    :param num_charts: Number of charts detected in the document
    :param num_tables: Number of tables detected in the document
    :param use_vlm: Whether VLM processing will be used
    :return: Estimated processing time in seconds
    """
    base_time = num_pages * 2

    visual_elements_time = (num_charts + num_tables) * 1

    vlm_time = 0
    if use_vlm:
        vlm_time = (num_charts + num_tables) * 3

    return base_time + visual_elements_time + vlm_time


def create_progress_callback(description: str, total: int):
    """
    Create a progress callback function for use with processing operations.
    
    Creates a beautiful tqdm progress bar and returns a callback function that
    can be used to update the progress during long-running operations.

    :param description: Description text for the progress bar
    :param total: Total number of items to process
    :return: Callable progress callback function that takes an integer
             representing the number of completed items
    """

    is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
    is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    if is_notebook:
        pbar = create_notebook_friendly_bar(total=total, desc=description)
    else:
        pbar = create_beautiful_progress_bar(total=total, desc=description, leave=True)

    def callback(completed: int):
        pbar.n = completed
        pbar.refresh()
        if completed >= total:
            pbar.close()

    return callback


def safe_create_directory(path: Path, parents: bool = True) -> bool:
    """
    Safely create a directory with error handling.
    
    Attempts to create a directory and handles common errors like
    permission issues gracefully.

    :param path: Directory path to create
    :param parents: Whether to create parent directories if they don't exist
    :return: True if directory was created successfully, False otherwise
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
    
    Analyzes the types and counts of detected elements and suggests
    appropriate Doctra commands for processing.

    :param element_counts: Dictionary mapping element types to their counts
                          (e.g., {'chart': 5, 'table': 3, 'text': 100})
    :return: Formatted string with command recommendations for the user
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