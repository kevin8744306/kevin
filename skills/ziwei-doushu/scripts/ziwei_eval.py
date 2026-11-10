# -*- coding: utf-8 -*-
"""应期检验：小限 vs 流年、四化哪一层更对应。

设计：同一事件类型、同一组判据，只换「时间层」（流年宫三方四正 / 小限宫与对宫），
比较该层给「事件发生年」打的分数在同类年份里的分位。分位高 = 该层对这一类事件有区分力。
"""

import ziwei_core as C
import ziwei_chart as Z
import ziwei_timing as T

EVENTS = ("婚", "子", "病", "官非", "破财")

PALACE_OF = {
    "婚": ("夫妻", "子女"), "子": ("子女",), "病": ("疾厄",),
    "官非": ("官禄", "命宫"), "破财": ("财帛", "田宅"),
}
MARK = {
    "婚": ("红鸾", "天喜"), "子": ("红鸾", "天喜", "天魁", "天贵"),
    "病": ("擎羊", "陀罗"), "官非": ("擎羊", "陀罗"), "破财": ("地劫", "地空"),
}
SHEN = {"病": ("病符",), "官非": ("官符", "贯索"), "破财": ("大耗", "小耗", "劫煞"),
        "婚": ("喜神", "青龙"), "子": ("龙德", "天德")}


def gong_gan(chart, idx):
    return C.palace_gan(chart["year_gan"], idx)


def hua_dict(gan_index):
    return C.SIHUA[gan_index]


def xiaoxian_hua(chart, age):
    xx = Z.xiaoxian_index(chart, age)
    return hua_dict(gong_gan(chart, xx)), xx


def liunian_hua(year):
    return hua_dict(C.year_gan_by_lunar_year(year))


def scope_of(chart, year, layer):
    age = year - chart["lunar_year"] + 1
    if layer == "流年":
        base = Z.liunian_index(year)
        return T.sanfang(base), base
    xx = Z.xiaoxian_index(chart, age)
    return [xx, (xx + 6) % 12], xx


def predicate_score(chart, year, event, layer, use_hua=None):
    """给该年该事件打分；use_hua 为四化表（小限四化或流年四化），None 则只用星与神。"""
    scope, base = scope_of(chart, year, layer)
    score = 0.0
    for i in scope:
        stars = chart["stars"].get(i, [])
        if chart["palace_of"][i] in PALACE_OF[event]:
            score += 1.0
        for m in MARK[event]:
            if m in stars:
                score += 1.0
        for sh in SHEN[event]:
            if chart["spirit_map"]["岁前"].get(sh) == i or chart["spirit_map"]["将前"].get(sh) == i                     or chart["spirit_map"]["博士"].get(sh) == i:
                score += 1.0
        if use_hua:
            for star, kind in use_hua.items():
                if star in stars and kind == "忌":
                    score += 1.5
                elif star in stars:
                    score += 0.5
        else:
            for star, kind in chart["hua_of_star"].items():
                if star in stars:
                    score += 1.5 if kind == "忌" else 0.5
    return score


def rank_percentile(chart, year, event, layer, use_hua=None, window=5):
    """事件年在同年数窗口内的分位（0~1，1 为最高）。"""
    years = [year - k for k in range(-window, window + 1)]
    scores = [predicate_score(chart, y, event, layer, use_hua) for y in years]
    target = predicate_score(chart, year, event, layer, use_hua)
    lower = sum(1 for s in scores if s < target)
    equal = sum(1 for s in scores if s == target) - 1
    return round((lower + 0.5 * max(equal, 0)) / (len(scores) - 1), 2), target


def compare(chart, year, event):
    """四种组合的分位。"""
    xh, _ = xiaoxian_hua(chart, year - chart["lunar_year"] + 1)
    return {
        "流年": rank_percentile(chart, year, event, "流年")[0],
        "小限": rank_percentile(chart, year, event, "小限")[0],
        "流年化": rank_percentile(chart, year, event, "流年", use_hua=liunian_hua(year))[0],
        "小限化": rank_percentile(chart, year, event, "小限", use_hua=xh)[0],
    }
