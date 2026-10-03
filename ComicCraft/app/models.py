from typing import List
from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=3, max_length=2000)
    character_name: str = Field(min_length=1, max_length=100)
    setting: str = Field(min_length=1, max_length=150)
    tone: str = Field(min_length=1, max_length=80)
    art_style: str = Field(min_length=1, max_length=100)

    @field_validator("*")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class ComicPanel(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[ComicPanel]

    @field_validator("panels")
    @classmethod
    def exactly_five(cls, value):
        if len(value) != 5:
            raise ValueError("ComicCraft requires exactly 5 panels.")
        return value


class StoryPanel(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    narration: str
    dialogue: str


class ComicStory(BaseModel):
    panels: List[StoryPanel]

    @field_validator("panels")
    @classmethod
    def exactly_five(cls, value):
        if len(value) != 5:
            raise ValueError("ComicCraft requires exactly 5 story panels.")
        return value


class LayoutPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    image_url: str
    narration: str
    dialogue: str


class ComicResponse(BaseModel):
    title: str
    panels: List[LayoutPanel]
    pdf_url: str
