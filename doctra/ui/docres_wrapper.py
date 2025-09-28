"""
DocRes wrapper for Gradio UI context

This module provides a wrapper around DocResEngine that handles
path issues when running in Gradio UI context.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Union
import numpy as np

from doctra.engines.image_restoration.docres_engine import DocResEngine


class DocResUIWrapper:
    """
    Wrapper for DocResEngine that handles path issues in Gradio UI context
    """
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the DocRes wrapper
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.device = device
        self._docres = None
        self._setup_model_paths()
    
    def _setup_model_paths(self):
        """Setup model paths to work in Gradio context"""
        try:
            # Initialize DocRes to download models
            self._docres = DocResEngine(device=self.device)
            
            # Get the actual model paths
            mbd_path = self._docres.mbd_path
            model_path = self._docres.model_path
            
            # Get DocRes directory
            current_dir = Path(__file__).parent.parent
            docres_dir = current_dir / "third_party" / "docres"
            
            # Create expected directory structure
            expected_mbd_dir = docres_dir / "data" / "MBD" / "checkpoint"
            expected_model_dir = docres_dir / "checkpoints"
            
            expected_mbd_dir.mkdir(parents=True, exist_ok=True)
            expected_model_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy model files to expected locations if they don't exist
            expected_mbd_path = expected_mbd_dir / "mbd.pkl"
            expected_model_path = expected_model_dir / "docres.pkl"
            
            if not expected_mbd_path.exists() and Path(mbd_path).exists():
                shutil.copy2(mbd_path, expected_mbd_path)
            
            if not expected_model_path.exists() and Path(model_path).exists():
                shutil.copy2(model_path, expected_model_path)
                
        except Exception as e:
            print(f"⚠️ DocRes setup warning: {e}")
            # Continue anyway, the original paths might work
    
    def restore_pdf(self, pdf_path: str, output_path: str, task: str = "appearance", dpi: int = 200) -> str:
        """
        Restore a PDF using DocRes with proper path handling
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path to output enhanced PDF
            task: Restoration task
            dpi: DPI for processing
            
        Returns:
            Path to enhanced PDF
        """
        if self._docres is None:
            raise RuntimeError("DocRes not properly initialized")
        
        try:
            # Use the original DocRes method
            return self._docres.restore_pdf(pdf_path, output_path, task, dpi)
        except Exception as e:
            # If it fails due to path issues, try to fix them and retry once
            if "No such file or directory" in str(e) and "mbd.pkl" in str(e):
                print("🔧 Attempting to fix DocRes model paths...")
                self._setup_model_paths()
                return self._docres.restore_pdf(pdf_path, output_path, task, dpi)
            else:
                raise e
    
    def restore_image(self, image: Union[str, np.ndarray], task: str = "appearance") -> tuple:
        """
        Restore a single image using DocRes
        
        Args:
            image: Image path or numpy array
            task: Restoration task
            
        Returns:
            Tuple of (restored_image, metadata)
        """
        if self._docres is None:
            raise RuntimeError("DocRes not properly initialized")
        
        try:
            return self._docres.restore_image(image, task)
        except Exception as e:
            # If it fails due to path issues, try to fix them and retry once
            if "No such file or directory" in str(e) and "mbd.pkl" in str(e):
                print("🔧 Attempting to fix DocRes model paths...")
                self._setup_model_paths()
                return self._docres.restore_image(image, task)
            else:
                raise e
