# yataimura2026-treasure-map-generator

「ロジックたからさがし」の問題データ（YAML）から、配布用の「たからのちず」PDFを生成するリポジトリです。  
通常の手順問題と、Pythonコードを読む問題の両方を扱えます。

## 何を作っているか

- 入力: `problems.yaml`
- 生成物:
  - `output/たからのちず.html`
  - `output/たからのちず.pdf`
- PDF 末尾に運営用の正誤表も自動で含めます。

## 必要環境

- Python 3.10 以上
- `uv`
- WeasyPrint の描画依存（macOS の場合）
  - `brew install pango`

## 実行方法

```bash
# 1) 依存インストール
uv sync

# 2) 既定の problems.yaml で PDF 生成
uv run generate.py
```

生成先:

- `output/たからのちず.html`
- `output/たからのちず.pdf`

## よく使う実行例

```bash
# 入力ファイルを指定
uv run generate.py -i my_problems.yaml

# 出力 PDF 名を指定
uv run generate.py -o output/maps.pdf

# HTML のみ生成（PDF 変換をスキップ）
uv run generate.py --html-only
```

## 問題データ（problems.yaml）の基本

通常問題:

- `"no"`: 問題番号（例: `R-01`）
- `difficulty`: 難易度（1〜5）
- `answer`: 正解の宝箱（例: `F`）
- `rules`: 特別ルール（任意）
- `steps`: 手順配列（先頭スペースでネストを表現）

コード問題:

- `type: code`
- `lang: Python`
- `layout: full`
- `code: |` でコード本文を記述

注意:

- YAML では `no` が真偽値扱いされる実装差があるため、キーは `"no"` のようにクオートしてください。
