#!/usr/bin/env python3
"""
人間ロボットゲーム フィールドマップ PDF 生成
YAMLファイルからマップ定義を読み込み、宝の地図風PDFを出力する。
"""

from __future__ import annotations

import argparse
import glob
import os
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# ============================================================
# データモデル
# ============================================================
@dataclass
class MapConfig:
    """YAMLから読み込むマップ設定。"""

    rows: int = 5
    cols: int = 10
    title: str = "人間ロボットゲーム"
    subtitle: str = "〜 フィールドマップ 〜"
    treasures: dict[tuple[int, int], str] = field(default_factory=dict)
    start: tuple[int, int] = (5, 4)
    obstacles: list[tuple[int, int]] = field(default_factory=list)
    output: str = "field_map.pdf"

    @classmethod
    def from_yaml(cls, path: str | Path) -> MapConfig:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        cfg = cls()
        grid = data.get("grid", {})
        cfg.rows = grid.get("rows", cfg.rows)
        cfg.cols = grid.get("cols", cfg.cols)
        cfg.title = data.get("title", cfg.title)
        cfg.subtitle = data.get("subtitle", cfg.subtitle)

        cfg.treasures = {}
        for t in data.get("treasures", []):
            pos = tuple(t["pos"])
            cfg.treasures[pos] = t["label"]

        s = data.get("start", [5, 4])
        cfg.start = (s[0], s[1])

        cfg.obstacles = [tuple(o) for o in data.get("obstacles", [])]
        cfg.output = data.get("output", cfg.output)
        return cfg


# ============================================================
# フォント解決
# ============================================================
_JP_FONT_NAME = "JP"


def _register_jp_font() -> str:
    """日本語フォントを検索・登録し、フォント名を返す。"""
    candidates = [
        # macOS
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    candidates += glob.glob("/usr/share/fonts/**/Noto*CJK*.ttf", recursive=True)
    candidates += glob.glob("/usr/share/fonts/**/Noto*CJK*.ttc", recursive=True)

    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(_JP_FONT_NAME, path))
                return _JP_FONT_NAME
            except Exception:
                continue

    print(
        "⚠  日本語フォントが見つかりません。Helveticaで代替します。",
        file=sys.stderr,
    )
    print(
        "   Ubuntu: sudo apt install fonts-noto-cjk",
        file=sys.stderr,
    )
    print(
        "   macOS:  標準搭載フォントが使われるはずです",
        file=sys.stderr,
    )
    return "Helvetica"


# ============================================================
# カラーパレット
# ============================================================
class Colors:
    BORDER = HexColor("#6B4226")
    TITLE = HexColor("#3A1A05")
    GRID_LINE = HexColor("#C4A882")
    DECO = HexColor("#7A5230")
    TREASURE_LABEL = HexColor("#8B0000")
    START_BLUE = HexColor("#2E5090")
    START_LIGHT = HexColor("#C8D8E8")
    OBSTACLE_RED = HexColor("#8B2500")
    GOLD = HexColor("#DAA520")
    TEXT_BROWN = HexColor("#5C3A1E")


# ============================================================
# レイアウト計算
# ============================================================
@dataclass
class Layout:
    """ページ内の各要素の座標を保持する。"""

    page_w: float
    page_h: float
    grid_x: float
    grid_y: float
    grid_w: float
    grid_h: float
    cell_w: float
    cell_h: float
    rows: int
    cols: int
    title_h: float
    legend_h: float

    @classmethod
    def compute(cls, cfg: MapConfig) -> Layout:
        page_w, page_h = A4[1], A4[0]  # landscape
        title_h = 42 * mm
        legend_h = 18 * mm
        pad_x = 8 * mm
        pad_y = 4 * mm
        cell_w = (page_w - 2 * pad_x) / cfg.cols
        cell_h = (page_h - title_h - legend_h - 2 * pad_y) / cfg.rows
        grid_x = pad_x
        grid_y = legend_h + pad_y
        return cls(
            page_w=page_w,
            page_h=page_h,
            grid_x=grid_x,
            grid_y=grid_y,
            grid_w=cfg.cols * cell_w,
            grid_h=cfg.rows * cell_h,
            cell_w=cell_w,
            cell_h=cell_h,
            rows=cfg.rows,
            cols=cfg.cols,
            title_h=title_h,
            legend_h=legend_h,
        )

    def rc_to_xy(self, row: int, col: int) -> tuple[float, float]:
        """(行, 列) → セル左下座標。"""
        x = self.grid_x + (col - 1) * self.cell_w
        y = self.grid_y + (self.rows - row) * self.cell_h
        return x, y

    def rc_center(self, row: int, col: int) -> tuple[float, float]:
        """(行, 列) → セル中心座標。"""
        x, y = self.rc_to_xy(row, col)
        return x + self.cell_w / 2, y + self.cell_h / 2


# ============================================================
# 描画関数
# ============================================================
class MapRenderer:
    """フィールドマップを描画するレンダラー。"""

    def __init__(self, c: canvas.Canvas, layout: Layout, font: str):
        self.c = c
        self.L = layout
        self.font = font

    # --- 背景 ---
    def draw_parchment(self) -> None:
        c, L = self.c, self.L
        c.setFillColor(HexColor("#F5EAD4"))
        c.rect(0, 0, L.page_w, L.page_h, fill=1, stroke=0)

        rng = random.Random(42)
        for _ in range(800):
            x = rng.uniform(0, L.page_w)
            y = rng.uniform(0, L.page_h)
            r = rng.uniform(0.3, 2.0)
            c.setFillColor(Color(0.6, 0.4, 0.2, rng.uniform(0.02, 0.07)))
            c.circle(x, y, r, fill=1, stroke=0)

        for i in range(6):
            c.setStrokeColor(Color(0.3, 0.18, 0.08, 0.02 * (6 - i)))
            c.setLineWidth(14)
            m = i * 7
            c.rect(m, m, L.page_w - 2 * m, L.page_h - 2 * m, fill=0, stroke=1)

        c.setFillColor(Color(0.95, 0.90, 0.78, 0.35))
        c.rect(L.grid_x, L.grid_y, L.grid_w, L.grid_h, fill=1, stroke=0)

    # --- 枠線 ---
    def draw_border(self) -> None:
        c, L = self.c, self.L
        pad = 5
        c.saveState()
        c.setStrokeColor(Colors.BORDER)
        c.setLineWidth(3.5)
        c.rect(
            L.grid_x - pad, L.grid_y - pad,
            L.grid_w + 2 * pad, L.grid_h + 2 * pad,
            fill=0, stroke=1,
        )
        ip = 3.5
        c.setLineWidth(1.2)
        c.rect(
            L.grid_x - pad + ip, L.grid_y - pad + ip,
            L.grid_w + 2 * pad - 2 * ip, L.grid_h + 2 * pad - 2 * ip,
            fill=0, stroke=1,
        )

        corners = [
            (L.grid_x - pad, L.grid_y - pad),
            (L.grid_x - pad + L.grid_w + 2 * pad, L.grid_y - pad),
            (L.grid_x - pad, L.grid_y - pad + L.grid_h + 2 * pad),
            (L.grid_x - pad + L.grid_w + 2 * pad, L.grid_y - pad + L.grid_h + 2 * pad),
        ]
        for cx, cy in corners:
            c.setFillColor(Colors.BORDER)
            c.circle(cx, cy, 6, fill=1, stroke=0)
            c.setFillColor(Colors.GOLD)
            c.circle(cx, cy, 3, fill=1, stroke=0)
        c.restoreState()

    # --- グリッド線 ---
    def draw_grid(self) -> None:
        c, L = self.c, self.L
        c.saveState()
        c.setStrokeColor(Colors.GRID_LINE)
        c.setLineWidth(0.5)
        c.setDash(5, 4)
        for i in range(1, L.cols):
            x = L.grid_x + i * L.cell_w
            c.line(x, L.grid_y, x, L.grid_y + L.grid_h)
        for j in range(1, L.rows):
            y = L.grid_y + j * L.cell_h
            c.line(L.grid_x, y, L.grid_x + L.grid_w, y)
        c.restoreState()

    # --- 宝箱アイコン ---
    def draw_chest(self, cx: float, cy: float, scale: float = 1.0) -> None:
        c = self.c
        c.saveState()
        s = scale * 0.32 * min(self.L.cell_w, self.L.cell_h)

        c.setFillColor(Color(0.3, 0.2, 0.1, 0.12))
        c.ellipse(cx - s * 1.1, cy - s * 0.95, cx + s * 1.1, cy - s * 0.5, fill=1, stroke=0)

        bx, by, bw, bh = cx - s, cy - s * 0.6, s * 2, s * 1.2

        c.setFillColor(HexColor("#8B5E3C"))
        c.setStrokeColor(HexColor("#5C3317"))
        c.setLineWidth(1.4)
        c.rect(bx, by, bw, bh * 0.55, fill=1, stroke=1)

        c.setFillColor(HexColor("#A0724A"))
        lid_y = by + bh * 0.55
        c.rect(bx, lid_y, bw, bh * 0.38, fill=1, stroke=1)

        c.setStrokeColor(HexColor("#C4955A"))
        c.setLineWidth(0.7)
        c.line(bx + 2, lid_y + bh * 0.32, bx + bw - 2, lid_y + bh * 0.32)

        c.setStrokeColor(Colors.GOLD)
        c.setLineWidth(2)
        c.line(bx, by + bh * 0.22, bx + bw, by + bh * 0.22)

        cs = s * 0.22
        c.setFillColor(HexColor("#FFD700"))
        c.setStrokeColor(HexColor("#B8860B"))
        c.setLineWidth(1)
        c.rect(cx - cs, lid_y - cs * 0.4, cs * 2, cs * 1.6, fill=1, stroke=1)
        c.setFillColor(HexColor("#5C3317"))
        c.circle(cx, lid_y + cs * 0.35, cs * 0.25, fill=1, stroke=0)

        c.setStrokeColor(Colors.GOLD)
        c.setLineWidth(1)
        for sx, sy in [
            (cx - s * 1.3, cy + s * 0.4),
            (cx + s * 1.3, cy + s * 0.6),
            (cx - s * 0.9, cy + s * 0.9),
            (cx + s * 1.0, cy - s * 0.05),
        ]:
            sp = s * 0.14
            c.line(sx - sp, sy, sx + sp, sy)
            c.line(sx, sy - sp, sx, sy + sp)

        c.restoreState()

    # --- ロボット(スタート)アイコン ---
    def draw_robot(self, cx: float, cy: float, scale: float = 1.0) -> None:
        c = self.c
        c.saveState()
        s = scale * 0.35 * min(self.L.cell_w, self.L.cell_h)

        c.setFillColor(Colors.START_BLUE)
        c.setStrokeColor(HexColor("#1A3260"))
        c.setLineWidth(2.5)
        c.circle(cx, cy, s * 1.15, fill=1, stroke=1)

        c.setFillColor(Colors.START_LIGHT)
        c.circle(cx, cy, s * 0.72, fill=1, stroke=0)

        c.setFillColor(Colors.START_BLUE)
        c.circle(cx - s * 0.26, cy + s * 0.1, s * 0.13, fill=1, stroke=0)
        c.circle(cx + s * 0.26, cy + s * 0.1, s * 0.13, fill=1, stroke=0)
        c.setStrokeColor(Colors.START_BLUE)
        c.setLineWidth(1.4)
        c.line(cx - s * 0.22, cy - s * 0.18, cx + s * 0.22, cy - s * 0.18)

        c.setLineWidth(1.8)
        c.line(cx, cy + s * 0.72, cx, cy + s * 1.05)
        c.setFillColor(HexColor("#FF4444"))
        c.circle(cx, cy + s * 1.05, s * 0.09, fill=1, stroke=0)

        c.restoreState()

    # --- 障害物アイコン ---
    def draw_obstacle(self, cx: float, cy: float, scale: float = 1.0) -> None:
        c = self.c
        c.saveState()
        s = scale * 0.32 * min(self.L.cell_w, self.L.cell_h)

        c.setFillColor(Color(0.55, 0.15, 0, 0.12))
        c.circle(cx, cy, s * 1.2, fill=1, stroke=0)

        c.setStrokeColor(Colors.OBSTACLE_RED)
        c.setLineCap(1)
        c.setLineWidth(4)
        c.line(cx - s, cy - s, cx + s, cy + s)
        c.line(cx - s, cy + s, cx + s, cy - s)

        c.setLineWidth(2)
        c.circle(cx, cy, s * 1.15, fill=0, stroke=1)
        c.restoreState()

    # --- コンパスローズ ---
    def draw_compass(self, cx: float, cy: float, size: float) -> None:
        c = self.c
        c.saveState()
        s = size

        c.setStrokeColor(Colors.DECO)
        c.setFillColor(Color(0.94, 0.88, 0.76, 0.8))
        c.setLineWidth(1.5)
        c.circle(cx, cy, s, fill=1, stroke=1)
        c.setLineWidth(0.8)
        c.circle(cx, cy, s * 0.3, fill=0, stroke=1)

        for dx, dy, label in [(0, 1, "N"), (1, 0, "E"), (0, -1, "S"), (-1, 0, "W")]:
            c.setStrokeColor(Colors.DECO)
            c.setLineWidth(1.5)
            c.line(cx, cy, cx + dx * s * 0.85, cy + dy * s * 0.85)
            c.setFont(self.font, 6)
            c.setFillColor(Colors.DECO)
            c.drawCentredString(cx + dx * s * 0.65, cy + dy * s * 0.65 - 2, label)

        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = dx * 0.707, dy * 0.707
            c.setStrokeColor(Colors.DECO)
            c.setLineWidth(0.8)
            c.line(cx + nx * s * 0.3, cy + ny * s * 0.3, cx + nx * s * 0.6, cy + ny * s * 0.6)

        c.setFillColor(HexColor("#8B0000"))
        p = c.beginPath()
        p.moveTo(cx, cy + s * 0.85)
        p.lineTo(cx - s * 0.1, cy + s * 0.15)
        p.lineTo(cx, cy + s * 0.25)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

        c.setFillColor(Colors.DECO)
        p = c.beginPath()
        p.moveTo(cx, cy - s * 0.85)
        p.lineTo(cx + s * 0.1, cy - s * 0.15)
        p.lineTo(cx, cy - s * 0.25)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

        c.restoreState()

    # --- タイトル ---
    def draw_title(self, title: str, subtitle: str) -> None:
        c, L = self.c, self.L
        c.saveState()
        ty = L.page_h - 18 * mm

        c.setFont(self.font, 36)
        c.setFillColor(Colors.TITLE)
        tw = c.stringWidth(title, self.font, 36)
        c.drawString((L.page_w - tw) / 2, ty, title)

        c.setFont(self.font, 18)
        c.setFillColor(Colors.TEXT_BROWN)
        sw = c.stringWidth(subtitle, self.font, 18)
        c.drawString((L.page_w - sw) / 2, ty - 22, subtitle)

        cx = L.page_w / 2
        line_y = ty + 7
        c.setStrokeColor(Colors.DECO)
        for sign in (-1, 1):
            c.setLineWidth(1.2)
            c.line(cx + sign * (tw / 2 + 15), line_y, cx + sign * (tw / 2 + 80), line_y)
            c.setLineWidth(0.5)
            c.line(cx + sign * (tw / 2 + 15), line_y + 3.5, cx + sign * (tw / 2 + 65), line_y + 3.5)
            ox = cx + sign * (tw / 2 + 85)
            c.setFillColor(Colors.GOLD)
            p = c.beginPath()
            p.moveTo(ox, line_y + 1.5)
            p.lineTo(ox + sign * 5, line_y + 6)
            p.lineTo(ox + sign * 10, line_y + 1.5)
            p.lineTo(ox + sign * 5, line_y - 3)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

        c.restoreState()

    # --- 凡例 ---
    def draw_legend(self) -> None:
        c, L = self.c, self.L
        c.saveState()
        ly = 5 * mm
        total_w = 620
        lx = (L.page_w - total_w) / 2
        s = 0.55

        self.draw_chest(lx + 14, ly + 7, scale=s)
        c.setFont(self.font, 11)
        c.setFillColor(Colors.TEXT_BROWN)
        c.drawString(lx + 32, ly + 2, "= たからもの")

        sx = lx + 175
        self.draw_robot(sx + 14, ly + 7, scale=s)
        c.drawString(sx + 32, ly + 2, "= スタート地点")

        ox = sx + 170
        self.draw_obstacle(ox + 14, ly + 7, scale=s)
        c.drawString(ox + 32, ly + 2, "= 障害物（通れません）")

        c.restoreState()

    # --- 薄い点線トレイル（装飾） ---
    def draw_trails(self, cfg: MapConfig) -> None:
        c, L = self.c, self.L
        if len(cfg.treasures) < 2:
            return

        c.saveState()
        c.setStrokeColor(Color(0.6, 0.4, 0.2, 0.15))
        c.setLineWidth(0.8)
        c.setDash(2, 6)

        positions = list(cfg.treasures.keys())
        # スタートから最も近い宝へ
        sx, sy = L.rc_center(*cfg.start)
        for pos in positions[:2]:
            tx, ty = L.rc_center(*pos)
            c.line(sx, sy, tx, ty)
        # 宝同士をいくつか繋ぐ
        for i in range(min(3, len(positions) - 1)):
            x1, y1 = L.rc_center(*positions[i])
            x2, y2 = L.rc_center(*positions[i + 1])
            c.line(x1, y1, x2, y2)

        c.restoreState()

    # --- メイン描画 ---
    def render(self, cfg: MapConfig) -> None:
        c, L = self.c, self.L

        # 1. 背景
        self.draw_parchment()

        # 2. タイトル
        self.draw_title(cfg.title, cfg.subtitle)

        # 3. グリッド＋枠
        self.draw_grid()
        self.draw_border()

        # 4. たからもの
        for (row, col), label in cfg.treasures.items():
            cx, cy = L.rc_center(row, col)
            self.draw_chest(cx, cy + L.cell_h * 0.08)

            c.saveState()
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(Colors.TREASURE_LABEL)
            lw = c.stringWidth(label, "Helvetica-Bold", 20)
            _, cell_y = L.rc_to_xy(row, col)
            c.drawString(cx - lw / 2, cell_y + 4, label)
            c.restoreState()

        # 5. スタート
        sx, sy = L.rc_center(*cfg.start)
        self.draw_robot(sx, sy + L.cell_h * 0.06)
        c.saveState()
        c.setFont(self.font, 12)
        c.setFillColor(Colors.START_BLUE)
        st = "スタート"
        stw = c.stringWidth(st, self.font, 12)
        _, cell_y = L.rc_to_xy(*cfg.start)
        c.drawString(sx - stw / 2, cell_y + 3, st)
        c.restoreState()

        # 6. 障害物
        for row, col in cfg.obstacles:
            ox, oy = L.rc_center(row, col)
            self.draw_obstacle(ox, oy + L.cell_h * 0.04)

            c.saveState()
            c.setFont(self.font, 10)
            c.setFillColor(Colors.OBSTACLE_RED)
            ot = "障害物"
            otw = c.stringWidth(ot, self.font, 10)
            _, cell_y = L.rc_to_xy(row, col)
            c.drawString(ox - otw / 2, cell_y + 3, ot)
            c.restoreState()

        # 7. コンパスローズ
        self.draw_compass(L.page_w - 20 * mm, L.legend_h / 2 + 1 * mm, 10)

        # 8. 凡例
        self.draw_legend()

        # 9. 装飾トレイル
        self.draw_trails(cfg)


# ============================================================
# エントリーポイント
# ============================================================
def generate(cfg: MapConfig, output: str | None = None) -> Path:
    """マップ設定からPDFを生成し、出力パスを返す。"""
    font = _register_jp_font()
    layout = Layout.compute(cfg)
    out = Path(output or cfg.output)

    c = canvas.Canvas(str(out), pagesize=(layout.page_w, layout.page_h))
    renderer = MapRenderer(c, layout, font)
    renderer.render(cfg)
    c.save()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="人間ロボットゲーム フィールドマップ PDF 生成",
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="map_config.yaml",
        help="マップ設定YAMLファイル (デフォルト: map_config.yaml)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="出力PDFパス（指定しない場合はYAML内の output を使用）",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_path}", file=sys.stderr)
        sys.exit(1)

    cfg = MapConfig.from_yaml(config_path)
    out = generate(cfg, args.output)

    print(f"✅ フィールドマップを生成しました: {out}")
    layout = Layout.compute(cfg)
    print(f"   ページ: {layout.page_w / mm:.0f} × {layout.page_h / mm:.0f} mm (A4横)")
    print(f"   グリッド: {cfg.cols}列 × {cfg.rows}行")
    print(f"   セル: {layout.cell_w / mm:.1f} × {layout.cell_h / mm:.1f} mm")
    print(f"   たからもの: {len(cfg.treasures)}個")


if __name__ == "__main__":
    main()
