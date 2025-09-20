"""
DocRes Image Restoration Engine

This module provides a wrapper around the DocRes inference functionality
for easy integration with Doctra's document processing pipeline.

DocRes supports 5 restoration tasks:
- dewarping: Corrects document perspective distortion
- deshadowing: Removes shadows from documents  
- appearance: General appearance enhancement
- deblurring: Reduces blur in document images
- binarization: Converts to clean black/white text
- end2end: Pipeline combining dewarping → deshadowing → appearance
"""

import os
import sys
import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Union, List, Tuple, Optional, Dict, Any

# Hugging Face Hub imports
try:
    from huggingface_hub import hf_hub_download
    from huggingface_hub.utils import disable_progress_bars
    disable_progress_bars()
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False

# Add DocRes to path and change to DocRes directory for relative imports
current_dir = Path(__file__).parent
docres_dir = current_dir.parent.parent / "third_party" / "docres"
sys.path.insert(0, str(docres_dir))

# Store original working directory
original_cwd = os.getcwd()

try:
    # Change to DocRes directory for relative imports to work
    os.chdir(str(docres_dir))
    
    # Now import DocRes modules (they use relative imports)
    from inference import (
        model_init, inference_one_im, dewarping, deshadowing, 
        appearance, deblurring, binarization
    )
    from utils import convert_state_dict
    from models import restormer_arch
    from data.preprocess.crop_merge_image import stride_integral
    from data.MBD.infer import net1_net2_infer_single_im
    
    DOCRES_AVAILABLE = True
except ImportError as e:
    DOCRES_AVAILABLE = False
    # Don't print warning here, let the user handle it when they try to use it
finally:
    # Always restore original working directory
    os.chdir(original_cwd)


def load_docres_weights_from_hf():
    """
    Load DocRes model weights from Hugging Face Hub.
    
    Returns:
        Tuple of (mbd_path, docres_path) - paths to downloaded model files
    """
    if not HF_HUB_AVAILABLE:
        raise ImportError(
            "huggingface_hub is required for downloading models from Hugging Face. "
            "Install with: pip install huggingface_hub"
        )
    
    print("🔄 Downloading DocRes models from Hugging Face Hub...")
    
    try:
        # Download DocRes main model
        print("   📥 Downloading DocRes main model...")
        _ = hf_hub_download("DaVinciCode/doctra-docres-main", filename="config.json")
        docres_path = hf_hub_download("DaVinciCode/doctra-docres-main", filename="docres.pkl")
        
        # Download MBD model
        print("   📥 Downloading MBD model...")
        _ = hf_hub_download("DaVinciCode/doctra-docres-mbd", filename="config.json")
        mbd_path = hf_hub_download("DaVinciCode/doctra-docres-mbd", filename="mbd.pkl")
        
        # Verify file sizes
        docres_size = Path(docres_path).stat().st_size
        mbd_size = Path(mbd_path).stat().st_size
        
        print(f"   ✅ DocRes model: {docres_size:,} bytes")
        print(f"   ✅ MBD model: {mbd_size:,} bytes")
        
        return mbd_path, docres_path
        
    except Exception as e:
        raise RuntimeError(f"Failed to download models from Hugging Face: {e}")


def get_model_paths(use_huggingface: bool = True, model_path: Optional[str] = None, mbd_path: Optional[str] = None):
    """
    Get model paths, either from Hugging Face or local files.
    
    Args:
        use_huggingface: Whether to use Hugging Face Hub for model loading
        model_path: Local path to DocRes model (if not using Hugging Face)
        mbd_path: Local path to MBD model (if not using Hugging Face)
        
    Returns:
        Tuple of (mbd_path, docres_path)
    """
    if use_huggingface and HF_HUB_AVAILABLE:
        try:
            return load_docres_weights_from_hf()
        except Exception as e:
            print(f"⚠️ Hugging Face download failed: {e}")
            print("   Falling back to local model files...")
            use_huggingface = False
    
    if not use_huggingface:
        # Use local model files
        if model_path is None:
            model_path = docres_dir / "checkpoints" / "docres.pkl"
        if mbd_path is None:
            mbd_path = docres_dir / "data" / "MBD" / "checkpoint" / "mbd.pkl"
        
        return str(mbd_path), str(model_path)
    
    raise RuntimeError("Cannot load models: Hugging Face Hub not available and no local paths provided")


class DocResEngine:
    """
    DocRes Image Restoration Engine
    
    A wrapper around DocRes inference functionality for easy integration
    with Doctra's document processing pipeline.
    """
    
    SUPPORTED_TASKS = [
        'dewarping', 'deshadowing', 'appearance', 
        'deblurring', 'binarization', 'end2end'
    ]
    
    def __init__(
        self, 
        device: Optional[str] = None,
        use_half_precision: bool = True,
        use_huggingface: bool = True,
        model_path: Optional[str] = None,
        mbd_path: Optional[str] = None
    ):
        """
        Initialize DocRes Engine
        
        Args:
            device: Device to run on ('cuda', 'cpu', or None for auto-detect)
            use_half_precision: Whether to use half precision for inference
            use_huggingface: Whether to download models from Hugging Face Hub (default: True)
            model_path: Path to DocRes model checkpoint (used if use_huggingface=False)
            mbd_path: Path to MBD model checkpoint (used if use_huggingface=False)
        """
        if not DOCRES_AVAILABLE:
            raise ImportError(
                "DocRes is not available. Please install the missing dependencies:\n"
                "pip install scikit-image>=0.19.3\n\n"
                "The DocRes module is already included in this library, but requires "
                "scikit-image for image processing operations."
            )
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            requested_device = torch.device(device)
            # Check if the requested device is available
            if requested_device.type == 'cuda' and not torch.cuda.is_available():
                print(f"Warning: CUDA requested but not available. Falling back to CPU.")
                self.device = torch.device('cpu')
            else:
                self.device = requested_device
        
        self.use_half_precision = use_half_precision
        self.use_huggingface = use_huggingface
        
        # Get model paths (from Hugging Face or local files)
        try:
            self.mbd_path, self.model_path = get_model_paths(
                use_huggingface=use_huggingface,
                model_path=model_path,
                mbd_path=mbd_path
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get model paths: {e}")
        
        # Verify model files exist
        if not os.path.exists(self.model_path):
            if use_huggingface:
                raise FileNotFoundError(
                    f"DocRes model not found at {self.model_path}. "
                    f"This may indicate a Hugging Face download failure. "
                    f"Please check your internet connection and try again."
                )
            else:
                raise FileNotFoundError(
                    f"DocRes model not found at {self.model_path}. "
                    f"Local models have been removed. Use use_huggingface=True to download from Hugging Face Hub."
                )
        
        if not os.path.exists(self.mbd_path):
            if use_huggingface:
                raise FileNotFoundError(
                    f"MBD model not found at {self.mbd_path}. "
                    f"This may indicate a Hugging Face download failure. "
                    f"Please check your internet connection and try again."
                )
            else:
                raise FileNotFoundError(
                    f"MBD model not found at {self.mbd_path}. "
                    f"Local models have been removed. Use use_huggingface=True to download from Hugging Face Hub."
                )
        
        # Initialize model
        self._model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the DocRes model"""
        try:
            # Create model architecture
            self._model = restormer_arch.Restormer( 
                inp_channels=6, 
                out_channels=3, 
                dim=48,
                num_blocks=[2,3,3,4], 
                num_refinement_blocks=4,
                heads=[1,2,4,8],
                ffn_expansion_factor=2.66,
                bias=False,
                LayerNorm_type='WithBias',
                dual_pixel_task=True        
            )
            
            # Load model weights - always load to CPU first, then move to target device
            state = convert_state_dict(torch.load(self.model_path, map_location='cpu')['model_state'])
            
            self._model.load_state_dict(state)
            self._model.eval()
            self._model = self._model.to(self.device)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DocRes model: {e}")
    
    def restore_image(
        self, 
        image: Union[str, np.ndarray], 
        task: str = "appearance",
        save_prompts: bool = False
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Restore a single image using DocRes
        
        Args:
            image: Path to image file or numpy array
            task: Restoration task to perform
            save_prompts: Whether to save intermediate prompts
            
        Returns:
            Tuple of (restored_image, metadata)
        """
        if task not in self.SUPPORTED_TASKS:
            raise ValueError(f"Unsupported task: {task}. Supported tasks: {self.SUPPORTED_TASKS}")
        
        # Load image if path provided
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img_array = cv2.imread(image)
            if img_array is None:
                raise ValueError(f"Could not load image: {image}")
        else:
            img_array = image.copy()
        
        original_shape = img_array.shape
        
        try:
            # Handle end2end pipeline
            if task == "end2end":
                return self._run_end2end_pipeline(img_array, save_prompts)
            
            # Run single task
            restored_img, metadata = self._run_single_task(img_array, task, save_prompts)
            
            metadata.update({
                'original_shape': original_shape,
                'restored_shape': restored_img.shape,
                'task': task,
                'device': str(self.device)
            })
            
            return restored_img, metadata
            
        except Exception as e:
            raise RuntimeError(f"Image restoration failed: {e}")
    
    def _run_single_task(self, img_array: np.ndarray, task: str, save_prompts: bool) -> Tuple[np.ndarray, Dict]:
        """Run a single restoration task"""
        import tempfile
        import time
        
        # Create temporary file for inference
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            cv2.imwrite(tmp_path, img_array)
        
        try:
            # Change to DocRes directory for inference to work properly
            original_cwd = os.getcwd()
            os.chdir(str(docres_dir))
            
            # Set global DEVICE variable that DocRes inference expects
            import torch
            import inference  # Import the inference module to set its global DEVICE
            inference.DEVICE = self.device
            
            try:
                # Run inference
                prompt1, prompt2, prompt3, restored = inference_one_im(self._model, tmp_path, task)
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
            
            metadata = {
                'task': task,
                'device': str(self.device)
            }
            
            if save_prompts:
                metadata['prompts'] = {
                    'prompt1': prompt1,
                    'prompt2': prompt2, 
                    'prompt3': prompt3
                }
            
            return restored, metadata
            
        finally:
            # Clean up temporary file with retry for Windows
            try:
                # Wait a bit for file handles to be released
                time.sleep(0.1)
                os.unlink(tmp_path)
            except PermissionError:
                # If still locked, try again after a longer wait
                time.sleep(1)
                try:
                    os.unlink(tmp_path)
                except PermissionError:
                    # If still failing, just leave it - it will be cleaned up by the OS
                    pass
    
    def _run_end2end_pipeline(self, img_array: np.ndarray, save_prompts: bool) -> Tuple[np.ndarray, Dict]:
        """Run the end2end pipeline: dewarping → deshadowing → appearance"""
        import tempfile
        import time
        
        intermediate_steps = {}
        
        # Change to DocRes directory for inference to work properly
        original_cwd = os.getcwd()
        os.chdir(str(docres_dir))
        
        # Set global DEVICE variable that DocRes inference expects
        import torch
        import inference  # Import the inference module to set its global DEVICE
        inference.DEVICE = self.device
        
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Step 1: Dewarping
                step1_path = os.path.join(tmp_dir, "step1.jpg")
                cv2.imwrite(step1_path, img_array)
                
                prompt1, prompt2, prompt3, dewarped = inference_one_im(self._model, step1_path, "dewarping")
                intermediate_steps['dewarped'] = dewarped
                
                # Step 2: Deshadowing
                step2_path = os.path.join(tmp_dir, "step2.jpg")
                cv2.imwrite(step2_path, dewarped)
                
                prompt1, prompt2, prompt3, deshadowed = inference_one_im(self._model, step2_path, "deshadowing")
                intermediate_steps['deshadowed'] = deshadowed
                
                # Step 3: Appearance
                step3_path = os.path.join(tmp_dir, "step3.jpg")
                cv2.imwrite(step3_path, deshadowed)
                
                prompt1, prompt2, prompt3, final = inference_one_im(self._model, step3_path, "appearance")
                
                metadata = {
                    'task': 'end2end',
                    'device': str(self.device),
                    'intermediate_steps': intermediate_steps
                }
                
                if save_prompts:
                    metadata['prompts'] = {
                        'prompt1': prompt1,
                        'prompt2': prompt2,
                        'prompt3': prompt3
                    }
                
                return final, metadata
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
    
    def batch_restore(
        self, 
        images: List[Union[str, np.ndarray]], 
        task: str = "appearance",
        save_prompts: bool = False
    ) -> List[Tuple[Optional[np.ndarray], Dict[str, Any]]]:
        """
        Restore multiple images in batch
        
        Args:
            images: List of image paths or numpy arrays
            task: Restoration task to perform
            save_prompts: Whether to save intermediate prompts
            
        Returns:
            List of (restored_image, metadata) tuples
        """
        results = []
        
        for i, image in enumerate(images):
            try:
                restored_img, metadata = self.restore_image(image, task, save_prompts)
                results.append((restored_img, metadata))
            except Exception as e:
                # Return None for failed images with error metadata
                error_metadata = {
                    'error': str(e),
                    'task': task,
                    'device': str(self.device),
                    'image_index': i
                }
                results.append((None, error_metadata))
        
        return results
    
    def get_supported_tasks(self) -> List[str]:
        """Get list of supported restoration tasks"""
        return self.SUPPORTED_TASKS.copy()
    
    def is_available(self) -> bool:
        """Check if DocRes is available and properly configured"""
        return DOCRES_AVAILABLE and self._model is not None
    
    def restore_pdf(
        self, 
        pdf_path: str, 
        output_path: str | None = None,
        task: str = "appearance",
        dpi: int = 200
    ) -> str | None:
        """
        Restore an entire PDF document using DocRes
        
        Args:
            pdf_path: Path to the input PDF file
            output_path: Path for the enhanced PDF (if None, auto-generates)
            task: DocRes restoration task (default: "appearance")
            dpi: DPI for PDF rendering (default: 200)
            
        Returns:
            Path to the enhanced PDF or None if failed
        """
        try:
            from PIL import Image
            import numpy as np
            from doctra.utils.pdf_io import render_pdf_to_images
            
            # Generate output path if not provided
            if output_path is None:
                pdf_dir = os.path.dirname(pdf_path)
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = os.path.join(pdf_dir, f"{pdf_name}_enhanced.pdf")
            
            print(f"🔄 Processing PDF with DocRes: {os.path.basename(pdf_path)}")
            
            # Render all pages to images
            pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=dpi)]
            
            if not pil_pages:
                print("❌ No pages found in PDF")
                return None
            
            print(f"📄 Found {len(pil_pages)} pages, processing with DocRes...")
            
            # Process each page with DocRes
            enhanced_pages = []
            for i, page_img in enumerate(pil_pages):
                try:
                    # Convert PIL to numpy array
                    img_array = np.array(page_img)
                    
                    # Apply DocRes restoration
                    restored_img, _ = self.restore_image(img_array, task)
                    
                    # Convert back to PIL Image
                    enhanced_page = Image.fromarray(restored_img)
                    enhanced_pages.append(enhanced_page)
                    
                    print(f"  ✅ Page {i+1}/{len(pil_pages)} processed")
                    
                except Exception as e:
                    print(f"  ⚠️ Page {i+1} processing failed: {e}, using original")
                    enhanced_pages.append(page_img)
            
            # Create enhanced PDF
            if enhanced_pages:
                enhanced_pages[0].save(
                    output_path,
                    "PDF",
                    resolution=100.0,
                    save_all=True,
                    append_images=enhanced_pages[1:] if len(enhanced_pages) > 1 else []
                )
                
                print(f"✅ Enhanced PDF saved: {output_path}")
                return output_path
            else:
                print("❌ No pages to save")
                return None
                
        except ImportError as e:
            print(f"❌ Required dependencies not available: {e}")
            print("Install with: pip install PyMuPDF")
            return None
        except Exception as e:
            print(f"❌ Error processing PDF with DocRes: {e}")
            return None