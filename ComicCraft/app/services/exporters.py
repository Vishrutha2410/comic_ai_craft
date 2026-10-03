from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "static"
EXPORT_DIR = STATIC_DIR / "exports"
PANEL_DIR = STATIC_DIR / "panels"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _pdf_safe_text(text: str) -> str:
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def _image_path(image_url: str) -> Path:
    parsed = urlparse(image_url)
    path = parsed.path.lstrip("/")

    candidate = BASE_DIR / path

    if not candidate.exists():
        raise FileNotFoundError(
            f"Generated image not found: {candidate}"
        )

    return candidate


def save_pdf(title: str, layout: list) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    output = EXPORT_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:
        pdf.add_page()

        content_x = 15
        content_w = 180

        # -------------------------
        # Panel title
        # -------------------------

        pdf.set_font("Helvetica", "B", 18)
        pdf.set_xy(content_x, 15)

        pdf.multi_cell(
            content_w,
            10,
            _pdf_safe_text(
                f"Panel {panel.panel_number}: {panel.title}"
            )
        )

        # -------------------------
        # Panel image
        # -------------------------

        image_path = _image_path(panel.image_url)

        pdf.image(
            str(image_path),
            x=content_x,
            y=35,
            w=content_w,
            h=120
        )

        # Start text below image
        current_y = 160

        # -------------------------
        # Scene description
        # -------------------------

        pdf.set_xy(content_x, current_y)

        pdf.set_font("Helvetica", "I", 10)

        pdf.multi_cell(
            content_w,
            6,
            _pdf_safe_text(panel.scene_description)
        )

        # Get current Y position after scene description
        current_y = pdf.get_y() + 3

        # -------------------------
        # Narration heading
        # -------------------------

        pdf.set_xy(content_x, current_y)

        pdf.set_font("Helvetica", "B", 11)

        pdf.multi_cell(
            content_w,
            6,
            "Narration"
        )

        # Reset X position after heading
        current_y = pdf.get_y()

        # -------------------------
        # Narration text
        # -------------------------

        pdf.set_xy(content_x, current_y)

        pdf.set_font("Helvetica", "", 11)

        pdf.multi_cell(
            content_w,
            6,
            _pdf_safe_text(panel.narration)
        )

        # Add spacing
        current_y = pdf.get_y() + 2

        # -------------------------
        # Dialogue heading
        # -------------------------

        pdf.set_xy(content_x, current_y)

        pdf.set_font("Helvetica", "B", 11)

        pdf.multi_cell(
            content_w,
            6,
            "Dialogue"
        )

        # Reset X position after heading
        current_y = pdf.get_y()

        # -------------------------
        # Dialogue text
        # -------------------------

        pdf.set_xy(content_x, current_y)

        pdf.set_font("Helvetica", "", 11)

        pdf.multi_cell(
            content_w,
            6,
            _pdf_safe_text(panel.dialogue)
        )

    pdf.output(str(output))

    return f"/static/exports/{filename}"