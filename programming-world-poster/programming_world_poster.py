# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "reportlab>=4.0",
# ]
# ///
"""
からだで学ぶ プログラミングワールド - 入口チラシ (A3)
宝探し風パーチメントデザイン

Usage:
    uv run programming_world_poster.py

日本語フォントが見つからない場合、IPAexゴシックを自動ダウンロードします。
"""

import math
import sys
from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ============================================================
# フォント設定
# ============================================================
# ReportLab は PostScript outlines の .ttc を読めないため
# TrueType outlines の .ttf を優先して探す。
# 見つからない場合は IPA ゴシックを自動ダウンロードする。
FONT_CANDIDATES = [
    # Linux (apt install fonts-ipafont-gothic)
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    # macOS / Windows に手動配置した場合
    str(Path.home() / ".fonts" / "ipagp.ttf"),
    str(Path.home() / "Library" / "Fonts" / "ipagp.ttf"),
    "C:/Windows/Fonts/ipagp.ttf",
]

IPA_FONT_URL = "https://moji.or.jp/wp-content/ipafont/IPAexfont/IPAexfont00401.zip"
IPA_FONT_NAME = "ipaexg.ttf"  # IPAexゴシック


def download_ipa_font() -> str:
    """IPAexゴシックをダウンロードして展開し、パスを返す"""
    import io
    import urllib.request
    import zipfile

    cache_dir = Path.home() / ".cache" / "fonts"
    cached = cache_dir / IPA_FONT_NAME
    if cached.exists():
        return str(cached)

    print(f"📥 日本語フォント (IPAexゴシック) をダウンロード中...")
    data = urllib.request.urlopen(IPA_FONT_URL).read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            if name.endswith(IPA_FONT_NAME):
                cache_dir.mkdir(parents=True, exist_ok=True)
                cached.write_bytes(zf.read(name))
                print(f"   保存先: {cached}")
                return str(cached)

    print("エラー: フォントの展開に失敗しました。", file=sys.stderr)
    sys.exit(1)


def find_font() -> str:
    """利用可能な日本語フォントを探し、なければダウンロード"""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    return download_ipa_font()


font_path = find_font()
pdfmetrics.registerFont(TTFont("JapaneseFont", font_path))

FONT = "JapaneseFont"

# ============================================================
# カラーパレット (パーチメント / 宝探し風)
# ============================================================
PARCHMENT_BG = HexColor("#F5E6C8")
BROWN_DARK = HexColor("#5C3A1E")
BROWN_MED = HexColor("#8B5E3C")
BROWN_LIGHT = HexColor("#A67C52")
DARK_RED = HexColor("#8B1A1A")
GOLD = HexColor("#B8860B")
CREAM = HexColor("#FFF8E7")
WHITE = HexColor("#FFFFFF")

# ============================================================
# 出力先
# ============================================================
OUTPUT = "programming_world_poster.pdf"


# ============================================================
# 描画ユーティリティ
# ============================================================
def draw_bold_centered(c: canvas.Canvas, x: float, y: float, text: str) -> None:
    """擬似ボールド: わずかにずらして重ね描き"""
    for dx, dy in [(0, 0), (0.6, 0), (0, 0.6), (0.6, 0.6)]:
        c.drawCentredString(x + dx, y + dy, text)


def draw_parchment_bg(c: canvas.Canvas, w: float, h: float) -> None:
    c.setFillColor(PARCHMENT_BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    edge = 15 * mm
    c.setFillColor(Color(0.82, 0.75, 0.58, alpha=0.4))
    for rect in [
        (0, h - edge, w, edge),
        (0, 0, w, edge),
        (0, 0, edge, h),
        (w - edge, 0, edge, h),
    ]:
        c.rect(*rect, fill=1, stroke=0)


def draw_border(c: canvas.Canvas, w: float, h: float) -> None:
    m1, m2 = 18 * mm, 22 * mm
    c.setStrokeColor(BROWN_DARK)
    c.setLineWidth(3)
    c.rect(m1, m1, w - 2 * m1, h - 2 * m1, fill=0, stroke=1)
    c.setStrokeColor(BROWN_MED)
    c.setLineWidth(1.5)
    c.rect(m2, m2, w - 2 * m2, h - 2 * m2, fill=0, stroke=1)
    for cx_, cy_ in [(m1, m1), (m1, h - m1), (w - m1, m1), (w - m1, h - m1)]:
        c.setFillColor(BROWN_DARK)
        c.circle(cx_, cy_, 3.5, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.circle(cx_, cy_, 2, fill=1, stroke=0)


def draw_compass(c: canvas.Canvas, cx: float, cy: float, sz: float) -> None:
    c.saveState()
    c.setStrokeColor(BROWN_MED)
    c.setLineWidth(1.5)
    c.circle(cx, cy, sz, fill=0, stroke=1)
    c.circle(cx, cy, sz * 0.3, fill=0, stroke=1)
    c.setStrokeColor(BROWN_DARK)
    c.setLineWidth(1.2)
    for d in [0, 90, 180, 270]:
        a = math.radians(d)
        c.line(
            cx + math.cos(a) * sz * 0.35,
            cy + math.sin(a) * sz * 0.35,
            cx + math.cos(a) * sz,
            cy + math.sin(a) * sz,
        )
    c.setStrokeColor(BROWN_LIGHT)
    c.setLineWidth(0.8)
    for d in [45, 135, 225, 315]:
        a = math.radians(d)
        c.line(
            cx + math.cos(a) * sz * 0.35,
            cy + math.sin(a) * sz * 0.35,
            cx + math.cos(a) * sz * 0.7,
            cy + math.sin(a) * sz * 0.7,
        )
    c.setFillColor(DARK_RED)
    c.circle(cx, cy, sz * 0.12, fill=1, stroke=0)
    c.restoreState()


def draw_ribbon(
    c: canvas.Canvas, cx: float, cy: float, bw: float, bh: float
) -> None:
    c.saveState()
    hw, hh = bw / 2, bh / 2
    tail, notch = 15 * mm, 8 * mm
    c.setFillColor(DARK_RED)
    c.rect(cx - hw, cy - hh, bw, bh, fill=1, stroke=0)
    for sign in [-1, 1]:
        p = c.beginPath()
        p.moveTo(cx + sign * hw, cy + hh)
        p.lineTo(cx + sign * (hw + tail), cy + hh + 2 * mm)
        p.lineTo(cx + sign * (hw + tail - notch), cy)
        p.lineTo(cx + sign * (hw + tail), cy - hh - 2 * mm)
        p.lineTo(cx + sign * hw, cy - hh)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_divider(c: canvas.Canvas, cx: float, cy: float, length: float) -> None:
    half = length / 2
    c.saveState()
    c.setStrokeColor(BROWN_LIGHT)
    c.setLineWidth(0.8)
    c.line(cx - half, cy, cx - 8 * mm, cy)
    c.line(cx + 8 * mm, cy, cx + half, cy)
    d = 3 * mm
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(cx, cy + d)
    p.lineTo(cx + d, cy)
    p.lineTo(cx, cy - d)
    p.lineTo(cx - d, cy)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_game_block(
    c: canvas.Canvas, cx: float, cy: float, title: str, desc: str, bw: float
) -> None:
    bh = 40 * mm
    hw = bw / 2
    c.saveState()
    c.setFillColor(Color(1, 0.97, 0.88, alpha=0.6))
    c.setStrokeColor(BROWN_MED)
    c.setLineWidth(1.5)
    c.roundRect(cx - hw, cy - bh / 2, bw, bh, 4 * mm, fill=1, stroke=1)
    c.setStrokeColor(BROWN_LIGHT)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    ins = 3 * mm
    c.roundRect(
        cx - hw + ins, cy - bh / 2 + ins, bw - 2 * ins, bh - 2 * ins, 4 * mm,
        fill=0, stroke=1,
    )
    c.setDash()

    c.setFont(FONT, 21)
    c.setFillColor(BROWN_DARK)
    ty = cy + 5 * mm
    draw_bold_centered(c, cx, ty, title)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(cx - 55 * mm, ty - 4 * mm, cx + 55 * mm, ty - 4 * mm)

    c.setFont(FONT, 13)
    c.setFillColor(BROWN_MED)
    c.drawCentredString(cx, ty - 15 * mm, desc)
    c.restoreState()


def gold_lines(c: canvas.Canvas, cx: float, y: float, w: float) -> None:
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(cx - w / 2, y, cx + w / 2, y)
    c.setLineWidth(0.8)
    c.line(cx - w / 2, y - 4, cx + w / 2, y - 4)


# ============================================================
# メイン
# ============================================================
def create_poster() -> None:
    c = canvas.Canvas(OUTPUT, pagesize=A3)
    w, h = A3
    cx = w / 2

    draw_parchment_bg(c, w, h)
    draw_border(c, w, h)

    # コンパスローズ (四隅)
    draw_compass(c, 42 * mm, h - 42 * mm, 12 * mm)
    draw_compass(c, w - 42 * mm, h - 42 * mm, 10 * mm)
    draw_compass(c, w - 42 * mm, 42 * mm, 10 * mm)
    draw_compass(c, 42 * mm, 42 * mm, 10 * mm)

    # === タイトル ===
    lw = 180 * mm
    gold_lines(c, cx, h - 60 * mm, lw)

    c.setFont(FONT, 46)
    c.setFillColor(BROWN_DARK)
    t1 = h - 85 * mm
    draw_bold_centered(c, cx, t1, "からだで学ぶ")

    c.setFont(FONT, 46)
    t2 = t1 - 58
    draw_bold_centered(c, cx, t2, "プログラミングワールド")

    gold_lines(c, cx, t2 - 16, lw)

    # === キャッチコピー (リボン) ===
    catch_y = t2 - 16 - 26 * mm
    draw_ribbon(c, cx, catch_y, 215 * mm, 17 * mm)
    c.setFont(FONT, 17)
    c.setFillColor(CREAM)
    draw_bold_centered(c, cx, catch_y - 3, "からだをうごかして プログラミングにちょうせん！")

    # === 区切り ===
    div1 = catch_y - 22 * mm
    draw_divider(c, cx, div1, 160 * mm)

    # === ゲーム紹介 ===
    bw = 210 * mm
    g1y = div1 - 32 * mm
    draw_game_block(
        c, cx, g1y,
        "にんげんロボットゲーム",
        "カードをならべて にんげんロボットに めいれいしよう！",
        bw,
    )

    g2y = g1y - 50 * mm
    draw_game_block(
        c, cx, g2y,
        "ロジックたからさがし",
        "たからのちずをよんで フィールドの たからをみつけよう！",
        bw,
    )

    # === 区切り ===
    div2 = g2y - 30 * mm
    draw_divider(c, cx, div2, 160 * mm)

    # === 開催時間 ===
    iy = div2 - 16 * mm
    c.setFont(FONT, 18)
    c.setFillColor(BROWN_DARK)
    draw_bold_centered(c, cx, iy, "かいさいじかん")

    c.setFont(FONT, 26)
    c.setFillColor(DARK_RED)
    ty1 = iy - 22 * mm
    draw_bold_centered(c, cx, ty1, "11:00 〜 13:00")

    c.setFont(FONT, 18)
    c.setFillColor(BROWN_MED)
    c.drawCentredString(cx, ty1 - 14 * mm, "／")

    c.setFont(FONT, 26)
    c.setFillColor(DARK_RED)
    ty2 = ty1 - 28 * mm
    draw_bold_centered(c, cx, ty2, "18:00 〜 20:00")

    # === だれでも さんかできるよ！ ===
    wy = ty2 - 30 * mm
    box_w, box_h = 200 * mm, 22 * mm
    c.setFillColor(WHITE)
    c.setStrokeColor(BROWN_MED)
    c.setLineWidth(1.5)
    c.roundRect(cx - box_w / 2, wy - box_h / 2 + 2, box_w, box_h, 4 * mm, fill=1, stroke=1)

    c.setFont(FONT, 24)
    c.setFillColor(DARK_RED)
    draw_bold_centered(c, cx, wy - 2, "だれでも さんかできるよ！")

    c.save()
    print(f"✅ 生成完了: {OUTPUT}")


if __name__ == "__main__":
    create_poster()
