"""
UniTable Inference Script

This script performs table structure recognition on table images using the UniTable model.
It extracts table structure, detects cell bounding boxes, and recognizes cell content.

Usage:
    python inference.py <image_path> [--output-dir OUTPUT_DIR] [--device DEVICE] [--visualize]

Note: If you encounter import errors related to torchtext, try clearing Python cache:
    python -B inference.py <image_path>  (runs without bytecode cache)
    Or delete __pycache__ directories in src/
"""

import argparse
import re
import time
import warnings
import urllib.request
import sys
from pathlib import Path
from typing import Sequence, Optional, Tuple, Union

import torch
import tokenizers as tk
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import patches
from torchvision import transforms
from torch import nn, Tensor
from functools import partial
from bs4 import BeautifulSoup as bs

# Import model components (avoid importing from src.trainer to prevent torchtext dependency)
from src.model import EncoderDecoder, ImgLinearBackbone, Encoder, Decoder
from src.utils import (
    subsequent_mask,
    pred_token_within_range,
    greedy_sampling,
    bbox_str_to_token_list,
    cell_str_to_token_list,
    html_str_to_token_list,
    build_table_from_html_and_cell,
    html_table_template,
)
# Import vocab constants directly to avoid torchtext dependency
# NOTE: Do NOT import from src.trainer.utils as it requires torchtext
from src.vocab.constant import HTML_TOKENS, TASK_TOKENS, RESERVED_TOKENS, BBOX_TOKENS

# Define constants needed for inference (matching src.trainer.utils)
VALID_HTML_TOKEN = ["<eos>"] + HTML_TOKENS
INVALID_CELL_TOKEN = (
    ["<sos>", "<pad>", "<empty>", "<sep>"] + TASK_TOKENS + RESERVED_TOKENS
)
VALID_BBOX_TOKEN = ["<eos>"] + BBOX_TOKENS

warnings.filterwarnings("ignore")


# Model configuration for UniTable large model
D_MODEL = 768
PATCH_SIZE = 16
NHEAD = 12
DROPOUT = 0.2

# Model file names
MODEL_FILE_NAMES = [
    "unitable_large_structure.pt",
    "unitable_large_bbox.pt",
    "unitable_large_content.pt",
]

# HuggingFace repository for UniTable model weights
HUGGINGFACE_REPO = "poloclub/UniTable"

# Try to import huggingface_hub for better downloads
try:
    from huggingface_hub import hf_hub_download
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    # Fallback to direct URL download
    HUGGINGFACE_BASE_URL = "https://huggingface.co/poloclub/UniTable/resolve/main"


def download_file_from_hf(model_name: str, dest_path: Path) -> None:
    """
    Download a file from HuggingFace Hub using huggingface_hub library.
    
    Args:
        model_name: Name of the model file to download
        dest_path: Destination file path
    """
    if not HF_HUB_AVAILABLE:
        raise ImportError(
            "huggingface_hub is not installed. Install with: pip install huggingface_hub\n"
            "Or the model files can be downloaded manually."
        )
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use huggingface_hub to download (handles caching, resumable downloads, etc.)
        # Download to HuggingFace cache first, then copy to our desired location
        downloaded_path = hf_hub_download(
            repo_id=HUGGINGFACE_REPO,
            filename=model_name,
            cache_dir=None,  # Use default cache
        )
        
        # Copy from cache to desired location
        downloaded_path_obj = Path(downloaded_path)
        if downloaded_path_obj.exists():
            import shutil
            if dest_path.exists():
                dest_path.unlink()
            shutil.copy2(downloaded_path_obj, dest_path)
        else:
            raise RuntimeError(f"Downloaded file not found: {downloaded_path}")
    except Exception as e:
        print(f"✗ Error downloading {model_name}: {e}")
        raise


def download_file_fallback(url: str, dest_path: Path) -> None:
    """
    Fallback download method using direct URL (when huggingface_hub is not available).
    
    Args:
        url: URL to download from
        dest_path: Destination file path
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100) if total_size > 0 else 0
            bar_length = 40
            filled = int(bar_length * downloaded / total_size) if total_size > 0 else 0
            bar = '=' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest_path, reporthook=show_progress)
        print()  # New line after progress bar
    except Exception as e:
        print(f"\n✗ Error downloading {dest_path.name}: {e}")
        raise


def is_valid_pytorch_model(model_path: Path) -> bool:
    """
    Check if a PyTorch model file is valid and not corrupted.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True if the model file is valid, False otherwise
    """
    if not model_path.exists():
        return False
    
    try:
        # Try to load the model file and check if it's a valid zip archive
        # PyTorch models are zip files internally
        import zipfile
        with zipfile.ZipFile(model_path, 'r') as zip_ref:
            # Check if we can read the central directory
            zip_ref.testzip()
        return True
    except (zipfile.BadZipFile, RuntimeError, Exception):
        return False


def ensure_model_weights(
    model_dir: Union[str, Path],
    download_missing: bool = True
) -> bool:
    """
    Check if all required model weights exist and download them if missing.
    Also validates existing files and re-downloads corrupted ones.
    
    Args:
        model_dir: Directory containing model weights
        download_missing: Whether to download missing weights automatically
        
    Returns:
        True if all weights exist and are valid, False otherwise
    """
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    missing_models = []
    corrupted_models = []
    
    for model_name in MODEL_FILE_NAMES:
        model_path = model_dir / model_name
        if not model_path.exists():
            missing_models.append(model_name)
        elif not is_valid_pytorch_model(model_path):
            print(f"⚠️  Detected corrupted model file: {model_name}")
            corrupted_models.append(model_name)
            # Delete corrupted file
            try:
                model_path.unlink()
                print(f"   Deleted corrupted file, will re-download.")
            except Exception as e:
                print(f"   Warning: Could not delete corrupted file: {e}")
    
    models_to_download = missing_models + corrupted_models
    
    if not models_to_download:
        return True
    
    if not download_missing:
        return False
    
    if len(models_to_download) > 0:
        if HF_HUB_AVAILABLE:
            print(f"Downloading {len(models_to_download)} model weight(s) from HuggingFace Hub...")
        else:
            print(f"Downloading {len(models_to_download)} model weight(s) from HuggingFace...")
            print("⚠️  Note: For better reliability, install huggingface_hub: pip install huggingface_hub")
    
    for model_name in models_to_download:
        dest_path = model_dir / model_name
        try:
            if HF_HUB_AVAILABLE:
                # Use HuggingFace Hub library (better handling, caching, resumable downloads)
                download_file_from_hf(model_name, dest_path)
            else:
                # Fallback to direct URL download
                url = f"{HUGGINGFACE_BASE_URL}/{model_name}"
                download_file_fallback(url, dest_path)
            
            # Verify the downloaded file
            if not is_valid_pytorch_model(dest_path):
                raise RuntimeError(f"Downloaded file {model_name} appears to be corrupted")
        except Exception as e:
            print(f"✗ Failed to download/verify {model_name}: {e}")
            # Delete the corrupted download if it exists
            if dest_path.exists():
                try:
                    dest_path.unlink()
                except:
                    pass
            raise
    
    return True


def autoregressive_decode(
    model: EncoderDecoder,
    image: Tensor,
    prefix: Sequence[int],
    max_decode_len: int,
    eos_id: int,
    token_whitelist: Optional[Sequence[int]] = None,
    token_blacklist: Optional[Sequence[int]] = None,
    device: torch.device = None,
) -> Tensor:
    """
    Perform autoregressive decoding.

    Args:
        model: The EncoderDecoder model
        image: Input image tensor
        prefix: Starting token sequence
        max_decode_len: Maximum decoding length
        eos_id: End-of-sequence token ID
        token_whitelist: Allowed token IDs
        token_blacklist: Disallowed token IDs
        device: Device to run inference on

    Returns:
        Decoded token sequence
    """
    if device is None:
        device = image.device

    model.eval()
    with torch.no_grad():
        memory = model.encode(image)
        context = torch.tensor(prefix, dtype=torch.int32).repeat(image.shape[0], 1).to(device)

    for _ in range(max_decode_len):
        eos_flag = [eos_id in k for k in context]
        if all(eos_flag):
            break

        with torch.no_grad():
            causal_mask = subsequent_mask(context.shape[1]).to(device)
            logits = model.decode(
                memory, context, tgt_mask=causal_mask, tgt_padding_mask=None
            )
            logits = model.generator(logits)[:, -1, :]

        logits = pred_token_within_range(
            logits.detach(),
            white_list=token_whitelist,
            black_list=token_blacklist,
        )

        next_probs, next_tokens = greedy_sampling(logits)
        context = torch.cat([context, next_tokens], dim=1)
    return context


def load_vocab_and_model(
    vocab_path: Union[str, Path],
    max_seq_len: int,
    model_weights: Union[str, Path],
    device: torch.device,
) -> Tuple[tk.Tokenizer, EncoderDecoder]:
    """
    Load vocabulary and model.

    Args:
        vocab_path: Path to vocabulary file
        max_seq_len: Maximum sequence length
        model_weights: Path to model weights file
        device: Device to load model on

    Returns:
        Tuple of (vocab, model)
    """
    vocab = tk.Tokenizer.from_file(str(vocab_path))
    
    backbone = ImgLinearBackbone(d_model=D_MODEL, patch_size=PATCH_SIZE)
    encoder = Encoder(
        d_model=D_MODEL,
        nhead=NHEAD,
        dropout=DROPOUT,
        activation="gelu",
        norm_first=True,
        nlayer=12,
        ff_ratio=4,
    )
    decoder = Decoder(
        d_model=D_MODEL,
        nhead=NHEAD,
        dropout=DROPOUT,
        activation="gelu",
        norm_first=True,
        nlayer=4,
        ff_ratio=4,
    )
    
    model = EncoderDecoder(
        backbone=backbone,
        encoder=encoder,
        decoder=decoder,
        vocab_size=vocab.get_vocab_size(),
        d_model=D_MODEL,
        padding_idx=vocab.token_to_id("<pad>"),
        max_seq_len=max_seq_len,
        dropout=DROPOUT,
        norm_layer=partial(nn.LayerNorm, eps=1e-6)
    )

    try:
        model.load_state_dict(torch.load(str(model_weights), map_location="cpu"))
    except (RuntimeError, Exception) as e:
        error_msg = str(e)
        if "failed finding central directory" in error_msg or "PytorchStreamReader" in error_msg:
            model_path = Path(model_weights)
            print(f"\n❌ Error: Model file {model_path.name} is corrupted.")
            print(f"   File path: {model_path}")
            print(f"   Please delete the corrupted file and re-run to download it again.")
            print(f"   Or manually download from: {HUGGINGFACE_BASE_URL}/{model_path.name}")
            raise RuntimeError(f"Corrupted model file: {model_path.name}. Please delete and re-download.") from e
        else:
            raise
    model = model.to(device)
    return vocab, model


def image_to_tensor(image: Image.Image, size: Tuple[int, int], device: torch.device) -> Tensor:
    """
    Convert PIL Image to tensor with preprocessing.

    Args:
        image: PIL Image
        size: Target size (width, height)
        device: Device to place tensor on

    Returns:
        Preprocessed image tensor
    """
    T = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.86597056, 0.88463002, 0.87491087],
            std=[0.20686628, 0.18201602, 0.18485524]
        )
    ])
    image_tensor = T(image)
    image_tensor = image_tensor.to(device).unsqueeze(0)
    return image_tensor


def rescale_bbox(
    bbox: Sequence[Sequence[float]],
    src: Tuple[int, int],
    tgt: Tuple[int, int]
) -> Sequence[Sequence[float]]:
    """
    Rescale bounding boxes from source size to target size.

    Args:
        bbox: List of bounding boxes [xmin, ymin, xmax, ymax]
        src: Source image size (width, height)
        tgt: Target image size (width, height)

    Returns:
        Rescaled bounding boxes
    """
    assert len(src) == len(tgt) == 2
    ratio = [tgt[0] / src[0], tgt[1] / src[1]] * 2
    bbox = [[int(round(i * j)) for i, j in zip(entry, ratio)] for entry in bbox]
    return bbox


def recognize_table(
    table_image_path: Union[str, Path],
    model_dir: Union[str, Path] = "./experiments/unitable_weights",
    vocab_dir: Union[str, Path] = "./vocab",
    device: Optional[torch.device] = None,
    visualize: bool = False,
    output_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """
    Recognize and extract a table from an image.

    Args:
        table_image_path: Path to the image file containing the table
        model_dir: Directory containing model weights
        vocab_dir: Directory containing vocabulary files
        device: Device to run inference on (default: cuda if available, else cpu)
        visualize: Whether to display visualizations (requires output_dir if True)
        output_dir: Directory to save visualization outputs (optional, only used with visualize=True)

    Returns:
        Dictionary containing:
            - 'html': Final HTML table code
            - 'bboxes': List of detected bounding boxes
            - 'cells': List of recognized cell contents
            - 'execution_time': Execution time in seconds
    """
    start_time = time.time()

    # Set device
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Convert paths
    table_image_path = Path(table_image_path)
    model_dir = Path(model_dir)
    vocab_dir = Path(vocab_dir)

    # Ensure model weights exist (download if missing)
    if not ensure_model_weights(model_dir, download_missing=True):
        raise FileNotFoundError(
            f"Model weights not found in {model_dir} and download failed.\n"
            f"Please download model weights manually from HuggingFace: "
            f"https://huggingface.co/poloclub/UniTable/tree/main"
        )

    # Load tabular image
    image = Image.open(table_image_path).convert("RGB")
    image_size = image.size

    # Only create output directory if output_dir is explicitly provided and visualize is enabled
    if visualize and output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Display original image if visualize is True
    if visualize and output_dir is not None:
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.imshow(image)
        ax.set_title("Original Table Image")
        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(output_dir / "original_image.png", dpi=150, bbox_inches="tight")
        try:
            plt.show()
        except Exception:
            # If display is not available (e.g., headless server), just save the figure
            print(f"Saved original image visualization to: {output_dir / 'original_image.png'}")
        plt.close()

    # ---------------------------------------------------
    # 1. Table structure extraction
    vocab_table_structure_extraction, model_table_structure_extraction = load_vocab_and_model(
        vocab_path=vocab_dir / "vocab_html.json",
        max_seq_len=784,
        model_weights=model_dir / MODEL_FILE_NAMES[0],
        device=device,
    )

    image_tensor = image_to_tensor(image, size=(448, 448), device=device)

    pred_html = autoregressive_decode(
        model=model_table_structure_extraction,
        image=image_tensor,
        prefix=[vocab_table_structure_extraction.token_to_id("[html]")],
        max_decode_len=512,
        eos_id=vocab_table_structure_extraction.token_to_id("<eos>"),
        token_whitelist=[vocab_table_structure_extraction.token_to_id(i) for i in VALID_HTML_TOKEN],
        token_blacklist=None,
        device=device,
    )

    # Convert token id to token text
    pred_html = pred_html.detach().cpu().numpy()[0]
    pred_html = vocab_table_structure_extraction.decode(pred_html, skip_special_tokens=False)
    pred_html = html_str_to_token_list(pred_html)

    # ---------------------------------------------------
    # 2. Table cell bbox detection
    vocab_cell_box_det, model_cell_box_det = load_vocab_and_model(
        vocab_path=vocab_dir / "vocab_bbox.json",
        max_seq_len=1024,
        model_weights=model_dir / MODEL_FILE_NAMES[1],
        device=device,
    )

    image_tensor = image_to_tensor(image, size=(448, 448), device=device)

    pred_bbox = autoregressive_decode(
        model=model_cell_box_det,
        image=image_tensor,
        prefix=[vocab_cell_box_det.token_to_id("[bbox]")],
        max_decode_len=1024,
        eos_id=vocab_cell_box_det.token_to_id("<eos>"),
        token_whitelist=[vocab_cell_box_det.token_to_id(i) for i in VALID_BBOX_TOKEN[:449]],
        token_blacklist=None,
        device=device,
    )

    # Convert token id to token text
    pred_bbox = pred_bbox.detach().cpu().numpy()[0]
    pred_bbox = vocab_cell_box_det.decode(pred_bbox, skip_special_tokens=False)

    # Visualize detected bbox
    pred_bbox = bbox_str_to_token_list(pred_bbox)
    pred_bbox = rescale_bbox(pred_bbox, src=(448, 448), tgt=image_size)

    # Display image with detected bounding boxes if visualize is True
    if visualize and output_dir is not None:
        fig, ax = plt.subplots(figsize=(12, 10))
        for i in pred_bbox:
            rect = patches.Rectangle(
                i[:2], i[2] - i[0], i[3] - i[1],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect)
        ax.set_title("Detected Table Cell Bboxes")
        ax.set_axis_off()
        ax.imshow(image)
        plt.tight_layout()
        plt.savefig(output_dir / "detected_bboxes.png", dpi=150, bbox_inches="tight")
        try:
            plt.show()
        except Exception:
            # If display is not available (e.g., headless server), just save the figure
            print(f"Saved bbox visualization to: {output_dir / 'detected_bboxes.png'}")
        plt.close()

    # ---------------------------------------------------
    # 3. Table cell content recognition
    vocab, model = load_vocab_and_model(
        vocab_path=vocab_dir / "vocab_cell_6k.json",
        max_seq_len=200,
        model_weights=model_dir / MODEL_FILE_NAMES[2],
        device=device,
    )

    # Cell image cropping and transformation
    image_tensor = [image_to_tensor(image.crop(bbox), size=(112, 448), device=device) for bbox in pred_bbox]
    image_tensor = torch.cat(image_tensor, dim=0)

    # Inference
    pred_cell = autoregressive_decode(
        model=model,
        image=image_tensor,
        prefix=[vocab.token_to_id("[cell]")],
        max_decode_len=200,
        eos_id=vocab.token_to_id("<eos>"),
        token_whitelist=None,
        token_blacklist=[vocab.token_to_id(i) for i in INVALID_CELL_TOKEN],
        device=device,
    )

    # Convert token id to token text
    pred_cell = pred_cell.detach().cpu().numpy()
    pred_cell = vocab.decode_batch(pred_cell, skip_special_tokens=False)
    pred_cell = [cell_str_to_token_list(i) for i in pred_cell]
    pred_cell = [re.sub(r'(\d).\s+(\d)', r'\1.\2', i) for i in pred_cell]

    # ---------------------------------------------------
    # 4. Combine the table structure and cell content
    pred_code = build_table_from_html_and_cell(pred_html, pred_cell)
    pred_code = "".join(pred_code)
    pred_code = html_table_template(pred_code)

    # Display the final HTML table if visualize is True
    if visualize:
        soup = bs(pred_code, "html.parser")
        table_code = soup.prettify()
        try:
            from IPython.display import display, HTML
            display(HTML(table_code))
        except ImportError:
            # If not in a Jupyter environment, just print the HTML
            print("\nFinal HTML Table:")
            print("=" * 80)
            print(table_code)
            print("=" * 80)

    # HTML output is returned in the result dictionary, not saved to files

    end_time = time.time()
    execution_time = end_time - start_time

    return {
        "html": pred_code,
        "bboxes": pred_bbox,
        "cells": pred_cell,
        "execution_time": execution_time,
    }


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="UniTable Table Structure Recognition Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inference.py image.jpg
  python inference.py image.jpg --output-dir ./output --visualize
  python inference.py image.jpg --device cpu
        """
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the image file containing the table"
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default="./experiments/unitable_weights",
        help="Directory containing model weights (default: ./experiments/unitable_weights)"
    )
    parser.add_argument(
        "--vocab-dir",
        type=str,
        default="./vocab",
        help="Directory containing vocabulary files (default: ./vocab)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Directory to save outputs (default: ./output)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to run inference on (cuda/cpu). Default: auto-detect"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Display visualizations during inference"
    )

    args = parser.parse_args()

    # Parse device
    if args.device:
        device = torch.device(args.device)
    else:
        device = None  # Will auto-detect

    # Run inference
    try:
        result = recognize_table(
            table_image_path=args.image_path,
            model_dir=args.model_dir,
            vocab_dir=args.vocab_dir,
            device=device,
            visualize=args.visualize,
            output_dir=args.output_dir,
        )
        print("\n✓ Inference completed successfully!")
        return result
    except Exception as e:
        print(f"\n✗ Error during inference: {e}")
        raise


if __name__ == "__main__":
    main()

