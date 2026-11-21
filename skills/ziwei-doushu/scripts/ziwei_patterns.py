# -*- coding: utf-8 -*-
"""格局识别：夹宫、禄马、杀破狼、机月同梁、府相朝垣。

判据按黑白书院《紫微斗数进阶》第 148–152 页：先画对连线（同宫／会照／夹宫），再谈格局成立。
"""

import ziwei_core as C
import ziwei_chart as Z


def _stars(chart, idx):
    return chart["stars"].get(idx, [])


def sanfang(idx):
    return [(idx + 4) % 12, (idx + 8) % 12, (idx + 6) % 12]


def detect(chart):
    """返回 {格局名: 成立说明} 列表。"""
    ming = chart["ming"]
    scope = [ming] + sanfang(ming)
    names = []
    all_stars = set()
    for i in scope:
        all_stars |= set(_stars(chart, i))
    if {"七杀", "破军", "贪狼"} <= all_stars:
        names.append(("杀破狼", "命宫三方见七杀、破军、贪狼，动中求成"))
    if {"天机", "太阴", "天同", "天梁"} <= all_stars:
        names.append(("机月同梁", "命宫三方见天机、太阴、天同、天梁，宜文职与技术"))
    if {"天府", "天相"} <= all_stars:
        names.append(("府相朝垣", "命宫三方见天府、天相，重守成与辅佐"))
    left, right = (ming - 1) % 12, (ming + 1) % 12
    l, r = set(_stars(chart, left)), set(_stars(chart, right))
    if {"太阳"} & l and {"太阴"} & r or {"太阴"} & l and {"太阳"} & r:
        names.append(("日月夹命", "命宫两侧被太阳、太阴夹住"))
    if {"天魁"} & l and {"天钺"} & r or {"天钺"} & l and {"天魁"} & r:
        names.append(("魁钺夹命", "命宫两侧见天魁、天钺"))
    if {"擎羊"} & l and {"陀罗"} & r or {"陀罗"} & l and {"擎羊"} & r:
        names.append(("羊陀夹命", "命宫两侧被擎羊、陀罗夹住，压力贴身"))
    for i in range(12):
        st = set(_stars(chart, i))
        if "禄存" in st and "天马" in st:
            names.append(("禄马交驰", "%s宫禄存与天马同宫" % chart["palace_of"][i]))
            break
    else:
        for i in range(12):
            if "禄存" in set(_stars(chart, i)) and "天马" in set(_stars(chart, (i + 6) % 12)):
                names.append(("禄马交驰", "%s宫禄存对%s宫天马" % (
                    chart["palace_of"][i], chart["palace_of"][(i + 6) % 12])))
                break
    return names
