import argparse
import math

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

OUT = "takarabako_flyer_kids_4up_landscape_final.pdf"
PANELS_PER_PAGE = 4

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
FONT = "HeiseiKakuGo-W5"


BAR_COLOR = colors.HexColor("#046E74")
CARD_LEFT_BG = colors.HexColor("#C9D9DE")
CARD_RIGHT_BG = colors.HexColor("#E9E2D9")
CARD_SHADOW = colors.HexColor("#DDE1E3")
PILL_LEFT = colors.HexColor("#04656D")
PILL_RIGHT = colors.HexColor("#CB8500")
TEXT_MAIN = colors.HexColor("#08333E")
TEXT_LEFT_SUB = colors.HexColor("#0C6670")
TEXT_RIGHT_SUB = colors.HexColor("#9A6308")
PHONE_STROKE = colors.HexColor("#59AAB0")
CARD_STROKE = colors.HexColor("#D18A0D")


def round_rect(c, x, y, w, h, r, fill=1, stroke=0):
    c.roundRect(x, y, w, h, r, fill=fill, stroke=stroke)


def draw_centered_lines(c, cx, start_y, lines, font_size, leading, color):
    c.setFillColor(color)
    c.setFont(FONT, font_size)
    y = start_y
    for line in lines:
        c.drawCentredString(cx, y, line)
        y -= leading


def draw_treasure_icon(c, x, y, w, h):
    lid_h = h * 0.45
    c.setFillColor(colors.HexColor("#F7C957"))
    round_rect(c, x, y, w, h, r=h * 0.30, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#FFD96A"))
    round_rect(c, x, y + h - lid_h, w, lid_h, r=h * 0.24, fill=1, stroke=0)

    band_w = w * 0.10
    c.setFillColor(colors.HexColor("#D6AB3F"))
    c.rect(x + (w - band_w) / 2, y, band_w, h, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#B28B2F"))
    c.circle(x + w / 2, y + h * 0.52, h * 0.10, fill=1, stroke=0)


def draw_phone_icon(c, x, y, w, h):
    c.setStrokeColor(PHONE_STROKE)
    c.setLineWidth(2.2)
    round_rect(c, x, y, w, h, r=w * 0.22, fill=0, stroke=1)
    c.circle(x + w / 2, y + h * 0.84, w * 0.04, fill=0, stroke=1)


def draw_card_icon(c, x, y, w, h):
    c.setStrokeColor(CARD_STROKE)
    c.setLineWidth(2.2)
    round_rect(c, x, y, w, h, r=h * 0.16, fill=0, stroke=1)
    line_x0 = x + w * 0.22
    line_x1 = x + w * 0.78
    for ratio in (0.30, 0.50, 0.70):
        yy = y + h * ratio
        c.line(line_x0, yy, line_x1, yy)


def draw_action_card(c, x, y, w, h, with_phone):
    if with_phone:
        bg = CARD_LEFT_BG
        pill_color = PILL_LEFT
        pill_label = "スマホあり"
        main_lines = ("はこのなかの", "QRコードを", "よみとる")
        sub_line = "カメラで ぴっ！"
        sub_color = TEXT_LEFT_SUB
    else:
        bg = CARD_RIGHT_BG
        pill_color = PILL_RIGHT
        pill_label = "スマホなし"
        main_lines = ("はこのなかの", "おたからカードを", "とる")
        sub_line = "カードを 1まい"
        sub_color = TEXT_RIGHT_SUB

    c.setFillColor(CARD_SHADOW)
    round_rect(c, x + 3, y - 3, w, h, r=22, fill=1, stroke=0)
    c.setFillColor(bg)
    round_rect(c, x, y, w, h, r=22, fill=1, stroke=0)

    pill_h = 9.6 * mm
    pill_w = w * 0.82
    pill_x = x + (w - pill_w) / 2
    pill_y = y + h - pill_h - 2.6 * mm
    c.setFillColor(pill_color)
    round_rect(c, pill_x, pill_y, pill_w, pill_h, r=pill_h / 2, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont(FONT, 17)
    c.drawCentredString(x + w / 2, pill_y + 2.5 * mm, pill_label)

    icon_y = y + h * 0.47
    if with_phone:
        icon_w = 16 * mm
        icon_h = 22 * mm
        draw_phone_icon(c, x + (w - icon_w) / 2, icon_y, icon_w, icon_h)
    else:
        icon_w = 18 * mm
        icon_h = 12 * mm
        draw_card_icon(c, x + (w - icon_w) / 2, icon_y + 3 * mm, icon_w, icon_h)

    draw_centered_lines(
        c,
        x + w / 2,
        y + h * 0.36,
        main_lines,
        font_size=20,
        leading=7.4 * mm,
        color=TEXT_MAIN,
    )

    c.setFillColor(sub_color)
    c.setFont(FONT, 14)
    c.drawCentredString(x + w / 2, y + 5.5 * mm, sub_line)


def draw_panel(c, x, y, w, h, no_text):
    side_pad = 3 * mm
    top_pad = 3 * mm
    bottom_pad = 3 * mm

    banner_x = x + side_pad
    banner_w = w - 2 * side_pad
    banner_h = 16 * mm
    banner_y = y + h - top_pad - banner_h
    c.setFillColor(BAR_COLOR)
    c.rect(banner_x, banner_y, banner_w, banner_h, fill=1, stroke=0)

    chest_w = 16 * mm
    chest_h = 10 * mm
    chest_x = banner_x + 3 * mm
    chest_y = banner_y + (banner_h - chest_h) / 2
    draw_treasure_icon(c, chest_x, chest_y, chest_w, chest_h)

    c.setFillColor(colors.white)
    c.setFont(FONT, 24)
    c.drawString(banner_x + 28 * mm, banner_y + 4.5 * mm, "たからばこ")
    c.setFillColor(colors.HexColor("#B9D5D8"))
    c.setFont(FONT, 9)
    c.drawRightString(
        banner_x + banner_w - 3.0 * mm, banner_y + 6.2 * mm, f"No.{no_text}"
    )

    cards_gap = 5 * mm
    cards_top = banner_y - 3.5 * mm
    cards_bottom = y + bottom_pad
    cards_h = cards_top - cards_bottom
    card_w = (banner_w - cards_gap) / 2

    draw_action_card(c, banner_x, cards_bottom, card_w, cards_h, with_phone=True)
    draw_action_card(
        c,
        banner_x + card_w + cards_gap,
        cards_bottom,
        card_w,
        cards_h,
        with_phone=False,
    )


def build_alpha_labels(count):
    labels = []
    for i in range(count):
        n = i
        name = ""
        while True:
            n, r = divmod(n, 26)
            name = chr(ord("A") + r) + name
            if n == 0:
                break
            n -= 1
        labels.append(name)
    return labels


def resolve_labels(count, labels_arg):
    if labels_arg:
        labels = [item.strip() for item in labels_arg.split(",") if item.strip()]
        if not labels:
            raise ValueError("--labels が空です。例: --labels A,B,C")
        return labels

    if count <= 0:
        raise ValueError("--count は 1 以上を指定してください")
    return build_alpha_labels(count)


def panel_position(index, cell_w, cell_h, margin):
    layout = [
        (0, 1),  # left-top
        (1, 1),  # right-top
        (0, 0),  # left-bottom
        (1, 0),  # right-bottom
    ]
    col, row = layout[index]
    x = col * cell_w + margin / 2
    y = row * cell_h + margin / 2
    w = cell_w - margin
    h = cell_h - margin
    return x, y, w, h


def draw_guides(c, pw, ph):
    c.setStrokeColor(colors.HexColor("#B7B7B7"))
    c.setLineWidth(0.5)
    c.line(pw / 2, 0, pw / 2, ph)
    c.line(0, ph / 2, pw, ph / 2)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate treasure-box flyer PDF")
    parser.add_argument(
        "--count",
        type=int,
        default=PANELS_PER_PAGE,
        help="生成する配布資料の数（--labels 未指定時に使用）",
    )
    parser.add_argument(
        "--labels",
        type=str,
        default="A,B,C,D,E,F,G",
        help="No の一覧（カンマ区切り）。例: A,B,C",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    labels = resolve_labels(args.count, args.labels)

    pw, ph = landscape(A4)
    c = canvas.Canvas(OUT, pagesize=(pw, ph))
    cell_w = pw / 2
    cell_h = ph / 2
    margin = 4 * mm
    pages = math.ceil(len(labels) / PANELS_PER_PAGE)

    for page in range(pages):
        c.setFillColor(colors.HexColor("#E6E6E6"))
        c.rect(0, 0, pw, ph, fill=1, stroke=0)

        start = page * PANELS_PER_PAGE
        end = min(start + PANELS_PER_PAGE, len(labels))

        for offset, label in enumerate(labels[start:end]):
            x, y, w, h = panel_position(offset, cell_w, cell_h, margin)
            draw_panel(c, x, y, w, h, label)

        draw_guides(c, pw, ph)
        c.showPage()

    c.save()
    print(f"Wrote: {OUT} (items={len(labels)}, pages={pages})")


if __name__ == "__main__":
    main()
