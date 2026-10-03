from pathlib import Path

from PIL import Image

from app.models import ComicOutline, ComicPanel, ComicStory, StoryPanel, PromptRequest
from app.services.exporters import save_pdf
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def sample_request():
    return PromptRequest(
        story_prompt="A fox finds a magical door.",
        character_name="Luna",
        setting="forest",
        tone="dramatic",
        art_style="comic book",
    )


def sample_outline():
    return ComicOutline(
        panels=[
            ComicPanel(
                panel_number=i,
                title=f"Panel {i}",
                scene_description=f"Scene {i}",
                image_prompt=f"Comic scene {i}",
            )
            for i in range(1, 6)
        ]
    )


def sample_story():
    return ComicStory(
        panels=[
            StoryPanel(
                panel_number=i,
                narration=f"Narration {i}",
                dialogue=f"Dialogue {i}",
            )
            for i in range(1, 6)
        ]
    )


def test_prompt_schema():
    request = sample_request()
    assert request.character_name == "Luna"


def test_layout_builder():
    outline = sample_outline()
    story = sample_story()
    urls = [f"/static/panels/panel_{i}.png" for i in range(1, 6)]

    layout = build_comic_layout(outline, story, urls)

    assert len(layout) == 5
    assert layout[0].panel_number == 1
    assert layout[4].dialogue == "Dialogue 5"


def test_placeholder_image_generation(monkeypatch):
    monkeypatch.setenv("IMAGE_BACKEND", "placeholder")
    from app.config import get_settings
    get_settings.cache_clear()

    url = generate_image("A fox in a forest", 1)
    assert url.startswith("/static/panels/")
    assert (Path("static") / "panels").exists()


def test_pdf_export(monkeypatch):
    monkeypatch.setenv("IMAGE_BACKEND", "placeholder")
    from app.config import get_settings
    get_settings.cache_clear()

    image_urls = []
    for i in range(1, 6):
        image_urls.append(generate_image(f"test panel {i}", i))

    outline = sample_outline()
    story = sample_story()
    layout = build_comic_layout(outline, story, image_urls)

    pdf_url = save_pdf("Test Comic", layout)
    pdf_path = Path(pdf_url.lstrip("/"))
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
