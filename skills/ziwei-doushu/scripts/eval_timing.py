# -*- coding: utf-8 -*-
"""应期检验：比较「流年 / 小限 / 流年四化 / 小限四化」对已发生事件的区分力。

用法：
    python scripts/eval_timing.py [cases.json]

cases.json 结构：
[
  {"birth": {"date": "1975-07-14", "time": "08:00", "lon": 108.2, "gender": "男"},
   "events": [{"year": 2006, "event": "婚", "precision": "月"},
              {"year": 2010, "event": "子"}]}
]

指标：事件年在该年 ±5 年窗口内的分位（0~1，1 = 该层把这一年排在最高）。
分位均值高、且四个假设差距一致，才说明该层有区分力；单例不作结论。
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ziwei_chart as Z
import ziwei_eval as E


def build(b):
    if "lunar" in b:
        y, m, d = [int(x) for x in b["lunar"].split("-")]
        return Z.build(lunar_known=True, year=y, month=m, day=d, hour=b.get("hour", 8),
                       gender=b.get("gender", "男"),
                       longitude=b.get("lon"), tz=b.get("tz", 8))
    y, m, d = [int(x) for x in b["date"].split("-")]
    hh, mm = [int(x) for x in b.get("time", "12:00").split(":")]
    return Z.build(lunar_known=False, year=y, month=m, day=d, hour=hh, minute=mm,
                   gender=b.get("gender", "男"), longitude=b.get("lon"),
                   latitude=b.get("lat"), tz=b.get("tz", 8))


def main(path):
    cases = json.load(open(path, encoding="utf-8"))
    rows = []
    for case in cases:
        ch = build(case["birth"])
        for ev in case["events"]:
            r = E.compare(ch, ev["year"], ev["event"])
            rows.append((ev["year"], ev["event"], r))
    if not rows:
        print("no events")
        return 1
    print("| 事件年 | 类型 | 流年 | 小限 | 流年四化 | 小限四化 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for year, event, r in rows:
        print("| %d | %s | %.2f | %.2f | %.2f | %.2f |" % (
            year, event, r["流年"], r["小限"], r["流年化"], r["小限化"]))
    n = len(rows)
    print()
    print("样本 %d 例（分位均值，1 = 最好）：" % n)
    for key in ("流年", "小限", "流年化", "小限化"):
        print("  %s: %.2f" % (key, sum(r[key] for _, _, r in rows) / n))
    if n < 20:
        print()
        print("注意：样本 %d 例，只能说明方法与个案，不构成对该层的结论。" % n)
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "cases.json")
    sys.exit(main(p))
