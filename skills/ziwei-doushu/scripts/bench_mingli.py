# -*- coding: utf-8 -*-
"""与 iztro 预排盘结果做逐项对照（MingLi-Bench 的 32 个盘）。

用法：
    python scripts/bench_mingli.py [fortune_api_results.json]

数据来源：https://github.com/DestinyLinker/MingLi-Bench 的 data/fortune_api_results.json
（用 its `gh api repos/.../contents/data/fortune_api_results.json` 下载到本地）。
对照项：命宫、身宫、五行局、紫微所在宫、四化星。iztro 不做真太阳时校正，故本脚本用 --no-solar 口径。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ziwei_core as C
import ziwei_chart as Z

ZHI = "子丑寅卯辰巳午未申酉戌亥"


def iztro_basics(chart_json):
    d = chart_json["api_response"]["data"]["data"]
    out = {
        "ming": ZHI.index(d["earthlyBranchOfSoulPalace"]),
        "shen": ZHI.index(d["earthlyBranchOfBodyPalace"]),
        "ju": d["fiveElementsClass"],
        "ziwei": None,
        "hua": {},
    }
    for pal in d["palaces"]:
        idx = ZHI.index(pal["earthlyBranch"])
        for st in pal.get("majorStars", []) + pal.get("minorStars", []):
            if st["name"] == "紫微":
                out["ziwei"] = idx
            if st.get("mutagen"):
                out["hua"][st["name"]] = st["mutagen"]
    return out


def our_basics(case):
    b = case["birth_info"]
    year, month, day = b["year"], b["month"], b["day"]
    hour, minute = b.get("hour", 12), b.get("minute", 0)
    gender = b.get("gender", "男")
    if b.get("calendar_type") == "lunar":
        ch = Z.build(lunar_known=True, year=year, month=month, day=day, hour=hour,
                     minute=minute, gender=gender, solar_correction=False)
    else:
        ch = Z.build(lunar_known=False, year=year, month=month, day=day, hour=hour,
                     minute=minute, gender=gender, solar_correction=False, dst=False)
    return ch


def main(path):
    cases = json.load(open(path, encoding="utf-8-sig"))
    rows = []
    for case in cases:
        if case.get("status") != "ok" and "api_response" not in case:
            continue
        api = case.get("api_response") or {}
        if not api.get("success"):
            continue
        try:
            ref = iztro_basics(case)
            mine = our_basics(case)
        except Exception as exc:  # noqa: BLE001
            rows.append((case["case_id"], False, "error: %s" % exc))
            continue
        ju_map = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}
        checks = [
            ("命宫", mine["ming"], ref["ming"]),
            ("身宫", mine["shen"], ref["shen"]),
            ("五行局", ju_map[mine["ju"]], ref["ju"]),
            ("紫微", mine["ziwei_index"], ref["ziwei"]),
        ]
        bad = ["%s %s≠%s" % (n, a, b) for n, a, b in checks if a != b]
        hua_mine = {k: v for k, v in mine["hua_of_star"].items()}
        hua_diff = {k: (hua_mine.get(k), ref["hua"].get(k)) for k in set(hua_mine) | set(ref["hua"])
                    if hua_mine.get(k) != ref["hua"].get(k)}
        if hua_diff:
            bad.append("四化差异 %s" % hua_diff)
        rows.append((case["case_id"], not bad, "; ".join(bad)))
    ok = sum(1 for _, good, _ in rows if good)
    print("| case | 一致 | 差异 |")
    print("| --- | --- | --- |")
    for cid, good, why in rows:
        print("| %s | %s | %s |" % (cid, "✓" if good else "✗", why or "—"))
    print()
    print("一致 %d / %d" % (ok, len(rows)))
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "bench", "fortune_api_results.json")
    sys.exit(main(p))
