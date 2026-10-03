from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models import ComicResponse, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


def _generate_comic(request_data: PromptRequest):
    outline = generate_outline(request_data)
    story = generate_story(request_data, outline)

    image_urls = []
    for panel in outline.panels:
        visual_prompt = (
            f"{panel.image_prompt}. "
            "Consistent character appearance, cinematic composition, "
            "clear subject, polished comic illustration, no text or speech bubbles."
        )
        image_urls.append(generate_image(visual_prompt, panel.panel_number))

    layout = build_comic_layout(outline, story, image_urls)

    title = f"{request_data.character_name}'s Comic"
    pdf_url = save_pdf(title, layout)

    return title, layout, pdf_url


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        title, layout, pdf_url = _generate_comic(data)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": title,
                "layout": layout,
                "pdf_url": pdf_url,
            },
        )

    except Exception as exc:
        print("=" * 70)
        print("GENERATION ERROR")
        print(f"Type: {type(exc).__name__}")
        print(f"Error: {exc}")
        print("=" * 70)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )

@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest) -> ComicResponse:
    try:
        title, layout, pdf_url = _generate_comic(data)
        return ComicResponse(
            title=title,
            panels=layout,
            pdf_url=pdf_url,
        )
    except Exception as e:
        print(f"GENERATION ERROR: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {type(e).__name__}: {e}"
    )


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        image_url = generate_image(prompt, 1)
        return {"success": True, "image_url": image_url}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_url: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_url": pdf_url},
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
