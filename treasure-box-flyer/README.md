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

`--count` を指定すると、`A, B, C, ...` を自動採番してその数だけ生成します。

```bash
uv run python main.py --count 10
```

`--labels` を指定すると、No を明示指定できます（指定した件数だけ生成）。

```bash
uv run python main.py --labels A,B,C,D,E
```

補足:

- 各配布資料の右上に `No.<添え字>`（例: `No.A`）を表示します
- 1ページに4面配置し、件数が5以上なら自動で複数ページになります

生成されるファイル:

- `yataimura2026-tools/treasure-box-flyer/takarabako_flyer_kids_4up_landscape_final.pdf`
