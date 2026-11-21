# -*- coding: utf-8 -*-
"""读取 data/star_palace.json：星曜落十二宫的「本宫主象」与「改判条件」。

数据来源见 references/05-星曜落宫断语.md（黑白书院《紫微斗数进阶》课件，
其逐宫条转自集文书局《紫微斗数全书》卷二并合读《天纪》星义）。
"""

import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "star_palace.json")
_DATA = None


def load():
    global _DATA
    if _DATA is None:
        with open(_PATH, encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


def reading(star, palace):
    """返回 (本宫主象, 改判条件) 或 None。"""
    d = load().get(star)
    if not d:
        return None
    row = d.get("palaces", {}).get(palace)
    return tuple(row) if row else None


def brightness(star):
    """返回 {地支: 亮度} 或 {}。"""
    d = load().get(star)
    return dict(d.get("bright", {})) if d else {}
