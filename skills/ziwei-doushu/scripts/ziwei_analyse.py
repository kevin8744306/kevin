# -*- coding: utf-8 -*-
"""依《天纪》框架做推导分析。

分析只依据盘面事实（宫位、星曜、四化、大限流年）与本文件列出的取象规则，
不臆造盘面没有的星曜；结论用“倾向、可调整”的措辞，落回倪海厦“以果决行”的用法。
"""

import ziwei_core as C
import ziwei_chart as Z
import ziwei_timing as T

STAR_TRAIT = {
    "紫微": ("尊贵自持、要面子、喜掌控，得势时能服众，失势时易孤高", "领导、名位、决策"),
    "天机": ("机敏善谋、思虑多、变化快，长于策划短于执守", "谋划、变动、技术"),
    "太阳": ("外放热心、重名节、付出型，易劳心而不聚财", "名声、公众、长辈"),
    "武曲": ("刚毅务实、执行力强、重财，性直少圆融", "财、行动、武职"),
    "天同": ("温和享福、怕压力、重感情，顺境安逸逆境退缩", "福气、闲适、生活品质"),
    "廉贞": ("刚柔并济、爱恨分明、重原则亦重情面，易走极端", "公关、纪律、情感"),
    "天府": ("稳重保守、善守成、有库藏之象，进取心不强", "库藏、管理、稳定"),
    "太阴": ("细腻内敛、重感受、善积累，情绪与财务均起伏", "阴柔、田宅、积蓄"),
    "贪狼": ("多才多欲、交际强、嗜新奇，易纵欲而分心", "才艺、社交、欲望"),
    "巨门": ("口才犀利、善辩、疑心重，是非与专业并存", "言语、专业、争讼"),
    "天相": ("端正守礼、重形象、辅佐型，依赖环境与贵人", "辅佐、协调、公职"),
    "天梁": ("老成持重、有原则、喜庇荫他人，易固执说教", "荫庇、监察、长上"),
    "七杀": ("果决独行、能开创、不耐拘束，成败皆快", "开创、竞争、变局"),
    "破军": ("破旧立新、敢冲敢舍、耗损亦大，宜先破后立", "变革、开创、消耗"),
}

PALACE_THEME = {
    "命宫": ("整体格局与性格底色", "我是谁、惯用什么方式应对世界"),
    "兄弟": ("手足与同辈、合作", "与平辈的互动与资源互换"),
    "夫妻": ("配偶特质与亲密关系", "亲密关系中的需求与冲突模式"),
    "子女": ("子女、下属、创作", "付出与教养、创造力的出口"),
    "财帛": ("求财方式与金钱观", "钱从哪来、怎么花、怎么守"),
    "疾厄": ("体质弱点与情绪积压", "身心最容易出问题的环节"),
    "迁移": ("外出、环境与他人评价", "离开熟悉环境后的际遇"),
    "交友": ("朋友、部属、群众", "人际资源的品质与风险"),
    "官禄": ("事业方向与工作方式", "靠什么立足、适合什么角色"),
    "田宅": ("不动产、家庭与根基", "安身之所与家族资源"),
    "福德": ("精神享受与福分", "内在满足感与抗压能力"),
    "父母": ("父母、长辈、文书", "与权威及制度的关系"),
}

HUA_MEANING = {
    "禄": "资源与顺遂：此事有甜头、来得自然，易因顺而懈怠",
    "权": "掌控与承担：此事要做主、要出力，耗神却长实力",
    "科": "名声与条理：此事讲体面、重过程，宜以专业与规矩取胜",
    "忌": "执着与缺口：此事的执念与消耗所在，越用力越容易卡住",
}

SHA_MEANING = {
    "擎羊": "刚烈冲突、外伤与决断，行事易硬碰硬",
    "陀罗": "拖延纠缠、内耗反复，宜设期限",
    "火星": "急躁爆发、突发之变，忌冲动决事",
    "铃星": "隐忍积压、阴火暗耗，情绪需出口",
    "地空": "落空与超脱，想法大而落地难",
    "地劫": "耗损与被夺，要守住合作边界",
}

JI_STARS = ["左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马"]
SHA_STARS = ["擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]


def _stars_of(chart, idx):
    stars = chart["stars"].get(idx, [])
    return [s for s in stars if s in Z.LUMA_STARS], stars


def analyse(chart, target_year=None):
    out = []
    ming = chart["ming"]
    main, _ = _stars_of(chart, ming)

    out.append("## 一、格局总论")
    out.append("")
    if main:
        traits = "；".join("%s（%s）：%s" % (s, C.brightness(s, ming), STAR_TRAIT[s][0]) for s in main)
        fields = "、".join(STAR_TRAIT[s][1] for s in main)
        out.append("- 命宫在%s坐%s：%s。用力方向偏%s。" % (
            C.ZHI[ming], "、".join(main), traits, fields))
    else:
        opp = _stars_of(chart, (ming + 6) % 12)[0]
        out.append("- 命宫在%s无主星，借对宫%s为用：性格随环境塑形，早年方向感弱，"
                   "宜借师承、制度、团队等外部秩序立身。" % (
                       C.ZHI[ming], "、".join(opp) or "空宫"))
    shen_main, _ = _stars_of(chart, chart["shen"])
    out.append("- 身宫在%s%s：后天用力处，越到中年越以此宫的方式成事。" % (
        chart["palace_of"][chart["shen"]],
        ("坐" + "、".join(shen_main)) if shen_main else "无主星，重环境与人脉"))
    san = [(ming + 4) % 12, (ming + 8) % 12, (ming + 6) % 12]
    san_main = []
    for i in san:
        san_main.extend(_stars_of(chart, i)[0])
    san_ji = any(s in JI_STARS for i in san for s in chart["stars"].get(i, []))
    san_sha = any(s in SHA_STARS for i in san for s in chart["stars"].get(i, []))
    out.append("- 三方四正会%s；%s。" % (
        "、".join(san_main) or "无主星",
        "吉星成局，外援足" if san_ji else ("煞星入三方，须自持" if san_sha else "平顺无奇")))
    out.append("- 五行局：%s（%d 局），%d 岁起大限，%s行。" % (
        chart["ju_wuxing"] + str(chart["ju"]), chart["ju"], chart["ju"],
        "顺" if chart["limits_forward"] else "逆"))
    out.append("")

    out.append("## 二、生年四化落宫")
    out.append("")
    for kind in ("禄", "权", "科", "忌"):
        star = chart["sihua"][kind]
        idx = None
        for i, ss in chart["stars"].items():
            if star in ss:
                idx = i
                break
        if idx is None:
            continue
        out.append("- %s化%s，落%s宫：%s" % (
            star, kind, chart["palace_of"][idx], HUA_MEANING[kind]))
    out.append("")

    out.append("## 三、十二宫提要")
    out.append("")
    for i in range(12):
        m, ss = _stars_of(chart, i)
        name = chart["palace_of"][i]
        theme = PALACE_THEME[name]
        parts = ["坐" + "、".join(m) if m else "空宫"]
        ji = [s for s in ss if s in JI_STARS]
        sha = [s for s in ss if s in SHA_STARS]
        if ji:
            parts.append("会" + "、".join(ji))
        if sha:
            parts.append("见" + "、".join(sha))
        note = ""
        if m:
            note = "；".join(STAR_TRAIT[s][0].split("、")[0] for s in m)
        elif sha:
            note = SHA_MEANING[sha[0]].split("、")[0]
        out.append("- **%s（%s）**：%s。此宫主%s%s" % (
            name, C.ZHI[i], "，".join(parts), theme[0],
            ("，" + note) if note else ""))
    out.append("")

    if target_year:
        out.append("## 四、%d 年行运" % target_year)
        out.append("")
        ln = Z.liunian_index(target_year)
        age = target_year - chart["lunar_year"] + 1
        out.append("- 流年命宫在%s（%s宫），%d 岁。" % (
            C.ZHI[ln], chart["palace_of"][ln], age))
        dx = Z.daxian_for_age(chart, age)
        if dx:
            dm, _ = _stars_of(chart, dx["palace_index"])
            out.append("- 行 %d-%d 大限（%s宫%s）：十年主调看%s。" % (
                dx["start_age"], dx["end_age"], dx["palace"],
                ("坐" + "、".join(dm)) if dm else "空宫", PALACE_THEME[dx["palace"]][0]))
        xx = Z.xiaoxian_index(chart, age)
        out.append("- 小限在%s（%s宫），取本宫与对宫看。" % (C.ZHI[xx], chart["palace_of"][xx]))
        out.append("")
        out.extend(T.render_layers(chart, target_year).split("\n"))
        out.append("")
        out.append("> 权重：本命 1.0 ＞ 大限 0.6 ＞ 流年 0.35 ＞ 小限 0.15；"
                   "同层内煞、忌加分，吉、禄权科减分。冲突时以大限压流年，本命压大限。")

    out.append("## 五、以果决行")
    out.append("")
    ji_star = chart["sihua"]["忌"]
    for i, ss in chart["stars"].items():
        if ji_star in ss:
            out.append("- 生年忌在%s宫（%s）：这是执念与消耗所在。功课是"
                       "“该放的不硬撑”，把力气转投他宫所长，忌就沉淀成经验。" % (
                           chart["palace_of"][i], C.ZHI[i]))
            break
    out.append("- 先定“我要什么结果”，再核对盘上哪个宫位给资源、哪个在耗损；"
               "命不改，改的是行为惯性。")
    out.append("- 大限流年只判“这一段宜攻或宜守”，具体事仍要回到现实条件验证。")
    return "\n".join(out)
