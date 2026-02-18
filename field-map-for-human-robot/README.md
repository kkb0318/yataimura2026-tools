# 人間ロボットゲーム フィールドマップ生成ツール

宝の地図風デザインのフィールドマップPDFを生成するツールです。  
YAMLファイルでマップ内容を定義し、コマンド一発でPDFを出力できます。

## 必要環境

- **Python** 3.10 以上
- **uv** （[インストール方法](https://docs.astral.sh/uv/getting-started/installation/)）
- **日本語フォント**（下記参照）

### 日本語フォントのインストール

タイトルやラベルに日本語を使用するため、システムに日本語フォントが必要です。

```bash
# Ubuntu / Debian
sudo apt install fonts-noto-cjk

# macOS
# → 標準搭載のヒラギノフォントが自動で使われます（追加不要）

# Windows (WSL)
sudo apt install fonts-noto-cjk
```

## クイックスタート

```bash
# リポジトリに移動
cd human-robot-fieldmap

# PDF生成（uv が依存関係を自動解決します）
uv run fieldmap
```

これだけで `field_map.pdf` が生成されます。

## 使い方

### 基本コマンド

```bash
# デフォルト設定で生成
uv run fieldmap

# 設定ファイルを指定
uv run fieldmap my_map.yaml

# 出力先を指定
uv run fieldmap map_config.yaml -o output/my_map.pdf
```

### モジュールとして直接実行

```bash
uv run python -m src.generate map_config.yaml
```

## マップ設定ファイル（YAML）

`map_config.yaml` を編集することでマップを自由にカスタマイズできます。

```yaml
# グリッドサイズ
grid:
  rows: 5       # 行数
  cols: 10      # 列数

# タイトル
title: "人間ロボットゲーム"
subtitle: "〜 フィールドマップ 〜"

# たからもの: 位置 [行, 列] とラベル
treasures:
  - pos: [1, 2]
    label: "A"
  - pos: [1, 5]
    label: "B"
  - pos: [3, 3]
    label: "C"

# スタート位置 [行, 列]
start: [5, 4]

# 障害物
obstacles:
  - [5, 5]
  - [5, 6]

# 出力ファイル名
output: "field_map.pdf"
```

### 座標の指定方法

座標は **[行, 列]** で指定します（1始まり）。

```
列:  1   2   3   4   5   6   7   8   9  10
行1 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
行2 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
行3 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
行4 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
行5 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
```

例: 3行目・9列目 → `[3, 9]`

## カスタマイズ例

### 宝を追加する

```yaml
treasures:
  # 既存の宝
  - pos: [1, 2]
    label: "A"
  # 新しい宝を追加
  - pos: [2, 6]
    label: "H"
```

### グリッドサイズを変更する

```yaml
grid:
  rows: 6    # 6行に増やす
  cols: 8    # 8列に減らす
```

### 障害物を増やす

```yaml
obstacles:
  - [5, 5]
  - [5, 6]
  - [3, 4]   # 追加
  - [2, 7]   # 追加
```

## 出力仕様

| 項目 | 値 |
|------|------|
| 用紙 | A4 横向き (297 × 210 mm) |
| デザイン | 宝の地図風（羊皮紙テクスチャ） |
| 余白 | ほぼなし（フチなし印刷推奨） |

## ファイル構成

```
human-robot-fieldmap/
├── pyproject.toml       # プロジェクト設定
├── map_config.yaml      # マップ定義（ここを編集）
├── README.md
└── src/
    ├── __init__.py
    └── generate.py      # PDF生成スクリプト
```
