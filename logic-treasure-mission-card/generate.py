# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "reportlab>=4.0",
#     "pyyaml>=6.0",
# ]
# ///
"""
人間ロボットゲーム ミッションカード PDF 生成スクリプト

使い方:
    uv run generate.py                       # デフォルト (missions.yaml → output/)
    uv run generate.py -i my_missions.yaml   # 別の YAML ファイルを指定
    uv run generate.py -o dist/              # 出力先ディレクトリを指定
    uv run generate.py --cards-only          # ミッションカードのみ生成
    uv run generate.py --staff-only          # 運営用解答集のみ生成
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import yaml
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ================================================================
# フォント検索
# ================================================================

_FONT_CANDIDATES = [
    # Linux (IPA Gothic)
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    # macOS - TrueType outlines のみ (CFF/OTF は ReportLab 非対応)
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/ipaexg.ttf",
    "/Library/Fonts/ipagp.ttf",
    # Windows
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/YuGothR.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
]

_FONT_MONO_CANDIDATES = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/ipaexg.ttf",
    "/Library/Fonts/ipag.ttf",
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/YuGothR.ttc",
]


def _find_font(candidates: list[str], name: str) -> str:
    errors = []
    for path in candidates:
        if not Path(path).exists():
            continue
        try:
            # TTC の場合は subfontIndex=0 を試す
            if path.lower().endswith(".ttc"):
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception as e:
            errors.append(f"  {path}: {e}")
            continue

    msg = "日本語フォントが見つからないか、対応形式ではありません。\n"
    if errors:
        msg += "試行したフォント:\n" + "\n".join(errors) + "\n\n"
    msg += (
        "解決方法:\n"
        "  macOS:  brew install font-ipa-gothic  または\n"
        "          https://moji.or.jp/ipafont/ から IPA ゴシックをダウンロードして\n"
        "          /Library/Fonts/ に .ttf ファイルを配置\n"
        "  Ubuntu: sudo apt install fonts-ipafont-gothic\n"
        "  Windows: 通常はプリインストール済み"
    )
    raise FileNotFoundError(msg)


# ================================================================
# カラーテーマ
# ================================================================

COLORS = {
    "blue": {
        "bg": HexColor("#E3EFFD"), "card_bg": white,
        "header": HexColor("#3672C4"), "header_dark": HexColor("#2A5A9E"),
        "border": HexColor("#7BAAF7"), "accent": HexColor("#4A90D9"),
        "accent_light": HexColor("#D0E2F9"),
        "star_on": HexColor("#3672C4"), "star_off": HexColor("#C8DAF0"),
        "text": HexColor("#1A3A5C"), "text_light": HexColor("#5A7A9C"),
        "rule_bg": HexColor("#EDF4FE"), "sparkle": HexColor("#7BAAF7"),
    },
    "yellow": {
        "bg": HexColor("#FFF3D0"), "card_bg": white,
        "header": HexColor("#E8941A"), "header_dark": HexColor("#C47A10"),
        "border": HexColor("#FFCC02"), "accent": HexColor("#E8941A"),
        "accent_light": HexColor("#FFF0C8"),
        "star_on": HexColor("#E8941A"), "star_off": HexColor("#F0DCA0"),
        "text": HexColor("#5C3D00"), "text_light": HexColor("#9C7A30"),
        "rule_bg": HexColor("#FFF8E8"), "sparkle": HexColor("#FFCC02"),
    },
    "red": {
        "bg": HexColor("#FCDEDE"), "card_bg": white,
        "header": HexColor("#C0392B"), "header_dark": HexColor("#962D22"),
        "border": HexColor("#E57373"), "accent": HexColor("#C0392B"),
        "accent_light": HexColor("#F8D8D8"),
        "star_on": HexColor("#C0392B"), "star_off": HexColor("#E0B0B0"),
        "text": HexColor("#5C1A1A"), "text_light": HexColor("#9C4A4A"),
        "rule_bg": HexColor("#FDF0F0"), "sparkle": HexColor("#E57373"),
    },
}

PAGE_W, PAGE_H = A4


# ================================================================
# 描画プリミティブ
# ================================================================

def draw_rounded_rect(c, x, y, w, h, r, *, fill_color=None, stroke_color=None, stroke_width=1):
    p = c.beginPath()
    p.moveTo(x + r, y); p.lineTo(x + w - r, y)
    p.arcTo(x + w - r, y, x + w, y + r, 0, 90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - r, y + h - r, x + w, y + h, 0, 90)
    p.lineTo(x + r, y + h)
    p.arcTo(x, y + h - r, x + r, y + h, 0, 90)
    p.lineTo(x, y + r)
    p.arcTo(x, y, x + r, y + r, 0, 90)
    p.close()
    if fill_color: c.setFillColor(fill_color)
    if stroke_color: c.setStrokeColor(stroke_color); c.setLineWidth(stroke_width)
    if fill_color and stroke_color: c.drawPath(p, fill=1, stroke=1)
    elif fill_color: c.drawPath(p, fill=1, stroke=0)
    elif stroke_color: c.drawPath(p, fill=0, stroke=1)


def draw_star(c, cx, cy, size, color):
    c.setFillColor(color)
    p = c.beginPath()
    for i in range(5):
        ao = math.radians(90 + i * 72)
        ai = math.radians(90 + i * 72 + 36)
        ox, oy = cx + size * math.cos(ao), cy + size * math.sin(ao)
        ix, iy = cx + size * 0.4 * math.cos(ai), cy + size * 0.4 * math.sin(ai)
        if i == 0: p.moveTo(ox, oy)
        else: p.lineTo(ox, oy)
        p.lineTo(ix, iy)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_sparkle(c, cx, cy, size, color):
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx, cy + size); p.lineTo(cx + size * 0.25, cy)
    p.lineTo(cx, cy - size); p.lineTo(cx - size * 0.25, cy); p.close()
    c.drawPath(p, fill=1, stroke=0)
    p2 = c.beginPath()
    p2.moveTo(cx + size, cy); p2.lineTo(cx, cy + size * 0.25)
    p2.lineTo(cx - size, cy); p2.lineTo(cx, cy - size * 0.25); p2.close()
    c.drawPath(p2, fill=1, stroke=0)


def draw_treasure_chest(c, cx, cy, size, color, color_light):
    w, h = size * 2, size * 1.2
    draw_rounded_rect(c, cx - w/2, cy - h/2, w, h, size * 0.15,
                      fill_color=color_light, stroke_color=color, stroke_width=1.5)
    c.saveState()
    p = c.beginPath()
    p.moveTo(cx - w/2 - size*0.08, cy + h/2)
    p.lineTo(cx - w/2 - size*0.08, cy + h/2 + h*0.45*0.3)
    ctrl_y = cy + h/2 + h*0.45*1.4
    p.curveTo(cx - w/3, ctrl_y, cx + w/3, ctrl_y, cx + w/2 + size*0.08, cy + h/2 + h*0.45*0.3)
    p.lineTo(cx + w/2 + size*0.08, cy + h/2); p.close()
    c.setFillColor(color_light); c.setStrokeColor(color); c.setLineWidth(1.5)
    c.drawPath(p, fill=1, stroke=1)
    c.restoreState()
    c.setStrokeColor(color); c.setLineWidth(1.5)
    c.line(cx - w/2, cy + h/2, cx + w/2, cy + h/2)
    clasp_r = size * 0.2
    c.setFillColor(color); c.circle(cx, cy + h/2, clasp_r, fill=1, stroke=0)
    c.setFillColor(color_light)
    c.circle(cx, cy + h/2 + clasp_r*0.15, clasp_r*0.35, fill=1, stroke=0)
    c.rect(cx - clasp_r*0.15, cy + h/2 - clasp_r*0.7, clasp_r*0.3, clasp_r*0.6, fill=1, stroke=0)


# ================================================================
# ミッションカード描画
# ================================================================

def _draw_card(c, x, y, card_w, card_h, m, font, font_mono):
    colors = COLORS[m["color"]]
    bm = 5 * mm
    bx, by = x + bm, y + bm
    bw, bh = card_w - 2*bm, card_h - 2*bm

    # 背景・枠
    c.setFillColor(colors["bg"])
    c.rect(x, y, card_w, card_h, fill=1, stroke=0)
    draw_rounded_rect(c, bx, by, bw, bh, 5*mm,
                      fill_color=colors["card_bg"], stroke_color=colors["border"], stroke_width=2.5)

    # キラキラ装飾
    sp_c = Color(colors["sparkle"].red, colors["sparkle"].green, colors["sparkle"].blue, 0.3)
    draw_sparkle(c, bx + 12*mm, by + bh - 30*mm, 3*mm, sp_c)
    draw_sparkle(c, bx + bw - 12*mm, by + bh - 30*mm, 2.5*mm, sp_c)
    draw_sparkle(c, bx + 18*mm, by + 22*mm, 2*mm, sp_c)
    draw_sparkle(c, bx + bw - 18*mm, by + 22*mm, 2.5*mm, sp_c)
    if m["stars"] >= 3:
        draw_sparkle(c, bx + 25*mm, by + bh - 38*mm, 2*mm, sp_c)
        draw_sparkle(c, bx + bw - 25*mm, by + 28*mm, 1.8*mm, sp_c)
    if m["stars"] >= 5:
        draw_sparkle(c, bx + 8*mm, by + bh/2, 2.5*mm, sp_c)
        draw_sparkle(c, bx + bw - 8*mm, by + bh/2, 2*mm, sp_c)

    # ヘッダー
    header_h = 24 * mm
    header_y = by + bh - header_h
    c.saveState()
    p = c.beginPath()
    r = 5 * mm
    p.moveTo(bx, header_y); p.lineTo(bx + bw, header_y)
    p.lineTo(bx + bw, by + bh - r)
    p.arcTo(bx + bw - r, by + bh - r, bx + bw, by + bh, 0, 90)
    p.lineTo(bx + r, by + bh)
    p.arcTo(bx, by + bh - r, bx + r, by + bh, 0, 90)
    p.close()
    c.setFillColor(colors["header"]); c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    strip_h = 3 * mm
    c.setFillColor(colors["header_dark"]); c.rect(bx, header_y, bw, strip_h, fill=1, stroke=0)

    c.setFillColor(white); c.setFont(font, 16)
    c.drawCentredString(bx + bw/2, header_y + header_h - 13*mm, "ミッションカード")
    c.setFont(font, 10)
    c.drawCentredString(bx + bw/2, header_y + strip_h + 1.5*mm, f'● {m["card_set"]} ●')
    c.setFillColor(Color(1, 1, 1, 0.6)); c.setFont(font_mono, 10)
    c.drawRightString(bx + bw - 6*mm, header_y + header_h - 13*mm, m["mission_id"])

    # 星
    stars_y = header_y - 12*mm
    star_sp = 13*mm
    sx = bx + bw/2 - 2 * star_sp
    for i in range(5):
        col = colors["star_on"] if i < m["stars"] else colors["star_off"]
        draw_star(c, sx + i * star_sp, stars_y, 5.5*mm, col)
    c.setFillColor(colors["text_light"]); c.setFont(font, 9)
    c.drawCentredString(bx + bw/2, stars_y - 8*mm, f'なんいど {m["difficulty"]}')

    # ミッションバッジ
    mb_y = stars_y - 17*mm
    bw2, bh2 = 42*mm, 8*mm
    draw_rounded_rect(c, bx + bw/2 - bw2/2, mb_y, bw2, bh2, 4*mm, fill_color=colors["accent"])
    c.setFillColor(white); c.setFont(font, 12)
    c.drawCentredString(bx + bw/2, mb_y + 1.5*mm, "ミッション")

    # ミッション本文 (自動フォントサイズ)
    lines = m["mission"].split("\n")
    max_len = max(len(l) for l in lines)
    n = len(lines)
    if n >= 3 or max_len > 18: fs, lh = 12, 6.5*mm
    elif max_len > 14: fs, lh = 14, 7.5*mm
    else: fs, lh = 15, 8*mm
    c.setFillColor(colors["text"]); c.setFont(font, fs)
    mt_y = mb_y - 8*mm
    for line in lines:
        c.drawCentredString(bx + bw/2, mt_y, line)
        mt_y -= lh

    # 区切り線
    sep_y = mt_y - 1*mm
    c.setStrokeColor(colors["border"]); c.setLineWidth(0.8); c.setDash(4, 4)
    lm = 12*mm
    c.line(bx + lm, sep_y, bx + bw/2 - 6*mm, sep_y)
    c.line(bx + bw/2 + 6*mm, sep_y, bx + bw - lm, sep_y)
    c.setDash()
    draw_sparkle(c, bx + bw/2, sep_y, 3*mm, colors["accent"])

    # ルール
    rules_top_y = sep_y - 5*mm
    total_rl = sum(len(r.split("\n")) for r in m["rules"])
    rb_h = 8*mm + total_rl * 5.5*mm + len(m["rules"]) * 1*mm
    rb_y = rules_top_y - rb_h
    draw_rounded_rect(c, bx + 7*mm, rb_y, bw - 14*mm, rb_h, 3*mm, fill_color=colors["rule_bg"])
    c.setFillColor(colors["accent"]); c.setFont(font, 11)
    rl_y = rules_top_y - 6*mm
    c.drawString(bx + 12*mm, rl_y, "【ルール】")
    c.setFillColor(colors["text"]); c.setFont(font, 10)
    r_y = rl_y - 7*mm
    for rule in m["rules"]:
        for j, rline in enumerate(rule.split("\n")):
            prefix = "● " if j == 0 else "　 "
            c.drawString(bx + 14*mm, r_y, f"{prefix}{rline}")
            r_y -= 5.5*mm
        r_y -= 1*mm

    # 宝箱アイコン
    if total_rl >= 5:
        ch_cx, ch_cy, ch_sz = bx + bw - 22*mm, by + 16*mm, 8*mm
    else:
        ch_cx, ch_cy, ch_sz = bx + bw/2, by + 16*mm, 9*mm
    draw_treasure_chest(c, ch_cx, ch_cy, ch_sz, colors["accent"], colors["accent_light"])
    sa = Color(colors["sparkle"].red, colors["sparkle"].green, colors["sparkle"].blue, 0.4)
    draw_sparkle(c, ch_cx - 16*mm, ch_cy + 5*mm, 2*mm, sa)
    draw_sparkle(c, ch_cx + 16*mm, ch_cy + 3*mm, 1.8*mm, sa)
    draw_sparkle(c, ch_cx - 12*mm, ch_cy - 4*mm, 1.5*mm, sa)
    draw_sparkle(c, ch_cx + 13*mm, ch_cy - 5*mm, 2*mm, sa)


# ================================================================
# ミッションカード PDF 生成
# ================================================================

def render_mission_cards(missions, output_path, font, font_mono):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("人間ロボットゲーム ミッションカード")
    card_w, card_h = PAGE_W, PAGE_H / 2
    for i, m in enumerate(missions):
        pos = i % 2
        if pos == 0 and i > 0: c.showPage()
        card_y = PAGE_H / 2 if pos == 0 else 0
        c.setStrokeColor(HexColor("#CCCCCC")); c.setLineWidth(0.5); c.setDash(5, 5)
        c.line(0, PAGE_H / 2, PAGE_W, PAGE_H / 2); c.setDash()
        _draw_card(c, 0, card_y, card_w, card_h, m, font, font_mono)
    c.save()
    n = len(missions)
    print(f"✅ ミッションカード: {output_path}  ({n} 枚 / {math.ceil(n / 2)} ページ)")


# ================================================================
# 運営用解答集 PDF 生成
# ================================================================

def render_staff_reference(missions, output_path, font, start_position="(5,4) 北向き"):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("人間ロボットゲーム 運営用ミッション＆解答集")
    margin = 18 * mm
    usable_w = PAGE_W - 2 * margin
    y = PAGE_H - margin

    def _header():
        nonlocal y
        c.setFont(font, 14); c.setFillColor(black)
        c.drawCentredString(PAGE_W / 2, y, "人間ロボットゲーム 運営用ミッション＆解答集")
        y -= 7 * mm
        c.setFont(font, 8); c.setFillColor(HexColor("#666666"))
        c.drawCentredString(PAGE_W / 2, y, "※ このシートは運営スタッフ用です。参加者には見せないでください。")
        y -= 5 * mm
        c.setFont(font, 8)
        c.drawCentredString(PAGE_W / 2, y, f"スタート: {start_position}")
        y -= 10 * mm

    _header()
    for m in missions:
        colors = COLORS[m["color"]]
        ans_n = len(m["answer"])
        rule_n = sum(len(r.split("\n")) for r in m["rules"])
        needed = 28*mm + ans_n * 4.5*mm + rule_n * 4.5*mm + 10*mm
        if y - needed < margin:
            c.showPage(); y = PAGE_H - margin; _header()

        bar_h = 7.5 * mm
        c.setFillColor(colors["header"])
        c.rect(margin, y - bar_h, usable_w, bar_h, fill=1, stroke=0)
        c.setFillColor(white); c.setFont(font, 9)
        stars = "★" * m["stars"] + "☆" * (5 - m["stars"])
        c.drawString(margin + 3*mm, y - bar_h + 1.8*mm,
                     f'{m["mission_id"]}　難易度{m["difficulty"]} {stars}　（{m["card_set"]}）')
        y -= bar_h + 3*mm

        c.setFillColor(black); c.setFont(font, 9)
        mt = m["mission"].replace("\n", " ")
        c.drawString(margin + 3*mm, y, f"【ミッション】{mt}")
        y -= 6*mm

        c.setFont(font, 7.5); c.setFillColor(HexColor("#444444"))
        c.drawString(margin + 3*mm, y, "【ルール】"); y -= 4.5*mm
        for rule in m["rules"]:
            c.drawString(margin + 7*mm, y, f'・{rule.replace(chr(10), "")}')
            y -= 4*mm
        y -= 2*mm

        c.setFillColor(HexColor("#1A5C1A")); c.setFont(font, 8.5)
        c.drawString(margin + 3*mm, y, "【解答例】"); y -= 5*mm
        c.setFont(font, 7.5)
        for ai, step in enumerate(m["answer"]):
            if "クリア" in step:
                c.setFillColor(HexColor("#C0392B")); c.setFont(font, 8)
            else:
                c.setFillColor(HexColor("#333333")); c.setFont(font, 7.5)
            c.drawString(margin + 7*mm, y, f"{ai + 1:>2}. {step}")
            y -= 4.5*mm
        y -= 5*mm
        c.setStrokeColor(HexColor("#CCCCCC")); c.setLineWidth(0.5)
        c.line(margin, y + 2*mm, margin + usable_w, y + 2*mm)

    c.save()
    print(f"✅ 運営用解答集: {output_path}  ({len(missions)} 問)")


# ================================================================
# メイン
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="人間ロボットゲーム ミッションカード PDF 生成")
    parser.add_argument("-i", "--input", default="missions.yaml",
                        help="ミッションデータ YAML ファイル (default: missions.yaml)")
    parser.add_argument("-o", "--output-dir", default="output",
                        help="出力ディレクトリ (default: output/)")
    parser.add_argument("--cards-only", action="store_true", help="ミッションカードのみ生成")
    parser.add_argument("--staff-only", action="store_true", help="運営用解答集のみ生成")
    args = parser.parse_args()

    yaml_path = Path(args.input)
    if not yaml_path.exists():
        print(f"❌ ファイルが見つかりません: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    missions = data["missions"]
    start_position = data.get("start_position", "(5,4) 北向き")
    print(f"📖 {yaml_path} を読み込みました ({len(missions)} ミッション)")

    font = _find_font(_FONT_CANDIDATES, "JPFont")
    font_mono = _find_font(_FONT_MONO_CANDIDATES, "JPFontMono")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.staff_only:
        render_mission_cards(missions, str(out_dir / "mission_cards.pdf"), font, font_mono)
    if not args.cards_only:
        render_staff_reference(missions, str(out_dir / "staff_reference.pdf"), font, start_position)

    print(f"\n🎉 完了！ 出力先: {out_dir}/")


if __name__ == "__main__":
    main()
