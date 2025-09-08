import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List

import gradio as gr

from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.parsers.table_chart_extractor import ChartTablePDFParser


def _gather_outputs(out_dir: Path) -> Tuple[List[tuple[str, str]], List[str], str]:
    gallery_items: List[tuple[str, str]] = []
    file_paths: List[str] = []

    if out_dir.exists():
        for p in out_dir.rglob("*"):
            if p.is_file():
                file_paths.append(str(p))

    for sub in ["tables", "charts", "figures"]:
        p = out_dir / "images" / sub
        if p.exists():
            for img in sorted(p.glob("*.jpg")):
                gallery_items.append((str(img), f"{sub}: {img.name}"))

    tmp_zip_dir = Path(tempfile.mkdtemp(prefix="doctra_zip_"))
    zip_base = tmp_zip_dir / "doctra_outputs"
    zip_path = shutil.make_archive(str(zip_base), 'zip', root_dir=str(out_dir))

    return gallery_items, file_paths, zip_path


def run_full_parse(
    pdf_file: str,
    use_vlm: bool,
    vlm_provider: str,
    vlm_api_key: str,
    layout_model_name: str,
    dpi: int,
    min_score: float,
    ocr_lang: str,
    ocr_psm: int,
    ocr_oem: int,
    ocr_extra_config: str,
    box_separator: str,
) -> Tuple[str, Optional[str], List[tuple[str, str]], List[str], str]:
    if not pdf_file:
        return ("No file provided.", None, [], [], "")

    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    input_pdf = tmp_dir / "input.pdf"
    shutil.copy2(pdf_file, input_pdf)

    parser = StructuredPDFParser(
        use_vlm=use_vlm,
        vlm_provider=vlm_provider,
        vlm_api_key=vlm_api_key or None,
        layout_model_name=layout_model_name,
        dpi=int(dpi),
        min_score=float(min_score),
        ocr_lang=ocr_lang,
        ocr_psm=int(ocr_psm),
        ocr_oem=int(ocr_oem),
        ocr_extra_config=ocr_extra_config or "",
        box_separator=box_separator or "\n",
    )

    parser.parse(str(input_pdf))

    outputs_root = Path("outputs")
    out_dir = outputs_root / Path(pdf_file).stem
    if not out_dir.exists():
        candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
        out_dir = candidates[0] if candidates else outputs_root

    md_file = next(out_dir.glob("*.md"), None)
    md_preview = None
    if md_file and md_file.exists():
        try:
            with md_file.open("r", encoding="utf-8", errors="ignore") as f:
                md_preview = f.read(5000)
        except Exception:
            md_preview = None

    gallery_items, file_paths, zip_path = _gather_outputs(out_dir)
    return (f"Completed. Results in: {out_dir}", md_preview, gallery_items, file_paths, zip_path)


def run_extract(
    pdf_file: str,
    target: str,
    use_vlm: bool,
    vlm_provider: str,
    vlm_api_key: str,
    layout_model_name: str,
    dpi: int,
    min_score: float,
) -> Tuple[str, List[tuple[str, str]], List[str], str]:
    if not pdf_file:
        return ("No file provided.", [], [], "")

    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    input_pdf = tmp_dir / "input.pdf"
    shutil.copy2(pdf_file, input_pdf)

    parser = ChartTablePDFParser(
        extract_charts=(target in ("charts", "both")),
        extract_tables=(target in ("tables", "both")),
        use_vlm=use_vlm,
        vlm_provider=vlm_provider,
        vlm_api_key=vlm_api_key or None,
        layout_model_name=layout_model_name,
        dpi=int(dpi),
        min_score=float(min_score),
    )

    output_base = Path("outputs")
    parser.parse(str(input_pdf), str(output_base))

    outputs_root = output_base
    out_dir = outputs_root / Path(pdf_file).stem
    if not out_dir.exists():
        if outputs_root.exists():
            candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
            out_dir = candidates[0] if candidates else outputs_root
        else:
            outputs_root.mkdir(parents=True, exist_ok=True)
            out_dir = outputs_root

    gallery_items, file_paths, zip_path = _gather_outputs(out_dir)
    return (f"Completed. Results in: {out_dir}", gallery_items, file_paths, zip_path)


THEME = gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")

CUSTOM_CSS = """
.gradio-container {max-width: 100% !important; padding-left: 24px; padding-right: 24px}
.container {max-width: 100% !important}
.app {max-width: 100% !important}
.header {margin-bottom: 8px}
.subtitle {color: var(--body-text-color-subdued)}
.card {border:1px solid var(--border-color); border-radius:12px; padding:8px}
.status-ok {color: var(--color-success)}
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Doctra - Document Parser", theme=THEME, css=CUSTOM_CSS) as demo:
        gr.Markdown(
            """
<div class="header">
  <h2 style="margin:0">Doctra — Document Parser</h2>
  <div class="subtitle">Parse PDFs, extract tables/charts, preview markdown, and download outputs.</div>
</div>
            """
        )

        with gr.Tab("Full Parse"):
            with gr.Row():
                pdf = gr.File(file_types=[".pdf"], label="PDF")
                use_vlm = gr.Checkbox(label="Use VLM (optional)", value=False)
                vlm_provider = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
                vlm_api_key = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")

            with gr.Accordion("Advanced", open=False):
                with gr.Row():
                    layout_model = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                    dpi = gr.Slider(100, 400, value=200, step=10, label="DPI")
                    min_score = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")
                with gr.Row():
                    ocr_lang = gr.Textbox(value="eng", label="OCR Language")
                    ocr_psm = gr.Slider(0, 13, value=4, step=1, label="Tesseract PSM")
                    ocr_oem = gr.Slider(0, 3, value=3, step=1, label="Tesseract OEM")
                with gr.Row():
                    ocr_config = gr.Textbox(value="", label="Extra OCR config")
                    box_sep = gr.Textbox(value="\n", label="Box separator")

            run_btn = gr.Button("▶ Run Full Parse", variant="primary")
            status = gr.Textbox(label="Status", elem_classes=["status-ok"])
            md_preview = gr.Markdown(label="Markdown preview (truncated)")
            gallery = gr.Gallery(label="Extracted images (tables/charts/figures)", columns=4, height=420, preview=True)
            files_out = gr.Files(label="Download individual output files")
            zip_out = gr.File(label="Download all outputs (ZIP)")

            run_btn.click(
                fn=lambda f, a, b, c, d, e, g, h, i, j, k, l: run_full_parse(
                    f.name if f else "",
                    a,
                    b,
                    c,
                    d,
                    e,
                    g,
                    h,
                    i,
                    j,
                    k,
                    l,
                ),
                inputs=[pdf, use_vlm, vlm_provider, vlm_api_key, layout_model, dpi, min_score, ocr_lang, ocr_psm, ocr_oem, ocr_config, box_sep],
                outputs=[status, md_preview, gallery, files_out, zip_out],
            )

        with gr.Tab("Extract Tables/Charts"):
            with gr.Row():
                pdf_e = gr.File(file_types=[".pdf"], label="PDF")
                target = gr.Dropdown(["tables", "charts", "both"], value="both", label="Target")
                use_vlm_e = gr.Checkbox(label="Use VLM (optional)", value=False)
                vlm_provider_e = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
                vlm_api_key_e = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")
            with gr.Accordion("Advanced", open=False):
                with gr.Row():
                    layout_model_e = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                    dpi_e = gr.Slider(100, 400, value=200, step=10, label="DPI")
                    min_score_e = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")

            run_btn_e = gr.Button("▶ Run Extraction", variant="primary")
            status_e = gr.Textbox(label="Status")
            gallery_e = gr.Gallery(label="Extracted images", columns=4, height=420, preview=True)
            files_out_e = gr.Files(label="Download individual output files")
            zip_out_e = gr.File(label="Download all outputs (ZIP)")

            run_btn_e.click(
                fn=lambda f, t, a, b, c, d, e, g: run_extract(
                    f.name if f else "",
                    t,
                    a,
                    b,
                    c,
                    d,
                    e,
                    g,
                ),
                inputs=[pdf_e, target, use_vlm_e, vlm_provider_e, vlm_api_key_e, layout_model_e, dpi_e, min_score_e],
                outputs=[status_e, gallery_e, files_out_e, zip_out_e],
            )

        gr.Markdown(
            """
<div class="card">
  <b>Tips</b>
  <ul>
    <li>On Spaces, set a secret <code>VLM_API_KEY</code> to enable VLM features.</li>
    <li>Outputs are saved under <code>outputs/&lt;pdf_stem&gt;/</code>.</li>
  </ul>
</div>
            """
        )

    return demo


def launch_ui(server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False):
    demo = build_demo()
    demo.launch(server_name=server_name, server_port=server_port, share=share)


