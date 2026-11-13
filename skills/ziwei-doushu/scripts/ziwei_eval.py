# -*- coding: utf-8 -*-
"""应期检验：小限 vs 流年、四化哪一层更对应；盘面判据的唯一定义处。

要点：
1. 事件判据按**该层命宫派生的十二宫**取（流年夫妻宫 = 流年命宫前两位），
   不按本命宫名——本命「夫妻宫」与流年「夫妻宫」是两件事。
2. 化忌的方向随事件而定：对婚、子、创业是阻力（减分），对离婚、官非、病、破财是触发（加分）。
3. 判据一旦定下不再按个案修改（见 references/04 第六节）。
"""

import ziwei_core as C
import ziwei_chart as Z
import ziwei_timing as T

EVENTS = ("婚", "子", "病", "官非", "破财", "创业", "离婚")

ROLE_OFFSET = {"命宫": 0, "夫妻": -2, "子女": -3, "财帛": -4, "疾厄": -5,
               "迁移": -6, "交友": -7, "官禄": -8, "田宅": -9}

ROLES = {
    "婚": ("夫妻", "子女"),
    "子": ("子女",),
    "病": ("疾厄",),
    "官非": ("官禄", "命宫"),
    "破财": ("财帛", "田宅"),
    "创业": ("迁移", "交友", "子女"),
    "离婚": ("夫妻",),
}

MARK = {
    "婚": ("红鸾", "天喜", "文昌", "文曲"),
    "子": ("红鸾", "天喜", "天魁", "天贵"),
    "病": ("擎羊", "陀罗", "天刑"),
    "官非": ("擎羊", "陀罗", "铃星", "天刑"),
    "破财": ("地劫", "地空", "大耗"),
    "创业": ("天府", "左辅", "巨门", "天魁", "天钺"),
    "离婚": ("火星", "擎羊", "寡宿"),
}

SHEN = {"病": ("病符",), "官非": ("官符", "贯索", "飞廉"),
        "破财": ("大耗", "小耗", "劫煞"), "婚": ("喜神", "青龙"),
        "子": ("龙德", "天德"), "创业": ("将星", "攀鞍", "岁驿"),
        "离婚": ("飞廉", "丧门")}

# 化忌对各类事件的方向：负 = 阻力，正 = 触发
JI_SIGN = {"婚": -1.5, "子": -1.5, "创业": -1.0,
           "离婚": 1.5, "官非": 1.5, "病": 1.5, "破财": 1.5}


def base_of(chart, year, layer, lunar_month=None):
    if layer == "流年":
        return Z.liunian_index(year)
    if layer == "小限":
        return Z.xiaoxian_index(chart, year - chart["lunar_year"] + 1)
    if layer == "流月":
        return T.month_palace(chart, year, lunar_month)
    raise ValueError(layer)


def score(chart, year, event, layer, lunar_month=None, hua=None):
    base = base_of(chart, year, layer, lunar_month)
    total = 0.0
    for role in ROLES[event]:
        idx = (base + ROLE_OFFSET[role]) % 12
        stars = chart["stars"].get(idx, [])
        total += 1.0                                  # 该角色宫本身命中
        for m in MARK[event]:
            if m in stars:
                total += 1.0
        for sh in SHEN[event]:
            for grp in ("岁前", "将前", "博士"):
                if chart["spirit_map"][grp].get(sh) == idx:
                    total += 1.0
        table = hua if hua is not None else chart["hua_of_star"]
        for star, kind in table.items():
            if star not in stars:
                continue
            if kind == "忌":
                total += JI_SIGN[event]
            else:
                total += 0.5
    return total


def rank(chart, year, event, layer, lunar_month=None, window=5, hua=None):
    """事件年（月）在同层相邻窗口内的分位，1 = 该层把它排最高。"""
    if layer == "流月":
        months = [m for m in range(max(1, lunar_month - window), min(12, lunar_month + window) + 1)]
        scores = [score(chart, year, event, layer, m, hua) for m in months]
        target = score(chart, year, event, layer, lunar_month, hua)
    else:
        years = [year + k for k in range(-window, window + 1)]
        scores = [score(chart, y, event, layer, None, hua) for y in years]
        target = score(chart, year, event, layer, None, hua)
    lower = sum(1 for s in scores if s < target)
    equal = sum(1 for s in scores if s == target) - 1
    return round((lower + 0.5 * max(equal, 0)) / max(len(scores) - 1, 1), 2)


def compare(chart, year, event):
    """四层对比（年层）：流年 / 小限 / 流年四化 / 小限四化。"""
    xh, _ = T.xiaoxian_hua(chart, year - chart["lunar_year"] + 1)
    return {
        "流年": rank(chart, year, event, "流年"),
        "小限": rank(chart, year, event, "小限"),
        "流年化": rank(chart, year, event, "流年", hua=T.liunian_hua(year)),
        "小限化": rank(chart, year, event, "小限", hua=xh),
    }
