"""日本語フォントの検出と登録。

IPAゴシックを自動検出します。見つからない場合は手動パス指定のガイドを表示します。
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# IPAゴシックの探索パス（優先順）
_SEARCH_PATHS = [
    # Linux (apt install fonts-ipafont-gothic)
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/IPAGothic/ipag.ttf",
    # macOS
    "/Library/Fonts/ipag.ttf",
    "/System/Library/Fonts/ipag.ttf",
    str(Path.home() / "Library/Fonts/ipag.ttf"),
    # Windows
    "C:/Windows/Fonts/ipag.ttf",
    # Nix / Homebrew
    "/usr/local/share/fonts/ipag.ttf",
]

FONT_NAME = "IPAGothic"

_registered = False


def _find_font() -> Path | None:
    """既知のパスからIPAゴシックを探す。"""
    for p in _SEARCH_PATHS:
        path = Path(p)
        if path.is_file():
            return path
    return None


def register_font(font_path: str | None = None) -> None:
    """IPAゴシックをreportlabに登録する。

    Args:
        font_path: フォントファイルのパス。Noneなら自動検出。
    """
    global _registered
    if _registered:
        return

    if font_path:
        path = Path(font_path)
    else:
        path = _find_font()

    if path is None or not path.is_file():
        print(
            "エラー: IPAゴシック (ipag.ttf) が見つかりません。\n"
            "\n"
            "以下のいずれかの方法でインストールしてください:\n"
            "  Ubuntu/Debian: sudo apt install fonts-ipafont-gothic\n"
            "  macOS:         brew install --cask font-ipa-gothic\n"
            "  Windows:       https://moji.or.jp/ipafont/ からダウンロード\n"
            "\n"
            "または --font オプションでパスを直接指定してください:\n"
            "  generate-cards --font /path/to/ipag.ttf",
            file=sys.stderr,
        )
        sys.exit(1)

    pdfmetrics.registerFont(TTFont(FONT_NAME, str(path)))
    _registered = True
