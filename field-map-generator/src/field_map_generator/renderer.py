"""
フィールドマップ PDF レンダラー

描画ロジックのみ。マップデータは map_data.py から読み込みます。
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from . import map_data as data


# ---------------------------------------------------------------------------
# フォント設定
# ---------------------------------------------------------------------------
# 日本語フォントのパス候補 (上から順に探索)
_FONT_CANDIDATES: list[tuple[str, str]] = [
    # macOS
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"),
    ("/System/Library/Fonts/Hiragino Sans GB W3.otf", "/System/Library/Fonts/Hiragino Sans GB W6.otf"),
    # Linux (IPA Gothic)
    ("/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"),
    # Linux (Noto) - TTF versions
    ("/usr/share/fonts/truetype/noto/NotoSansCJKjp-Regular.otf", "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Bold.otf"),
    # Windows
    ("C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/msgothic.ttc"),
    ("C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/meiryob.ttc"),
    # Generic fallback
    ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"),
]

_FONT_REG = "JP"
_FONT_BOLD = "JPB"


def _register_fonts() -> None:
    """利用可能な日本語フォントを自動検出して登録する。"""
    for regular, bold in _FONT_CANDIDATES:
        if Path(regular).exists():
            try:
                pdfmetrics.registerFont(TTFont(_FONT_REG, regular))
                bold_path = bold if Path(bold).exists() else regular
                pdfmetrics.registerFont(TTFont(_FONT_BOLD, bold_path))
                return
            except Exception:
                continue

    raise RuntimeError(
        "日本語フォントが見つかりません。\n"
        "以下のいずれかをインストールしてください:\n"
        "  - fonts-ipafont-gothic (Ubuntu/Debian)\n"
        "  - google-noto-sans-jp-fonts (Fedora/RHEL)\n"
        "  - macOS / Windows は標準フォントを自動検出します"
    )


# ---------------------------------------------------------------------------
# 色定義 (モノクロ)
# ---------------------------------------------------------------------------
BLACK = black
DARK = HexColor("#333333")
MID = HexColor("#666666")
LIGHT_GRAY = HexColor("#E0E0E0")
VERY_LIGHT = HexColor("#F0F0F0")
WHITE = white


# ---------------------------------------------------------------------------
# レイアウト定数
# ---------------------------------------------------------------------------
CELL_SIZE = 52


class _Layout:
    """ページ・グリッドの座標計算"""

    def __init__(self) -> None:
        self.page_w, self.page_h = landscape(A4)
        self.rows = data.GRID_ROWS
        self.cols = data.GRID_COLS
        self.cell = CELL_SIZE
        self.grid_w = self.cols * self.cell
        self.grid_h = self.rows * self.cell
        self.grid_x = 58
        self.grid_y = (self.page_h - self.grid_h) / 2 - 30

    def cell_center(self, row: int, col: int) -> tuple[float, float]:
        """セル中心座標を返す (row, col は 1-indexed)。"""
        x = self.grid_x + (col - 1) * self.cell + self.cell / 2
        y = self.grid_y + self.grid_h - row * self.cell + self.cell / 2
        return x, y

    def cell_origin(self, row: int, col: int) -> tuple[float, float]:
        """セル左下座標を返す。"""
        x = self.grid_x + (col - 1) * self.cell
        y = self.grid_y + self.grid_h - row * self.cell
        return x, y


# ---------------------------------------------------------------------------
# 各セルタイプの描画
# ---------------------------------------------------------------------------


def _draw_grid(c: canvas.Canvas, lay: _Layout) -> None:
    """グリッド線を描画。"""
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.5)
    for i in range(lay.cols + 1):
        x = lay.grid_x + i * lay.cell
        c.line(x, lay.grid_y, x, lay.grid_y + lay.grid_h)
    for i in range(lay.rows + 1):
        y = lay.grid_y + i * lay.cell
        c.line(lay.grid_x, y, lay.grid_x + lay.grid_w, y)
    c.setLineWidth(2)
    c.rect(lay.grid_x, lay.grid_y, lay.grid_w, lay.grid_h, fill=0, stroke=1)


def _draw_labels(c: canvas.Canvas, lay: _Layout) -> None:
    """行・列ラベルを描画。"""
    c.setFont(_FONT_BOLD, 10)
    c.setFillColor(BLACK)
    for col in range(1, lay.cols + 1):
        cx, _ = lay.cell_center(0, col)
        c.drawCentredString(cx, lay.grid_y + lay.grid_h + 8, f"{col}列")
    for row in range(1, lay.rows + 1):
        _, cy = lay.cell_center(row, 0)
        c.drawCentredString(lay.grid_x - 18, cy - 4, f"{row}行")


def _draw_number_cells(c: canvas.Canvas, lay: _Layout) -> None:
    """数字マスを描画。"""
    for row, col, num in data.NUMBER_CELLS:
        ox, oy = lay.cell_origin(row, col)
        c.setFillColor(LIGHT_GRAY)
        c.rect(ox + 1, oy + 1, lay.cell - 2, lay.cell - 2, fill=1, stroke=0)
        cx, cy = lay.cell_center(row, col)
        c.setFont(_FONT_BOLD, 22)
        c.setFillColor(BLACK)
        c.drawCentredString(cx, cy - 8, str(num))


def _draw_obstacles(c: canvas.Canvas, lay: _Layout) -> None:
    """障害物を描画。"""
    for row, col in data.OBSTACLES:
        ox, oy = lay.cell_origin(row, col)
        c.setFillColor(DARK)
        c.rect(ox + 1, oy + 1, lay.cell - 2, lay.cell - 2, fill=1, stroke=0)
        c.setStrokeColor(WHITE)
        c.setLineWidth(2)
        m = 8
        c.line(ox + m, oy + m, ox + lay.cell - m, oy + lay.cell - m)
        c.line(ox + m, oy + lay.cell - m, ox + lay.cell - m, oy + m)
        cx, cy = lay.cell_center(row, col)
        c.setFont(_FONT_BOLD, 7)
        c.setFillColor(WHITE)
        c.drawCentredString(cx, cy - 14, "障害物")


def _draw_treasures(c: canvas.Canvas, lay: _Layout) -> None:
    """お宝マスを描画。"""
    for t in data.TREASURES:
        ox, oy = lay.cell_origin(t.row, t.col)
        c.setFillColor(VERY_LIGHT)
        c.rect(ox + 1, oy + 1, lay.cell - 2, lay.cell - 2, fill=1, stroke=0)
        c.setStrokeColor(BLACK)
        c.setLineWidth(1.5)
        c.rect(ox + 2, oy + 2, lay.cell - 4, lay.cell - 4, fill=0, stroke=1)

        cx, cy = lay.cell_center(t.row, t.col)
        c.setFont(_FONT_BOLD, 8)
        c.setFillColor(BLACK)
        c.drawCentredString(cx, cy + 14, f"[{t.label}]")
        c.setFont(_FONT_BOLD, 13)
        c.drawCentredString(cx, cy - 2, t.short)
        c.setFont(_FONT_REG, 5.5)
        c.setFillColor(MID)
        c.drawCentredString(cx, cy - 15, t.name)


def _draw_start(
    c: canvas.Canvas,
    lay: _Layout,
    pos: data.StartPosition,
    *,
    style: str = "dashed",
) -> None:
    """スタート位置を描画。style: 'dashed'=破線, 'double'=二重線"""
    ox, oy = lay.cell_origin(pos.row, pos.col)
    cx, cy = lay.cell_center(pos.row, pos.col)
    c.setStrokeColor(BLACK)

    if style == "dashed":
        c.setLineWidth(1.5)
        c.setDash(4, 2)
        c.rect(ox + 2, oy + 2, lay.cell - 4, lay.cell - 4, fill=0, stroke=1)
        c.setDash()
    else:  # double
        c.setLineWidth(1.5)
        c.rect(ox + 2, oy + 2, lay.cell - 4, lay.cell - 4, fill=0, stroke=1)
        c.setLineWidth(0.8)
        c.rect(ox + 5, oy + 5, lay.cell - 10, lay.cell - 10, fill=0, stroke=1)

    # テキスト行を縦中央に配置
    c.setFillColor(BLACK)
    n = len(pos.lines)
    line_h = 11
    top_y = cy + (n - 1) * line_h / 2
    for i, line in enumerate(pos.lines):
        size = 7 if i < n - 1 else 7
        font = _FONT_BOLD if i < n - 1 else _FONT_REG
        c.setFont(font, size)
        c.drawCentredString(cx, top_y - i * line_h - 3, line)


def _draw_treasure_table(c: canvas.Canvas, lay: _Layout) -> None:
    """右パネルのお宝一覧テーブルを描画。"""
    panel_x = lay.grid_x + lay.grid_w + 20
    panel_w = lay.page_w - panel_x - 18
    panel_top = lay.grid_y + lay.grid_h + 18

    c.setFont(_FONT_BOLD, 14)
    c.setFillColor(BLACK)
    c.drawString(panel_x, panel_top, "【お宝一覧】")

    table_top = panel_top - 12
    row_h = (table_top - lay.grid_y) / len(data.TREASURES)

    for i, t in enumerate(data.TREASURES):
        ty = table_top - (i + 1) * row_h

        c.setStrokeColor(BLACK)
        c.setLineWidth(0.8)
        c.rect(panel_x, ty + 2, panel_w, row_h - 4, fill=0, stroke=1)

        row_mid = ty + 2 + (row_h - 4) / 2

        c.setFillColor(BLACK)
        c.circle(panel_x + 16, row_mid, 11, fill=1, stroke=0)
        c.setFont(_FONT_BOLD, 13)
        c.setFillColor(WHITE)
        c.drawCentredString(panel_x + 16, row_mid - 5, t.label)

        c.setFont(_FONT_BOLD, 16)
        c.setFillColor(BLACK)
        c.drawString(panel_x + 34, row_mid + 2, t.short)

        c.setFont(_FONT_REG, 10)
        c.setFillColor(MID)
        c.drawString(panel_x + 34, row_mid - 13, t.name)


def _draw_legend(c: canvas.Canvas, lay: _Layout) -> None:
    """凡例を描画。"""
    ly = lay.grid_y - 18
    c.setFont(_FONT_BOLD, 12)
    c.setFillColor(BLACK)
    c.drawString(lay.grid_x, ly, "【凡例】")

    iy = ly - 22
    sz = 14
    items: list[tuple[float, str, str]] = [
        (0, "number", "数字マス"),
        (90, "obstacle", "障害物"),
        (170, "treasure", "お宝"),
        (240, "robot", "人間ロボット スタート"),
        (390, "logic", "ロジック宝探し スタート"),
    ]

    for dx, kind, label in items:
        ix = lay.grid_x + dx

        if kind == "number":
            c.setFillColor(LIGHT_GRAY)
            c.rect(ix, iy, sz, sz, fill=1, stroke=0)
            c.setStrokeColor(BLACK)
            c.setLineWidth(0.5)
            c.rect(ix, iy, sz, sz, fill=0, stroke=1)
        elif kind == "obstacle":
            c.setFillColor(DARK)
            c.rect(ix, iy, sz, sz, fill=1, stroke=0)
        elif kind == "treasure":
            c.setFillColor(VERY_LIGHT)
            c.setStrokeColor(BLACK)
            c.setLineWidth(1.2)
            c.rect(ix, iy, sz, sz, fill=1, stroke=1)
        elif kind == "robot":
            c.setStrokeColor(BLACK)
            c.setLineWidth(1)
            c.setDash(3, 2)
            c.rect(ix, iy, sz, sz, fill=0, stroke=1)
            c.setDash()
        elif kind == "logic":
            c.setStrokeColor(BLACK)
            c.setLineWidth(1)
            c.rect(ix, iy, sz, sz, fill=0, stroke=1)
            c.setLineWidth(0.5)
            c.rect(ix + 2, iy + 2, sz - 4, sz - 4, fill=0, stroke=1)

        c.setFont(_FONT_REG, 9)
        c.setFillColor(BLACK)
        c.drawString(ix + sz + 4, iy + 2, label)


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------


def generate_pdf(output_path: str | Path) -> Path:
    """フィールドマップPDFを生成して保存先パスを返す。"""
    _register_fonts()

    output_path = Path(output_path)
    lay = _Layout()
    c = canvas.Canvas(str(output_path), pagesize=landscape(A4))

    # 背景
    c.setFillColor(WHITE)
    c.rect(0, 0, lay.page_w, lay.page_h, fill=1, stroke=0)

    # タイトル
    c.setFont(_FONT_BOLD, 22)
    c.setFillColor(BLACK)
    c.drawCentredString(lay.grid_x + lay.grid_w / 2, lay.page_h - 40, data.TITLE)
    c.setFont(_FONT_REG, 13)
    c.setFillColor(MID)
    c.drawCentredString(lay.grid_x + lay.grid_w / 2, lay.page_h - 60, data.SUBTITLE)

    # グリッド・各要素
    _draw_grid(c, lay)
    _draw_labels(c, lay)
    _draw_number_cells(c, lay)
    _draw_obstacles(c, lay)
    _draw_treasures(c, lay)
    _draw_start(c, lay, data.ROBOT_START, style="dashed")
    _draw_start(c, lay, data.LOGIC_START, style="double")
    _draw_treasure_table(c, lay)
    _draw_legend(c, lay)

    # フッター
    c.setFont(_FONT_REG, 8)
    c.setFillColor(MID)
    c.drawCentredString(lay.page_w / 2, 15, data.FOOTER)

    c.save()
    return output_path
