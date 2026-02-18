# yataimura2026-tools

屋台村2026向けの配布資料生成ツール群です。各フォルダは独立しており、基本的に `uv sync` 後に `uv run ...` で実行します。

## 共通メモ
- 主な実行環境: Python 3.10+（`treasure-box-flyer` は 3.14+）
- 日本語PDFのため、フォントが必要なツールがあります
- 生成物は配布用/運営用の PDF（必要に応じて HTML も出力）

## フォルダ別サマリー

### `treasure-box-flyer`
- 目的: たからばこの使い方を案内するカード（A4横・4面付け）を生成
- 内容: 「スマホあり / スマホなし」を1面に配置、右上に管理用 `No.<添え字>` を表示可能
- 実行: `cd treasure-box-flyer && uv sync && uv run python main.py`
- オプション: `--count 10`（A,B,C...自動採番）/ `--labels A,B,C`（明示指定）
- 出力: `treasure-box-flyer/takarabako_flyer_kids_4up_landscape_final.pdf`

### `treasure-map-generator`
- 目的: `problems.yaml` から「たからのちず」を生成（通常問題 + Pythonコード問題）
- 実行: `cd treasure-map-generator && uv sync && uv run generate.py`
- オプション: `-i` 入力YAML指定 / `-o` 出力PDF指定 / `--html-only`
- 出力: `output/たからのちず.html`, `output/たからのちず.pdf`（末尾に運営用正誤表付き）
- 補足: macOS は WeasyPrint 依存として `brew install pango` が必要

### `field-map-generator`
- 目的: 人間ロボットゲーム＆ロジック宝探しの運営用フィールドマップPDFを生成
- 実行: `cd field-map-generator && uv sync && uv run generate-map`
- カスタマイズ: `src/field_map_generator/map_data.py` を編集（宝、数字マス、障害物、開始位置など）
- 出力: `field_map.pdf`（または `-o` 指定先）
- 補足: 日本語フォントが必要（OSごとにREADME記載）

### `field-map-for-human-robot`
- 目的: 宝の地図風デザインのフィールドマップPDFをYAML定義から生成
- 実行: `cd field-map-for-human-robot && uv run fieldmap`
- オプション: 設定YAML指定、`-o` 出力先指定
- カスタマイズ: `map_config.yaml`（グリッド、宝、スタート、障害物、タイトル等）
- 出力: `field_map.pdf`

### `human-robot-cards`
- 目的: 人間ロボットゲームで使う指令カードPDFを生成
- 実行: `cd human-robot-cards && uv sync && uv run generate-cards`
- オプション: `-o` 出力ファイル / `-c` カード定義YAML / `--font` フォントパス
- カスタマイズ: `cards.yaml`（カード文言、難易度色、カテゴリ、枚数、アイコン）
- 出力: `human_robot_cards.pdf`（トレカサイズ 63x88mm をA4面付け）

### `logic-treasure-mission-card`
- 目的: 人間ロボットゲームのミッションカード（参加者用）と運営用解答集を生成
- 実行: `cd logic-treasure-mission-card && uv run generate.py`
- オプション: `-i` 入力YAML / `-o` 出力ディレクトリ / `--cards-only` / `--staff-only`
- カスタマイズ: `missions.yaml`（難易度、色、ルール、解答、ID体系）
- 出力: `output/mission_cards.pdf`, `output/staff_reference.pdf`
- 補足: ReportLabで使える `.ttf` 日本語フォントが必要（README参照）
