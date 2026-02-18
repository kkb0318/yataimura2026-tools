"""QRコードをA4 PDFへ面付けして出力する。"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Literal

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

from .loader import QrItem

PAGE_W, PAGE_H = A4
CAPTION_H = 6 * mm
DEFAULT_CAPTION_FONT = "Helvetica"
JP_CAPTION_FONT = "HeiseiKakuGo-W5"

QR_DARK = HexColor("#2B1B12")
CARD_BG = HexColor("#F3E5C8")
CARD_BORDER = HexColor("#8A5A2B")
ACCENT_GOLD = HexColor("#C9962A")
SCROLL_BG = HexColor("#EAD8B1")
SCROLL_TEXT = HexColor("#3B2A18")

MAX_LABEL_CHARS = 12
LOGO_SIZE_RATIO = 0.12
QR_PADDING = 0.6 * mm


def _resolve_caption_font() -> str:
    """日本語ラベルを優先して表示できるフォント名を返す。"""
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(JP_CAPTION_FONT))
        return JP_CAPTION_FONT
    except Exception:
        return DEFAULT_CAPTION_FONT


@dataclass(frozen=True)
class LayoutOptions:
    qr_size_mm: float = 50.0
    margin_mm: float = 10.0
    gap_mm: float = 5.0
    caption_mode: Literal["index", "none"] = "index"


@dataclass(frozen=True)
class RenderSummary:
    total_items: int
    per_page: int
    pages: int
    columns: int
    rows: int


def _truncate_label(text: str) -> str:
    if len(text) <= MAX_LABEL_CHARS:
        return text
    return f"{text[:MAX_LABEL_CHARS]}…"


def _draw_slot_card(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    radius = 1.8 * mm
    inner_inset = 0.8 * mm

    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BORDER)
    c.setLineWidth(0.45 * mm)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

    c.setStrokeColor(ACCENT_GOLD)
    c.setLineWidth(0.28 * mm)
    c.roundRect(
        x + inner_inset,
        y + inner_inset,
        w - 2 * inner_inset,
        h - 2 * inner_inset,
        1.2 * mm,
        fill=0,
        stroke=1,
    )


def _draw_scroll_tag(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    font_name: str,
) -> None:
    c.setFillColor(SCROLL_BG)
    c.setStrokeColor(CARD_BORDER)
    c.setLineWidth(0.35 * mm)
    c.roundRect(x, y, w, h, 1.3 * mm, fill=1, stroke=1)

    c.setStrokeColor(ACCENT_GOLD)
    c.setLineWidth(0.25 * mm)
    c.line(x + 1.3 * mm, y + h - 0.9 * mm, x + w - 1.3 * mm, y + h - 0.9 * mm)

    c.setFillColor(SCROLL_TEXT)
    c.setFont(font_name, 7)
    c.drawCentredString(x + w / 2, y + 1.3 * mm, text)


def _draw_treasure_logo(c: canvas.Canvas, cx: float, cy: float, diameter: float) -> None:
    radius = diameter / 2

    # Center knock-out keeps surrounding modules readable.
    c.setFillColor(white)
    c.setStrokeColor(white)
    c.circle(cx, cy, radius, fill=1, stroke=1)

    c.setStrokeColor(ACCENT_GOLD)
    c.setLineWidth(0.22 * mm)
    c.circle(cx, cy, radius - 0.18 * mm, fill=0, stroke=1)

    chest_w = diameter * 0.56
    chest_h = diameter * 0.34
    chest_x = cx - chest_w / 2
    chest_y = cy - chest_h / 2 - diameter * 0.08
    lid_h = chest_h * 0.48

    c.setFillColor(HexColor("#A56E27"))
    c.roundRect(chest_x, chest_y, chest_w, chest_h, diameter * 0.05, fill=1, stroke=0)

    c.setFillColor(HexColor("#D2A248"))
    c.roundRect(
        chest_x,
        chest_y + chest_h - lid_h * 0.75,
        chest_w,
        lid_h,
        diameter * 0.06,
        fill=1,
        stroke=0,
    )

    band_w = chest_w * 0.14
    c.setFillColor(HexColor("#6C441B"))
    c.rect(cx - band_w / 2, chest_y, band_w, chest_h, fill=1, stroke=0)
    c.circle(cx, chest_y + chest_h * 0.52, diameter * 0.045, fill=1, stroke=0)


def generate_pdf(
    items: list[QrItem], output_path: str | Path, options: LayoutOptions
) -> RenderSummary:
    if not items:
        raise ValueError("URLが0件です。YAMLに1件以上設定してください。")

    qr_size = options.qr_size_mm * mm
    margin = options.margin_mm * mm
    gap = options.gap_mm * mm
    caption_h = CAPTION_H if options.caption_mode != "none" else 0.0
    slot_h = qr_size + caption_h

    if qr_size <= 0 or margin <= 0 or gap <= 0:
        raise ValueError("qr-size / margin / gap は正の値を指定してください。")

    usable_w = PAGE_W - 2 * margin
    usable_h = PAGE_H - 2 * margin
    if usable_w <= 0 or usable_h <= 0:
        raise ValueError("余白が大きすぎるため、A4に配置領域がありません。")

    columns = int((usable_w + gap) // (qr_size + gap))
    rows = int((usable_h + gap) // (slot_h + gap))
    if columns < 1 or rows < 1:
        raise ValueError(
            "指定サイズではA4に1つも配置できません。"
            " qr-size-mm / margin-mm / gap-mm を調整してください。"
        )

    per_page = columns * rows
    pages = ceil(len(items) / per_page)

    grid_w = columns * qr_size + (columns - 1) * gap
    grid_h = rows * slot_h + (rows - 1) * gap
    grid_x = (PAGE_W - grid_w) / 2
    grid_y = (PAGE_H - grid_h) / 2

    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setTitle("QR Sheet")
    c.setAuthor("qr-sheet-generator")
    caption_font = _resolve_caption_font()

    for page_idx in range(pages):
        start = page_idx * per_page
        end = min(start + per_page, len(items))

        for local_idx, item_idx in enumerate(range(start, end)):
            item = items[item_idx]
            col = local_idx % columns
            row = local_idx // columns

            slot_x = grid_x + col * (qr_size + gap)
            slot_top = PAGE_H - grid_y - row * (slot_h + gap)
            slot_bottom = slot_top - slot_h

            _draw_slot_card(c, slot_x, slot_bottom, qr_size, slot_h)

            qr_draw_size = qr_size - 2 * QR_PADDING
            qr_x = slot_x + QR_PADDING
            qr_y = slot_bottom + caption_h + QR_PADDING
            _draw_qr(c, item.url, qr_x, qr_y, qr_draw_size)

            logo_size = qr_size * LOGO_SIZE_RATIO
            _draw_treasure_logo(
                c,
                qr_x + qr_draw_size / 2,
                qr_y + qr_draw_size / 2,
                logo_size,
            )

            if options.caption_mode == "index":
                caption_text = _truncate_label(item.label or f"No.{item_idx + 1}")
                tag_margin = 1.2 * mm
                tag_w = qr_size - 2 * tag_margin
                tag_h = max(3.8 * mm, CAPTION_H - 1.1 * mm)
                tag_x = slot_x + tag_margin
                tag_y = slot_bottom + (CAPTION_H - tag_h) / 2
                _draw_scroll_tag(
                    c,
                    tag_x,
                    tag_y,
                    tag_w,
                    tag_h,
                    caption_text,
                    caption_font,
                )

        c.showPage()

    c.save()

    return RenderSummary(
        total_items=len(items),
        per_page=per_page,
        pages=pages,
        columns=columns,
        rows=rows,
    )


def _draw_qr(
    c: canvas.Canvas,
    value: str,
    x: float,
    y: float,
    size: float,
) -> None:
    widget = qr.QrCodeWidget(value, barLevel="H", barFillColor=QR_DARK)
    min_x, min_y, max_x, max_y = widget.getBounds()
    width = max_x - min_x
    height = max_y - min_y
    drawing = Drawing(
        size,
        size,
        transform=[size / width, 0, 0, size / height, 0, 0],
    )
    drawing.add(widget)
    renderPDF.draw(drawing, c, x, y)
