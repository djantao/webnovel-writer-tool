#!/usr/bin/env python3
"""修复 novel.json 中的 AI味问题"""

import json
import os

NOVEL_PATH = "/workspace/AI_novel/workspace/novels/mengzhu_fitness/novel.json"

with open(NOVEL_PATH, "r", encoding="utf-8") as f:
    novel = json.load(f)

changes = []

# ================================================================
# 1. 修复角色中的"未详"字段
# ================================================================
for char in novel["characters"]:
    cid = char["character_id"]
    name = char["name"]

    # 1a. appearance 中"未详" → None
    app = char.get("appearance", {})
    for field in ["height", "build", "hair", "eyes", "clothing_style"]:
        if app.get(field) in ("未详", ""):
            app[field] = None
            changes.append(f"{name}.appearance.{field}: '未详' → null")

    # 1b. 根据角色特征补全外观
    if cid == "lao-zhou":
        if not app.get("build"): app["build"] = "微胖"
        if not app.get("hair"): app["hair"] = "灰白短发"
        if not app.get("clothing_style"): app["clothing_style"] = "旧运动外套"
    elif cid == "chen-pang":
        if not app.get("height"): app["height"] = "175cm"
        if not app.get("hair"): app["hair"] = "普通短发"
        if not app.get("clothing_style"): app["clothing_style"] = "宽松T恤运动裤"
    elif cid == "cheng-du":
        if not app.get("height"): app["height"] = "178cm"
        if not app.get("build"): app["build"] = "匀称"
        if not app.get("hair"): app["hair"] = "有型的短发"
        if not app.get("clothing_style"): app["clothing_style"] = "有品位的休闲装"
    elif cid == "zhang-yang":
        if not app.get("height"): app["height"] = "180cm"
        if not app.get("build"): app["build"] = "标准教练体型"
        if not app.get("hair"): app["hair"] = "精神短发"
        if not app.get("clothing_style"): app["clothing_style"] = "专业运动装备"
    elif cid == "qiao-yu":
        if not app.get("height"): app["height"] = "183cm"
        if not app.get("build"): app["build"] = "精干"
        if not app.get("hair"): app["hair"] = "短发"
    elif cid == "huang-mao":
        if not app.get("height"): app["height"] = "172cm"
        if not app.get("build"): app["build"] = "瘦"
        if not app.get("hair"): app["hair"] = "黄色染发"
        if not app.get("clothing_style"): app["clothing_style"] = "工地工装"
    elif cid == "li-shifu":
        if not app.get("height"): app["height"] = "170cm"
        if not app.get("build"): app["build"] = "结实"
        if not app.get("hair"): app["hair"] = "花白短发"
        if not app.get("clothing_style"): app["clothing_style"] = "旧夹克"
    elif cid == "lao-wei":
        if not app.get("build"): app["build"] = "干瘦"
        if not app.get("clothing_style"): app["clothing_style"] = "旧工装"
    elif cid == "liu-yutong":
        if not app.get("height"): app["height"] = "165cm"
        if not app.get("hair"): app["hair"] = "马尾辫"
        if not app.get("clothing_style"): app["clothing_style"] = "运动背心短裤"
    elif cid == "zhao-yifan":
        if not app.get("height"): app["height"] = "173cm"
        if not app.get("hair"): app["hair"] = "刘海遮眼"
        if not app.get("clothing_style"): app["clothing_style"] = "宽松卫衣"
    elif cid == "su-jie":
        if not app.get("height"): app["height"] = "160cm"
        if not app.get("build"): app["build"] = "普通"
        if not app.get("hair"): app["hair"] = "中长发"
        if not app.get("clothing_style"): app["clothing_style"] = "素色运动服"
    elif cid == "gao-jie":
        if not app.get("height"): app["height"] = "158cm"
        if not app.get("build"): app["build"] = "微胖"
        if not app.get("hair"): app["hair"] = "短发微卷"
        if not app.get("clothing_style"): app["clothing_style"] = "宽松运动装"
    elif cid == "xiao-he":
        if not app.get("height"): app["height"] = "162cm"
        if not app.get("build"): app["build"] = "瘦"
        if not app.get("hair"): app["hair"] = "扎小辫"
        if not app.get("clothing_style"): app["clothing_style"] = "休闲卫衣"

    # 1c. personality 中"未详" → 更自然的描述
    per = char.get("personality", {})
    for field in ["core_belief", "motivation", "flaw", "speech_style"]:
        if per.get(field) in ("未详", ""):
            # 根据角色自动推断
            if cid == "a-qi" and field == "core_belief":
                per[field] = "跟着师兄走，不会错"
            elif cid == "a-qi" and field == "motivation":
                per[field] = "替师兄挡事"
            elif cid == "a-qi" and field == "flaw":
                per[field] = "太在意师兄"
            elif cid == "huang-mao" and field == "core_belief":
                per[field] = "有意思的事就该拍下来"
            elif cid == "huang-mao" and field == "motivation":
                per[field] = "凑热闹、找乐子"
            elif cid == "huang-mao" and field == "flaw":
                per[field] = "三分钟热度"
            elif cid == "lao-wei" and field == "core_belief":
                per[field] = "活干好就行"
            elif cid == "lao-wei" and field in ("motivation","flaw"):
                per[field] = "——"  # 这种角色不用填，沉默就是特色
            elif cid == "lao-zhou" and field == "flaw":
                per[field] = "老婆走后怕再失去任何人"
            elif cid == "chen-pang" and field == "flaw":
                per[field] = "道歉比'你好'多"
            elif cid == "cheng-du" and field == "flaw":
                per[field] = "嘴太碎，心事太重不说"
            elif cid == "yang-yang":
                per[field] = "——"
            elif cid == "gao-jie" and field in ("core_belief","motivation"):
                per[field] = "不给孩子添负担，靠自己站起来"
            elif cid == "gao-jie" and field == "flaw":
                per[field] = "这把年纪还在逞强"
            elif cid == "xu-man" and field == "core_belief":
                per[field] = "新闻不追到底不罢休"
            elif cid == "xu-man" and field == "motivation":
                per[field] = "挖出真相"
            elif cid == "xu-man" and field == "speech_style":
                per[field] = "追问式，不给逃避空间"
            elif cid == "meng-jie" and field == "core_belief":
                per[field] = "合同条款就是天"
            elif cid == "meng-jie" and field == "motivation":
                per[field] = "帮朋友的朋友，但不能坏了规矩"
            elif cid == "meng-jie" and field == "speech_style":
                per[field] = "干练直接，不绕弯"
            elif cid == "chen-zong" and field == "speech_style":
                per[field] = "自信，带'我有一个方案'的口头禅"
            elif cid == "a-xing" and field == "core_belief":
                per[field] = "好的主持人是让被采访者说话"
            elif cid == "a-xing" and field == "motivation":
                per[field] = "做一档有影响力的节目"
            elif cid == "a-xing" and field == "speech_style":
                per[field] = "会做效果但不失人情"
            elif cid == "liulanghan" and field in ("core_belief","motivation"):
                per[field] = "活一天算一天"
            elif cid == "liulanghan" and field == "flaw":
                per[field] = "——"
            elif cid == "liulanghan" and field == "speech_style":
                per[field] = "话少，问句多"
            elif per.get(field) in ("未详", ""):
                per[field] = None  # 实在不知道的设为 null
                changes.append(f"{name}.personality.{field}: '未详' → null")

    # 1d. 补全 speech_style（如果用"——"占位）或补全 catchphrases
    if cid == "lao-wei" and not per.get("catchphrases"):
        per["catchphrases"] = ["……（沉默）"]
    if cid == "yang-yang" and not per.get("catchphrases"):
        per["catchphrases"] = ["啊啊啊", "你们看！"]
    if cid == "gao-jie" and not per.get("catchphrases"):
        per["catchphrases"] = ["不给孩子添负担"]
    if cid == "su-jie" and not per.get("speech_style"):
        per["speech_style"] = "轻声细语但坚定"
    if cid == "qiao-yu" and not per.get("speech_style"):
        per["speech_style"] = "自信断言，短视频口吻"
    if cid == "xiao-he" and not per.get("speech_style"):
        per["speech_style"] = "年轻直接，想到什么说什么"
    if cid == "zhao-yifan" and not per.get("speech_style"):
        per["speech_style"] = "声音很小，说半句停半句"

    # 1e. 修复 character_arc 中"未详"或空字段
    arc = char.get("character_arc", {})
    if arc.get("final_state") in ("未详", ""):
        if cid == "yang-yang":
            arc["final_state"] = "气脉健身最活跃的前台+野生品牌推广"
            changes.append(f"{name}.character_arc.final_state: 补全")
        elif cid == "gao-jie":
            arc["final_state"] = "气脉健身常驻学员，心态越来越好"
            changes.append(f"{name}.character_arc.final_state: 补全")
        elif cid == "xu-man":
            arc["final_state"] = "做完专题后离开了成都，没再追"
            changes.append(f"{name}.character_arc.final_state: 补全")
        elif cid == "meng-jie":
            arc["final_state"] = "气脉健身的常年法律顾问"
            changes.append(f"{name}.character_arc.final_state: 补全")
        elif cid == "chen-zong":
            arc["final_state"] = "没投成气脉健身，后来投了别的"
            changes.append(f"{name}.character_arc.final_state: 补全")
        elif cid == "liulanghan":
            arc["final_state"] = "后来不见了，不知道去了哪"

changes.append("--- 角色信息修复完成 ---")

# ================================================================
# 2. 修复力量体系描述（去学术化）
# ================================================================
power_levels = novel["world_setting"]["power_system"]["levels"]
power_levels[0]["description"] = "膝盖微屈、重心下沉，姿势摆对了就行"
power_levels[1]["description"] = "吸一口气从脚底到丹田，身体开始发热，疼的地方不疼了"
power_levels[2]["description"] = "把练功那套道理翻成现代人听得懂的——不用内力这个词"
power_levels[3]["description"] = "丹田=核心稳定、经络=筋膜链，气脉这一套东西能教给徒弟了"
changes.append("力量体系描述: 去学术化改写")

# ================================================================
# 3. 修复术语定义（去百科味）
# ================================================================
novel["world_setting"]["terms"]["气脉健身"] = "江临渊自己琢磨出来的教法，站桩打底，呼吸跟上，让身体自己说话"
novel["world_setting"]["terms"]["降龙掌"] = "降龙十八掌，当年全天下没人接得住。现在没人知道。"
novel["world_setting"]["terms"]["气脉"] = "站桩站到脚底发热、丹田有东西在走——江临渊管那条线叫气脉"
changes.append("术语定义: 去百科味改写")

# ================================================================
# 4. 修复角色 traits 中过于单薄的标签
# ================================================================
for char in novel["characters"]:
    cid = char["character_id"]
    traits = char["personality"]["traits"]

    if cid == "xiao-he" and traits == ["专业", "喜剧感"]:
        char["personality"]["traits"] = ["专业眼光准", "说话带梗", "年轻人有冲劲"]
        changes.append("小何.traits: 扩展描述")
    elif cid == "gao-jie" and traits == ["想靠自己站起来"]:
        char["personality"]["traits"] = ["要强", "怕给孩子添麻烦", "有股不服输的劲"]
        changes.append("高姐.traits: 扩展描述")
    elif cid == "liulanghan" and traits == ["善良"]:
        char["personality"]["traits"] = ["自己也没多少", "但看不得别人更苦"]
        changes.append("流浪汉.traits: 扩展描述")
    elif cid == "huang-mao":
        if "话多" in traits and len(traits) < 4:
            char["personality"]["traits"] = ["话多", "自来熟", "拍什么都觉得好玩", "心大不记仇"]
            changes.append("黄毛.traits: 扩展描述")
    elif cid == "chen-zong" and traits == ["自信", "商业思维"]:
        char["personality"]["traits"] = ["自信", "只看市场", "相信包装大于本质"]
        changes.append("陈总.traits: 扩展描述")
    elif cid == "xu-man" and traits == ["不站队", "追问到底"]:
        char["personality"]["traits"] = ["不站队", "追问到底", "对真相有执念"]
        changes.append("许曼.traits: 扩展描述")
    elif cid == "meng-jie" and traits == ["干练", "直接"]:
        char["personality"]["traits"] = ["干练", "直接", "信条款不信人情"]
        changes.append("孟姐.traits: 扩展描述")
    elif cid == "a-xing" and traits == ["会做效果", "不失人情"]:
        char["personality"]["traits"] = ["会做效果", "不失人情", "见过很多场面"]
        changes.append("阿星.traits: 扩展描述")

changes.append("角色性格标签: 单薄标签已扩展")

# ================================================================
# 5. 修复世界观规则的书面表述
# ================================================================
novel["world_setting"]["rules"][0] = "这世界看你有没有钱、什么学历、认识谁、工作稳不稳——全是他没有的东西"
novel["world_setting"]["rules"][2] = "教健身要证，有证才能上台，没证你教得再好也是'违规'"
novel["world_setting"]["rules"][3] = "他那一身本事只有一样能派上用场——对身体的理解"
changes.append("世界观规则: 去书面化改写")

# ================================================================
# 6. 章节摘要中去标签化
# ================================================================
for ch in novel["outline"]["chapters"]:
    summary = ch.get("chapter_summary", "")
    if not summary:
        continue
    original = summary

    # 去除 "C级/B级/A级/S级 爽点" 等标签前缀
    import re
    summary = re.sub(r'^——[ABCSE级]级（?\w*）?爽点[,，]?\s*', '', summary)
    summary = re.sub(r'^[ABCSE]级（?\w*）?爽点[,，]?\s*', '', summary)
    summary = re.sub(r'^[ABCSE]级[信息型情感型打脸型价值观型多重暖意双线]?爽点[,，]?\s*', '', summary)

    # 去除 "铺垫章"、"悬念章" 开头的标签
    summary = re.sub(r'^——', '', summary)
    if summary.startswith("铺垫章"):
        summary = summary.replace("铺垫章", "", 1).strip().lstrip("，,")
    if summary.startswith("悬念章"):
        summary = summary.replace("悬念章", "", 1).strip().lstrip("，,")

    # 对于占位章节，保持原样
    if summary == "（规划中，未写）":
        continue

    # 如果清理后为空或太短，保留原内容
    if len(summary) < 5:
        summary = original

    ch["chapter_summary"] = summary
    if summary != original:
        changes.append(f"ch{ch['chapter_number']:03d}.summary: 去标签化")

changes.append("章节摘要: 爽点等级标签已去除")

# ================================================================
# 保存
# ================================================================
with open(NOVEL_PATH, "w", encoding="utf-8") as f:
    json.dump(novel, f, ensure_ascii=False, indent=2)

print("=== 修复变更日志 ===")
for c in changes:
    print(f"  {c}")
print(f"\n总计: {len(changes)} 项变更")
print("novel.json 已保存")

# 二次验证 JSON 格式
with open(NOVEL_PATH, "r", encoding="utf-8") as f:
    json.load(f)
print("JSON 格式验证通过")