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
    vlm_provider: str | None = "gemini",
    vlm_model: str | None = None,
    *,
    api_key: str | None = None,
):
    """
    Build a callable Outlines model for VLM processing.
    
    Creates an Outlines model instance configured for either Gemini or OpenAI
    providers. Only one backend is active at a time, with Gemini as the default.

    :param vlm_provider: VLM provider to use ("gemini" or "openai", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param api_key: API key for the VLM provider (required for both Gemini and OpenAI)
    :return: Configured Outlines model instance
    :raises ValueError: If provider is unsupported or API key is missing
    """
    vlm_provider = (vlm_provider or "gemini").lower()
    
    # Set default models if not provided
    if vlm_model is None:
        if vlm_provider == "gemini":
            vlm_model = "gemini-1.5-flash-latest"
        elif vlm_provider == "openai":
            vlm_model = "gpt-4o"

    if vlm_provider == "gemini":
        if not api_key:
            raise ValueError("Gemini provider requires api_key to be passed to make_model(...).")
        # Create the model (exactly like your snippet)
        return outlines.from_gemini(
            Client(api_key=api_key),
            vlm_model,
        )

    if vlm_provider == "openai":
        if not api_key:
            raise ValueError("OpenAI provider requires api_key to be passed to make_model(...).")
        # this part is for the openai models (exactly like your snippet)
        return outlines.from_openai(
            openai.OpenAI(api_key=api_key),
            vlm_model,
        )

    raise ValueError(f"Unsupported provider: {vlm_provider}. Use 'gemini' or 'openai'.")