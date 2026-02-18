"""PDF レンダリングエンジン。

cards.yaml から読み込んだデータ構造を受け取り、A4 PDF を生成する。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .fonts import FONT_NAME

# ==================== レイアウト定数 ====================
CARD_W = 63 * mm
CARD_H = 88 * mm
COLS = 3
ROWS = 3
CARDS_PER_PAGE = COLS * ROWS

PAGE_W, PAGE_H = A4
TOTAL_CARDS_W = COLS * CARD_W
TOTAL_CARDS_H = ROWS * CARD_H
MARGIN_L = (PAGE_W - TOTAL_CARDS_W) / 2
MARGIN_B = (PAGE_H - TOTAL_CARDS_H) / 2

TRIM_LEN = 5 * mm
TRIM_OFFSET = 2 * mm


# ==================== データ構造 ====================
@dataclass
class LevelStyle:
    """難易度レベルの色とラベル。"""

    name: str  # 内部名 (blue, yellow, red, ...)
    label: str  # 表示名 (きほん, ちゅうきゅう, ...)
    bg: str
    border: str
    header_bg: str
    accent: str


@dataclass
class CategoryStyle:
    """カテゴリバッジのラベルと色。"""

    label: str
    color: str


@dataclass
class CardInstance:
    """展開済みの1枚分のカードデータ。"""

    text1: str
    text2: str
    icon_func: Callable
    category: CategoryStyle
    level: LevelStyle
    step_number: str = ""


# ==================== 描画関数 ====================


def _draw_trim_marks(c: canvas.Canvas) -> None:
    c.setStrokeColor(HexColor("#999999"))
    c.setLineWidth(0.3)
    for row in range(ROWS + 1):
        y = MARGIN_B + row * CARD_H
        c.line(MARGIN_L - TRIM_LEN - TRIM_OFFSET, y, MARGIN_L - TRIM_OFFSET, y)
        c.line(
            MARGIN_L + TOTAL_CARDS_W + TRIM_OFFSET,
            y,
            MARGIN_L + TOTAL_CARDS_W + TRIM_LEN + TRIM_OFFSET,
            y,
        )
    for col in range(COLS + 1):
        x = MARGIN_L + col * CARD_W
        c.line(
            x,
            MARGIN_B + TOTAL_CARDS_H + TRIM_OFFSET,
            x,
            MARGIN_B + TOTAL_CARDS_H + TRIM_LEN + TRIM_OFFSET,
        )
        c.line(x, MARGIN_B - TRIM_OFFSET, x, MARGIN_B - TRIM_LEN - TRIM_OFFSET)


def _auto_font_size(text: str) -> float:
    n = len(text)
    if n <= 4:
        return 12
    if n <= 6:
        return 10
    if n <= 8:
        return 8.5
    if n <= 10:
        return 7.5
    return 6.5


def _draw_card(c: canvas.Canvas, x: float, y: float, card: CardInstance) -> None:
    lv = card.level
    cat = card.category

    # 背景（隙間なし）
    c.setFillColor(HexColor(lv.bg))
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # 枠線
    c.setStrokeColor(HexColor(lv.border))
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H, fill=0, stroke=1)

    # ヘッダー帯
    header_h = 12 * mm
    c.setFillColor(HexColor(lv.header_bg))
    c.rect(x, y + CARD_H - header_h, CARD_W, header_h, fill=1, stroke=0)

    # レベルラベル
    c.setFillColor(white)
    c.setFont(FONT_NAME, 7)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H - 10 * mm, f"● {lv.label} ●")

    # カテゴリバッジ
    badge_w = 28 * mm
    badge_h = 5.5 * mm
    badge_x = x + (CARD_W - badge_w) / 2
    badge_y = y + CARD_H - 17.5 * mm
    c.setFillColor(HexColor(cat.color))
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_NAME, 6.5)
    c.drawCentredString(x + CARD_W / 2, badge_y + 1.5 * mm, cat.label)

    # アイコン
    icon_cx = x + CARD_W / 2
    icon_cy = y + 38 * mm
    icon_size = 22 * mm
    card.icon_func(c, icon_cx, icon_cy, icon_size, HexColor(lv.accent))

    # 移動カードの歩数表示
    if card.step_number:
        c.setFillColor(HexColor(lv.header_bg))
        c.setFont(FONT_NAME, 14)
        c.drawCentredString(icon_cx, icon_cy - 4 * mm, card.step_number)

    # テキスト
    c.setFillColor(HexColor("#333333"))
    c.setFont(FONT_NAME, _auto_font_size(card.text1))
    c.drawCentredString(x + CARD_W / 2, y + 18 * mm, card.text1)
    c.setFont(FONT_NAME, _auto_font_size(card.text2))
    c.drawCentredString(x + CARD_W / 2, y + 10 * mm, card.text2)

    # 下部アクセントライン
    c.setStrokeColor(HexColor(lv.accent))
    c.setLineWidth(1)
    c.line(x + 6 * mm, y + 5 * mm, x + CARD_W - 6 * mm, y + 5 * mm)


def _draw_guide_page(c: canvas.Canvas, level_summaries: list[tuple[str, int]]) -> None:
    """作り方ガイドページを描画。"""
    c.setFont(FONT_NAME, 16)
    c.setFillColor(HexColor("#333333"))
    c.drawCentredString(PAGE_W / 2, PAGE_H - 30 * mm, "カード 作り方ガイド")

    y = PAGE_H - 55 * mm
    lh = 7 * mm

    total = sum(cnt for _, cnt in level_summaries)
    pages = (total + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE

    lines: list[tuple[str, bool]] = [
        ("【裁断方法】", True),
        ("① トンボ（角の短い線）を目印にカッターで裁断します", False),
        ("② 定規をあてて、まず横方向に3本切ります", False),
        ("③ 次に縦方向に2本切ると、9枚のカードになります", False),
        ("④ 同じページに違う色のカードが混在する場合があります", False),
        ("", False),
        ("【セルフラミネート方式の場合】", True),
        ("① 裁断したカードをラミネートフィルムに挟みます", False),
        ("② フィルムの端をカードより2mm程度大きく切ります", False),
        ("③ 角を丸くカットすると安全です", False),
        ("", False),
        ("【カードスリーブ方式の場合】", True),
        ("① トレカ用スリーブ（63×88mm対応）を用意します", False),
        ("② 裁断したカードをスリーブに入れるだけ！", False),
        ("③ 差し替え可能なので内容変更も簡単です", False),
        ("", False),
        ("【カード枚数】", True),
    ]

    for label, cnt in level_summaries:
        lines.append((f"  {label}: {cnt}枚", False))
    lines.append((f"  合計: {total}枚 → A4用紙 {pages}枚", False))
    lines.append(("", False))
    lines.append(("【印刷のヒント】", True))
    lines.append(("  ・予備が必要な場合は2部印刷してください", False))
    lines.append(("  ・用紙サイズ: A4 / 倍率: 100%（実寸）", False))
    lines.append(("  ・余白: なし or 最小", False))

    for text, is_heading in lines:
        if text == "":
            y -= lh * 0.3
            continue
        if is_heading:
            c.setFont(FONT_NAME, 9)
            c.setFillColor(HexColor("#1565C0"))
        else:
            c.setFont(FONT_NAME, 7.5)
            c.setFillColor(HexColor("#333333"))
        c.drawString(20 * mm, y, text)
        y -= lh
        if y < 20 * mm:
            c.showPage()
            y = PAGE_H - 25 * mm

    c.showPage()


# ==================== メイン生成関数 ====================


def generate_pdf(
    cards: list[CardInstance],
    level_summaries: list[tuple[str, int]],
    output_path: str,
) -> None:
    """カード一覧からPDFを生成する。

    Args:
        cards: 展開済みの全カードリスト（並び順がそのまま配置順）
        level_summaries: [("青カード（きほん）", 14), ...] ガイドページ用
        output_path: 出力PDFファイルパス
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("人間ロボットゲーム カード")
    c.setAuthor("Programming Education")

    total = len(cards)
    pages_needed = (total + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE

    for page_idx in range(pages_needed):
        _draw_trim_marks(c)

        # ページヘッダー
        c.setFillColor(HexColor("#666666"))
        c.setFont(FONT_NAME, 7)
        c.drawString(
            MARGIN_L, PAGE_H - 8 * mm, f"カード - {page_idx + 1}/{pages_needed}ページ"
        )
        c.drawRightString(PAGE_W - MARGIN_L, PAGE_H - 8 * mm, "人間ロボットゲーム")

        start = page_idx * CARDS_PER_PAGE
        end = min(start + CARDS_PER_PAGE, total)

        for i, card_idx in enumerate(range(start, end)):
            col = i % COLS
            row = ROWS - 1 - (i // COLS)
            card_x = MARGIN_L + col * CARD_W
            card_y = MARGIN_B + row * CARD_H
            _draw_card(c, card_x, card_y, cards[card_idx])

        c.showPage()

    _draw_guide_page(c, level_summaries)
    c.save()
