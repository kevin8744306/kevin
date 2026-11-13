# -*- coding: utf-8 -*-
"""排盘装配、真太阳时、大限流年与命盘渲染。"""

import math
from datetime import date, datetime, timedelta

import ziwei_core as C

PALACE_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
                "迁移", "交友", "官禄", "田宅", "福德", "父母"]

LUMA_STARS = set(["紫微", "天机", "太阳", "武曲", "天同", "廉贞",
                  "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"])
AUX_STARS = ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺",
             "禄存", "天马", "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
             "红鸾", "天喜", "天刑", "天姚", "天哭", "天虚", "龙池", "凤阁",
             "孤辰", "寡宿", "三台", "八座", "恩光", "天贵",
             "天官", "天福", "天才", "天寿", "台辅", "封诰"]
SPIRIT_NAMES = set(["岁建", "晦气", "丧门", "贯索", "官符", "小耗", "大耗",
                    "龙德", "白虎", "天德", "吊客", "病符", "将星", "攀鞍",
                    "岁驿", "息神", "华盖", "劫煞", "灾煞", "天煞", "指背",
                    "咸池", "月煞", "亡神", "博士", "力士", "青龙", "将军",
                    "奏书", "飞廉", "喜神", "伏兵", "官府", "长生", "沐浴",
                    "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝",
                    "胎", "养"])


def equation_of_time(d):
    """均时差（分钟），Cooper/Meeus 近似，误差 < 30 秒。"""
    n = (d - date(d.year, 1, 1)).days + 1
    b = 2 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def true_solar(dt, longitude, tz=8.0):
    """标准时 -> 真太阳时。dt 为该时区标准时间。"""
    minutes = (longitude - tz * 15.0) * 4.0 + equation_of_time(dt.date())
    return dt + timedelta(minutes=minutes), minutes


def shichen_index(dt):
    h = dt.hour
    return ((h + 1) // 2) % 12


def build(lunar_known=False, year=None, month=None, day=None, hour=12, minute=0,
          gender="男", city=None, longitude=None, latitude=None, tz=8.0,
          late_zi=False, leap_half_month_rule=True):
    """排一张紫微斗数命盘，返回 dict。"""
    if not lunar_known:
        std = datetime(year, month, day, hour, minute)
        if longitude is None:
            longitude = 120.0
        tst, correction = true_solar(std, longitude, tz)
        d = tst.date()
        hour_eff = tst.hour
        minute_eff = tst.minute
        lunar_year, lunar_month, lunar_day = C.solar_to_lunar(d)
    else:
        tst = None
        correction = 0.0
        lunar_year, lunar_month, lunar_day = year, month, day
        hour_eff = hour
        minute_eff = minute

    leap = lunar_month < 0
    lm = -lunar_month if leap else lunar_month

    # 晚子时：23 点后按次日排（可选，默认不换日，只记时支子）
    if hour_eff >= 23 and late_zi:
        lunar_year, lunar_month, lunar_day = C.solar_to_lunar(
            C.lunar_to_solar(lunar_year, lunar_month, lunar_day) + timedelta(days=1))

    hour_zhi = shichen_index(tst) if tst is not None else (((hour_eff + 1) // 2) % 12)
    if hour_eff >= 23:
        hour_zhi = 0

    # 闰月前半月算本月、后半月算下月（常见取法，可关）
    month_eff = lm
    if leap and leap_half_month_rule and lunar_day > 15:
        month_eff = lm + 1 if lm < 12 else 1

    year_gan = C.year_gan_by_lunar_year(lunar_year)
    year_zhi = C.year_zhi_by_lunar_year(lunar_year)
    ming, shen = C.ming_shen_gong(month_eff, hour_zhi)
    ming_gan = C.palace_gan(year_gan, ming)
    ju, ju_wuxing = C.wuxing_ju(ming_gan, ming)

    zi = C.ziwei_index(lunar_day, ju)
    chart = {
        "lunar_year": lunar_year, "lunar_month": lunar_month, "lunar_day": lunar_day,
        "lunar_month_leap": leap, "lunar_month_eff": month_eff,
        "year_gan": year_gan, "year_zhi": year_zhi,
        "hour_zhi": hour_zhi, "ming": ming, "shen": shen,
        "ming_gan": ming_gan, "ju": ju, "ju_wuxing": ju_wuxing,
        "ziwei_index": zi,
        "gender": gender,
        "longitude": longitude, "latitude": latitude, "tz": tz,
        "solar_correction_min": correction,
        "hour_eff": hour_eff, "minute_eff": minute_eff,
        "late_zi": late_zi,
    }
    if tst is not None:
        chart["true_solar"] = tst.strftime("%Y-%m-%d %H:%M")

    stars = C.place_stars(chart)
    chart["stars"] = stars

    # 宫位：命宫逆布十二宫
    palace_of = {}
    for i, name in enumerate(PALACE_NAMES):
        palace_of[(ming - i) % 12] = name
    chart["palace_of"] = palace_of

    # 生年四化
    sh = C.SIHUA[year_gan]
    hua_of_star = {}
    for kind, star in sh.items():
        hua_of_star[star] = kind
    chart["sihua"] = sh
    chart["hua_of_star"] = hua_of_star

    # 大限
    yang = (year_gan % 2 == 0)
    male = (gender == "男")
    forward = (yang and male) or ((not yang) and (not male))
    limits = []
    for k in range(12):
        idx = (ming + k) % 12 if forward else (ming - k) % 12
        start_age = ju + k * 10
        limits.append({"palace_index": idx, "palace": palace_of[idx],
                       "start_age": start_age, "end_age": start_age + 9})
    chart["limits"] = limits
    chart["limits_forward"] = forward

    # 小限
    if year_zhi in (2, 6, 10):
        xiao_start = 4 if male else 10
    elif year_zhi in (8, 0, 4):
        xiao_start = 10 if male else 4
    elif year_zhi in (5, 9, 1):
        xiao_start = 7 if male else 1
    else:
        xiao_start = 1 if male else 7
    chart["xiaoxian_start"] = xiao_start

    # 命主、身主
    chart["mingzhu"] = MING_ZHU[year_zhi]
    chart["shenzhu"] = SHEN_ZHU[year_zhi]
    return chart


MING_ZHU = ["贪狼", "巨门", "禄存", "文曲", "廉贞", "武曲",
            "破军", "武曲", "廉贞", "文曲", "禄存", "巨门"]
SHEN_ZHU = ["火星", "天相", "天梁", "天同", "文昌", "天机",
            "火星", "天相", "天梁", "天同", "文昌", "天机"]


def xiaoxian_index(chart, age):
    step = age - 1
    if chart["gender"] == "男":
        return (chart["xiaoxian_start"] + step) % 12
    return (chart["xiaoxian_start"] - step) % 12


def daxian_for_age(chart, age):
    for lim in chart["limits"]:
        if lim["start_age"] <= age <= lim["end_age"]:
            return lim
    return None


def liunian_index(year):
    return C.year_zhi_by_lunar_year(year)


JU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}


def ju_name(chart):
    return JU_NAMES.get(chart["ju"], "%d局" % chart["ju"])


def render_chart(chart, birth_text=""):
    """渲染为 Markdown 命盘。"""
    out = ["## 命盘", ""]
    out.append("- 农历：%s年%s月%s日 %s时%s" % (
        chart["lunar_year"],
        ("闰" if chart["lunar_month_leap"] else "") + str(abs(chart["lunar_month"])),
        chart["lunar_day"], C.SHICHEN[chart["hour_zhi"]],
        ("，真太阳时 %s" % chart["true_solar"]) if chart.get("true_solar") else ""))
    out.append("- 年干支：%s%s　五行局：%s　起限 %d 岁" % (
        C.GAN[chart["year_gan"]], C.ZHI[chart["year_zhi"]], ju_name(chart), chart["ju"]))
    out.append("- 命宫：%s　身宫：%s　命主：%s　身主：%s" % (
        C.ZHI[chart["ming"]], C.ZHI[chart["shen"]], chart["mingzhu"], chart["shenzhu"]))
    out.append("- 阴阳男女：%s%s　大限%s行" % (
        "阳" if chart["year_gan"] % 2 == 0 else "阴", chart["gender"],
        "顺" if chart["limits_forward"] else "逆"))
    out.append("")
    out.append("| 宫位 | 地支 | 主星（庙旺） | 吉煞辅星 | 四化 | 大限 | 长生 | 博士 | 岁前 | 将前 |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for i in range(12):
        name = chart["palace_of"][i]
        stars = chart["stars"].get(i, [])
        main = [s for s in stars if s in LUMA_STARS]
        aux = [s for s in stars if s in AUX_STARS]
        hua = ["%s化%s" % (s, chart["hua_of_star"][s]) for s in stars if s in chart["hua_of_star"]]
        lim = [l for l in chart["limits"] if l["palace_index"] == i][0]
        def pick(group):
            for nm, at in chart["spirit_map"][group].items():
                if at == i:
                    return nm
            return "—"
        out.append("| %s%s | %s | %s | %s | %s | %d–%d | %s | %s | %s | %s |" % (
            "★" if i == chart["ming"] else "",
            name, C.ZHI[i],
            "、".join("%s(%s)" % (s, C.brightness(s, i)) for s in main) or "（空宫）",
            "、".join(aux) or "—",
            "、".join(hua) or "—",
            lim["start_age"], lim["end_age"],
            pick("长生"), pick("博士"), pick("岁前"), pick("将前")))
    out.append("")
    out.append("> 星曜亮度为通行庙旺表，各派略有出入；空宫借对宫看。")
    return "\n".join(out)
