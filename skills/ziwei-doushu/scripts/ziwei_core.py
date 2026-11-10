# -*- coding: utf-8 -*-
"""紫微斗数排盘内核：农历换算、干支、安星、大限流年。

依据：
- 安星法：集文书局《紫微斗数》（本仓库 references/01-排盘规则.md 有逐条核对）
- 解读框架：倪海厦《天纪》（references/02-天纪解读框架.md）

只依赖 Python 标准库。
"""

from datetime import date, datetime, timedelta

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
SHICHEN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 农历 1900-2100：每年 13 位，(闰月 << 13) | 月大小位（bit0 = 正月，bit12 = 闰月）
from lunar_data import LUNAR_INFO

BASE_DATE = date(1900, 1, 31)  # 1900 年正月初一


def lunar_year_days(info):
    leap = info >> 13
    mbits = info & 0xFFF
    total = 348 + bin(mbits).count("1")
    if leap:
        total += 29 + ((info >> 12) & 1)
    return total


def solar_to_lunar(d):
    """公历 date -> (农历年, 农历月(闰月为负数), 农历日)。"""
    info = LUNAR_INFO
    off = (d - BASE_DATE).days
    y = 1900
    while off >= lunar_year_days(info[y - 1900]):
        off -= lunar_year_days(info[y - 1900])
        y += 1
    v = info[y - 1900]
    leap = v >> 13
    mbits = v & 0xFFF
    m = 1
    while m <= 12:
        ln = 29 + ((mbits >> (m - 1)) & 1)
        if off < ln:
            return (y, m, off + 1)
        off -= ln
        if leap == m:
            ln = 29 + ((v >> 12) & 1)
            if off < ln:
                return (y, -m, off + 1)
            off -= ln
        m += 1
    raise ValueError("农历换算失败: %s" % d)


def lunar_to_solar(ly, lm, ld):
    """农历 -> 公历 date。lm<0 表示闰月。"""
    leap = -lm if lm < 0 else 0
    m = -lm if lm < 0 else lm
    info = LUNAR_INFO
    off = 0
    for y in range(1900, ly):
        off += lunar_year_days(info[y - 1900])
    v = info[ly - 1900]
    mbits = v & 0xFFF
    for k in range(1, m):
        off += 29 + ((mbits >> (k - 1)) & 1)
        if (v >> 13) == k:
            off += 29 + ((v >> 12) & 1)
    if leap:
        off += 29 + ((mbits >> (m - 1)) & 1)
    off += ld - 1
    return BASE_DATE + timedelta(days=off)


# 日干支锚点：1900-01-31（农历正月初一）为甲辰日
DAY_GANZHI_ANCHOR = (date(1900, 1, 31), 40)  # 甲辰 = 第 41 个，索引 40


def day_ganzhi(d):
    base, idx = DAY_GANZHI_ANCHOR
    return (idx + (d - base).days) % 60


def ganzhi_name(i):
    return GAN[i % 10] + ZHI[i % 12]


def year_ganzhi(lunar_year):
    # 1984 甲子
    return ((lunar_year - 1984) % 60)


def year_gan_by_lunar_year(lunar_year):
    return (lunar_year - 1984) % 10


def year_zhi_by_lunar_year(lunar_year):
    return (lunar_year - 1984) % 12


WUHU_DUN = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}  # 年干 -> 寅宫天干


def palace_gan(year_gan, branch_index):
    """五虎遁：由年干推某地支宫的天干索引。"""
    start = WUHU_DUN[year_gan]
    return (start + (branch_index - 2)) % 10


NAYIN = [
    (2, "水二局"), (3, "木三局"), (4, "金四局"), (5, "土五局"), (6, "火六局"),
]

NAYIN_WUXING = [
    "金", "火", "木", "土", "金", "火", "水", "土", "金", "木",
    "水", "土", "火", "木", "水", "金", "火", "木", "土", "金",
    "火", "水", "土", "金", "木", "水", "土", "火", "木", "水",
]
WUXING_JU = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}


def naying_of(gan, zhi):
    idx = None
    for i in range(60):
        if i % 10 == gan and i % 12 == zhi:
            idx = i
            break
    if idx is None:
        raise ValueError("干支不合: %s%s" % (GAN[gan], ZHI[zhi]))
    return NAYIN_WUXING[idx // 2]


def wuxing_ju(gan, zhi):
    wx = naying_of(gan, zhi)
    return WUXING_JU[wx], wx


# ---- 安星表 ----
TIAN_KUI = {0: 1, 1: 0, 2: 11, 3: 11, 4: 1, 5: 0, 6: 1, 7: 6, 8: 3, 9: 3}
TIAN_YUE = {0: 7, 1: 8, 2: 9, 3: 9, 4: 7, 5: 8, 6: 7, 7: 2, 8: 5, 9: 5}
LU_CUN = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
TIAN_GUAN = [7, 4, 5, 2, 3, 9, 11, 9, 10, 6]
TIAN_FU = [9, 8, 0, 11, 3, 2, 6, 5, 6, 5]
SIHUA = {
    0: {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    1: {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    2: {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    3: {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    4: {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    5: {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    6: {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    7: {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    8: {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    9: {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

ZHU_XING = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

# 紫微起例：日数 + 五行局 -> 紫微宫
# 基准序列（局数为 6 时，日 1..6 的位置），其余局顺移
ZIWEI_SEQ = [9, 6, 11, 4, 1, 2]  # 酉 午 亥 辰 丑 寅


def ziwei_index(day, ju):
    r = day % ju
    k = (day - r) // ju
    if r == 0:
        r = ju
        k -= 1
    base = ZIWEI_SEQ[(6 - ju) + (r - 1)]
    return (base + k) % 12


def tianfu_index(ziwei):
    return (4 - ziwei) % 12


def ming_shen_gong(lunar_month, hour_index):
    ming = (2 + (lunar_month - 1) - hour_index) % 12
    shen = (2 + (lunar_month - 1) + hour_index) % 12
    return ming, shen


def place_stars(chart):
    """依据已确定的紫微位置安十四主星与主要辅煞星。"""
    zi = chart["ziwei_index"]
    tf = tianfu_index(zi)
    stars = {}

    def put(name, idx):
        stars.setdefault(idx, []).append(name)

    put("紫微", zi)
    put("天机", (zi - 1) % 12)
    put("太阳", (zi - 3) % 12)
    put("武曲", (zi - 4) % 12)
    put("天同", (zi - 5) % 12)
    put("廉贞", (zi - 8) % 12)
    put("天府", tf)
    put("太阴", (tf + 1) % 12)
    put("贪狼", (tf + 2) % 12)
    put("巨门", (tf + 3) % 12)
    put("天相", (tf + 4) % 12)
    put("天梁", (tf + 5) % 12)
    put("七杀", (tf + 6) % 12)
    put("破军", (tf + 10) % 12)

    month = chart["lunar_month_eff"]
    hour = chart["hour_zhi"]
    ygan = chart["year_gan"]
    yzhi = chart["year_zhi"]
    day = chart["lunar_day"]

    put("左辅", (4 + month - 1) % 12)
    put("右弼", (10 - (month - 1)) % 12)
    put("文昌", (10 - hour) % 12)
    put("文曲", (4 + hour) % 12)
    put("天魁", TIAN_KUI[ygan])
    put("天钺", TIAN_YUE[ygan])
    lucun = LU_CUN[ygan]
    put("禄存", lucun)
    put("擎羊", (lucun + 1) % 12)
    put("陀罗", (lucun - 1) % 12)

    # 火星、铃星：寅午戌 丑/卯；申子辰 寅/戌；巳酉丑 卯/戌；亥卯未 酉/戌
    if yzhi in (2, 6, 10):
        h_start, l_start = 1, 3
    elif yzhi in (8, 0, 4):
        h_start, l_start = 2, 10
    elif yzhi in (5, 9, 1):
        h_start, l_start = 3, 10
    else:
        h_start, l_start = 9, 10
    put("火星", (h_start + hour) % 12)
    put("铃星", (l_start + hour) % 12)

    put("地劫", (11 + hour) % 12)
    put("地空", (11 - hour) % 12)

    # 天马
    if yzhi in (2, 6, 10):
        tianma = 8
    elif yzhi in (8, 0, 4):
        tianma = 2
    elif yzhi in (5, 9, 1):
        tianma = 11
    else:
        tianma = 5
    put("天马", tianma)

    # 红鸾天喜
    hongluan = (3 - yzhi) % 12
    put("红鸾", hongluan)
    put("天喜", (hongluan + 6) % 12)

    put("天刑", (9 + month - 1) % 12)
    put("天姚", (1 + month - 1) % 12)
    put("天哭", (6 - yzhi) % 12)
    put("天虚", (6 + yzhi) % 12)
    put("龙池", (4 + yzhi) % 12)
    put("凤阁", (10 - yzhi) % 12)

    # 孤辰寡宿
    if yzhi in (11, 0, 1):
        gu, gua = 2, 10
    elif yzhi in (2, 3, 4):
        gu, gua = 5, 1
    elif yzhi in (5, 6, 7):
        gu, gua = 8, 4
    else:
        gu, gua = 11, 7
    put("孤辰", gu)
    put("寡宿", gua)

    # 天官、天福（依年干）
    put("天官", TIAN_GUAN[ygan])
    put("天福", TIAN_FU[ygan])
    # 天才、天寿（命宫／身宫起子顺数至年支）
    put("天才", (chart["ming"] + chart["year_zhi"]) % 12)
    put("天寿", (chart["shen"] + chart["year_zhi"]) % 12)
    # 台辅、封诰（午／寅起子时顺行）
    put("台辅", (6 + hour) % 12)
    put("封诰", (2 + hour) % 12)
    # 三台八座、恩光天贵
    zuofu = (4 + month - 1) % 12
    youbi = (10 - (month - 1)) % 12
    wenchang = (10 - hour) % 12
    wenqu = (4 + hour) % 12
    put("三台", (zuofu + day - 2) % 12)
    put("八座", (youbi - (day - 2)) % 12)
    put("恩光", (wenchang + day - 2) % 12)
    put("天贵", (wenqu + day - 2) % 12)

    place_spirits(chart, stars)

    chart["stars_by_palace"] = stars
    return stars


# 十四主星庙旺利陷（通行表；子丑寅卯辰巳午未申酉戌亥）
BRIGHTNESS = {
    "紫微": ["平", "庙", "庙", "旺", "得地", "旺", "庙", "庙", "旺", "平", "得地", "旺"],
    "天机": ["庙", "陷", "得地", "旺", "利", "平", "庙", "陷", "得地", "旺", "利", "平"],
    "太阳": ["陷", "陷", "旺", "庙", "旺", "旺", "庙", "得地", "得地", "平", "陷", "陷"],
    "武曲": ["旺", "庙", "得地", "利", "庙", "平", "旺", "庙", "得地", "利", "庙", "平"],
    "天同": ["旺", "陷", "利", "庙", "平", "庙", "陷", "陷", "旺", "平", "平", "庙"],
    "廉贞": ["平", "利", "庙", "平", "利", "陷", "平", "利", "庙", "平", "利", "陷"],
    "天府": ["庙", "庙", "庙", "得地", "庙", "得地", "旺", "庙", "得地", "旺", "庙", "得地"],
    "太阴": ["庙", "庙", "陷", "陷", "陷", "陷", "陷", "得地", "旺", "旺", "庙", "庙"],
    "贪狼": ["旺", "庙", "平", "利", "庙", "陷", "旺", "利", "平", "庙", "利", "陷"],
    "巨门": ["旺", "陷", "庙", "庙", "陷", "平", "旺", "陷", "庙", "庙", "陷", "旺"],
    "天相": ["庙", "庙", "庙", "陷", "得地", "得地", "庙", "得地", "庙", "陷", "得地", "得地"],
    "天梁": ["庙", "旺", "庙", "庙", "庙", "陷", "庙", "旺", "陷", "得地", "庙", "陷"],
    "七杀": ["旺", "庙", "庙", "旺", "庙", "平", "旺", "庙", "庙", "旺", "庙", "平"],
    "破军": ["旺", "庙", "得地", "陷", "旺", "平", "庙", "旺", "得地", "陷", "旺", "平"],
}


def brightness(star, branch):
    return BRIGHTNESS.get(star, ["平"] * 12)[branch % 12]


# ---- 十二神：长生 / 博士 / 岁前 / 将前 ----
SUIQIAN = ["岁建", "晦气", "丧门", "贯索", "官符", "小耗",
           "大耗", "龙德", "白虎", "天德", "吊客", "病符"]
JIANGQIAN = ["将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞",
             "灾煞", "天煞", "指背", "咸池", "月煞", "亡神"]
BOSHI = ["博士", "力士", "青龙", "小耗", "将军", "奏书",
         "飞廉", "喜神", "病符", "大耗", "伏兵", "官府"]
CHANGSHENG = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰",
              "病", "死", "墓", "绝", "胎", "养"]
JIANGXING = {2: 6, 6: 6, 10: 6, 8: 0, 0: 0, 4: 0, 5: 9, 9: 9, 1: 9, 11: 3, 3: 3, 7: 3}
CHANGSHENG_START = {2: 8, 3: 11, 4: 5, 5: 8, 6: 2}


def place_spirits(chart, stars):
    """安四组十二神；流年定位与应期用（见 references/01 第 6.5 节）。"""
    yg = chart["year_gan"]
    yz = chart["year_zhi"]
    male = chart["gender"] == "男"
    yang = (yg % 2 == 0)
    forward = (yang and male) or ((not yang) and (not male))

    start = CHANGSHENG_START[chart["ju"]]
    for k, name in enumerate(CHANGSHENG):
        idx = (start + k) % 12 if forward else (start - k) % 12
        stars.setdefault(idx, []).append(name)

    lc = LU_CUN[yg]
    for k, name in enumerate(BOSHI):
        idx = (lc + k) % 12 if forward else (lc - k) % 12
        stars.setdefault(idx, []).append(name)

    for k, name in enumerate(SUIQIAN):
        stars.setdefault((yz + k) % 12, []).append(name)

    jx = JIANGXING[yz]
    for k, name in enumerate(JIANGQIAN):
        stars.setdefault((jx + k) % 12, []).append(name)

    chart["spirits"] = {"长生": CHANGSHENG, "博士": BOSHI,
                        "岁前": SUIQIAN, "将前": JIANGQIAN}
    smap = {}
    for gname, names, start0 in (("长生", CHANGSHENG, CHANGSHENG_START[chart["ju"]]),
                                 ("博士", BOSHI, LU_CUN[yg]),
                                 ("岁前", SUIQIAN, yz),
                                 ("将前", JIANGQIAN, JIANGXING[yz])):
        step = 1 if (gname in ("岁前", "将前") or forward) else -1
        smap[gname] = {name: (start0 + k * step) % 12 for k, name in enumerate(names)}
    chart["spirit_map"] = smap
    return stars
