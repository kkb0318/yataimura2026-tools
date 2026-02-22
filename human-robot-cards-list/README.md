# 人間ロボットゲーム カード一覧 PDF 生成

青・黄・赤の全3レベル（計55枚）のカード一覧をA4一枚のPDFに出力します。

## 必要なもの

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- 日本語フォント（Noto Sans CJK JP 推奨）

## 使い方

```bash
uv run gen_cards.py                # → card_list.pdf
uv run gen_cards.py output.pdf     # → 出力先を指定
```

## カード構成

| レベル | 枚数 | 内容 |
|--------|------|------|
| 🔵 青（基本） | 14枚 | 移動・方向転換・たからばこ |
| 🟡 黄（中級） | 20枚 | + ループ・ポイント |
| 🔴 赤（上級） | 21枚 | + ネストループ・条件分岐 |
