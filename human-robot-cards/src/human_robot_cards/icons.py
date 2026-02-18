"""カードに描画するアイコン関数群。

新しいアイコンを追加するには:
1. draw_xxx(c, cx, cy, size, color) 関数を定義
2. ICON_REGISTRY に "xxx": draw_xxx を追加
cards.yaml の icon: xxx で参照可能になります。
"""

from __future__ import annotations

import math

from reportlab.lib.colors import HexColor, white


def draw_arrow_up(c, cx, cy, size, color):
    """前進アイコン（上向き矢印）"""
    c.setFillColor(color)
    s = size
    path = c.beginPath()
    path.moveTo(cx, cy + s * 0.5)
    path.lineTo(cx - s * 0.35, cy - s * 0.1)
    path.lineTo(cx - s * 0.12, cy - s * 0.1)
    path.lineTo(cx - s * 0.12, cy - s * 0.5)
    path.lineTo(cx + s * 0.12, cy - s * 0.5)
    path.lineTo(cx + s * 0.12, cy - s * 0.1)
    path.lineTo(cx + s * 0.35, cy - s * 0.1)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_turn_right(c, cx, cy, size, color):
    """右向き矢印"""
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    s = size
    path = c.beginPath()
    path.moveTo(cx - s * 0.3, cy - s * 0.3)
    path.lineTo(cx - s * 0.3, cy + s * 0.15)
    path.lineTo(cx + s * 0.1, cy + s * 0.15)
    c.drawPath(path, fill=0, stroke=1)
    path2 = c.beginPath()
    path2.moveTo(cx + s * 0.1, cy + s * 0.35)
    path2.lineTo(cx + s * 0.35, cy + s * 0.15)
    path2.lineTo(cx + s * 0.1, cy - s * 0.05)
    path2.close()
    c.drawPath(path2, fill=1, stroke=0)


def draw_turn_left(c, cx, cy, size, color):
    """左向き矢印"""
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    s = size
    path = c.beginPath()
    path.moveTo(cx + s * 0.3, cy - s * 0.3)
    path.lineTo(cx + s * 0.3, cy + s * 0.15)
    path.lineTo(cx - s * 0.1, cy + s * 0.15)
    c.drawPath(path, fill=0, stroke=1)
    path2 = c.beginPath()
    path2.moveTo(cx - s * 0.1, cy + s * 0.35)
    path2.lineTo(cx - s * 0.35, cy + s * 0.15)
    path2.lineTo(cx - s * 0.1, cy - s * 0.05)
    path2.close()
    c.drawPath(path2, fill=1, stroke=0)


def draw_turn_back(c, cx, cy, size, color):
    """Uターン矢印"""
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    s = size
    path = c.beginPath()
    path.moveTo(cx - s * 0.2, cy + s * 0.3)
    path.lineTo(cx - s * 0.2, cy - s * 0.15)
    c.drawPath(path, fill=0, stroke=1)
    c.arc(cx - s * 0.2, cy - s * 0.35, cx + s * 0.2, cy + s * 0.05, 180, 180)
    path2 = c.beginPath()
    path2.moveTo(cx + s * 0.2, cy - s * 0.15)
    path2.lineTo(cx + s * 0.2, cy + s * 0.1)
    c.drawPath(path2, fill=0, stroke=1)
    path3 = c.beginPath()
    path3.moveTo(cx + s * 0.02, cy + s * 0.1)
    path3.lineTo(cx + s * 0.2, cy + s * 0.35)
    path3.lineTo(cx + s * 0.38, cy + s * 0.1)
    path3.close()
    c.drawPath(path3, fill=1, stroke=0)


def draw_treasure(c, cx, cy, size, color):
    """宝箱アイコン"""
    s = size
    c.setFillColor(color)
    c.roundRect(cx - s * 0.35, cy - s * 0.35, s * 0.7, s * 0.45, 2, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFD700"))
    path = c.beginPath()
    path.moveTo(cx - s * 0.38, cy + s * 0.1)
    path.lineTo(cx - s * 0.3, cy + s * 0.35)
    path.lineTo(cx + s * 0.3, cy + s * 0.35)
    path.lineTo(cx + s * 0.38, cy + s * 0.1)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFA000"))
    c.circle(cx, cy, s * 0.08, fill=1, stroke=0)


def draw_loop_start(c, cx, cy, size, color):
    """ループ開始アイコン（回転矢印）"""
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.8)
    s = size
    c.arc(cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3, 30, 280)
    angle = math.radians(30)
    ax = cx + s * 0.3 * math.cos(angle)
    ay = cy + s * 0.3 * math.sin(angle)
    path = c.beginPath()
    path.moveTo(ax + s * 0.15, ay + s * 0.05)
    path.lineTo(ax - s * 0.02, ay + s * 0.15)
    path.lineTo(ax - s * 0.02, ay - s * 0.1)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_loop_end(c, cx, cy, size, color):
    """ループ終了アイコン"""
    c.setFillColor(color)
    s = size
    c.roundRect(cx - s * 0.28, cy - s * 0.28, s * 0.56, s * 0.56, 4, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(cx - s * 0.15, cy - s * 0.15, s * 0.3, s * 0.3, 2, fill=1, stroke=0)


def draw_point(c, cx, cy, size, color):
    """ポイントアイコン（星）"""
    c.setFillColor(HexColor("#FFD700"))
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    s = size
    points = []
    for i in range(5):
        angle = math.radians(90 + i * 72)
        points.append((cx + s * 0.35 * math.cos(angle), cy + s * 0.35 * math.sin(angle)))
        angle = math.radians(90 + i * 72 + 36)
        points.append((cx + s * 0.15 * math.cos(angle), cy + s * 0.15 * math.sin(angle)))
    path = c.beginPath()
    path.moveTo(points[0][0], points[0][1])
    for p in points[1:]:
        path.lineTo(p[0], p[1])
    path.close()
    c.drawPath(path, fill=1, stroke=1)


def draw_variable_step(c, cx, cy, size, color):
    """変数マス数アイコン（足跡+?）"""
    c.setFillColor(color)
    s = size
    c.ellipse(cx - s * 0.15, cy - s * 0.3, cx + s * 0.15, cy + s * 0.15, fill=1, stroke=0)
    c.circle(cx - s * 0.18, cy + s * 0.25, s * 0.08, fill=1, stroke=0)
    c.circle(cx - s * 0.05, cy + s * 0.3, s * 0.08, fill=1, stroke=0)
    c.circle(cx + s * 0.1, cy + s * 0.28, s * 0.08, fill=1, stroke=0)
    c.circle(cx + s * 0.2, cy + s * 0.2, s * 0.07, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("IPAGothic", s * 0.3)
    c.drawCentredString(cx, cy - s * 0.18, "?")


def draw_condition(c, cx, cy, size, color):
    """条件分岐アイコン（ひし形）"""
    c.setFillColor(color)
    s = size
    path = c.beginPath()
    path.moveTo(cx, cy + s * 0.4)
    path.lineTo(cx + s * 0.35, cy)
    path.lineTo(cx, cy - s * 0.4)
    path.lineTo(cx - s * 0.35, cy)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("IPAGothic", s * 0.28)
    c.drawCentredString(cx, cy - s * 0.1, "?")


# --- アイコン名 → 描画関数 のレジストリ ---
# cards.yaml の icon: に指定する名前をここに登録する
ICON_REGISTRY: dict[str, callable] = {
    "arrow_up": draw_arrow_up,
    "turn_right": draw_turn_right,
    "turn_left": draw_turn_left,
    "turn_back": draw_turn_back,
    "treasure": draw_treasure,
    "loop_start": draw_loop_start,
    "loop_end": draw_loop_end,
    "point": draw_point,
    "variable_step": draw_variable_step,
    "condition": draw_condition,
}
