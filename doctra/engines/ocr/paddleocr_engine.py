from __future__ import annotations

import tempfile
import os
import contextlib
import logging
import warnings
from typing import Optional
from PIL import Image
from paddleocr import PaddleOCR


@contextlib.contextmanager
def silence():
    """Context manager to suppress stdout, stderr, and logging output."""
    # Store original logging levels
    original_levels = {}
    loggers_to_suppress = [
        'paddleocr', 'paddle', 'paddlex', 'paddlepaddle', 'ppocr',
        'transformers', 'huggingface_hub', 'urllib3', 'requests'
    ]
    
    # Suppress logging for various libraries
    for logger_name in loggers_to_suppress:
        logger = logging.getLogger(logger_name)
        original_levels[logger_name] = logger.level
        logger.setLevel(logging.CRITICAL)
    
    # Also suppress root logger
    root_logger = logging.getLogger()
    original_root_level = root_logger.level
    root_logger.setLevel(logging.CRITICAL)
    
    # Set environment variables to suppress PaddleOCR output
    original_env = {}
    env_vars_to_set = {
        'DISABLE_AUTO_LOGGING_CONFIG': '1',
        'PADDLE_LOG_LEVEL': '3',  # Only show fatal errors
        'GLOG_minloglevel': '3',  # Suppress glog output
        'TF_CPP_MIN_LOG_LEVEL': '3'  # Suppress TensorFlow output
    }
    
    for key, value in env_vars_to_set.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    # Temporarily disable all logging handlers
    original_handlers = {}
    for logger_name in loggers_to_suppress + ['']:
        logger = logging.getLogger(logger_name)
        original_handlers[logger_name] = logger.handlers[:]
        logger.handlers.clear()
    
    try:
        with open(os.devnull, "w") as devnull, \
             contextlib.redirect_stdout(devnull), \
             contextlib.redirect_stderr(devnull):
            yield
    finally:
        # Restore original logging levels
        for logger_name, level in original_levels.items():
            logging.getLogger(logger_name).setLevel(level)
        root_logger.setLevel(original_root_level)
        
        # Restore original handlers
        for logger_name, handlers in original_handlers.items():
            logger = logging.getLogger(logger_name)
            logger.handlers = handlers
        
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class PaddleOCREngine:
    """
    OCR engine using PaddleOCR with PP-OCRv5_server model.
    
    Accepts a cropped PIL image (e.g., a text block from layout detection)
    and returns raw text. Uses PaddleOCR's default PP-OCRv5_server model
    with configurable parameters.

    :param use_doc_orientation_classify: Enable document orientation classification (default: False)
    :param use_doc_unwarping: Enable text image rectification (default: False)
    :param use_textline_orientation: Enable text line orientation classification (default: False)
    :param device: Device to use for OCR ("cpu" or "gpu", default: "gpu")
    """

    def __init__(
        self,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
        use_textline_orientation: bool = False,
        device: str = "gpu",
    ):
        """
        Initialize the PaddleOCREngine with OCR configuration.
        
        Sets up the PaddleOCR instance with the specified parameters.
        The PP-OCRv5_server model is used by default in PaddleOCR.
        All output is suppressed during initialization to minimize console noise.

        :param use_doc_orientation_classify: Enable document orientation classification (default: False)
        :param use_doc_unwarping: Enable text image rectification (default: False)
        :param use_textline_orientation: Enable text line orientation classification (default: False)
        :param device: Device to use for OCR ("cpu" or "gpu", default: "gpu")
        """
        # Suppress all output during PaddleOCR initialization
        with silence():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.ocr = PaddleOCR(
                    use_doc_orientation_classify=use_doc_orientation_classify,
                    use_doc_unwarping=use_doc_unwarping,
                    use_textline_orientation=use_textline_orientation,
                    device=device
                )

    def recognize(self, image: Image.Image) -> str:
        """
        Run OCR on a cropped PIL image and return extracted text.
        
        Performs text recognition on the provided image using PaddleOCR
        and returns the extracted text. The `rec_texts` from the result
        are joined with newlines.

        :param image: PIL Image object to perform OCR on
        :return: Extracted text string with lines joined by newlines
        :raises TypeError: If the input is not a PIL Image object
        """
        if not isinstance(image, Image.Image):
            raise TypeError("PaddleOCREngine expects a PIL.Image.Image as input.")

        # Save PIL image to temporary file since PaddleOCR.predict() expects a file path
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            image.save(tmp_path, format='PNG')
        
        try:
            # Run OCR prediction with suppressed output
            with silence():
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result = self.ocr.predict(tmp_path)
            
            # Extract rec_texts from the result
            # The result is a list with one dictionary containing the OCR results
            if result and len(result) > 0:
                ocr_result = result[0]
                rec_texts = ocr_result.get('rec_texts', [])
                
                # Join all text elements with newlines
                text = '\n'.join(rec_texts) if rec_texts else ''
                return text.strip()
            
            return ""
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

