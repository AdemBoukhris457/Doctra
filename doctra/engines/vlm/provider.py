from __future__ import annotations

import io
import json
import os
import PIL
import re
import openai
import outlines
from pydantic import BaseModel
from google.genai import Client
from outlines.inputs import Image
from anthropic import Anthropic
import ollama

def make_model(
    vlm_provider: str | None = "gemini",
    vlm_model: str | None = None,
    *,
    api_key: str | None = None,
):
    """
    Build a callable Outlines model for VLM processing.
    
    Creates an Outlines model instance configured for Gemini, OpenAI, Anthropic, OpenRouter, Qianfan, or Ollama
    providers. Only one backend is active at a time, with Gemini as the default.

    :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", "openrouter", "qianfan", or "ollama", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param api_key: API key for the VLM provider (required for all providers except Ollama)
    :return: Configured Outlines model instance
    :raises ValueError: If provider is unsupported or API key is missing
    """
    vlm_provider = (vlm_provider or "gemini").lower()
    
    if vlm_model is None:
        if vlm_provider == "gemini":
            vlm_model = "gemini-2.5-pro"
        elif vlm_provider == "openai":
            vlm_model = "gpt-5"
        elif vlm_provider == "anthropic":
            vlm_model = "claude-opus-4-1"
        elif vlm_provider == "openrouter":
            vlm_model = "x-ai/grok-4"
        elif vlm_provider == "qianfan":
            vlm_model = "ernie-4.5-turbo-vl-32k"
        elif vlm_provider == "ollama":
            vlm_model = "llava:latest"

    if vlm_provider == "gemini":
        if not api_key:
            raise ValueError("Gemini provider requires api_key to be passed to make_model(...).")
        return outlines.from_gemini(
            Client(api_key=api_key),
            vlm_model,
        )

    if vlm_provider == "openai":
        if not api_key:
            raise ValueError("OpenAI provider requires api_key to be passed to make_model(...).")
        return outlines.from_openai(
            openai.OpenAI(api_key=api_key),
            vlm_model,
        )

    if vlm_provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic provider requires api_key to be passed to make_model(...).")
        client = Anthropic(api_key=api_key)
        return outlines.from_anthropic(
            client,
            vlm_model,
        )

    if vlm_provider == "openrouter":
        if not api_key:
            raise ValueError("OpenRouter provider requires api_key to be passed to make_model(...).")
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        return outlines.from_openai(
            client,
            vlm_model
        )

    if vlm_provider == "qianfan":
        if not api_key:
            raise ValueError("Qianfan provider requires api_key to be passed to make_model(...).")
        client = openai.OpenAI(
            base_url="https://qianfan.baidubce.com/v2",
            api_key=api_key,
        )
        return outlines.from_openai(
            client,
            vlm_model
        )

    if vlm_provider == "ollama":
        # Ollama doesn't use Outlines, so we return a custom wrapper
        return OllamaModelWrapper(vlm_model)

    raise ValueError(f"Unsupported provider: {vlm_provider}. Use 'gemini', 'openai', 'anthropic', 'openrouter', 'qianfan', or 'ollama'.")


class OllamaModelWrapper:
    """
    Wrapper class to make Ollama compatible with the Outlines interface.
    
    This class provides a callable interface that matches the Outlines model
    signature, allowing Ollama to be used as a drop-in replacement for other
    VLM providers in the Doctra framework.
    """
    
    def __init__(self, model_name: str):
        """
        Initialize the Ollama model wrapper.
        
        :param model_name: Name of the Ollama model to use (e.g., "llava:latest", "gemma3:latest")
        """
        self.model_name = model_name
    
    def __call__(self, prompt, schema):
        """
        Call the Ollama model with the given prompt and schema.
        
        :param prompt: List containing [text_prompt, Image] - the text prompt and PIL Image
        :param schema: Pydantic model class for structured output
        :return: Structured data object matching the provided schema
        """
        if not isinstance(prompt, list) or len(prompt) != 2:
            raise ValueError("Prompt must be a list with [text, image] format")
        
        text_prompt, image = prompt
        
        # Convert Image object to bytes for Ollama
        # The Image object from Outlines might be a PIL Image or a different type
        try:
            # Try to get the PIL Image from the Outlines Image object
            if hasattr(image, 'image'):
                pil_image = image.image
            elif hasattr(image, '_image'):
                pil_image = image._image
            else:
                pil_image = image
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='JPEG')
            img_bytes = img_buffer.getvalue()
        except Exception as e:
            # Try alternative approach - save the image directly to a file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                try:
                    if hasattr(image, 'image'):
                        image.image.save(tmp_file.name, format='JPEG')
                    else:
                        image.save(tmp_file.name, format='JPEG')
                    with open(tmp_file.name, 'rb') as f:
                        img_bytes = f.read()
                    os.unlink(tmp_file.name)
                except Exception as e2:
                    raise
        
        # Save image to temporary file for Ollama
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(img_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Call Ollama with the image and prompt
            response = ollama.chat(
                messages=[{
                    "role": "user",
                    "content": text_prompt,
                    "images": [tmp_path],
                }],
                model=self.model_name,
                format=schema.model_json_schema(),  # Use Pydantic schema for structured output
            )
            
            # Handle different response formats
            if 'message' in response and 'content' in response['message']:
                content = response['message']['content']
            elif 'response' in response:
                content = response['response']
            else:
                content = str(response)
            
            # Try to parse as JSON
            try:
                result = schema.model_validate_json(content)
                return result
            except Exception as json_error:
                # Try to extract data manually from text response
                return self._extract_from_text_response(content, schema)
            
        except Exception as e:
            # Return a default structure to prevent crashes
            return schema(
                title="Extraction Failed",
                description="Failed to extract data from image",
                headers=["Error"],
                rows=[["Could not process image"]]
            )
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def _extract_from_text_response(self, content: str, schema):
        """
        Extract structured data from text response when JSON parsing fails.
        
        :param content: Text response from Ollama
        :param schema: Pydantic schema class
        :return: Structured data object
        """
        try:
            # Try to find JSON in the response
            
            # Look for JSON-like content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return schema.model_validate_json(json_str)
            
            # If no JSON found, create a basic structure
            lines = content.split('\n')
            title = "Extracted Data"
            description = content[:300] if len(content) > 300 else content
            
            # Try to extract headers and rows from text
            headers = ["Column 1", "Column 2"]  # Default headers
            rows = [["Data 1", "Data 2"]]  # Default row
            
            # Look for table-like patterns
            for line in lines:
                if '|' in line and len(line.split('|')) > 2:
                    # This looks like a table row
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if len(cells) > 1:
                        rows.append(cells)
            
            return schema(
                title=title,
                description=description,
                headers=headers,
                rows=rows
            )
            
        except Exception as e:
            # Return minimal structure
            return schema(
                title="Text Extraction",
                description=content[:300] if len(content) > 300 else content,
                headers=["Content"],
                rows=[[content[:100]]]
            )