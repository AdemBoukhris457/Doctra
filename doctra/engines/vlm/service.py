from __future__ import annotations
import os
from outlines.inputs import Image

from ...utils.io_utils import get_image_from_local
from .outlines_types import Chart, Table
from .provider import make_model


class VLMStructuredExtractor:
    """
    Thin service around prompts + Outlines calls for structured data extraction.
    
    Provides a high-level interface for extracting structured data (charts and tables)
    from images using Vision Language Models (VLM) with Outlines for type safety.

    Usage:
        vlm = VLMStructuredExtractor(vlm_provider="gemini", api_key="YOUR_KEY", debug=True)
        chart = vlm.extract_chart("/abs/path/chart.jpg")
        table = vlm.extract_table("/abs/path/table.jpg")
    """

    def __init__(
        self,
        vlm_provider: str = "gemini",
        vlm_model: str | None = None,
        *,
        api_key: str | None = None,
        debug: bool = True,
    ):
        """
        Initialize the VLMStructuredExtractor with provider configuration.
        
        Sets up the VLM model and debug settings for structured data extraction
        from images.

        :param vlm_provider: VLM provider to use ("gemini" or "openai", default: "gemini")
        :param vlm_model: Model name to use (defaults to provider-specific defaults)
        :param api_key: API key for the VLM provider (required for both Gemini and OpenAI)
        :param debug: Whether to enable debug output for error handling (default: True)
        """
        self.model = make_model(
            vlm_provider,
            vlm_model,
            api_key=api_key,
        )
        self.debug = debug

    def _call(self, prompt_text: str, image_path: str, schema):
        """
        Common call: open/normalize image, convert to RGB, invoke model with schema.
        
        Internal method that handles the common workflow for VLM processing:
        loading the image, normalizing it, and calling the model with the provided
        prompt and schema.

        :param prompt_text: Text prompt to send to the VLM
        :param image_path: Path to the image file to process
        :param schema: Pydantic schema class for structured output
        :return: Structured data object matching the provided schema
        :raises Exception: If image processing or VLM call fails
        """
        try:
            # Normalize path and verify readability
            # (get_image_from_local already absolutizes & raises if missing)
            img = get_image_from_local(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")

            prompt = [prompt_text, Image(img)]
            return self.model(prompt, schema)
        except Exception as e:
            if self.debug:
                import traceback
                print(f"[VLM ERROR] while processing: {image_path}")
                traceback.print_exc()
                print(f"[VLM ERROR] type={type(e).__name__} msg={e}")
            # Re-raise so caller can handle/log too
            raise

    def extract_chart(self, image_path: str) -> Chart:
        """
        Extract structured chart data from an image.
        
        Uses VLM to analyze a chart image and extract the data in a structured
        format with title, headers, and rows.

        :param image_path: Path to the chart image file
        :return: Chart object containing extracted title, headers, and data rows
        :raises Exception: If image processing or VLM extraction fails
        """
        prompt_text = (
            "Convert the given chart into a table format with headers and rows. "
            "If the title is not present in the image, generate a suitable title. "
            "Ensure that the table represents the data from the chart accurately."
            "The number of columns in the headers must match the number of columns in each row."
        )
        return self._call(prompt_text, image_path, Chart)

    def extract_table(self, image_path: str) -> Table:
        """
        Extract structured table data from an image.
        
        Uses VLM to analyze a table image and extract the data in a structured
        format with title, headers, and rows.

        :param image_path: Path to the table image file
        :return: Table object containing extracted title, headers, and data rows
        :raises Exception: If image processing or VLM extraction fails
        """
        prompt_text = (
            "Extract the data from the given table in image format. "
            "Provide the headers and rows of the table, ensuring accuracy in the extraction. "
            "If the title is not present in the image, generate a suitable title."
            "The number of columns in the headers must match the number of columns in each row."
        )
        return self._call(prompt_text, image_path, Table)
