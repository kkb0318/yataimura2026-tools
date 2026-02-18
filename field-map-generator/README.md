# field-map-generator

**人間ロボットゲーム ＆ ロジック宝探し** のフィールドマップ PDF を生成するツールです。
運営スタッフが正誤確認などに使用するためのマップを出力します。

## 必要な環境

- **Python** 3.10 以上
- **uv** ([インストール方法](https://docs.astral.sh/uv/getting-started/installation/))
- **日本語フォント** — 以下のいずれかがシステムにインストールされていること
  - macOS: 標準搭載のヒラギノ角ゴシック（追加作業不要）
  - Windows: 標準搭載の MS ゴシックまたはメイリオ（追加作業不要）
  - Ubuntu / Debian: `sudo apt install fonts-ipafont-gothic`
  - Fedora / RHEL: `sudo dnf install google-noto-sans-cjk-jp-fonts`

## クイックスタート

```bash
# リポジトリに移動
cd field-map-generator

# PDF を生成（uv が依存関係を自動解決）
uv run generate-map

# 出力先を指定する場合
uv run generate-map -o output/my_map.pdf
```

`field_map.pdf` が生成されます。

## プロジェクト構成

```
field-map-generator/
├── pyproject.toml                          # プロジェクト設定・依存関係
├── README.md
└── src/
    └── field_map_generator/
        ├── __init__.py
        ├── cli.py            # CLI エントリーポイント
        ├── map_data.py       # ★ マップデータ定義（編集対象）
        └── renderer.py       # PDF 描画ロジック
```

## マップのカスタマイズ

マップの内容を変更したい場合は **`src/field_map_generator/map_data.py`** を編集してください。
描画ロジック (`renderer.py`) を変更する必要はありません。

### グリッドサイズの変更

```python
GRID_ROWS = 5   # 行数
GRID_COLS = 10   # 列数
```

### お宝の追加・変更

```python
TREASURES: list[Treasure] = [
    Treasure("A", 1, 2, "伝説の剣", "剣", "⚔️"),
    #        ^    ^  ^   ^          ^     ^
    #        |    |  |   |          |     元データの emoji (参照用)
    #        |    |  |   |          マス内の短縮表示
    #        |    |  |   フルネーム (お宝一覧に表示)
    #        |    |  列 (1-indexed)
    #        |    行 (1-indexed)
    #        ラベル (A, B, C, ...)

    # 追加例:
    Treasure("H", 2, 3, "星のかけら", "星", "⭐"),
]
```

### 数字マスの追加・変更

```python
NUMBER_CELLS: list[tuple[int, int, int]] = [
    (1, 3, 2),   # 1行3列に数字「2」
    # ...
    (5, 9, 3),   # 5行9列に数字「3」
]
```

### 障害物の追加・変更

```python
OBSTACLES: list[tuple[int, int]] = [
    (5, 5),   # 5行5列
    (5, 6),   # 5行6列
]
```

### スタート位置の変更

```python
ROBOT_START = StartPosition(5, 4, ["人間ロボット", "ゲーム", "スタート"])
LOGIC_START = StartPosition(5, 7, ["ロジック", "宝探し", "スタート"])
```

### タイトル・フッターの変更

```python
TITLE = "人間ロボットゲーム ＆ ロジック宝探し"
SUBTITLE = "フィールドマップ（運営用）"
FOOTER = "※ 運営スタッフ用　参加者には配布しないでください"
```

## ライセンス

MIT
