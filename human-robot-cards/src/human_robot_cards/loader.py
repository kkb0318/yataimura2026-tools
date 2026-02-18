"""cards.yaml の読み込みと CardInstance への変換。"""

from __future__ import annotations

from pathlib import Path

import yaml

from .icons import ICON_REGISTRY
from .renderer import CardInstance, CategoryStyle, LevelStyle


def load_cards(yaml_path: str | Path) -> tuple[list[CardInstance], list[tuple[str, int]]]:
    """YAMLファイルを読み込み、展開済みカードリストとサマリを返す。

    Returns:
        (cards, level_summaries)
        - cards: 全レベルのカードを順番に展開したリスト
        - level_summaries: [("青カード（きほん）", 14), ...] ガイドページ用
    """
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # レベル定義の構築
    levels: dict[str, LevelStyle] = {}
    for name, ldef in data["levels"].items():
        levels[name] = LevelStyle(
            name=name,
            label=ldef["label"],
            bg=ldef["colors"]["bg"],
            border=ldef["colors"]["border"],
            header_bg=ldef["colors"]["header_bg"],
            accent=ldef["colors"]["accent"],
        )

    # カテゴリ定義の構築
    categories: dict[str, CategoryStyle] = {}
    for name, cdef in data["categories"].items():
        categories[name] = CategoryStyle(label=cdef["label"], color=cdef["color"])

    # カード展開
    all_cards: list[CardInstance] = []
    level_summaries: list[tuple[str, int]] = []

    # cards.yaml の levels 定義順にカードを展開
    for level_name in data["levels"]:
        if level_name not in data.get("cards", {}):
            continue

        level = levels[level_name]
        card_defs = data["cards"][level_name]
        count_total = 0

        for cdef in card_defs:
            text1 = cdef["text1"]
            text2 = cdef["text2"]
            icon_name = cdef["icon"]
            cat_name = cdef["category"]
            count = cdef.get("count", 1)

            if icon_name not in ICON_REGISTRY:
                raise ValueError(
                    f"不明なアイコン '{icon_name}' (カード: {text1} {text2})。"
                    f" 利用可能: {', '.join(ICON_REGISTRY.keys())}"
                )
            if cat_name not in categories:
                raise ValueError(
                    f"不明なカテゴリ '{cat_name}' (カード: {text1} {text2})。"
                    f" 利用可能: {', '.join(categories.keys())}"
                )

            icon_func = ICON_REGISTRY[icon_name]
            category = categories[cat_name]

            # 移動カードの歩数抽出
            step_number = ""
            if cat_name == "move" and text1 and text1[0].isdigit():
                step_number = text1[0]

            for _ in range(count):
                all_cards.append(
                    CardInstance(
                        text1=text1,
                        text2=text2,
                        icon_func=icon_func,
                        category=category,
                        level=level,
                        step_number=step_number,
                    )
                )
            count_total += count

        # レベルごとの日本語ラベルを生成
        _LEVEL_KANJI = {"blue": "青", "yellow": "黄", "red": "赤"}
        kanji = _LEVEL_KANJI.get(level_name, level_name)
        level_summaries.append((f"{kanji}カード（{level.label}）", count_total))

    return all_cards, level_summaries
