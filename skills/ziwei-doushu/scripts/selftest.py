# -*- coding: utf-8 -*-
"""自检：农历换算、紫微起例、命宫与大限顺逆。

运行：python scripts/selftest.py
"""

import sys
from datetime import date

import ziwei_core as C
import ziwei_chart as Z

FAIL = []


def check(name, got, want):
    if got != want:
        FAIL.append("%s: got %r want %r" % (name, got, want))


def main():
    # 农历换算（对照权威历法数据）
    for solar, lunar in [
        ((1990, 5, 17), (1990, 4, 23)),
        ((1961, 4, 19), (1961, 3, 5)),
        ((1947, 7, 21), (1947, 6, 4)),
        ((2023, 3, 22), (2023, -2, 1)),
        ((2024, 2, 10), (2024, 1, 1)),
        ((2000, 1, 1), (1999, 11, 25)),
        ((2100, 12, 31), (2100, 12, 1)),
        ((1900, 2, 1), (1900, 1, 2)),
    ]:
        d = date(*solar)
        check("solar_to_lunar %s" % (solar,), C.solar_to_lunar(d), lunar)
        check("lunar_to_solar %s" % (lunar,), C.lunar_to_solar(*lunar), d)

    # 紫微起例：书内简索表若干格
    cases = [
        ((1, 2), 1), ((2, 2), 2), ((3, 2), 2), ((16, 2), 9),
        ((1, 3), 4), ((2, 3), 1), ((28, 3), 1),
        ((1, 4), 11), ((2, 4), 4), ((18, 4), 8),
        ((1, 5), 6), ((30, 5), 7),
        ((1, 6), 9), ((2, 6), 6), ((13, 6), 11), ((30, 6), 6),
    ]
    for (day, ju), want in cases:
        check("ziwei day=%d ju=%d" % (day, ju), C.ziwei_index(day, ju), want)

    # 天府 = (4 - 紫微) mod 12
    check("tianfu(0)", C.tianfu_index(0), 4)
    check("tianfu(2)", C.tianfu_index(2), 2)
    check("tianfu(8)", C.tianfu_index(8), 8)

    # 《天纪》紫微19：1961 辛丑年三月初五 戌时 阴女
    ch = Z.build(lunar_known=True, year=1961, month=3, day=5, hour=20, gender="女")
    check("case19 命宫", C.ZHI[ch["ming"]], "午")
    check("case19 身宫", C.ZHI[ch["shen"]], "寅")
    check("case19 局", ch["ju"], 4)
    check("case19 紫微", C.ZHI[ch["ziwei_index"]], "子")
    check("case19 命宫星", ch["stars"][ch["ming"]], ["贪狼", "左辅", "天魁"])
    check("case19 大限逆行", ch["limits_forward"], True)
    check("case19 首限", (ch["limits"][0]["start_age"], ch["limits"][0]["end_age"]), (4, 13))

    # 《天纪》紫微22：1947 丁亥年六月初四 巳时 阴男
    ch2 = Z.build(lunar_known=True, year=1947, month=6, day=4, hour=10, gender="男")
    check("case22 命宫", C.ZHI[ch2["ming"]], "寅")
    check("case22 局", ch2["ju"], 4)
    check("case22 紫微", C.ZHI[ch2["ziwei_index"]], "寅")
    check("case22 命宫星", ch2["stars"][ch2["ming"]], ["紫微", "天府", "火星", "天刑", "孤辰"])
    check("case22 大限逆行", ch2["limits_forward"], False)

    # 真太阳时：成都应比标准时早约 64 分钟
    from datetime import datetime
    tst, corr = Z.true_solar(datetime(1990, 5, 17, 12, 0), 104.1)
    check("成都经度校正范围", -70 < corr < -55, True)
    check("成都真太阳时小时", tst.hour, 11)

    if FAIL:
        print("FAILED %d" % len(FAIL))
        for f in FAIL:
            print(" -", f)
        return 1
    print("ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
