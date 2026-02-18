# treasure-box-flyer

`たからばこ` 用の配布資料（A4 横・4面付け）を PDF で自動生成するツールです。  
印刷して四分割することで、同じ案内カードを 4 枚まとめて作れます。

## この資料の目的

- 子ども向けイベントで、たからばこの使い方を直感的に案内する
- `スマホあり` と `スマホなし` の2パターンの参加方法を同時に説明する
- スタッフ間で同一デザインの案内物を毎回同じ品質で再生成できるようにする

## セットアップ

前提:

- Python `3.14` 以上
- `uv` が使える環境（推奨）

### 1. 依存関係のインストール

```bash
cd /Users/kkb/ghq/github.com/kkb0318/yataimura2026-tools/treasure-box-flyer
uv sync
```

### 2. PDF を生成

```bash
uv run python main.py
```

生成されるファイル:

- `/Users/kkb/ghq/github.com/kkb0318/yataimura2026-tools/treasure-box-flyer/takarabako_flyer_kids_4up_landscape_final.pdf`

## 代替実行方法（uv を使わない場合）

```bash
cd /Users/kkb/ghq/github.com/kkb0318/yataimura2026-tools/treasure-box-flyer
python3 -m venv .venv
.venv/bin/pip install reportlab
.venv/bin/python main.py
```

## デザインを調整する場所

- レイアウト・配色・文言: `/Users/kkb/ghq/github.com/kkb0318/yataimura2026-tools/treasure-box-flyer/main.py`
- 出力ファイル名: `/Users/kkb/ghq/github.com/kkb0318/yataimura2026-tools/treasure-box-flyer/main.py` の `OUT`
