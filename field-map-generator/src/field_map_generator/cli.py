"""CLI エントリーポイント"""

from __future__ import annotations

import argparse
from pathlib import Path

from .renderer import generate_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        description="人間ロボットゲーム＆ロジック宝探し フィールドマップ PDF 生成",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("field_map.pdf"),
        help="出力ファイルパス (デフォルト: field_map.pdf)",
    )
    args = parser.parse_args()

    result = generate_pdf(args.output)
    print(f"✅ 生成完了: {result}")


if __name__ == "__main__":
    main()
