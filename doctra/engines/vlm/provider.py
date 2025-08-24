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
    Build a callable Outlines model for VLM processing.
    
    Creates an Outlines model instance configured for either Gemini or OpenAI
    providers. Only one backend is active at a time, with Gemini as the default.

    :param provider: VLM provider to use ("gemini" or "openai", default: "gemini")
    :param api_key: API key for the VLM provider (required for Gemini)
    :param gemini_model: Gemini model name to use (default: "gemini-1.5-flash-latest")
    :param openai_model: OpenAI model name to use (default: "gpt-4o")
    :return: Configured Outlines model instance
    :raises ValueError: If provider is unsupported or API key is missing for Gemini
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