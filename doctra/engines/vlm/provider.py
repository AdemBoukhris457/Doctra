from __future__ import annotations

# --- keep these imports to match your snippet style ---
import io
import PIL
import openai
import outlines
from pydantic import BaseModel
from google.genai import Client
from outlines.inputs import Image
from anthropic import Anthropic
# ------------------------------------------------------

def make_model(
    vlm_provider: str | None = "gemini",
    vlm_model: str | None = None,
    *,
    api_key: str | None = None,
):
    """
    Build a callable Outlines model for VLM processing.
    
    Creates an Outlines model instance configured for Gemini, OpenAI, Anthropic, or OpenRouter
    providers. Only one backend is active at a time, with Gemini as the default.

    :param vlm_provider: VLM provider to use ("gemini", "openai", or "anthropic", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param api_key: API key for the VLM provider (required for all providers)
    :return: Configured Outlines model instance
    :raises ValueError: If provider is unsupported or API key is missing
    """
    vlm_provider = (vlm_provider or "gemini").lower()
    
    # Set default models if not provided
    if vlm_model is None:
        if vlm_provider == "gemini":
            vlm_model = "gemini-2.5-pro"
        elif vlm_provider == "openai":
            vlm_model = "gpt-5"
        elif vlm_provider == "anthropic":
            vlm_model = "claude-opus-4-1"
        elif vlm_provider == "openrouter":
            vlm_model = "x-ai/grok-4"

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

    if vlm_provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic provider requires api_key to be passed to make_model(...).")
        # Create the Anthropic client and model (exactly like your snippet)
        client = Anthropic(api_key=api_key)
        return outlines.from_anthropic(
            client,
            vlm_model,
        )

    if vlm_provider == "openrouter":
        if not api_key:
            raise ValueError("OpenRouter provider requires api_key to be passed to make_model(...).")
        # Create the Anthropic client and model (exactly like your snippet)
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return outlines.from_openai(
            client,
            vlm_model
        )

    raise ValueError(f"Unsupported provider: {vlm_provider}. Use 'gemini', 'openai', or 'anthropic'.")