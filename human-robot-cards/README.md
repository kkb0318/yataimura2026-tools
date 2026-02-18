# 人間ロボットゲーム 指令カード生成ツール

「人間ロボットゲーム」で使用する指令カードのPDFを生成するツールです。

## 前提条件

- **Python 3.10 以上**
- **[uv](https://docs.astral.sh/uv/)** — Pythonパッケージマネージャ
- **IPAゴシックフォント** (`ipag.ttf`)

### IPAゴシックのインストール

| OS | コマンド |
|---|---|
| Ubuntu / Debian | `sudo apt install fonts-ipafont-gothic` |
| macOS (Homebrew) | `brew install --cask font-ipa-gothic` |
| Windows | [IPA公式サイト](https://moji.or.jp/ipafont/) からダウンロードしてインストール |

## セットアップ

```bash
# リポジトリに移動
cd human-robot-cards

# 依存パッケージを同期（初回のみ）
uv sync
```

## 使い方

### 基本（デフォルト設定で生成）

```bash
uv run generate-cards
```

カレントディレクトリに `human_robot_cards.pdf` が出力されます。

### オプション

```bash
# 出力ファイル名を指定
uv run generate-cards -o output/my_cards.pdf

# 別のカード定義ファイルを使用
uv run generate-cards -c my_custom_cards.yaml

# フォントパスを手動指定
uv run generate-cards --font /path/to/ipag.ttf
```

### uv を使わずに実行する場合

```bash
pip install -e .
generate-cards
```

## 印刷方法

- **用紙サイズ**: A4
- **倍率**: 100%（実寸）
- **余白**: なし or 最小
- **カードサイズ**: 63×88mm（トレカサイズ）

カード間に隙間がないため、罫線に沿って定規とカッターで裁断してください。

## カードのカスタマイズ

`cards.yaml` を編集することで、コードを変更せずにカードの追加・変更ができます。

### カードを追加する

`cards:` セクションの該当レベルにエントリを追加します:

```yaml
cards:
  blue:
    # ... 既存のカード ...

    - text1: "ジャンプ"        # カード上段テキスト
      text2: "する"           # カード下段テキスト
      icon: arrow_up          # アイコン名
      category: action        # カテゴリ名
      count: 2                # 枚数
```

### 新しい難易度（色）を追加する

`levels:` と `cards:` の両方にエントリを追加します:

```yaml
levels:
  # ... 既存のレベル ...
  green:
    label: "チャレンジ"
    colors:
      bg: "#E8F5E9"
      border: "#2E7D32"
      header_bg: "#2E7D32"
      accent: "#43A047"

cards:
  # ... 既存のカード ...
  green:
    - text1: "1マス"
      text2: "すすむ"
      icon: arrow_up
      category: move
      count: 4
```

### 新しいカテゴリを追加する

`categories:` にエントリを追加します:

```yaml
categories:
  # ... 既存のカテゴリ ...
  special:
    label: "スペシャル"
    color: "#E91E63"
```

### 利用可能なアイコン一覧

| アイコン名 | 説明 |
|---|---|
| `arrow_up` | 前進（上向き矢印） |
| `turn_right` | 右を向く |
| `turn_left` | 左を向く |
| `turn_back` | 後ろを向く（Uターン） |
| `treasure` | たからばこ |
| `loop_start` | くりかえし開始（回転矢印） |
| `loop_end` | くりかえし終了（停止マーク） |
| `point` | ポイント（星） |
| `variable_step` | 変数マス（足跡+?） |
| `condition` | 条件分岐（ひし形+?） |

### 新しいアイコンを追加する

`src/human_robot_cards/icons.py` を編集します:

```python
# 1. 描画関数を定義
def draw_my_icon(c, cx, cy, size, color):
    """カスタムアイコン。"""
    s = size
    c.setFillColor(color)
    c.circle(cx, cy, s * 0.3, fill=1, stroke=0)

# 2. レジストリに登録
ICON_REGISTRY["my_icon"] = draw_my_icon
```

これで `cards.yaml` で `icon: my_icon` として使えるようになります。

## プロジェクト構成

```
human-robot-cards/
├── pyproject.toml                  # プロジェクト設定・依存定義
├── cards.yaml                      # カード定義（ここを編集）
├── README.md
└── src/human_robot_cards/
    ├── __init__.py
    ├── cli.py                      # CLIエントリーポイント
    ├── fonts.py                    # フォント検出・登録
    ├── icons.py                    # アイコン描画関数
    ├── loader.py                   # YAML読み込み・変換
    └── renderer.py                 # PDF描画エンジン
```

## ライセンス

本ツールで使用するIPAゴシックフォントは [IPAフォントライセンスv1.0](https://moji.or.jp/ipafont/license/) に基づきます。
