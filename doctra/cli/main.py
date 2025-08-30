"""
Doctra CLI - Command line interface for document processing

This module provides a comprehensive CLI for the Doctra library, enabling
users to process PDF documents, extract charts/tables, visualize layout 
detection results, and analyze document structure from the command line.
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional

# Import parsers
try:
    from doctra.parsers.structured_pdf_parser_enhancer import StructuredPDFParser
    from doctra.parsers.chart_table_pdf_parser import ChartTablePDFParser
except ImportError:
    # Fallback for development/testing
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from doctra.parsers.structured_pdf_parser import StructuredPDFParser
    from doctra.parsers.table_chart_extractor import ChartTablePDFParser


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0", prog_name="doctra")
def cli(ctx):
    """
    🔬 Doctra - Advanced Document Processing Library

    Extract text, tables, charts, and figures from PDF documents using
    layout detection, OCR, and optional VLM (Vision Language Model) enhancement.

    \b
    Commands:
      parse      Full document parsing with text, tables, charts, and figures
      extract    Extract only charts and/or tables from documents
      visualize  Visualize layout detection results
      analyze    Quick document analysis without processing
      info       Show system information and dependencies

    \b
    Examples:
      doctra parse document.pdf                    # Full document parsing
      doctra extract charts document.pdf          # Extract only charts
      doctra extract both document.pdf --use-vlm  # Extract charts & tables with VLM
      doctra visualize document.pdf               # Visualize layout detection
      doctra analyze document.pdf                 # Quick document analysis
      doctra info                                 # System information

    For more help on any command, use: doctra COMMAND --help

    :param ctx: Click context object containing command information
    :return: None
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Common options for VLM configuration
def vlm_options(func):
    """
    Decorator to add common VLM options to commands.
    
    Adds the following options to a Click command:
    - --use-vlm/--no-vlm: Enable/disable VLM processing
    - --vlm-provider: Choose between 'gemini' or 'openai'
    - --vlm-model: Model name to use (defaults to provider-specific defaults)
    - --vlm-api-key: API key for VLM provider

    :param func: The Click command function to decorate
    :return: Decorated function with VLM options
    """
    func = click.option('--use-vlm/--no-vlm', default=False,
                        help='Use Vision Language Model for table/chart extraction')(func)
    func = click.option('--vlm-provider', type=click.Choice(['gemini', 'openai']), default='gemini',
                        help='VLM provider to use (default: gemini)')(func)
    func = click.option('--vlm-model', type=str, default=None,
                        help='Model name to use (defaults to provider-specific defaults)')(func)
    func = click.option('--vlm-api-key', type=str, envvar='VLM_API_KEY',
                        help='API key for VLM provider (or set VLM_API_KEY env var)')(func)
    return func


# Common options for layout detection
def layout_options(func):
    """
    Decorator to add common layout detection options to commands.
    
    Adds the following options to a Click command:
    - --layout-model: Layout detection model name
    - --dpi: DPI for PDF rendering
    - --min-score: Minimum confidence score for layout detection

    :param func: The Click command function to decorate
    :return: Decorated function with layout options
    """
    func = click.option('--layout-model', default='PP-DocLayout_plus-L',
                        help='Layout detection model name (default: PP-DocLayout_plus-L)')(func)
    func = click.option('--dpi', type=int, default=200,
                        help='DPI for PDF rendering (default: 200)')(func)
    func = click.option('--min-score', type=float, default=0.0,
                        help='Minimum confidence score for layout detection (default: 0.0)')(func)
    return func


# Common options for OCR
def ocr_options(func):
    """
    Decorator to add common OCR options to commands.
    
    Adds the following options to a Click command:
    - --ocr-lang: OCR language code
    - --ocr-psm: Tesseract page segmentation mode
    - --ocr-oem: Tesseract OCR engine mode
    - --ocr-config: Additional Tesseract configuration

    :param func: The Click command function to decorate
    :return: Decorated function with OCR options
    """
    func = click.option('--ocr-lang', default='eng',
                        help='OCR language code (default: eng)')(func)
    func = click.option('--ocr-psm', type=int, default=4,
                        help='Tesseract page segmentation mode (default: 4)')(func)
    func = click.option('--ocr-oem', type=int, default=3,
                        help='Tesseract OCR engine mode (default: 3)')(func)
    func = click.option('--ocr-config', default='',
                        help='Additional Tesseract configuration string')(func)
    return func


def validate_vlm_config(use_vlm: bool, vlm_api_key: Optional[str]) -> None:
    """
    Validate VLM configuration and exit with error if invalid.
    
    Checks if VLM is enabled but no API key is provided, and exits
    with an appropriate error message if the configuration is invalid.

    :param use_vlm: Whether VLM processing is enabled
    :param vlm_api_key: The VLM API key (can be None if VLM is disabled)
    :return: None
    :raises SystemExit: If VLM is enabled but no API key is provided
    """
    if use_vlm and not vlm_api_key:
        click.echo("❌ Error: VLM API key is required when using --use-vlm", err=True)
        click.echo("   Set the VLM_API_KEY environment variable or use --vlm-api-key", err=True)
        click.echo("   Example: export VLM_API_KEY=your_api_key", err=True)
        sys.exit(1)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path),
              help='Output directory (default: outputs/{pdf_filename})')
@vlm_options
@layout_options
@ocr_options
@click.option('--box-separator', default='\n',
              help='Separator between text boxes in output (default: newline)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def parse(pdf_path: Path, output_dir: Optional[Path], use_vlm: bool,
          vlm_provider: str, vlm_model: Optional[str], vlm_api_key: Optional[str],
          layout_model: str, dpi: int, min_score: float,
          ocr_lang: str, ocr_psm: int, ocr_oem: int, ocr_config: str,
          box_separator: str, verbose: bool):
    """
    Parse a PDF document and extract all structured content.

    Performs comprehensive document processing including text extraction,
    layout detection, OCR, and optional VLM-based table/chart extraction.
    Outputs markdown file and optionally Excel file with structured data.

    \b
    Examples:
      doctra parse document.pdf
      doctra parse document.pdf --use-vlm --vlm-api-key your_key
      doctra parse document.pdf -o ./results --dpi 300
      doctra parse document.pdf --vlm-provider openai --use-vlm

    \b
    VLM Setup:
      Set environment variable: export VLM_API_KEY=your_api_key
      Or use: --vlm-api-key your_api_key

    :param pdf_path: Path to the input PDF file
    :param output_dir: Output directory for results (optional)
    :param use_vlm: Whether to use VLM for enhanced extraction
    :param vlm_provider: VLM provider ('gemini' or 'openai')
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider
    :param layout_model: Layout detection model name
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param ocr_lang: OCR language code
    :param ocr_psm: Tesseract page segmentation mode
    :param ocr_oem: Tesseract OCR engine mode
    :param ocr_config: Additional Tesseract configuration
    :param box_separator: Separator between text boxes in output
    :param verbose: Whether to enable verbose output
    :return: None
    """
    validate_vlm_config(use_vlm, vlm_api_key)

    if verbose:
        click.echo(f"🔍 Starting full PDF parsing...")
        click.echo(f"   Input: {pdf_path}")
        if output_dir:
            click.echo(f"   Output: {output_dir}")

    # Create parser instance
    try:
        if verbose:
            click.echo(f"🔧 Initializing full parser...")
            if use_vlm:
                click.echo(f"   VLM Provider: {vlm_provider}")
                click.echo(f"   VLM Model: {vlm_model or 'default'}")
            click.echo(f"   Layout Model: {layout_model}")
            click.echo(f"   DPI: {dpi}")
            click.echo(f"   OCR Language: {ocr_lang}")
        else:
            click.echo(f"🔍 Initializing full document parser...")
            if use_vlm:
                click.echo(f"   Using VLM: {vlm_provider}")

        parser = StructuredPDFParser(
            use_vlm=use_vlm,
            vlm_provider=vlm_provider,
            vlm_model=vlm_model,
            vlm_api_key=vlm_api_key,
            layout_model_name=layout_model,
            dpi=dpi,
            min_score=min_score,
            ocr_lang=ocr_lang,
            ocr_psm=ocr_psm,
            ocr_oem=ocr_oem,
            ocr_extra_config=ocr_config,
            box_separator=box_separator
        )
    except Exception as e:
        click.echo(f"❌ Error initializing parser: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)

    # Change to output directory if specified
    original_cwd = os.getcwd()
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(output_dir)
        click.echo(f"📁 Output directory: {output_dir.absolute()}")

    try:
        # Parse the document
        click.echo(f"📄 Processing: {pdf_path.name}")
        parser.parse(str(pdf_path.absolute()))
        click.echo("✅ Full document processing completed successfully!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Processing interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error during parsing: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


@cli.group(invoke_without_command=True)
@click.pass_context
def extract(ctx):
    """
    Extract charts and/or tables from PDF documents.

    This command focuses specifically on chart and table extraction,
    providing faster processing when you only need these elements.

    \b
    Subcommands:
      charts    Extract only charts from the document
      tables    Extract only tables from the document
      both      Extract both charts and tables

    \b
    Examples:
      doctra extract charts document.pdf
      doctra extract tables document.pdf --use-vlm
      doctra extract both document.pdf --output-dir ./results

    :param ctx: Click context object containing command information
    :return: None
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@extract.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), default=Path("outputs"),
              help='Output base directory (default: outputs)')
@vlm_options
@layout_options
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def charts(pdf_path: Path, output_dir: Path, use_vlm: bool, vlm_provider: str,
           vlm_model: Optional[str], vlm_api_key: Optional[str],
           layout_model: str, dpi: int, min_score: float, verbose: bool):
    """
    Extract only charts from a PDF document.

    Saves chart images and optionally converts them to structured data using VLM.

    \b
    Examples:
      doctra extract charts document.pdf
      doctra extract charts document.pdf --use-vlm --vlm-api-key your_key
      doctra extract charts document.pdf -o ./my_outputs --dpi 300

    :param pdf_path: Path to the input PDF file
    :param output_dir: Output base directory for results
    :param use_vlm: Whether to use VLM for enhanced chart extraction
    :param vlm_provider: VLM provider ('gemini' or 'openai')
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider
    :param layout_model: Layout detection model name
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param verbose: Whether to enable verbose output
    :return: None
    """
    validate_vlm_config(use_vlm, vlm_api_key)

    if verbose:
        click.echo(f"📊 Starting chart extraction...")
        click.echo(f"   Input: {pdf_path}")
        click.echo(f"   Output base: {output_dir}")

    try:
        if verbose:
            click.echo(f"🔧 Initializing chart extractor...")
            if use_vlm:
                click.echo(f"   VLM Provider: {vlm_provider}")
        else:
            click.echo(f"📊 Initializing chart extractor...")
            if use_vlm:
                click.echo(f"   Using VLM: {vlm_provider}")

        parser = ChartTablePDFParser(
            extract_charts=True,
            extract_tables=False,
            use_vlm=use_vlm,
            vlm_provider=vlm_provider,
            vlm_model=vlm_model,
            vlm_api_key=vlm_api_key,
            layout_model_name=layout_model,
            dpi=dpi,
            min_score=min_score
        )

        click.echo(f"📄 Processing: {pdf_path.name}")
        parser.parse(str(pdf_path), str(output_dir))
        click.echo("✅ Chart extraction completed successfully!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Extraction interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error during chart extraction: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@extract.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), default=Path("outputs"),
              help='Output base directory (default: outputs)')
@vlm_options
@layout_options
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def tables(pdf_path: Path, output_dir: Path, use_vlm: bool, vlm_provider: str,
           vlm_model: Optional[str], vlm_api_key: Optional[str],
           layout_model: str, dpi: int, min_score: float, verbose: bool):
    """
    Extract only tables from a PDF document.

    Saves table images and optionally converts them to structured data using VLM.

    \b
    Examples:
      doctra extract tables document.pdf
      doctra extract tables document.pdf --use-vlm --vlm-api-key your_key
      doctra extract tables document.pdf -o ./my_outputs --min-score 0.5

    :param pdf_path: Path to the input PDF file
    :param output_dir: Output base directory for results
    :param use_vlm: Whether to use VLM for enhanced table extraction
    :param vlm_provider: VLM provider ('gemini' or 'openai')
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider
    :param layout_model: Layout detection model name
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param verbose: Whether to enable verbose output
    :return: None
    """
    validate_vlm_config(use_vlm, vlm_api_key)

    if verbose:
        click.echo(f"📋 Starting table extraction...")
        click.echo(f"   Input: {pdf_path}")
        click.echo(f"   Output base: {output_dir}")

    try:
        if verbose:
            click.echo(f"🔧 Initializing table extractor...")
            if use_vlm:
                click.echo(f"   VLM Provider: {vlm_provider}")
        else:
            click.echo(f"📋 Initializing table extractor...")
            if use_vlm:
                click.echo(f"   Using VLM: {vlm_provider}")

        parser = ChartTablePDFParser(
            extract_charts=False,
            extract_tables=True,
            use_vlm=use_vlm,
            vlm_provider=vlm_provider,
            vlm_model=vlm_model,
            vlm_api_key=vlm_api_key,
            layout_model_name=layout_model,
            dpi=dpi,
            min_score=min_score
        )

        click.echo(f"📄 Processing: {pdf_path.name}")
        parser.parse(str(pdf_path), str(output_dir))
        click.echo("✅ Table extraction completed successfully!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Extraction interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error during table extraction: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@extract.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), default=Path("outputs"),
              help='Output base directory (default: outputs)')
@vlm_options
@layout_options
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def both(pdf_path: Path, output_dir: Path, use_vlm: bool, vlm_provider: str,
         vlm_model: Optional[str], vlm_api_key: Optional[str],
         layout_model: str, dpi: int, min_score: float, verbose: bool):
    """
    Extract both charts and tables from a PDF document.

    Saves both chart and table images, and optionally converts them
    to structured data using VLM.

    \b
    Examples:
      doctra extract both document.pdf
      doctra extract both document.pdf --use-vlm --vlm-api-key your_key
      doctra extract both document.pdf -o ./my_outputs --dpi 300

    :param pdf_path: Path to the input PDF file
    :param output_dir: Output base directory for results
    :param use_vlm: Whether to use VLM for enhanced extraction
    :param vlm_provider: VLM provider ('gemini' or 'openai')
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider
    :param layout_model: Layout detection model name
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param verbose: Whether to enable verbose output
    :return: None
    """
    validate_vlm_config(use_vlm, vlm_api_key)

    if verbose:
        click.echo(f"📊📋 Starting chart and table extraction...")
        click.echo(f"   Input: {pdf_path}")
        click.echo(f"   Output base: {output_dir}")

    try:
        if verbose:
            click.echo(f"🔧 Initializing chart/table extractor...")
            if use_vlm:
                click.echo(f"   VLM Provider: {vlm_provider}")
        else:
            click.echo(f"📊📋 Initializing chart and table extractor...")
            if use_vlm:
                click.echo(f"   Using VLM: {vlm_provider}")

        parser = ChartTablePDFParser(
            extract_charts=True,
            extract_tables=True,
            use_vlm=use_vlm,
            vlm_provider=vlm_provider,
            vlm_model=vlm_model,
            vlm_api_key=vlm_api_key,
            layout_model_name=layout_model,
            dpi=dpi,
            min_score=min_score
        )

        click.echo(f"📄 Processing: {pdf_path.name}")
        parser.parse(str(pdf_path), str(output_dir))
        click.echo("✅ Chart and table extraction completed successfully!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Extraction interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error during extraction: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@click.option('--pages', '-p', type=int, default=3,
              help='Number of pages to visualize (default: 3)')
@click.option('--columns', '-c', type=int, default=2,
              help='Number of columns in grid layout (default: 2)')
@click.option('--width', '-w', type=int, default=800,
              help='Width of each page in pixels (default: 800)')
@click.option('--spacing', '-s', type=int, default=40,
              help='Spacing between pages in pixels (default: 40)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Save visualization to file (PNG/JPG)')
@layout_options
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def visualize(pdf_path: Path, pages: int, columns: int, width: int,
              spacing: int, output: Optional[Path], dpi: int, min_score: float,
              layout_model: str, verbose: bool):
    """
    Visualize layout detection results for a PDF.

    Shows detected layout elements (text, tables, figures, charts)
    with bounding boxes and confidence scores in a modern grid layout.

    \b
    Examples:
      doctra visualize document.pdf
      doctra visualize document.pdf --pages 5 --output layout.png
      doctra visualize document.pdf --columns 3 --width 600

    :param pdf_path: Path to the input PDF file
    :param pages: Number of pages to visualize
    :param columns: Number of columns in the grid layout
    :param width: Width of each page in pixels
    :param spacing: Spacing between pages in pixels
    :param output: Optional path to save visualization as image file
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param layout_model: Layout detection model name
    :param verbose: Whether to enable verbose output
    :return: None
    """
    try:
        if verbose:
            click.echo(f"🎨 Creating layout visualization...")
            click.echo(f"   Input: {pdf_path}")
            click.echo(f"   Pages: {pages}, Columns: {columns}")
            click.echo(f"   Page width: {width}px, Spacing: {spacing}px")
            click.echo(f"   DPI: {dpi}, Min score: {min_score}")
        else:
            click.echo(f"🎨 Creating layout visualization...")

        # Create parser instance (no VLM needed for visualization)
        parser = StructuredPDFParser(
            layout_model_name=layout_model,
            dpi=dpi,
            min_score=min_score
        )

        click.echo(f"📄 Processing: {pdf_path.name}")
        if output:
            click.echo(f"💾 Saving to: {output}")
        else:
            click.echo("👁️  Will display visualization window")

        parser.display_pages_with_boxes(
            pdf_path=str(pdf_path),
            num_pages=pages,
            cols=columns,
            page_width=width,
            spacing=spacing,
            save_path=str(output) if output else None
        )

        if not output:
            click.echo("   Close the window to continue...")
        else:
            click.echo("✅ Visualization saved successfully!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Visualization interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error creating visualization: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, path_type=Path))
@layout_options
@click.option('--verbose', '-v', is_flag=True, help='Show detailed per-page breakdown')
def analyze(pdf_path: Path, dpi: int, min_score: float, layout_model: str, verbose: bool):
    """
    Analyze a PDF and show statistics without processing.

    Quick analysis to understand document structure before full processing.
    Shows total pages, element counts, and distribution statistics.

    \b
    Examples:
      doctra analyze document.pdf
      doctra analyze document.pdf --verbose
      doctra analyze document.pdf --min-score 0.5

    :param pdf_path: Path to the input PDF file
    :param dpi: DPI for PDF rendering
    :param min_score: Minimum confidence score for layout detection
    :param layout_model: Layout detection model name
    :param verbose: Whether to show detailed per-page breakdown
    :return: None
    """
    try:
        click.echo(f"🔍 Analyzing: {pdf_path.name}")

        # Create layout engine for analysis only
        from doctra.engines.layout.paddle_layout import PaddleLayoutEngine

        if verbose:
            click.echo(f"   Using model: {layout_model}")
            click.echo(f"   DPI: {dpi}, Min score: {min_score}")

        layout_engine = PaddleLayoutEngine(model_name=layout_model)
        pages = layout_engine.predict_pdf(str(pdf_path), dpi=dpi, min_score=min_score)

        click.echo(f"\n📊 Document Analysis Results:")
        click.echo(f"   Total pages: {len(pages)}")

        # Collect statistics
        total_elements = 0
        element_counts = {}
        page_elements = []

        for page in pages:
            page_element_count = len(page.boxes)
            total_elements += page_element_count
            page_elements.append(page_element_count)

            for box in page.boxes:
                element_counts[box.label] = element_counts.get(box.label, 0) + 1

        click.echo(f"   Total elements: {total_elements}")

        if total_elements > 0:
            # Average elements per page
            avg_elements = total_elements / len(pages)
            click.echo(f"   Average per page: {avg_elements:.1f}")

            click.echo(f"\n   📋 Elements by type:")
            for element_type, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_elements) * 100
                click.echo(f"     • {element_type.ljust(10)}: {str(count).rjust(3)} ({percentage:4.1f}%)")

            # Chart and table specific analysis
            charts = element_counts.get('chart', 0)
            tables = element_counts.get('table', 0)

            if charts > 0 or tables > 0:
                click.echo(f"\n   🎯 Extraction recommendations:")
                if charts > 0 and tables > 0:
                    click.echo(f"     • Use: doctra extract both document.pdf")
                    click.echo(f"     • Charts: {charts}, Tables: {tables}")
                elif charts > 0:
                    click.echo(f"     • Use: doctra extract charts document.pdf")
                    click.echo(f"     • Charts found: {charts}")
                elif tables > 0:
                    click.echo(f"     • Use: doctra extract tables document.pdf")
                    click.echo(f"     • Tables found: {tables}")

            # Page-by-page breakdown
            if verbose:
                click.echo(f"\n   📄 Page-by-page breakdown:")
                for i, page in enumerate(pages[:20]):  # Show first 20 pages in verbose mode
                    page_stats = {}
                    for box in page.boxes:
                        page_stats[box.label] = page_stats.get(box.label, 0) + 1

                    stats_str = ", ".join([f"{k}: {v}" for k, v in sorted(page_stats.items())])
                    click.echo(f"     Page {page.page_index:3d}: {len(page.boxes):2d} elements ({stats_str})")

                if len(pages) > 20:
                    click.echo(f"     ... and {len(pages) - 20} more pages")
            else:
                click.echo(f"\n   📄 Page summary:")
                if page_elements:
                    min_elements = min(page_elements)
                    max_elements = max(page_elements)
                    click.echo(f"     Range: {min_elements} - {max_elements} elements per page")

                    # Show pages with most/least elements
                    max_page = page_elements.index(max_elements) + 1
                    min_page = page_elements.index(min_elements) + 1
                    click.echo(f"     Most elements: Page {max_page} ({max_elements} elements)")
                    click.echo(f"     Least elements: Page {min_page} ({min_elements} elements)")

            # Processing time estimate
            estimated_time = len(pages) * 2  # Rough estimate: 2 seconds per page
            if element_counts.get('table', 0) > 0 or element_counts.get('chart', 0) > 0:
                estimated_time += (element_counts.get('table', 0) + element_counts.get('chart', 0)) * 5

            click.echo(f"\n   ⏱️  Estimated processing time: ~{estimated_time} seconds")
            if element_counts.get('table', 0) > 0 or element_counts.get('chart', 0) > 0:
                vlm_time = (element_counts.get('table', 0) + element_counts.get('chart', 0)) * 3
                click.echo(
                    f"      (Add ~{vlm_time}s more with VLM for {element_counts.get('table', 0) + element_counts.get('chart', 0)} tables/charts)")
        else:
            click.echo("   ⚠️  No elements detected (try lowering --min-score)")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Analysis interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Error analyzing PDF: {e}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
def info():
    """
    Show system information and available models.

    Displays Python version, dependency status, available VLM providers,
    layout models, and OCR language information.

    :return: None
    """
    click.echo("🔬 Doctra System Information")
    click.echo("=" * 50)

    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    click.echo(f"Python version: {python_version}")

    # Check key dependencies
    dependencies = [
        ('PIL', 'Pillow', 'Image processing'),
        ('paddle', 'PaddlePaddle', 'Layout detection engine'),
        ('pytesseract', 'pytesseract', 'OCR engine'),
        ('tqdm', 'tqdm', 'Progress bars'),
        ('click', 'click', 'CLI framework'),
    ]

    click.echo("\nCore Dependencies:")
    for module_name, package_name, description in dependencies:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            click.echo(f"  ✅ {package_name} ({version}) - {description}")
        except ImportError:
            click.echo(f"  ❌ {package_name} - {description} (not installed)")

    # Optional VLM dependencies
    click.echo("\nVLM Dependencies (Optional):")
    vlm_deps = [
        ('google.generativeai', 'google-generativeai', 'Gemini VLM support'),
        ('openai', 'openai', 'OpenAI VLM support'),
    ]

    for module_name, package_name, description in vlm_deps:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            click.echo(f"  ✅ {package_name} ({version}) - {description}")
        except ImportError:
            click.echo(f"  ⚠️  {package_name} - {description} (not installed)")

    # Available commands
    click.echo("\nAvailable Commands:")
    click.echo("  📄 parse      - Full document processing (text, tables, charts, figures)")
    click.echo("  📊 extract    - Chart/table extraction only")
    click.echo("    ├─ charts   - Extract only charts")
    click.echo("    ├─ tables   - Extract only tables")
    click.echo("    └─ both     - Extract charts and tables")
    click.echo("  🎨 visualize  - Layout detection visualization")
    click.echo("  🔍 analyze    - Document structure analysis")
    click.echo("  ℹ️  info      - System information (this command)")

    # VLM providers
    click.echo("\nVLM Providers:")
    click.echo("  • Gemini (Google) - gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.0-flash")
    click.echo("  • OpenAI - gpt-5, gpt-5-mini, gpt-4.1, gpt-4.1-mini, gpt-4o")

    # Available layout models
    click.echo("\nLayout Detection Models:")
    click.echo("  • PP-DocLayout_plus-L (default) - High accuracy layout detection")
    click.echo("  • PP-DocLayout_plus-M - Balanced speed and accuracy")
    click.echo("  • PP-DocLayout_plus-S - Fast inference")

    # OCR information
    click.echo("\nOCR Configuration:")
    click.echo("  Engine: Tesseract OCR")
    click.echo("  Common languages: eng, fra, deu, spa, ita, por, rus, ara, chi_sim, jpn")
    click.echo("  Use 'tesseract --list-langs' for complete language list")

    # Environment variables
    click.echo("\nEnvironment Variables:")
    vlm_key = os.environ.get('VLM_API_KEY')
    if vlm_key:
        masked_key = vlm_key[:8] + '*' * (len(vlm_key) - 12) + vlm_key[-4:] if len(vlm_key) > 12 else '*' * len(vlm_key)
        click.echo(f"  VLM_API_KEY: {masked_key}")
    else:
        click.echo("  VLM_API_KEY: (not set)")

    # Usage examples
    click.echo("\n💡 Quick Start Examples:")
    click.echo("  doctra parse document.pdf                    # Full document parsing")
    click.echo("  doctra extract both document.pdf --use-vlm  # Charts & tables with VLM")
    click.echo("  doctra extract charts document.pdf          # Only charts")
    click.echo("  doctra extract tables document.pdf          # Only tables")
    click.echo("  doctra visualize document.pdf               # Visualize layout")
    click.echo("  doctra analyze document.pdf                 # Quick analysis")


if __name__ == '__main__':
    cli()