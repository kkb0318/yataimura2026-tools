# yataimura2026-tools

屋台村2026向けの配布資料を生成するツール群です（主に `uv` + Python）。

## フォルダ概要
- `treasure-box-flyer`: たからばこ案内カード（A4横・4面付け）をPDF生成
- 用途: 子ども向けに「スマホあり / なし」の参加方法を同時に案内
- 実行: `cd treasure-box-flyer && uv sync && uv run python main.py`
- オプション: `--count`（自動採番） / `--labels A,B,C`（管理No指定）
- 出力: `treasure-box-flyer/takarabako_flyer_kids_4up_landscape_final.pdf`

- `treasure-map-generator`: 問題データ（YAML）から「たからのちず」PDFを生成
- 用途: 通常問題とPythonコード問題の両形式を含む配布資料を作成
- 実行: `cd treasure-map-generator && uv sync && uv run generate.py`
- 入力: `problems.yaml`（キー `"no"` はクオート推奨）
- 出力: `output/たからのちず.html` / `output/たからのちず.pdf`（末尾に正誤表付き）
