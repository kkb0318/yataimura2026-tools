"""QRコードをA4 PDFへ面付けして出力する。"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Literal

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
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

            qr_x = slot_x
            qr_y = slot_bottom + caption_h
            _draw_qr(c, item.url, qr_x, qr_y, qr_size)

            if options.caption_mode == "index":
                caption_text = item.label or f"No.{item_idx + 1}"
                c.setFillColor(HexColor("#333333"))
                c.setFont(caption_font, 8)
                c.drawCentredString(
                    slot_x + qr_size / 2,
                    slot_bottom + 2.2 * mm,
                    caption_text,
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
    widget = qr.QrCodeWidget(value)
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
