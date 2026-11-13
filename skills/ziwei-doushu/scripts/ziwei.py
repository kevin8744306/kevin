# -*- coding: utf-8 -*-
"""紫微斗数排盘 + 天纪框架推导分析（命令行）。

示例：
    python ziwei.py --date 1990-05-17 --time 14:30 --city 成都 --gender 男
    python ziwei.py --date 1978-11-03 --time 06:05 --lon 113.3 --gender 女 --year 2026
    python ziwei.py --lunar 1990-4-23 --time 14:30 --city 上海 --gender 男 --json
"""

import argparse
import json
import re
import sys

import cities
import ziwei_core as C
import ziwei_chart as Z
import ziwei_analyse as A


def main(argv=None):
    p = argparse.ArgumentParser(description="紫微斗数排盘与推导分析")
    p.add_argument("--date", help="公历生日 YYYY-MM-DD")
    p.add_argument("--lunar", help="农历生日 YYYY-M-D（闰月用负数，如 2020--4-1）")
    p.add_argument("--time", default="12:00", help="出生时间 HH:MM（当地标准时）")
    p.add_argument("--hour", type=int, help="只给时辰：0-23")
    p.add_argument("--city", help="出生地城市名")
    p.add_argument("--lon", type=float, help="出生地东经（覆盖城市经度）")
    p.add_argument("--lat", type=float, help="出生地北纬（仅记录）")
    p.add_argument("--tz", type=float, help="时区偏移小时，默认取城市值或 8")
    p.add_argument("--gender", default="男", choices=["男", "女"])
    p.add_argument("--year", type=int, help="要看流年的年份")
    p.add_argument("--late-zi", action="store_true", help="23 点后算次日")
    p.add_argument("--month", type=int, help="农历月 1-12，配合 --year 输出流月宫")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    args = p.parse_args(argv)

    city_info = cities.lookup(args.city)
    lon = args.lon
    lat = args.lat
    tz = args.tz
    if city_info:
        lon = lon if lon is not None else city_info[0]
        lat = lat if lat is not None else city_info[1]
        tz = tz if tz is not None else city_info[2]
    if tz is None:
        tz = 8.0

    if args.time:
        hh, mm = [int(x) for x in args.time.replace("：", ":").split(":")]
    else:
        hh, mm = args.hour or 12, 0

    if args.lunar:
        mt = re.match(r"^(-?\d{4})-(-?\d{1,2})-(\d{1,2})$", args.lunar.strip())
        if not mt:
            p.error("--lunar 需要形如 1990-4-23（闰月用负月，如 2020--4-1）")
        y, m, d = int(mt.group(1)), int(mt.group(2)), int(mt.group(3))
        chart = Z.build(lunar_known=True, year=y, month=m, day=d,
                        hour=hh, minute=mm, gender=args.gender,
                        city=args.city, longitude=lon, latitude=lat, tz=tz,
                        late_zi=args.late_zi)
        birth = "农历 %d 年 %d 月 %d 日 %02d:%02d" % (y, abs(m), d, hh, mm)
    else:
        if not args.date:
            p.error("需要 --date 或 --lunar")
        y, m, d = [int(x) for x in args.date.split("-")]
        chart = Z.build(lunar_known=False, year=y, month=m, day=d, hour=hh, minute=mm,
                        gender=args.gender, city=args.city, longitude=lon, latitude=lat,
                        tz=tz, late_zi=args.late_zi)
        birth = "公历 %04d-%02d-%02d %02d:%02d" % (y, m, d, hh, mm)

    if args.json:
        payload = {k: v for k, v in chart.items() if k not in ("stars_by_palace",)}
        payload["stars"] = {str(k): v for k, v in chart["stars"].items()}
        payload["palaces"] = [
            {"index": i, "branch": C.ZHI[i], "name": chart["palace_of"][i],
             "stars": chart["stars"].get(i, [])} for i in range(12)]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    lines = ["# 紫微斗数命盘", ""]
    lines.append("- 生辰：%s（%s）" % (birth, args.city or "未注城市"))
    if chart.get("true_solar"):
        lines.append("- 真太阳时：%s（经度校正 %+.1f 分钟）" % (
            chart["true_solar"], chart["solar_correction_min"]))
    lines.append("")
    lines.append(Z.render_chart(chart, birth))
    lines.append("")
    lines.append(A.analyse(chart, args.year))
    if args.year and args.month:
        import ziwei_timing as T
        idx = T.month_palace(chart, args.year, args.month)
        snap = T.month_snapshot(chart, args.year, args.month)
        facts = snap["palace"]
        lines.append("")
        lines.append("## 流月（%d 年第 %d 月，斗君在%s）" % (
            args.year, args.month, C.ZHI[T.doujun(chart, args.year)]))
        lines.append("")
        lines.append("- 流月命宫：%s（%s）%s" % (
            C.ZHI[idx], facts["palace"],
            ("，坐" + "、".join(facts["main"])) if facts["main"] else "，空宫"))
        if facts["sha"]:
            lines.append("- 煞：%s" % "、".join(facts["sha"]))
        if facts["hua"]:
            lines.append("- 化：%s" % "、".join(k + v for k, v in facts["hua"].items()))
        lines.append("- 长生%s、博士%s" % (snap["chang_sheng"], snap["bo_shi"]))
        lines.append("- 对宫：%s（%s）" % (snap["opposite"]["zhi"], snap["opposite"]["palace"]))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())

