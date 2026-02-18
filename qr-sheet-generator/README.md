# QRシート生成ツール

設定したURL一覧からQRコードを作成し、A4 PDFに面付けして出力するツールです。

- QRコードサイズはデフォルトで **50mm x 50mm**（約5x5cm）
- A4に収まる数を自動計算して配置
- 件数が多い場合は自動で複数ページ化

## 前提条件

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/)

## セットアップ

```bash
cd qr-sheet-generator
uv sync
```

## 使い方

```bash
uv run generate-qr-sheet
```

デフォルトでは `urls.yaml` を読み込み、`qr_sheets.pdf` を生成します。

### オプション例

```bash
# 入力/出力ファイルを指定
uv run generate-qr-sheet -i urls.yaml -o output/qr_sheets.pdf

# QRサイズや余白を調整
uv run generate-qr-sheet --qr-size-mm 50 --margin-mm 10 --gap-mm 5

# label（指定がない項目は連番）を表示
uv run generate-qr-sheet --caption index

# 表示を消す
uv run generate-qr-sheet --caption none
```

## YAML形式

`urls` 配列は「文字列URL」または「オブジェクト（url,label）」のどちらでも指定できます。

```yaml
urls:
  - "https://example.com/a"
  - url: "https://example.com/b"
    label: "Bチーム"
```

- `label` は `--caption index` 時にQR下へ表示されます（未指定時は連番）。
- 日本語ラベルは ReportLab の日本語CIDフォント（`HeiseiKakuGo-W5`）で描画します。

### バリデーション

- `urls` は1件以上必要
- URLは `http://` または `https://` で始まる必要あり

## 出力

- PDF: `qr_sheets.pdf`（`-o` で変更可）
