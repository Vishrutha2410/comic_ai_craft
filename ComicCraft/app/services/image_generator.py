from pathlib import Path
import re

from PIL import Image, ImageDraw

from app.config import get_settings


BASE_DIR = Path(__file__).resolve().parents[2]
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(text: str, max_length: int = 100) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    return text.strip("_")[:max_length]


def _generate_placeholder(prompt: str, panel_number: int) -> str:
    """
    Development fallback image.
    """

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt)}.png"
    )

    output = PANEL_DIR / filename

    image = Image.new(
        "RGB",
        (1024, 768),
        "lightgray"
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (40, 40),
        "ComicCraft",
        fill="black"
    )

    draw.text(
        (40, 100),
        prompt[:180],
        fill="black"
    )

    image.save(output)

    return f"/static/panels/{filename}"


def _generate_huggingface(prompt: str, panel_number: int) -> str:
    """
    Generate an actual AI image using Hugging Face Inference Providers.
    """

    from huggingface_hub import InferenceClient

    settings = get_settings()

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is missing. Add your Hugging Face token to .env."
        )

    client = InferenceClient(
        api_key=settings.hf_token
    )

    clean_prompt = f"""
Create a cinematic digital illustration based on this scene:

{prompt}

VISUAL STYLE:
- polished cinematic digital artwork
- detailed character design
- expressive characters
- atmospheric environment
- dramatic lighting
- strong composition
- consistent visual storytelling

STRICTLY VISUAL:
- artwork only
- no speech bubbles
- no dialogue bubbles
- no captions
- no subtitles
- no comic-panel borders
- no graphic overlays
- no written language
- no readable words
- no letters
- no numbers
- no labels
- no logos
- no UI overlays

Show the scene through characters, expressions, environment, objects,
lighting, and composition only.
"""
    image = client.text_to_image(
    prompt=clean_prompt,
    model=settings.hf_image_model,
)

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt)}.png"
    )

    output = PANEL_DIR / filename

    image.save(output)

    return f"/static/panels/{filename}"


def generate_image(prompt: str, panel_number: int) -> str:
    """
    Generate a comic panel image.

    Supported backends:
    - placeholder
    - hf
    """

    settings = get_settings()

    backend = settings.image_backend.lower()

    if backend == "placeholder":
        return _generate_placeholder(
            prompt,
            panel_number
        )

    if backend == "hf":
        return _generate_huggingface(
            prompt,
            panel_number
        )

    raise RuntimeError(
        f"Unsupported IMAGE_BACKEND: {settings.image_backend}"
    )