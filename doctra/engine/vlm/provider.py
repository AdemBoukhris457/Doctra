# doctra/engines/vlm/provider.py
from __future__ import annotations

# --- keep these imports to match your snippet style ---
import io
import PIL
import openai
import outlines
from pydantic import BaseModel
from google.genai import Client
from outlines.inputs import Image
# ------------------------------------------------------

def make_model(
    provider: str | None = "gemini",
    *,
    api_key: str | None = None,
    gemini_model: str = "gemini-1.5-flash-latest",
    openai_model: str = "gpt-4o",
):
    """
    Build a callable Outlines model exactly in your snippet's style.
    One backend is active at a time.

    - Gemini: requires api_key passed here → Client(api_key=api_key)
    - OpenAI: uses openai.OpenAI() (reads OPENAI_API_KEY from environment)
    """
    provider = (provider or "gemini").lower()

    if provider == "gemini":
        if not api_key:
            raise ValueError("Gemini provider requires api_key to be passed to make_model(...).")
        # Create the model (exactly like your snippet)
        return outlines.from_gemini(
            Client(api_key=api_key),
            gemini_model,
        )

    if provider == "openai":
        # this part is for the openai models (exactly like your snippet)
        # return outlines.from_openai(
        #     openai.OpenAI(),
        #     "gpt-4o"
        # )
        return outlines.from_openai(
            openai.OpenAI(),
            openai_model,
        )

    raise ValueError(f"Unsupported provider: {provider}. Use 'gemini' or 'openai'.")