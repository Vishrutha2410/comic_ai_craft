from app.models import ComicOutline, ComicStory, LayoutPanel


def build_comic_layout(
    outline: ComicOutline,
    story: ComicStory,
    image_urls: list[str],
) -> list[LayoutPanel]:
    story_by_panel = {panel.panel_number: panel for panel in story.panels}

    layout = []
    for panel in outline.panels:
        story_panel = story_by_panel.get(panel.panel_number)
        if story_panel is None:
            raise ValueError(f"Missing story data for panel {panel.panel_number}.")

        image_url = image_urls[panel.panel_number - 1]

        layout.append(
            LayoutPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                image_prompt=panel.image_prompt,
                image_url=image_url,
                narration=story_panel.narration,
                dialogue=story_panel.dialogue,
            )
        )

    return layout
