#!/usr/bin/env python3
"""
ロジックたからさがし ─ たからのちず PDF ジェネレータ

Usage:
    uv run generate.py                          # → output/たからのちず.pdf
    uv run generate.py -i my_problems.yaml      # カスタム問題ファイル
    uv run generate.py -o maps.pdf              # 出力ファイル名指定
    uv run generate.py --html-only              # HTML のみ出力（PDF 変換なし）
"""

from __future__ import annotations

import argparse
import html as ht
import re
import sys
from pathlib import Path

import yaml
from pygments import highlight as _pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

# ── Paths ───────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DEFAULT_PROBLEMS = ROOT / "problems.yaml"
DEFAULT_CSS = ROOT / "style.css"
OUTPUT_DIR = ROOT / "output"

# ── Constants ───────────────────────────────────────────────
TWO_COL_THRESHOLD = 15  # ステップ数がこれ以上なら 2 カラム
INDENT_UNIT = 2  # YAML の先頭スペース何個で 1 インデント

COMPASS_SVG = (
    '<svg viewBox="0 0 60 60" width="78" height="88">'
    '<line x1="30" y1="6" x2="30" y2="54" stroke="#7D4E37" stroke-width="1.5"/>'
    '<line x1="6" y1="30" x2="54" y2="30" stroke="#7D4E37" stroke-width="1.2"/>'
    '<polygon points="30,6 27,22 33,22" fill="#7D4E37"/>'
    '<line x1="18" y1="18" x2="42" y2="42" stroke="#7D4E37" stroke-width="0.7"/>'
    '<line x1="42" y1="18" x2="18" y2="42" stroke="#7D4E37" stroke-width="0.7"/>'
    '<circle cx="30" cy="30" r="3" fill="#C5940A"/>'
    '<circle cx="30" cy="30" r="1.5" fill="#F5E6C8"/>'
    '<text x="30" y="4" text-anchor="middle" fill="#5B2E1A" '
    'font-size="7" font-weight="bold">N</text>'
    "</svg>"
)

PARCHMENT = (
    '<div class="pbg"></div>'
    '<div class="pe-t"></div><div class="pe-b"></div>'
    '<div class="pe-l"></div><div class="pe-r"></div>'
)
BORDERS = '<div class="bo"></div><div class="bi"></div>'
CORNERS = (
    '<div class="cd cd-tl"></div><div class="cd cd-tr"></div>'
    '<div class="cd cd-bl"></div><div class="cd cd-br"></div>'
)
BOTTOM_DECO = (
    '<div class="bdeco">'
    '<span class="bdd"></span><span class="bdd bds"></span>'
    '<span class="bdd"></span><span class="bdd bds"></span>'
    '<span class="bdc"></span>'
    '<span class="bdd bds"></span><span class="bdd"></span>'
    '<span class="bdd bds"></span><span class="bdd"></span>'
    "</div>"
)


# ════════════════════════════════════════════════════════════
#  Data Loading
# ════════════════════════════════════════════════════════════


def parse_step(raw: str) -> tuple[str, int]:
    """先頭スペースからインデントレベルを算出し、(テキスト, レベル) を返す。"""
    stripped = raw.lstrip(" ")
    spaces = len(raw) - len(stripped)
    level = spaces // INDENT_UNIT
    return stripped, level


def load_problems(path: Path) -> list[dict]:
    """YAML を読み込み、内部データ形式に変換する。"""
    with open(path, encoding="utf-8") as f:
        raw_list: list[dict] = yaml.safe_load(f)

    problems = []
    for item in raw_list:
        prob: dict = {
            "no": item["no"],
            "difficulty": item["difficulty"],
            "answer": str(item["answer"]),
        }

        # 特別ルール
        if "rules" in item:
            prob["rules"] = item["rules"]

        # コード問題
        if item.get("type") == "code":
            prob["type"] = "code"
            prob["lang"] = item.get("lang", "Python")
            prob["code"] = item["code"].rstrip("\n")
            prob["layout"] = item.get("layout", "full")
        else:
            # 通常問題: ステップ解析
            steps = []
            for i, raw in enumerate(item["steps"], 1):
                text, indent = parse_step(str(raw))
                steps.append((i, text, indent))
            prob["steps"] = steps

        problems.append(prob)

    return problems


# ════════════════════════════════════════════════════════════
#  HTML Renderers
# ════════════════════════════════════════════════════════════


def _header(prob: dict) -> str:
    """Banner / subtitle / stars / divider 共通ヘッダ"""
    stars = "<span>★</span>" * prob["difficulty"]
    return (
        f'<div class="compass">{COMPASS_SVG}</div>'
        f'<div class="mno"><span class="mno-l">No.</span>'
        f'<span class="mno-v">{prob["no"]}</span></div>'
        '<div class="bw"><div class="bn">'
        '<div class="blt"></div>たからのちず<div class="blb"></div>'
        "</div></div>"
        '<div class="subtitle">ロジックたからさがし</div>'
        f'<div class="stars">{stars}</div>'
        '<div class="dv"><div class="dvl"></div>'
        '<div class="dvd"></div><div class="dvr"></div></div>'
        '<div class="sh">▶ おたからまでのみちすじ</div>'
    )


def _rules_box(rules: list[str]) -> str:
    body = "<br>".join(r for r in rules)
    return (
        '<div class="srb"><div class="srh">【とくべつルール】</div>'
        f'<div class="srt">{body}</div></div>'
    )


def _step_div(num: int, text: str, indent: int) -> str:
    cls = f" si{indent}" if indent else ""
    return (
        f'<div class="step{cls}"><span class="sn">{num}.</span> {ht.escape(text)}</div>'
    )


def _font_params(n_steps: int, two_col: bool) -> tuple[int, float]:
    """ステップ数に応じたフォントサイズと行高を返す。"""
    if two_col:
        return (12, 1.7) if n_steps > 20 else (13, 1.75)
    if n_steps <= 7:
        return 18, 2.2
    if n_steps <= 10:
        return 16, 1.9
    return 14, 1.75


def render_step_map(prob: dict) -> str:
    """通常問題（半ページ用）の map-card 中身を返す。"""
    steps = prob["steps"]
    n = len(steps)
    two_col = n >= TWO_COL_THRESHOLD
    fs, lh = _font_params(n, two_col)

    parts = [PARCHMENT, BORDERS, CORNERS, '<div class="ct">', _header(prob)]

    if "rules" in prob:
        parts.append(_rules_box(prob["rules"]))

    if two_col:
        mid = 14
        parts.append(
            f'<table class="tc" style="font-size:{fs}px;line-height:{lh};"><tr><td>'
        )
        parts.extend(_step_div(*s) for s in steps[:mid])
        parts.append("</td><td>")
        parts.extend(_step_div(*s) for s in steps[mid:])
        parts.append("</td></tr></table>")
    else:
        parts.append(f'<div style="font-size:{fs}px;line-height:{lh};">')
        parts.extend(_step_div(*s) for s in steps)
        parts.append("</div>")

    parts.append("</div>")  # .ct

    if not two_col:
        parts.append(BOTTOM_DECO)

    return "\n".join(parts)


def _highlight_python(code: str) -> str:
    """Pygments でハイライトし、行番号付き HTML を返す。"""
    formatter = HtmlFormatter(
        nowrap=False,
        linenos="inline",
        cssclass="highlight",
        noclasses=False,
    )
    return _pygments_highlight(code, PythonLexer(), formatter)


def render_code_map(prob: dict) -> str:
    """コード問題（フルページ用）の page 全体を返す。"""
    lang = prob.get("lang", "Python")
    highlighted = _highlight_python(prob["code"])

    parts = [
        '<div class="page">',
        '<div class="map-full">',
        PARCHMENT,
        BORDERS,
        CORNERS,
        '<div class="ct">',
        _header(prob),
    ]
    if "rules" in prob:
        parts.append(_rules_box(prob["rules"]))
    parts.append(
        f'<div class="code-block">'
        f'<span class="code-label">{ht.escape(lang)}</span>'
        f"<pre>{highlighted}</pre></div>"
    )
    parts.append("</div></div></div>")  # .ct, .map-full, .page
    return "\n".join(parts)


def render_answer_key(problems: list[dict]) -> str:
    """正誤表ページを返す。"""
    rows = []
    for p in problems:
        stars = "★" * p["difficulty"]
        answer = f"宝箱 {p['answer']}"
        memo = ""
        if p.get("type") == "code":
            memo = f"{p.get('lang', 'Code')} コード形式"
        rows.append(
            f"<tr><td>{p['no']}</td><td>{stars}</td>"
            f"<td>{answer}</td><td>{memo}</td></tr>"
        )

    notes = [
        "・参加者が「たからばこをひらく」を実行して得たお宝を、地図のNo.と照合して正解かどうか判定してください。",
        "・難しすぎる/簡単すぎると思ったら問題の変更OK",
        "・景品は参加者全員に渡してください",
        "・間違えた場合はやりなおし(混雑時除く) & 適宜ヒントを出してもOK。",
    ]

    return (
        '<div class="page">'
        '<div class="ahdr">'
        "<h1>◆ ロジックたからさがし ─ 正誤表（運営用）</h1>"
        "<p>※ このシートは参加者には見せないでください</p>"
        "</div>"
        '<div class="abdy">'
        '<table class="atbl"><thead><tr>'
        "<th>No.</th><th>なんいど</th><th>正解のたからばこ</th><th>メモ</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        '<div class="anotes"><h3>【運営メモ】</h3><p>'
        + "<br>".join(notes)
        + "</p></div></div></div>"
    )


# ════════════════════════════════════════════════════════════
#  Page Assembly
# ════════════════════════════════════════════════════════════


def generate_html(problems: list[dict], css_text: str) -> str:
    parts = [
        '<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">',
        f"<style>{css_text}</style>",
        "</head><body>",
    ]

    # 通常問題を拾う（half-page cards）
    step_maps = [p for p in problems if p.get("type") != "code"]
    # コード問題を拾う（full-page）
    code_maps = [p for p in problems if p.get("type") == "code"]

    # 通常問題: 2 枚ずつ A4 1 ページにペアリング
    for i in range(0, len(step_maps), 2):
        top = step_maps[i]
        bot = step_maps[i + 1] if i + 1 < len(step_maps) else None

        parts.append('<div class="page"><div class="cut-line"></div>')
        parts.append(f'<div class="map-card map-top">{render_step_map(top)}</div>')
        if bot:
            parts.append(
                f'<div class="map-card map-bottom">{render_step_map(bot)}</div>'
            )
        else:
            parts.append(
                '<div class="map-card map-bottom"><div class="pbg"></div></div>'
            )
        parts.append("</div>")

    # コード問題: それぞれフルページ
    for p in code_maps:
        parts.append(render_code_map(p))

    # 正誤表
    parts.append(render_answer_key(problems))

    parts.append("</body></html>")
    return "\n".join(parts)


# ════════════════════════════════════════════════════════════
#  PDF Generation (WeasyPrint)
# ════════════════════════════════════════════════════════════


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    from weasyprint import HTML

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    print(f"✅ PDF 生成完了: {pdf_path}")


# ════════════════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="ロジックたからさがし ─ たからのちず PDF ジェネレータ"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_PROBLEMS,
        help="問題 YAML ファイル (default: problems.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="出力 PDF ファイル名 (default: output/たからのちず.pdf)",
    )
    parser.add_argument(
        "--css",
        type=Path,
        default=DEFAULT_CSS,
        help="CSS ファイル (default: style.css)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="HTML のみ出力し、PDF 変換をスキップ",
    )
    args = parser.parse_args()

    # 出力先
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_path = args.output or OUTPUT_DIR / "たからのちず.pdf"
    html_path = pdf_path.with_suffix(".html")

    # 読み込み
    problems = load_problems(args.input)
    css_text = args.css.read_text(encoding="utf-8")

    # HTML 生成
    html_content = generate_html(problems, css_text)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"📄 HTML 生成完了: {html_path}")
    print(f"   問題数: {len(problems)} 問")

    # PDF 生成
    if not args.html_only:
        html_to_pdf(html_path, pdf_path)


if __name__ == "__main__":
    main()
