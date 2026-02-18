"""YAML から URL 一覧を読み込む。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml


@dataclass(frozen=True)
class QrItem:
    """QR化する 1 件分のデータ。"""

    url: str
    label: str | None = None


def load_items(yaml_path: str | Path) -> list[QrItem]:
    """YAMLを読み込み、URL一覧を返す。"""
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("YAMLのルートはオブジェクト形式で指定してください。")

    raw_urls = data.get("urls")
    if not isinstance(raw_urls, list) or not raw_urls:
        raise ValueError("`urls` は1件以上の配列で指定してください。")

    items: list[QrItem] = []
    for idx, raw_entry in enumerate(raw_urls, start=1):
        url, label = _parse_entry(raw_entry, idx)
        _validate_url(url, idx)
        items.append(QrItem(url=url, label=label))

    return items


def _parse_entry(raw_entry: object, index: int) -> tuple[str, str | None]:
    if isinstance(raw_entry, str):
        return raw_entry.strip(), None

    if isinstance(raw_entry, dict):
        if "url" not in raw_entry:
            raise ValueError(f"urls[{index}] に `url` キーがありません。")

        raw_url = raw_entry["url"]
        if not isinstance(raw_url, str):
            raise ValueError(f"urls[{index}].url は文字列で指定してください。")

        raw_label = raw_entry.get("label")
        label = None
        if raw_label is not None:
            if not isinstance(raw_label, str):
                raise ValueError(f"urls[{index}].label は文字列で指定してください。")
            label = raw_label.strip() or None

        return raw_url.strip(), label

    raise ValueError(
        f"urls[{index}] は文字列URLまたは {{url, label}} 形式で指定してください。"
    )


def _validate_url(url: str, index: int) -> None:
    if not url:
        raise ValueError(f"urls[{index}] のURLが空です。")

    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            f"urls[{index}] のURLが不正です: {url} "
            "(http:// または https:// から始まる完全なURLを指定してください)"
        )
