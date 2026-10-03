import json
import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline, ComicStory, PromptRequest


def _client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
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


def generate_story(
    request: PromptRequest,
    outline: ComicOutline,
) -> ComicStory:

    settings = get_settings()

    outline_text = outline.model_dump_json(indent=2)

    prompt = f"""
You are the story writer for ComicCraft.

Write narration and dialogue for exactly the 5 panels below.

Original user information:
Story prompt: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Panel outline:
{outline_text}

Requirements:
- Preserve the panel order and events.
- Keep character names consistent.
- Narration should be concise enough for a comic panel.
- Dialogue should sound natural and match the requested tone.
- Do not invent additional panels.
- Return exactly five story panels.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "narration": "Short narration for panel 1",
      "dialogue": "Dialogue for panel 1"
    }}
  ]
}}

The panels array MUST contain exactly 5 panels.
panel_number must be 1, 2, 3, 4, and 5.
"""

    client = _client()

    response = _generate_with_retry(
        client,
        settings.gemini_story_model,
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

    return ComicStory.model_validate(data)