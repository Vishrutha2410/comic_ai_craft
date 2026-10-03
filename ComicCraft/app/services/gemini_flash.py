import json
import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline, PromptRequest


def _client():
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def _generate_with_retry(client, model, prompt):
    """
    Generate Gemini content with retries for temporary 503 errors.
    """

    delays = [2, 5, 10]

    for attempt in range(len(delays) + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

        except Exception as exc:
            error_text = str(exc)

            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt == len(delays):
                raise RuntimeError(
                    "Gemini is currently unavailable after multiple retries. "
                    "Please try generating the comic again in a few minutes."
                ) from exc

            time.sleep(delays[attempt])


def generate_outline(request: PromptRequest) -> ComicOutline:
    settings = get_settings()
    client = _client()

    prompt = f"""
Create a 5-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "Panel title",
      "scene_description": "Description of what happens in the panel",
      "image_prompt": "Detailed prompt for generating the panel image"
    }}
  ]
}}

The panels array MUST contain exactly 5 panels.

panel_number must be:
1, 2, 3, 4, 5.
"""

    response = _generate_with_retry(
        client,
        settings.gemini_outline_model,
        prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini returned invalid JSON: {response.text}"
        ) from exc

    return ComicOutline.model_validate(data)