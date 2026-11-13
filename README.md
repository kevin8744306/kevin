# kevin
> 本仓库由 Super agent 自动维护。

## Skills

### ziwei-doushu —— 紫微斗数排盘与推导分析

输入出生年月日时与出生地，排出命盘并给出分层推导（本命／大限／流年／小限），
附应期检验工具。面相与阳宅按约定只作对照，不进评分。

```bash
# 公历生日 + 出生地（真太阳时自动校正）
python skills/ziwei-doushu/scripts/ziwei.py --date 1975-07-14 --time 08:00 --lon 108.2 --gender 男 --year 2030

# 农历生日（闰月用负数，如 2020--4-1）；带流月
python skills/ziwei-doushu/scripts/ziwei.py --lunar 1961-3-5 --time 20:00 --city 台北 --gender 女 --year 2026 --month 8

# 自检与应期检验
python skills/ziwei-doushu/scripts/selftest.py
python skills/ziwei-doushu/scripts/eval_timing.py
```

只依赖 Python 标准库。规则来源与校验记录见 `skills/ziwei-doushu/references/`，判断维度见 `07-判断模型.md`。
