"""CLI エントリーポイント。"""

from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_items
from .renderer import LayoutOptions, generate_pdf


def _positive_mm(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value} は数値ではありません。") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("0より大きい値を指定してください。")
    return parsed


def _resolve_input_path(input_arg: str) -> Path:
    candidates = [
        Path(input_arg),
        Path.cwd() / input_arg,
        Path(__file__).resolve().parents[2] / input_arg,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return Path(input_arg)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="URL一覧からQRコード面付けPDFを生成するツール",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="urls.yaml",
        help="入力YAMLファイル (デフォルト: urls.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="qr_sheets.pdf",
        help="出力PDFファイル (デフォルト: qr_sheets.pdf)",
    )
    parser.add_argument(
        "--qr-size-mm",
        type=_positive_mm,
        default=50.0,
        help="QRコード1辺のサイズmm (デフォルト: 50)",
    )
    parser.add_argument(
        "--margin-mm",
        type=_positive_mm,
        default=10.0,
        help="ページ余白mm (デフォルト: 10)",
    )
    parser.add_argument(
        "--gap-mm",
        type=_positive_mm,
        default=5.0,
        help="QR同士の間隔mm (デフォルト: 5)",
    )
    parser.add_argument(
        "--caption",
        choices=["index", "none"],
        default="index",
        help=(
            "QR下の表示内容。index: 宝探しタグ上にlabel優先で表示、なければ連番 / "
            "none: 表示なし (デフォルト: index)"
        ),
    )
    args = parser.parse_args()

    yaml_path = _resolve_input_path(args.input)
    if not yaml_path.is_file():
        parser.error(f"入力YAMLが見つかりません: {args.input}")

    try:
        items = load_items(yaml_path)
        summary = generate_pdf(
            items,
            args.output,
            LayoutOptions(
                qr_size_mm=args.qr_size_mm,
                margin_mm=args.margin_mm,
                gap_mm=args.gap_mm,
                caption_mode=args.caption,
            ),
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(f"✅ PDF生成完了: {args.output}")
    print(f"   入力URL数: {summary.total_items}")
    print(
        f"   1ページあたり: {summary.per_page}個"
        f" ({summary.columns}列 x {summary.rows}行)"
    )
    print(f"   生成ページ数: {summary.pages}")


if __name__ == "__main__":
    main()
