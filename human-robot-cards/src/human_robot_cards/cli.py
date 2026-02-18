"""CLI エントリーポイント。"""

from __future__ import annotations

import argparse
from pathlib import Path

from .fonts import register_font
from .loader import load_cards
from .renderer import generate_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        description="人間ロボットゲーム 指令カード PDF生成ツール",
    )
    parser.add_argument(
        "-c",
        "--cards",
        default=None,
        help="カード定義YAMLファイル (デフォルト: プロジェクトルートの cards.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="human_robot_cards.pdf",
        help="出力PDFファイルパス (デフォルト: human_robot_cards.pdf)",
    )
    parser.add_argument(
        "--font",
        default=None,
        help="IPAゴシック (ipag.ttf) のパス (省略時は自動検出)",
    )
    args = parser.parse_args()

    # フォント登録
    register_font(args.font)

    # cards.yaml の探索
    if args.cards:
        yaml_path = Path(args.cards)
    else:
        # プロジェクトルートの cards.yaml を探す
        candidates = [
            Path.cwd() / "cards.yaml",
            Path(__file__).resolve().parent.parent.parent.parent / "cards.yaml",
        ]
        yaml_path = None
        for p in candidates:
            if p.is_file():
                yaml_path = p
                break
        if yaml_path is None:
            parser.error(
                "cards.yaml が見つかりません。-c オプションで指定してください。"
            )

    # 読み込み & 生成
    cards, summaries = load_cards(yaml_path)

    generate_pdf(cards, summaries, args.output)

    total = len(cards)
    pages = (total + 8) // 9
    print(f"✅ PDF生成完了: {args.output}")
    for label, cnt in summaries:
        print(f"   {label}: {cnt}枚")
    print(f"   合計: {total}枚 → {pages}ページ（+ガイド1ページ）")


if __name__ == "__main__":
    main()
