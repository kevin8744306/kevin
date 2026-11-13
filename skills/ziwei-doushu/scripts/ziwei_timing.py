# -*- coding: utf-8 -*-
"""分层推演：本命 / 大限 / 流年 / 小限 的四正与权重。

规则来源：
- 大限看三方四正、流年亦看三方四正 —— 《天纪》上册 第72页
- 小限看本宫与对宫 —— 《紫微斗数全书》小限取法（本 skill references/01 第 8 节）
- 命好不如限好 —— 《天纪》上册 第71页

权重不是玄学系数，是「先看哪一层、以哪一层为准」的裁决顺序，
数值只用于把四层证据合成一个可比较的强度，便于排序与复核。
"""

import ziwei_core as C
import ziwei_chart as Z

LAYER_WEIGHT = {"本命": 1.0, "大限": 0.6, "流年": 0.35, "小限": 0.15}
SHA = ("擎羊", "陀罗", "火星", "铃星", "地空", "地劫")
JI = ("左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马")



CHANGSHENG_MEANING = {
    "长生": "萌发、起步", "沐浴": "不稳、易动", "冠带": "成形、有模样",
    "临官": "任事、可担", "帝旺": "极盛、到顶", "衰": "由盛转减",
    "病": "力弱、需养", "死": "止住、不动", "墓": "收藏、入库",
    "绝": "断、空", "胎": "酝酿、未显", "养": "蓄积、待发",
}
BOSHI_MEANING = {
    "博士": "智与专业", "力士": "力与执行", "青龙": "喜与得助", "小耗": "小损与零耗",
    "将军": "势与主事", "奏书": "文书与公文", "飞廉": "口舌与被议", "喜神": "喜庆",
    "病符": "病与就医", "大耗": "大损与破财", "伏兵": "暗与隐忧", "官府": "官与规制",
}
CHANGSHENG_SCORE = {"长生": -0.3, "沐浴": 0.1, "冠带": -0.2, "临官": -0.4, "帝旺": -0.4,
                    "衰": 0.2, "病": 0.3, "死": 0.3, "墓": 0.2, "绝": 0.4,
                    "胎": -0.1, "养": -0.1}
BOSHI_SCORE = {"博士": -0.2, "力士": -0.1, "青龙": -0.3, "小耗": 0.1, "将军": -0.1,
               "奏书": -0.2, "飞廉": 0.2, "喜神": -0.3, "病符": 0.3, "大耗": 0.4,
               "伏兵": 0.2, "官府": 0.2}


def sanfang(idx):
    """三方四正：本宫、两个三合宫、对宫。"""
    return [idx, (idx + 4) % 12, (idx + 8) % 12, (idx + 6) % 12]


def palace_facts(chart, idx):
    stars = chart["stars"].get(idx, [])
    main = [s for s in stars if s in Z.LUMA_STARS]
    sha = [s for s in stars if s in SHA]
    ji = [s for s in stars if s in JI]
    hua = {s: chart["hua_of_star"][s] for s in stars if s in chart["hua_of_star"]}
    return {"zhi": C.ZHI[idx], "palace": chart["palace_of"][idx],
            "main": main, "sha": sha, "ji": ji, "hua": hua,
            "bright": {s: C.brightness(s, idx) for s in main}}


def layer_strength(facts):
    """单层强度：煞与忌加，吉与禄权科减。可比较、可解释。"""
    score = 0.0
    for s in facts["sha"]:
        score += 1.0
    for star, kind in facts["hua"].items():
        score += 1.5 if kind == "忌" else -0.5
    for s in facts["ji"]:
        score -= 0.5
    for s, b in facts["bright"].items():
        if b in ("庙", "旺"):
            score -= 0.3
        elif b in ("陷", "不得地"):
            score += 0.3
    return score


def spirit_state(chart, idx):
    """取该宫的长生与博士状态。"""
    cs = None
    bs = None
    for name, at in chart["spirit_map"]["长生"].items():
        if at == idx:
            cs = name
    for name, at in chart["spirit_map"]["博士"].items():
        if at == idx:
            bs = name
    return cs, bs


def state_score(chart, idx):
    cs, bs = spirit_state(chart, idx)
    return CHANGSHENG_SCORE.get(cs, 0.0) + BOSHI_SCORE.get(bs, 0.0)


def snapshot(chart, year):
    """某一年的四层快照，含各自三方四正（小限取本宫与对宫）。"""
    ln = Z.liunian_index(year)
    age = year - chart["lunar_year"] + 1
    dx = Z.daxian_for_age(chart, age)
    xx = Z.xiaoxian_index(chart, age)
    layers = []
    layers.append({"layer": "本命", "base": chart["ming"],
                   "scope": sanfang(chart["ming"])})
    if dx:
        layers.append({"layer": "大限", "base": dx["palace_index"],
                       "scope": sanfang(dx["palace_index"]),
                       "range": "%d-%d" % (dx["start_age"], dx["end_age"])})
    layers.append({"layer": "流年", "base": ln, "scope": sanfang(ln), "ganzhi": C.GAN[C.year_gan_by_lunar_year(year)] + C.ZHI[ln]})
    layers.append({"layer": "小限", "base": xx,
                   "scope": [xx, (xx + 6) % 12]})
    out = []
    for layer in layers:
        facts = [palace_facts(chart, i) for i in layer["scope"]]
        strength = layer_strength(facts[0]) + state_score(chart, layer["scope"][0])
        out.append({"layer": layer["layer"], "range": layer.get("range", ""),
                    "ganzhi": layer.get("ganzhi", ""),
                    "base": facts[0], "scope": facts,
                    "strength": round(LAYER_WEIGHT[layer["layer"]]
                                      * (1 + max(-0.55, min(1.2, strength))), 2)})
    return out


def render_layers(chart, year):
    out = ["### %d 年四层快照（%s）" % (year, "、".join(
        ("%s%.2f" % (l["layer"], l["strength"])) for l in snapshot(chart, year))), ""]
    for l in snapshot(chart, year):
        b = l["base"]
        desc = "%s%s%s" % (b["zhi"], b["palace"],
                           ("坐" + "、".join(b["main"])) if b["main"] else "空宫")
        extra = []
        if b["sha"]:
            extra.append("煞：" + "、".join(b["sha"]))
        if b["hua"]:
            extra.append("化：" + "、".join(s + k for s, k in b["hua"].items()))
        if b["ji"]:
            extra.append("吉：" + "、".join(b["ji"]))
        scope = "、".join("%s%s" % (f["zhi"], f["palace"]) for f in l["scope"][1:])
        tag = ""
        if l["range"]:
            tag += l["range"]
        if l["ganzhi"]:
            tag += ("" if not tag else " ") + l["ganzhi"]
        out.append("- **%s**%s：%s；%s。四正含 %s。" % (
            l["layer"], ("（%s）" % tag) if tag else "",
            desc, "，".join(extra) or "无煞忌", scope))
    return "\n".join(out)

def doujun(chart, year):
    """斗君：流年正月宫。以流年太岁宫起正月逆数至生月，再自该宫起子时顺数至生时。"""
    tai = Z.liunian_index(year)
    month = chart["lunar_month_eff"]
    base = (tai - (month - 1)) % 12
    return (base + chart["hour_zhi"]) % 12


def month_palace(chart, year, lunar_month):
    """流月宫：斗君起正月，顺行。lunar_month 取 1–12（闰月按本月算）。"""
    return (doujun(chart, year) + (lunar_month - 1)) % 12


def month_snapshot(chart, year, lunar_month):
    idx = month_palace(chart, year, lunar_month)
    facts = palace_facts(chart, idx)
    cs, bs = spirit_state(chart, idx)
    return {
        "palace": facts,
        "index": idx,
        "opposite": palace_facts(chart, (idx + 6) % 12),
        "chang_sheng": cs, "bo_shi": bs,
        "strength": round(LAYER_WEIGHT["流年"] * (1 + layer_strength(facts) + state_score(chart, idx)), 2),
    }


def gong_gan(chart, idx):
    """宫干：由年干五虎遁推某地支宫的天干。"""
    return C.palace_gan(chart["year_gan"], idx)


def xiaoxian_hua(chart, age):
    """小限四化：以小限宫宫干起四化。"""
    xx = Z.xiaoxian_index(chart, age)
    return C.SIHUA[gong_gan(chart, xx)], xx


def liunian_hua(year):
    """流年四化：以流年干起四化（本 skill 默认不用于断，只作对照）。"""
    return C.SIHUA[C.year_gan_by_lunar_year(year)]
