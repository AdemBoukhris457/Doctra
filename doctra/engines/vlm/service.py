from __future__ import annotations
import os
from outlines.inputs import Image

from ...utils.io_utils import get_image_from_local
from .outlines_types import Chart, Table
from .provider import make_model


class VLMStructuredExtractor:
    """
    Thin service around your prompts + Outlines calls.

    Usage:
        vlm = VLMStructuredExtractor(provider="gemini", api_key="YOUR_KEY", debug=True)
        chart = vlm.extract_chart("/abs/path/chart.jpg")
        table = vlm.extract_table("/abs/path/table.jpg")
    """

    def __init__(
        self,
        provider: str = "gemini",
        *,
        api_key: str | None = None,
        gemini_model: str = "gemini-1.5-flash-latest",
        openai_model: str = "gpt-4o",
        debug: bool = True,                      # <-- NEW
    ):
        self.model = make_model(
            provider,
            api_key=api_key,
            gemini_model=gemini_model,
            openai_model=openai_model,
        )
        self.debug = debug

    def _call(self, prompt_text: str, image_path: str, schema):
        """
        Common call: open/normalize image, convert to RGB, invoke model with schema.
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
        prompt_text = (
            "Convert the given chart into a table format with headers and rows. "
            "If the title is not present in the image, generate a suitable title. "
            "Ensure that the table represents the data from the chart accurately."
        )
        return self._call(prompt_text, image_path, Chart)

    def extract_table(self, image_path: str) -> Table:
        prompt_text = (
            "Extract the data from the given table in image format. "
            "Provide the headers and rows of the table, ensuring accuracy in the extraction. "
            "If the title is not present in the image, generate a suitable title."
        )
        return self._call(prompt_text, image_path, Table)
