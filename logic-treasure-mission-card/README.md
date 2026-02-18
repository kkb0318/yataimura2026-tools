# 人間ロボットゲーム ミッションカード生成ツール

人間ロボットゲームのミッションカード（参加者配布用）と運営用解答集の PDF を生成するツールです。

## 必要な環境

- **Python** 3.10 以上
- **uv** ([インストール方法](https://docs.astral.sh/uv/getting-started/installation/))
- **日本語フォント** (TrueType 形式の .ttf が必要です)
  - Ubuntu: `sudo apt install fonts-ipafont-gothic`
  - macOS: `brew install font-ipa-gothic`  
    または [IPA フォント](https://moji.or.jp/ipafont/) から .ttf をダウンロードして `/Library/Fonts/` に配置  
    ※ ヒラギノ角ゴシック (.ttc) は CFF 形式のため ReportLab で使用できません
  - Windows: MS ゴシック or メイリオ（プリインストール）

## クイックスタート

```bash
uv run generate.py
```

初回実行時に依存パッケージ（reportlab, pyyaml）が自動でインストールされます。  
`output/` ディレクトリに以下の 2 ファイルが生成されます：

| ファイル | 内容 |
|----------|------|
| `mission_cards.pdf` | ミッションカード（A4 に A5×2 枚、切り取りガイド付き） |
| `staff_reference.pdf` | 運営用ミッション＆解答集（スタッフ配布用） |

## コマンドオプション

```bash
uv run generate.py [OPTIONS]

オプション:
  -i, --input FILE       ミッションデータ YAML ファイル (default: missions.yaml)
  -o, --output-dir DIR   出力ディレクトリ (default: output/)
  --cards-only           ミッションカードのみ生成
  --staff-only           運営用解答集のみ生成
```

### 使用例

```bash
# 別の YAML ファイルを使う
uv run generate.py -i missions_v2.yaml

# 出力先を変える
uv run generate.py -o dist/

# ミッションカードだけ生成
uv run generate.py --cards-only
```

## ミッションの追加・編集

`missions.yaml` を編集するだけでミッションの追加・変更ができます。

### データ構造

```yaml
start_position: "(5,4) 北向き"    # 運営用解答集に表示されるスタート位置

missions:
  - mission_id: C-01               # ミッション ID
    difficulty: 1                   # 難易度 (1-5)
    stars: 1                        # 星の数 (1-5)
    color: blue                     # カード色 (blue / yellow / red)
    card_set: きほん                # カードセット名
    mission: "たからばこ A を\nあけよう！"  # ミッション文 (\n で改行)
    rules:                          # ルール一覧
      - "フィールドの外にいどうしたらアウト！"
    answer:                         # 解答例 (運営用解答集にのみ表示)
      - 1マスすすむ
      - たからばこをひらく → クリア！
```

### ID 体系

| プレフィックス | カードセット | カード色 |
|------------|----------|--------|
| `C-xx` | きほん | 青 (blue) |
| `B-xx` | ちゅうきゅう | 黄 (yellow) |
| `A-xx` | 上級 | 赤 (red) |

### ルールの改行

ルール文中の `\n` はカード上での折り返し位置です。  
1 つのルール項目が長い場合に使います：

```yaml
rules:
  - "すうじマスでないところでは\n[マスのすうじ]は0だよ"   # 2行で表示
```

### 色とデザインの対応

| color | 背景色 | 対象レベル |
|-------|--------|----------|
| `blue` | 青系 | 難易度 1-2 |
| `yellow` | 黄/オレンジ系 | 難易度 3-4 |
| `red` | 赤系 | 難易度 4-5 |

## ファイル構成

```
mission-cards/
├── generate.py        # PDF 生成スクリプト（uv run で直接実行）
├── missions.yaml      # ★ ミッションデータ（ここを編集）
├── README.md
└── output/            # 生成された PDF（自動作成）
```

## 印刷ガイド

### ミッションカード
- **用紙**: A4
- **倍率**: 100%（実寸）
- **余白**: なし or 最小
- 中央の点線で切り取ると A5 サイズ × 2 枚になります
- ラミネート推奨

### 運営用解答集
- **用紙**: A4
- 通常の印刷設定で OK
