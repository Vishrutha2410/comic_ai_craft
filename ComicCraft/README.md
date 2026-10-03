# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project documentation. It accepts a story prompt, character, setting, tone, and art style, then:

1. Generates a structured 5-panel outline with Gemini.
2. Expands the outline into narration and dialogue with Gemini.
3. Generates one illustration per panel through Hugging Face Inference Providers.
4. Builds a panel layout.
5. Exports the comic as a multi-page PDF.
6. Shows the result in a Jinja2 web UI.

## Architecture

Browser → FastAPI → Gemini outline → Gemini story → image generation → layout → PDF

## Important implementation note

The supplied document names Gemini 1.5 Flash/Pro and `google-generativeai`. Those examples are legacy. This implementation uses Google's current `google-genai` SDK. Model names are environment variables, so you can use any currently available Gemini text models.

For images, the default is Hugging Face Inference Providers rather than downloading a multi-GB diffusion checkpoint to the local PC. This makes the project much easier to run on a normal Windows laptop. `image_generator.py` still contains a local Diffusers/Stable-Diffusion backend if you have suitable GPU hardware.

## Requirements

- Python 3.11 or 3.12 recommended
- Internet connection
- Gemini API key
- Hugging Face token with inference permissions for remote image generation

## VS Code setup — Windows

```powershell
cd ComicCraft

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
```

Open `.env` and add:

```env
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```

Then run:

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Linux/macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## API test

The Swagger UI is available at `/docs`.

Example JSON request:

```json
{
  "story_prompt": "A brave fox discovers a glowing door in an enchanted forest.",
  "character_name": "Luna",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

POST it to:

`/generate-comic/json`

## Image backend

Default:

```env
IMAGE_BACKEND=hf
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell
```

The HF backend uses `huggingface_hub.InferenceClient`.

For a local Diffusers installation, change:

```env
IMAGE_BACKEND=diffusers
DIFFUSION_MODEL=sd-legacy/stable-diffusion-v1-5
```

Local diffusion requires a compatible PyTorch installation and enough RAM/VRAM. It is not recommended on a normal integrated-GPU laptop.

## Testing without paid/remote image generation

Run:

```powershell
pytest -q
```

The test suite checks schemas, layout, filenames, and PDF creation without calling external AI services.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   └── templates/
│       ├── index.html
│       ├── comic_preview.html
│       └── export_success.html
├── static/
│   ├── css/style.css
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── tests/
│   └── test_core.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Copy `.env.example` to `.env` and add your Gemini key.

### Gemini model unavailable

Change `GEMINI_OUTLINE_MODEL` and/or `GEMINI_STORY_MODEL` in `.env` to a model available to your Google AI Studio account.

### Hugging Face image error

Check that `HF_TOKEN` is valid and has inference permissions. You can also change `HF_IMAGE_MODEL` to another text-to-image model available through Hugging Face Inference Providers.

### PDF generation error

The project uses `fpdf2` and an included Unicode-capable font is not required for the default English UI. If you add non-Latin narration and experience font issues, add a Unicode TTF font and configure `exporters.py`.

### Long generation time

A complete comic makes multiple AI calls. Image generation is normally the slowest stage. The UI shows a loading state while the server processes the request.

## Security

Never commit `.env` or API keys. `.gitignore` already excludes `.env`.

## Source alignment

The supplied documentation specifies FastAPI, Jinja2, Gemini Flash/Pro, Stable Diffusion/Diffusers, panel layout construction, PDF export, and the `/`, `/generate`, `/generate-comic/json`, `/test-image`, and `/export-success` routes. This implementation keeps those concepts while updating the SDK and making image generation practical for local development.
