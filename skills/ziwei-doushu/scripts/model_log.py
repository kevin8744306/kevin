# -*- coding: utf-8 -*-
"""模型变更日志工具。

    python scripts/model_log.py --show              # 版本 + 最近条目
    python scripts/model_log.py --add "标题" --why "原因" --evidence "证据"
"""

import argparse
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ziwei_core as C

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "model-changelog.md")


def show(n=8):
    print("MODEL_VERSION:", C.MODEL_VERSION)
    rows = [l for l in open(LOG, encoding="utf-8").read().splitlines() if l.startswith("| 2026")]
    for row in rows[-n:]:
        print(row)
    print("\n共 %d 条记录。回滚：git log --oneline / git revert <sha> / git checkout <tag>" % len(rows))


def add(title, why, evidence):
    row = "| %s | %s | %s | %s | 待填 |" % (C.MODEL_VERSION.split("-")[0], date.today(), title, evidence)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(row + "\n")
    print("appended:", row)
    if why:
        print("原因：", why)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--show", action="store_true")
    p.add_argument("--add")
    p.add_argument("--why", default="")
    p.add_argument("--evidence", default="")
    a = p.parse_args()
    if a.add:
        add(a.add, a.why, a.evidence)
    else:
        show()


if __name__ == "__main__":
    main()
