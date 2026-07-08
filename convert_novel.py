#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_novel.py
将"盟主穿越当健身教练"小说素材转换为 AI_novel 项目标准格式。
纯 Python 标准库实现，无外部依赖。
"""

import json
import os
import re
import uuid
import shutil
from datetime import datetime, timezone, timedelta

# ============================================================
# 路径配置
# ============================================================

BASE_DIR = "/workspace"
OUTPUT_DIR = os.path.join(BASE_DIR, "AI_novel", "workspace", "novels", "mengzhu_fitness")

INPUT_FILES = {
    "concept": os.path.join(BASE_DIR, "designs", "concept.md"),
    "characters": os.path.join(BASE_DIR, "designs", "characters.md"),
    "worldbuilding": os.path.join(BASE_DIR, "designs", "worldbuilding.md"),
    "structure": os.path.join(BASE_DIR, "designs", "structure.md"),
    "relationships": os.path.join(BASE_DIR, "designs", "relationships.md"),
    "outline_01_10": os.path.join(BASE_DIR, "outlines", "chapters-01-10.md"),
    "outline_11_15": os.path.join(BASE_DIR, "outlines", "chapters-11-15.md"),
    "outline_16_30": os.path.join(BASE_DIR, "outlines", "chapters-16-30.md"),
    "outline_31_50": os.path.join(BASE_DIR, "outlines", "chapters-31-50.md"),
}

CHAPTER_TYPES_MAP = {
    "序章": "setup",
    "铺垫章": "setup",
    "过渡章": "interlude",
    "爽点章": "climax",
    "高潮章": "climax",
    "收尾章": "resolution",
}

MOOD_MAP = {
    "S": "大爽",
    "A级": "大爽",
    "B级": "小爽",
    "C级": "日常",
}

# ============================================================
# 章节编号映射
# chapter-00a -> 001, chapter-00b -> 002, chapter-01 -> 003, ...
# ============================================================

def chapter_file_to_number(filename):
    """将 chapter-XX.md 文件名转换为三位数字编号"""
    base = filename.replace("chapter-", "").replace(".md", "")
    if base == "00a":
        return 1
    elif base == "00b":
        return 2
    else:
        return int(base) + 2  # chapter-01 -> 3, chapter-02 -> 4, ...

def number_to_chapter_file(num):
    """反向映射：数字 -> 原始文件名"""
    if num == 1:
        return "chapter-00a"
    elif num == 2:
        return "chapter-00b"
    else:
        return f"chapter-{num - 2:02d}"

# ============================================================
# 读取 markdown 文件
# ============================================================

def read_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# ============================================================
# 提取章节正文（去掉 # 标题标记）
# ============================================================

def extract_text(md_content):
    """去掉 markdown 标题标记 #，保留段落分隔"""
    lines = md_content.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            # 去掉 # 前缀，保留标题文字
            cleaned = re.sub(r"^#+\s*", "", stripped)
            if cleaned:
                result.append(cleaned)
        else:
            result.append(line)
    return "\n".join(result)

def count_words(text):
    """统计中文字数（粗略统计：中文字符 + 英文单词数）"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 英文单词
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words

# ============================================================
# 从 markdown 标题行提取章节标题
# ============================================================

def extract_title(md_content):
    """从第一行 # 标题提取章节标题"""
    for line in md_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return re.sub(r"^#+\s*", "", stripped)
    return ""

# ============================================================
# 解析大纲文件，提取章节信息
# ============================================================

def parse_outline_outlines(outlines_text_list):
    """
    从多个大纲文件中解析章节信息。
    返回 dict: key=章节编号(int), value=章节大纲信息
    """
    chapters = {}

    # 第1-12章（含序章）大纲 —— 从 chapters-01-10.md
    # 手动建立 1-12 章的大纲映射
    # 序章A(ch1), 序章B(ch2), 第1章(ch3) ... 第10章(ch12)
    outlines_01_10 = read_md(INPUT_FILES["outline_01_10"])
    outlines_11_15 = read_md(INPUT_FILES["outline_11_15"])
    outlines_16_30 = read_md(INPUT_FILES["outline_16_30"])
    outlines_31_50 = read_md(INPUT_FILES["outline_31_50"])

    # ---- 解析序章 + 第1-10章 (对应编号 1-12) ----
    ch_data_01_10 = parse_outline_file_01_10(outlines_01_10)
    chapters.update(ch_data_01_10)

    # ---- 解析第11-15章 (对应编号 13-17) ----
    ch_data_11_15 = parse_outline_file_11_15(outlines_11_15)
    chapters.update(ch_data_11_15)

    # ---- 解析第16-30章 (对应编号 18-32) ----
    ch_data_16_30 = parse_outline_file_16_30(outlines_16_30)
    chapters.update(ch_data_16_30)

    # ---- 解析第31-50章 (对应编号 33-52) ----
    ch_data_31_50 = parse_outline_file_31_50(outlines_31_50)
    chapters.update(ch_data_31_50)

    return chapters


def _parse_chapter_block(block_text):
    """
    从单个章节大纲块中提取信息。
    block_text 是 "### 第X章：标题" 到下一个 "###" 之间的内容。
    """
    info = {}
    lines = block_text.strip().split("\n")

    # 提取章节标题行
    title_match = re.match(r"###\s+(.+)", lines[0])
    if title_match:
        info["raw_title"] = title_match.group(1).strip()

    # 提取冲突
    conflict = ""
    goal = ""
    for line in lines:
        cm = re.match(r"[-\*]?\s*(?:本章)?冲突[：:]\s*(.+)", line)
        if cm:
            conflict = cm.group(1).strip()
            goal = conflict
            break
        # 有些用 **本章冲突** 格式
        cm2 = re.match(r"[-\*]?\s*\*+\s*(?:本章)?冲突\*+[：:]\s*(.+)", line)
        if cm2:
            conflict = cm2.group(1).strip()
            goal = conflict
            break
    info["goal"] = goal

    # 提取爽点等级
    shuangdian = None
    for line in lines:
        sm = re.search(r"爽点(?:等级)?[：:]\s*(.+)", line)
        if sm:
            shuangdian = sm.group(1).strip()
            break
        # 粗体格式
        sm2 = re.search(r"\*+\s*爽点(?:等级)?\s*\*+[：:]\s*(.+)", line)
        if sm2:
            shuangdian = sm2.group(1).strip()
            break
    info["shuangdian"] = shuangdian

    # 提取推法 / 章尾推法
    push_method = ""
    for line in lines:
        pm = re.search(r"[-\*]?\s*(?:章尾)?推法[：:]\s*(.+)", line)
        if pm:
            push_method = pm.group(1).strip()
            break
    info["push_method"] = push_method

    # 提取钩子
    hook = ""
    for line in lines:
        hm = re.search(r"[-\*]?\s*钩子(?:类型)?[：:]\s*(.+)", line)
        if hm:
            hook = hm.group(1).strip()
            break
    info["hook"] = hook

    # 提取因果链
    causal_chain = ""
    for line in lines:
        ccm = re.search(r"[-\*]?\s*因果链[：:]\s*(.+)", line)
        if ccm:
            causal_chain = ccm.group(1).strip()
            break
    info["causal_chain"] = causal_chain

    # 提取场景
    scene = ""
    for line in lines:
        scm = re.search(r"[-\*]?\s*场景[：:]\s*(.+)", line)
        if scm:
            scene = scm.group(1).strip()
            break
    info["scene"] = scene

    # 提取伏笔
    foreshadow = ""
    for line in lines:
        fm = re.search(r"[-\*]?\s*伏笔[：:]\s*(.+)", line)
        if fm:
            foreshadow = fm.group(1).strip()
            break
    info["foreshadow"] = foreshadow

    return info


def parse_outline_file_01_10(text):
    """解析序章+第1-10章大纲 -> 编号1-12"""
    chapters = {}

    # 序章A: 编号1
    chapters[1] = {
        "chapter_number": 1,
        "title": "序章·上：盟主",
        "goal": "江临渊的'不转弯'——拒绝朝廷招揽",
        "key_events": ["评剑/师弟缝鞋/陆沉'有约'伏笔/拒绝朝廷/女人鞋印"],
        "involved_characters": ["jiang-linyuan", "a-qi", "lu-chen"],
        "chapter_type": "setup",
        "mood": "过渡/蓄力",
        "estimated_words": 2500,
        "chapter_summary": "盟主巅峰——评剑、师弟缝鞋、陆沉'有约'伏笔、拒绝朝廷。全章靠'这是一个有原则的人'建立读者认同。",
        "storyline_progress": "序章：建立'有'——武林盟主万人跪伏的巅峰",
        "shuangdian": "无",
    }

    # 序章B: 编号2
    chapters[2] = {
        "chapter_number": 2,
        "title": "序章·下：天牢",
        "goal": "在天牢中守住最后一点尊严",
        "key_events": ["铁钉穿骨", "师弟递馒头", "陆沉来访(脸被抹除)", "第二根铁钉/穿越"],
        "involved_characters": ["jiang-linyuan", "a-qi", "lu-chen"],
        "chapter_type": "setup",
        "mood": "过渡/蓄力",
        "estimated_words": 2500,
        "chapter_summary": "天牢坠落——铁钉穿骨、师弟递馒头、陆沉来访（脸被记忆抹除）、第二根铁钉、穿越。",
        "storyline_progress": "序章：建立'失'——天牢受死穿越到2026年",
        "shuangdian": "无",
    }

    # 第1-10章 -> 编号3-12
    raw_chapters = [
        {"num": 3, "orig": 1, "title": "醒来", "goal": "搞清楚这是哪里——一切都不对",
         "events": ["穿越到2026年成都", "降龙掌无人知", "玉佩换不来包子"],
         "chars": ["jiang-linyuan"], "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "穿越后第一天——降龙掌无人知，玉佩换不来包子，被时代抛弃的刺痛。",
         "progress": "信息之钩——降龙掌没有人看"},
        {"num": 4, "orig": 2, "title": "空腹", "goal": "填饱肚子但没有一个铜板",
         "events": ["生存危机", "流浪汉给半个馒头", "工地招工"],
         "chars": ["jiang-linyuan", "liulanghan"], "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "生存挣扎——流浪汉的半个馒头给了温暖，工地招工有了第一份工作。",
         "progress": "危险之钩——生存危机，钩子驱动"},
        {"num": 5, "orig": 3, "title": "扛楼", "goal": "用体力证明自己",
         "events": ["工头多给二十块", "黄毛开始拍视频"],
         "chars": ["jiang-linyuan", "li-shifu", "huang-mao"], "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "扛水泥体力证明——C级爽点，工头多给二十块，黄毛开始拍视频。",
         "progress": "不公之钩——被低估，体力证明"},
        {"num": 6, "orig": 4, "title": "水泥哥", "goal": "不理解'走红'",
         "events": ["'一千个人在看我扛水泥'", "老周在工地门口等他"],
         "chars": ["jiang-linyuan", "huang-mao", "lao-zhou"], "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "水泥哥走红——短视频扩散，老周在工地门口等他。",
         "progress": "信息之钩——一千个人在看他扛水泥"},
        {"num": 7, "orig": 5, "title": "新入", "goal": "从水泥哥到健身房前台",
         "events": ["老周给他钥匙", "张扬出场质疑"],
         "chars": ["jiang-linyuan", "lao-zhou", "zhang-yang"], "type": "interlude", "mood": "过渡/蓄力", "sd": "无",
         "summary": "健身房第一天——老周给钥匙，张扬出场质疑没证不能教学。",
         "progress": "反转式——张扬出场质疑"},
        {"num": 8, "orig": 6, "title": "无证", "goal": "能力无法通过任何渠道证明",
         "events": ["三百年修为顶不过一章纸", "忍不住指导陈胖"],
         "chars": ["jiang-linyuan", "zhang-yang", "chen-pang"], "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "无证困境——三百年修为顶不过一章纸，看到学员动作错误忍不住指导陈胖。",
         "progress": "不公之钩——能力无法证明"},
        {"num": 9, "orig": 7, "title": "第一次碰", "goal": "需要证明的机会",
         "events": ["陈胖主动来问'还有没有别的'", "张扬警告"],
         "chars": ["jiang-linyuan", "chen-pang", "zhang-yang"], "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "第一次碰——C级爽点，陈胖主动来问'还有没有别的'，张扬警告。",
         "progress": "信息之钩——知识被换了名字"},
        {"num": 10, "orig": 8, "title": "第一次证", "goal": "水泥哥+没证教练同时曝光",
         "events": ["陈胖数据动了", "工友集体办卡", "老周宣布升实习教练"],
         "chars": ["jiang-linyuan", "chen-pang", "lao-zhou", "zhang-yang", "huang-mao"], "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "第一次证——C→B双重爽点，陈胖数据动了，工友集体办卡，老周宣布升实习教练。",
         "progress": "信息之钩——双重身份曝光"},
        {"num": 11, "orig": 9, "title": "程渡", "goal": "考证培训+程渡深入接触",
         "events": ["知识可以'翻译'", "火锅药浴", "顾长风在走廊拦下他"],
         "chars": ["jiang-linyuan", "cheng-du", "gu-changfeng"], "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "程渡线——考证培训，火锅药浴喜剧，顾长风在走廊拦下他。",
         "progress": "反转式——顾长风在走廊拦下他"},
        {"num": 12, "orig": 10, "title": "故人", "goal": "旧世界的招揽 vs 新的方向",
         "events": ["工友送鞋", "笔记本'翻译'", "行。明天。", "刘雨桐出现"],
         "chars": ["jiang-linyuan", "lao-zhou", "gu-changfeng", "liu-yutong", "li-shifu", "huang-mao"], "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "第一卷高潮——B级情感型爽点，工友送鞋，笔记本翻译，告别工地。刘雨桐出现为下卷铺垫。",
         "progress": "第一卷高潮——选择方向+告别工地"},
    ]

    for ch in raw_chapters:
        chapters[ch["num"]] = {
            "chapter_number": ch["num"],
            "title": ch["title"],
            "goal": ch["goal"],
            "key_events": ch["events"],
            "involved_characters": ch["chars"],
            "chapter_type": ch["type"],
            "mood": ch["mood"],
            "estimated_words": 2500,
            "chapter_summary": ch["summary"],
            "storyline_progress": ch["progress"],
            "shuangdian": ch["sd"],
        }

    return chapters


def parse_outline_file_11_15(text):
    """解析第11-15章大纲 -> 编号13-17"""
    chapters = {}
    raw = [
        {"num": 13, "title": "刘雨桐", "goal": "克服膝盖恐惧——不是不能站，是不敢",
         "events": ["凌晨五点刘雨桐已经在等", "站桩姿势对了", "程渡告知顾长风比赛邀请"],
         "chars": ["jiang-linyuan", "liu-yutong", "cheng-du", "gu-changfeng"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "刘雨桐第一天站桩——C级爽点，凌晨五点已经在等，站桩姿势对了，程渡告知顾长风消息。",
         "progress": "升级式——程渡告知顾长风比赛邀请"},
        {"num": 14, "title": "站桩", "goal": "站桩的内在意义——不是练腿，是练心",
         "events": ["站桩第三天腿不抖了", "考试通过正式教练", "陈胖老婆加入"],
         "chars": ["jiang-linyuan", "liu-yutong", "chen-pang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "站桩见效——C级爽点，刘雨桐腿不抖了，考试通过成为正式教练，陈胖老婆加入。",
         "progress": "升级式——考试通过正式上班"},
        {"num": 15, "title": "蜕变", "goal": "刘雨桐从站桩到深蹲的跨越",
         "events": ["正式上班第一天戴工牌", "刘雨桐跑了五十米膝盖不疼", "想学'以前练的那种'"],
         "chars": ["jiang-linyuan", "liu-yutong"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "蜕变——C级爽点，正式上班戴工牌，刘雨桐跑了五十米膝盖不疼了。",
         "progress": "升级式——刘雨桐想学'以前练的那种'"},
        {"num": 16, "title": "比赛", "goal": "现代搏击 vs 真正的武功",
         "events": ["顾长风武馆搏击比赛", "江临渊当众拒绝顾长风", "顾长风约吃饭被拒"],
         "chars": ["jiang-linyuan", "gu-changfeng"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "比赛——C级爽点，江临渊当众拒绝顾长风的公开挑战。",
         "progress": "升级式——顾长风约三人火锅"},
        {"num": 17, "title": "标准", "goal": "张扬朋友圈暗箭+顾长风通过程渡施压",
         "events": ["刘雨桐首次感知'气'", "张扬朋友圈暗箭", "顾长风约三人火锅"],
         "chars": ["jiang-linyuan", "liu-yutong", "zhang-yang", "cheng-du", "gu-changfeng"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "标准——C级爽点，刘雨桐首次感知'气'，张扬朋友圈暗箭，顾长风约三人火锅。",
         "progress": "断章式——明天火锅正面交锋"},
    ]
    for ch in raw:
        chapters[ch["num"]] = {
            "chapter_number": ch["num"],
            "title": ch["title"],
            "goal": ch["goal"],
            "key_events": ch["events"],
            "involved_characters": ch["chars"],
            "chapter_type": ch["type"],
            "mood": ch["mood"],
            "estimated_words": 2500,
            "chapter_summary": ch["summary"],
            "storyline_progress": ch["progress"],
            "shuangdian": ch["sd"],
        }
    return chapters


def _parse_chapter_block_detailed(block_text):
    """从16-50章详细大纲块提取信息"""
    info = {}
    lines = block_text.strip().split("\n")

    # 标题
    title_match = re.match(r"###\s+(第\d+章)[：:]\s*(.+)", lines[0])
    if title_match:
        info["raw_title"] = f"{title_match.group(1).strip()}：{title_match.group(2).strip()}"
        info["short_title"] = title_match.group(2).strip()

    # 本章冲突
    conflict = ""
    for line in lines:
        cm = re.match(r"[-\*]?\s*\*+(?:本章)?冲突\*+[：:]\s*(.+)", line)
        if cm:
            conflict = cm.group(1).strip()
            break
        cm2 = re.match(r"[-\*]?\s*(?:本章)?冲突[：:]\s*(.+)", line)
        if cm2:
            conflict = cm2.group(1).strip()
            break
    info["goal"] = conflict

    # 爽点等级
    sd = None
    for line in lines:
        sm = re.search(r"\*+\s*爽点(?:等级)?\s*\*+[：:]\s*(.+)", line)
        if sm:
            sd = sm.group(1).strip()
            break
        sm2 = re.search(r"爽点(?:等级)?[：:]\s*(.+)", line)
        if sm2:
            sd = sm2.group(1).strip()
            break
    info["shuangdian"] = sd

    # 章尾推法
    push = ""
    for line in lines:
        pm = re.match(r"[-\*]?\s*\*+章尾推法\*+[：:]\s*(.+)", line)
        if pm:
            push = pm.group(1).strip()
            break
        pm2 = re.match(r"[-\*]?\s*章尾推法[：:]\s*(.+)", line)
        if pm2:
            push = pm2.group(1).strip()
            break
    info["push_method"] = push

    # 钩子类型
    hook = ""
    for line in lines:
        hm = re.match(r"[-\*]?\s*\*+钩子类型\*+[：:]\s*(.+)", line)
        if hm:
            hook = hm.group(1).strip()
            break
    info["hook"] = hook

    # 因果链
    causal = ""
    for line in lines:
        ccm = re.match(r"[-\*]?\s*\*+因果链\*+[：:]\s*(.+)", line)
        if ccm:
            causal = ccm.group(1).strip()
            break
    info["causal_chain"] = causal

    return info


def parse_outline_file_16_30(text):
    """解析第16-30章大纲 -> 编号18-32"""
    chapters = {}

    # 按章节块分割
    blocks = re.split(r"\n###\s+", text)
    blocks = [b for b in blocks if b.strip()]

    raw_chapters = [
        {"num": 18, "title": "火锅", "goal": "顾长风在火锅桌上试探江临渊的底线",
         "events": ["顾长风以老朋友姿态拉拢", "程渡察觉气氛不对", "张扬匿名爆料扩散"],
         "chars": ["jiang-linyuan", "gu-changfeng", "cheng-du", "zhang-yang", "yang-yang"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "火锅——顾长风试探底线，程渡察觉不对，张扬匿名爆料扩散到会员群。铺垫章。",
         "progress": "升级——火锅散场，匿名爆料升级"},
        {"num": 19, "title": "暗箭", "goal": "张扬朋友圈被截图扩散，老周面临信任危机",
         "events": ["刘雨桐当面维护江临渊", "张扬删朋友圈", "实操考试报名"],
         "chars": ["jiang-linyuan", "liu-yutong", "zhang-yang", "lao-zhou", "chen-pang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "暗箭——C级情感型爽点，刘雨桐公开维护江临渊，张扬删帖，实操考试报名到手。",
         "progress": "反转——老周请剑南春"},
        {"num": 20, "title": "规则", "goal": "实操考试——'科学vs气脉'的冲突",
         "events": ["拿到证书SC202600317", "体能测试省队水平", "气脉健身体系雏形形成"],
         "chars": ["jiang-linyuan", "lao-zhou", "cheng-du", "liu-yutong", "zhang-yang"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "规则——B级信息型爽点，实操考试通过拿到证书，体能测试碾压式通过，气脉健身体系雏形形成。",
         "progress": "升级——气脉健身体系雏形形成"},
        {"num": 21, "title": "站桩", "goal": "三类学员站桩对比：规则vs人心",
         "events": ["高姐出场——'靠自己站起来'", "三学员站桩数据进步", "笔记本写下'气脉'又划掉"],
         "chars": ["jiang-linyuan", "gao-jie", "liu-yutong", "chen-pang", "zhang-yang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "站桩——C级信息型爽点，高姐出场'靠自己站起来'，三学员站桩内外对比冲突。",
         "progress": "断章——笔记本'气脉'二字写下又划掉"},
        {"num": 22, "title": "发酵", "goal": "匿名爆料扩散到行业圈，老周面临选择",
         "events": ["自媒体推文'某健身房违规聘用无证教练'", "老周面临保江还是保店", "老周公开表态"],
         "chars": ["jiang-linyuan", "lao-zhou", "zhang-yang"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "发酵——B级情感型爽点，老周当众公开表态'他是我的人，我的店，我的规矩'。",
         "progress": "反转——老周公开挺江临渊"},
        {"num": 23, "title": "验收", "goal": "四个学员数据摆在面前，无声胜有声",
         "events": ["四学员数据震惊全场", "张扬第一次无言以对", "刘雨桐正式请求学功夫"],
         "chars": ["jiang-linyuan", "lao-zhou", "chen-pang", "liu-yutong", "zhang-yang"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "验收——A级打脸爽点，四学员数据震惊全场，张扬无言以对，刘雨桐请求学'以前练的那种'。",
         "progress": "升级——刘雨桐请求学真正的功夫"},
        {"num": 24, "title": "功夫", "goal": "教'功夫'还是教'健身'的界限冲突",
         "events": ["教刘雨桐真正的站桩心法", "气脉核心概念完成", "内力在现代世界的名字"],
         "chars": ["jiang-linyuan", "liu-yutong"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "功夫——B级信息型爽点，江临渊教刘雨桐真正的站桩心法，'气脉健身法'核心概念完成。",
         "progress": "断章——丹田到脚底的那条线"},
        {"num": 25, "title": "暗流", "goal": "顾长风从个人挑战转向商业施压",
         "events": ["顾长风提出联合办班", "程渡暗中摸底", "确认收编意图"],
         "chars": ["jiang-linyuan", "gu-changfeng", "cheng-du", "lao-zhou"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "暗流——铺垫章，顾长风商业合作邀约实为收编，程渡摸底确认意图。",
         "progress": "升级——不是合作是收编"},
        {"num": 26, "title": "靠近", "goal": "陈胖从'江教练'到'师父'的情感转变铺垫",
         "events": ["陈胖深蹲突破100公斤", "'能扛得住'不是杠铃是生活", "陈胖想说什么没说出口"],
         "chars": ["jiang-linyuan", "chen-pang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "靠近——C级暖意，陈胖深蹲突破100公斤，'能扛得住'不是杠铃是生活。",
         "progress": "断章——陈胖想说什么没说出口"},
        {"num": 27, "title": "师父", "goal": "陈胖脱口叫'师父'——全书情感高潮",
         "events": ["陈胖叫'师父'", "江临渊说'不是师父是教练'", "右手摸腰侧"],
         "chars": ["jiang-linyuan", "chen-pang"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "师父——A级情感型爽点，全书情感高潮之一，陈胖叫出'师父'两个字。",
         "progress": "升级——从'教练'到'师父'的情感临界点"},
        {"num": 28, "title": "气脉", "goal": "气脉健身法正式命名+教学大纲完成",
         "events": ["教学大纲整理成形", "老周决定支持独立开课", "'气脉健身'正式命名"],
         "chars": ["jiang-linyuan", "lao-zhou"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "气脉——B级信息型爽点，气脉健身法正式命名，老周决定腾时段支持独立开课。",
         "progress": "升级——气脉健身法正式课程"},
        {"num": 29, "title": "回应", "goal": "顾长风从收编到围堵——第四家分馆+百万粉博主",
         "events": ["长风武馆开第四家分馆", "乔宇发视频质疑", "张扬开始观察转变"],
         "chars": ["jiang-linyuan", "gu-changfeng", "cheng-du", "qiao-yu", "zhang-yang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "回应——C级信息型，顾长风围堵升级开店+博主质疑，张扬开始观察转变。",
         "progress": "反转——顾长风在开业时邀请"},
        {"num": 30, "title": "求存", "goal": "第二卷收尾——回望'求存'主题",
         "events": ["回顾从扛水泥到被叫师父", "气脉健身法完成", "老周腾时段开课"],
         "chars": ["jiang-linyuan", "lao-zhou", "chen-pang", "liu-yutong", "gao-jie"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "求存——B级情感型，第二卷收尾，'存不是活着，是存在着，被人需要着'。",
         "progress": "升级——第三卷'破土'开始"},
        {"num": 31, "title": "破土", "goal": "气脉健身第一堂课——六个人站了四十分钟",
         "events": ["第一堂气脉健身课", "新学员立竿见影改善", "程渡'像本来就该站在那里'"],
         "chars": ["jiang-linyuan", "lao-zhou", "cheng-du", "liu-yutong", "chen-pang"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "破土——B级情感型，气脉健身第一堂课，新学员效果立竿见影，程渡说他'像本来就该站在那里'。",
         "progress": "升级——气脉健身从理论到实践"},
        {"num": 32, "title": "名声", "goal": "口碑传播带来规模化问题——一个人教不过来",
         "events": ["朋友圈被疯狂转发", "八个咨询电话", "核心矛盾：内力感知只有他能做到"],
         "chars": ["jiang-linyuan", "lao-zhou"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "名声——C级信息型，气脉健身法口碑传播，八个咨询电话，面临规模化问题。",
         "progress": "断章——怎么教别人教别人"},
    ]

    for ch in raw_chapters:
        chapters[ch["num"]] = {
            "chapter_number": ch["num"],
            "title": ch["title"],
            "goal": ch["goal"],
            "key_events": ch["events"],
            "involved_characters": ch["chars"],
            "chapter_type": ch["type"],
            "mood": ch["mood"],
            "estimated_words": 2500,
            "chapter_summary": ch["summary"],
            "storyline_progress": ch["progress"],
            "shuangdian": ch["sd"],
        }

    return chapters


def parse_outline_file_31_50(text):
    """解析第31-50章大纲 -> 编号33-52"""
    chapters = {}

    raw_chapters = [
        {"num": 33, "title": "带人", "goal": "陈胖第一次带新人——'教别人教别人'实验",
         "events": ["陈胖教程序员站桩成功", "刘雨桐主动提出带跑者", "老学员可以教基础"],
         "chars": ["jiang-linyuan", "chen-pang", "liu-yutong"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "带人——C级信息型，陈胖第一次带新人成功，'教别人教别人'实验初见成效。",
         "progress": "升级——老学员可以教基础"},
        {"num": 34, "title": "呼吸", "goal": "赵一帆焦虑症——呼吸法可以独立成板块",
         "events": ["赵一帆焦虑发作手抖", "'抖没关系呼吸就行'", "呼吸法独立板块确认"],
         "chars": ["jiang-linyuan", "zhao-yifan"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "呼吸——B级情感型，赵一帆出场，呼吸法让手抖停了，'终于有人没让我别抖了'。",
         "progress": "断章——呼吸可为独立板块"},
        {"num": 35, "title": "试试", "goal": "苏姐'不变应万变'——心态板块确认",
         "events": ["苏姐门口犹豫三天", "'站不住就站不住'", "不变应万变心态教学"],
         "chars": ["jiang-linyuan", "su-jie"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "试试——C级暖意，苏姐出场'不变应万变'，'站不住就站不住'落在需要的人身上。",
         "progress": "反转——苏姐主动提出不变应万变"},
        {"num": 36, "title": "三徒", "goal": "三徒格局成形——学员在教学员",
         "events": ["三组同时训练", "陈胖基础/刘雨桐身体/赵一帆呼吸/苏姐心境", "'不必处处在场'"],
         "chars": ["jiang-linyuan", "liu-yutong", "zhao-yifan", "su-jie", "chen-pang"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "三徒——B级信息型，三徒格局成形，三角结构完成框架搭建。",
         "progress": "升级——刘雨桐收到格斗赛邀请"},
        {"num": 37, "title": "师父（格斗赛）", "goal": "刘雨桐业余格斗赛赢了——徒弟公开叫师父",
         "events": ["刘雨桐赢了业余格斗赛", "公开叫'江临渊我师父'", "乔宇在现场录像被触动"],
         "chars": ["jiang-linyuan", "liu-yutong", "qiao-yu"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "师父（格斗赛）——A级多重爽点，刘雨桐赢了比赛公开叫师父，乔宇被触动。",
         "progress": "断章——乔宇开始研究站桩"},
        {"num": 38, "title": "玄学", "goal": "乔宇发视频质疑——有道理的质疑",
         "events": ["乔宇发视频'健身不是玄学'", "粉丝涌入评论区", "确实没有标准化数据"],
         "chars": ["jiang-linyuan", "qiao-yu", "lao-zhou"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "玄学——铺垫章，乔宇发视频质疑，有道理的质疑，江临渊承认'他说得对'。",
         "progress": "升级——但数据不只是"},
        {"num": 39, "title": "数据", "goal": "用学员手写记录回应'数据'",
         "events": ["三个月学员记录摆在桌上", "找茬者无言以对", "张扬第一次公开开口帮忙"],
         "chars": ["jiang-linyuan", "zhang-yang", "lao-zhou", "yang-yang"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "数据——B级双线爽点，数据碾压+张扬第一次公开站队'数据是真的'。",
         "progress": "反转——张扬第一次开口"},
        {"num": 40, "title": "定位", "goal": "程渡介绍小何——'水泥哥'需要新定位",
         "events": ["程渡介绍小何做运营", "程渡在车里想说什么没说", "小何加微信"],
         "chars": ["jiang-linyuan", "cheng-du", "xiao-he"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "定位——铺垫章，程渡介绍小何，程渡感情线在暗处蓄力。",
         "progress": "断章——小何加微信"},
        {"num": 41, "title": "登门", "goal": "乔宇亲自登门体验——'不是骗人的'",
         "events": ["乔宇一个人来没有摄像机", "亲自体验站桩脚底发热", "'不是玄学''我会再来的'"],
         "chars": ["jiang-linyuan", "qiao-yu", "lao-zhou"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "登门——A级信息型+情感型，百万粉博主亲身体验后被触动，'不是骗人的'。",
         "progress": "升级——小何问定位"},
        {"num": 42, "title": "生根", "goal": "定位视频爆了——'教你生根'",
         "events": ["小何拍第一条定位视频", "'教你生根'概念确立", "二十四小时播放量破百万"],
         "chars": ["jiang-linyuan", "xiao-he", "liu-yutong"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "生根——B级信息型，定位从'水泥哥'蜕变为'教你生根'，视频播放量破百万。",
         "progress": "反转——品牌定位确立"},
        {"num": 43, "title": "围堵", "goal": "顾长风免费体验月+收购邀约",
         "events": ["四家武馆免费体验月", "顾长风'开个价'收购课程版权", "程渡拒绝顾长风方案"],
         "chars": ["jiang-linyuan", "gu-changfeng", "cheng-du", "lao-zhou"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "围堵——铺垫章，顾长风从收编升级为收购，商业打压进入新阶段。",
         "progress": "断章——不卖，让他加码"},
        {"num": 44, "title": "拒绝", "goal": "程渡表白被拒——干净而笨拙",
         "events": ["程渡做三菜一汤表白", "江临渊'你做的菜很好吃'", "程渡选择继续帮助"],
         "chars": ["jiang-linyuan", "cheng-du"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "拒绝——B级情感型，全书最干净的拒绝戏，程渡从'喜欢'到'选择继续'。",
         "progress": "反转——碗我洗你回去备课"},
        {"num": 45, "title": "站队", "goal": "张扬正式站队——拒绝顾长风",
         "events": ["顾长风派人来挖张扬", "张扬拒绝'我留下来'", "张扬私下练了两个月站桩"],
         "chars": ["jiang-linyuan", "zhang-yang"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "站队——A级情感型，张扬四步弧线完成，从对手到站队，'数据是真的'。",
         "progress": "反转——张扬第一次感觉到气"},
        {"num": 46, "title": "扩张", "goal": "从'一半店面'到'独立门店'",
         "events": ["老周盘隔壁铺子", "江临渊坚持出一半钱", "'一起扛'"],
         "chars": ["jiang-linyuan", "lao-zhou"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "扩张——C级暖意，老周谈扩张，江临渊第一次主动花钱，'一起扛'。",
         "progress": "升级——江临渊出钱合伙"},
        {"num": 47, "title": "沉默", "goal": "乔宇学员体验站桩——'和而不同'",
         "events": ["乔宇带学员做对比", "'膝盖热了'", "乔宇握手'不打架了'"],
         "chars": ["jiang-linyuan", "qiao-yu", "lao-zhou"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "沉默——A级信息型，乔宇从质疑到合作，'和而不同'，体育局邀请行业交流。",
         "progress": "断章——体育局邀请函"},
        {"num": 48, "title": "老王", "goal": "系统内第一个盟友——私下认可但不公开挺",
         "events": ["老王私下见面摸底", "'你是真的'", "给你一个说话的机会"],
         "chars": ["jiang-linyuan", "lao-wang"],
         "type": "climax", "mood": "日常", "sd": "C级",
         "summary": "老王——C级信息型，系统内第一个盟友出场，'你是真的'但不能公开挺。",
         "progress": "升级——交流会还有顾长风"},
        {"num": 49, "title": "交流（上）", "goal": "行业交流会——江临渊不辩解而是站桩",
         "events": ["圆桌二十人各路质疑", "江临渊站桩十五分钟不动", "张扬站起来公开站队"],
         "chars": ["jiang-linyuan", "zhang-yang", "lao-wang", "gu-changfeng"],
         "type": "setup", "mood": "过渡/蓄力", "sd": "无",
         "summary": "交流（上）——悬念章，行业交流会，江临渊站桩十五分钟+张扬站起来站队。",
         "progress": "断章——为下半场做准备"},
        {"num": 50, "title": "交流（下）", "goal": "不打而胜——全场沉默",
         "events": ["教授站桩失败", "连锁教练站了十二分钟'不一样'", "乔宇当众承认'我现在还在学'", "顾长风被留在原地"],
         "chars": ["jiang-linyuan", "qiao-yu", "zhang-yang", "lao-wang", "gu-changfeng"],
         "type": "climax", "mood": "大爽", "sd": "S级",
         "summary": "交流（下）——S级全书最高级爽点，不打而胜，全场沉默，'三百年了'。",
         "progress": "反转——但'他们看到了'"},
        {"num": 51, "title": "改名", "goal": "投资人要改名包装——'改名不行'",
         "events": ["陈总提出三百万+改名方案", "江临渊拒绝'改名不行'", "'气脉不是一个名字是一个东西'"],
         "chars": ["jiang-linyuan", "chen-zong"],
         "type": "climax", "mood": "小爽", "sd": "B级",
         "summary": "改名——B级价值观型，'改名不行'是全书核心价值观的宣言。",
         "progress": "反转——钱可以没有但气脉不能改"},
        {"num": 52, "title": "破土", "goal": "第三卷收尾——从一个人到一个体系",
         "events": ["隔壁铺子打通独立空间", "三徒格局全部就位", "未知号码短信——陆沉线索"],
         "chars": ["jiang-linyuan", "liu-yutong", "zhao-yifan", "su-jie", "chen-pang", "zhang-yang", "xiao-he"],
         "type": "climax", "mood": "大爽", "sd": "A级",
         "summary": "破土——A级多重收束，第三卷破土主题完成闭环，第四卷悬念引爆。",
         "progress": "断章——'天牢里的那个人不是只有顾长风'"},
    ]

    for ch in raw_chapters:
        chapters[ch["num"]] = {
            "chapter_number": ch["num"],
            "title": ch["title"],
            "goal": ch["goal"],
            "key_events": ch["events"],
            "involved_characters": ch["chars"],
            "chapter_type": ch["type"],
            "mood": ch["mood"],
            "estimated_words": 2500,
            "chapter_summary": ch["summary"],
            "storyline_progress": ch["progress"],
            "shuangdian": ch["sd"],
        }

    return chapters


# ============================================================
# 构建角色数据
# ============================================================

def build_characters():
    """构建所有角色数据"""
    characters = []

    # 主角
    characters.append({
        "character_id": "jiang-linyuan",
        "name": "江临渊",
        "alias": ["盟主", "水泥哥", "江教练", "师父"],
        "gender": "男",
        "age": 28,
        "occupation": "健身教练",
        "role": "主角",
        "status": "active",
        "appearance": {
            "height": "182cm",
            "build": "魁梧，肩极宽",
            "hair": "长发束冠",
            "eyes": "深邃沉稳",
            "clothing_style": "黑色紧身运动衣（现代）/白色囚衣（穿越初期）",
            "distinctive_features": ["手骨粗大有剑痕", "虎口旧剑痕", "膝盖微屈如随时发力"]
        },
        "personality": {
            "traits": ["隐忍", "有原则", "不认命", "骨子里的傲", "话少", "在乎的人面前极软"],
            "core_belief": "被需要才能证明活着",
            "motivation": "被需要——不是当最强，是当一个有用的人",
            "flaw": "无法放下'我必须亲自在场'的执念",
            "speech_style": "冷淡简短，短句直给，不解释，不用语气词",
            "catchphrases": ["行。", "不错。"]
        },
        "relationships": [
            {"target": "a-qi", "type": "师徒", "description": "师弟，从小跟在身后，铁链两边互相递馒头三年"},
            {"target": "lu-chen", "type": "背叛", "description": "师叔，暗中与顾长风合作，背叛了门派"},
            {"target": "gu-changfeng", "type": "敌对", "description": "死敌，同穿越者，走完全相反的路"},
            {"target": "lao-zhou", "type": "合作", "description": "老板→大哥→合伙人，气脉健身第一个投资人"},
            {"target": "chen-pang", "type": "师徒", "description": "第一个徒弟，第一个叫他'师父'的人"},
            {"target": "cheng-du", "type": "合作", "description": "被拒绝后仍选择继续帮助，'说。'"},
            {"target": "zhang-yang", "type": "竞争", "description": "从对手到站队，被数据说服的科班教练"},
            {"target": "liu-yutong", "type": "师徒", "description": "第一个真正的徒弟，运动康复板块继承者"},
            {"target": "zhao-yifan", "type": "师徒", "description": "呼吸法板块继承者"},
            {"target": "su-jie", "type": "师徒", "description": "心态/定力板块继承者"},
            {"target": "qiao-yu", "type": "合作", "description": "从对手到'和而不同'，不打架了"},
        ],
        "character_arc": {
            "initial_state": "武林盟主，万人跪伏",
            "turning_points": [
                {"chapter": 1, "event": "穿越到2026年成都", "change": "所有强大变成无用"},
                {"chapter": 12, "event": "告别工地进健身房", "change": "找到第一个位置"},
                {"chapter": 27, "event": "陈胖叫师父", "change": "重新被需要"},
                {"chapter": 50, "event": "行业交流不打而胜", "change": "从用拳头赢到不需要赢"},
            ],
            "final_state": "气脉健身创始人，新'门派'建立者"
        }
    })

    # 师弟（阿七）
    characters.append({
        "character_id": "a-qi",
        "name": "阿七",
        "alias": ["师弟"],
        "gender": "男",
        "age": 22,
        "occupation": "武林弟子",
        "role": "旧世界角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "手指粗，手上有练拳的茧",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["牙缺了一颗——替人挡剑磕掉的"]
        },
        "personality": {
            "traits": ["最笨的手+最细的心", "忠诚", "话多"],
            "core_belief": "跟着师兄走",
            "motivation": "守护师兄",
            "flaw": "未详",
            "speech_style": "话比江临渊多，语速快，笑的时候嘴咧很大",
            "catchphrases": ["没事", "你别管"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "师徒", "description": "师弟，铁链两边互相递馒头三年，比亲兄弟多一层东西"},
        ],
        "character_arc": {
            "initial_state": "江临渊的师弟，从小跟在身边",
            "turning_points": [],
            "final_state": "门派被血洗时——（待揭示）"
        }
    })

    # 陆沉
    characters.append({
        "character_id": "lu-chen",
        "name": "陆沉",
        "alias": ["师叔"],
        "gender": "男",
        "age": 55,
        "occupation": "门派长老",
        "role": "旧世界角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "背微驼",
            "hair": "头发白了大半",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["左手垂着——年轻时被人伤了筋"]
        },
        "personality": {
            "traits": ["看起来温和", "做了最不可挽回的事", "自欺"],
            "core_belief": "我只是把他移开——不会让他死",
            "motivation": "怕江临渊的'不转弯'会毁了整个门派",
            "flaw": "把背叛包装成保护",
            "speech_style": "温和、慢、长辈的语调，话在喉咙里磨一遍才出来",
            "catchphrases": ["那孩子不会转弯。你帮我看着他。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "背叛", "description": "看着他长大，暗中与顾长风合作背叛门派"},
            {"target": "gu-changfeng", "type": "合作", "description": "同盟——陆沉提供内部信息和信任，顾长风提供外部力量"},
        ],
        "character_arc": {
            "initial_state": "看着江临渊长大的师叔，门派长老",
            "turning_points": [],
            "final_state": "第五卷——江临渊直播时不说他的名字，不是原谅，是不值得再提"
        }
    })

    # 李师傅
    characters.append({
        "character_id": "li-shifu",
        "name": "李师傅",
        "alias": ["工头"],
        "gender": "男",
        "age": 52,
        "occupation": "包工头",
        "role": "第一卷角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["说话糙", "心不坏", "看人看干不干活"],
            "core_belief": "不偷的人，命长",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "说话糙",
            "catchphrases": ["这娃不说话，但干活不偷。不偷的人，命长。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "收留他的人，第一个上级"},
        ],
        "character_arc": {
            "initial_state": "成都本地包工头",
            "turning_points": [],
            "final_state": "第10章告别——留了一双新鞋，'买的，不是偷的'"
        }
    })

    # 黄毛
    characters.append({
        "character_id": "huang-mao",
        "name": "黄毛",
        "alias": [],
        "gender": "男",
        "age": 21,
        "occupation": "工友",
        "role": "第一卷角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "染黄发",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["手机不离手"]
        },
        "personality": {
            "traits": ["话多", "自来熟", "拍什么都觉得好玩"],
            "core_belief": "好玩就拍",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "话多，自来熟",
            "catchphrases": []
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "'水泥哥'账号的创建者，这个世界的解说员"},
        ],
        "character_arc": {
            "initial_state": "年轻工友，手机不离手",
            "turning_points": [],
            "final_state": "第10章和工友们一起出现在健身房办卡"
        }
    })

    # 老魏
    characters.append({
        "character_id": "lao-wei",
        "name": "老魏",
        "alias": [],
        "gender": "男",
        "age": 52,
        "occupation": "老工友",
        "role": "第一卷角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["沉默", "干活稳", "从不多问"],
            "core_belief": "干活就行",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "沉默寡言",
            "catchphrases": []
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "沉默同类——坐在一起不说话但最舒服的沉默"},
        ],
        "character_arc": {
            "initial_state": "老工友，沉默寡言",
            "turning_points": [],
            "final_state": "第8章——签名的安全帽就是他递给江临渊的"
        }
    })

    # 老周
    characters.append({
        "character_id": "lao-zhou",
        "name": "老周",
        "alias": ["周建国"],
        "gender": "男",
        "age": 51,
        "occupation": "健身房老板",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "戴眼镜",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["看起来圆滑", "交了最深的朋友", "唠叨但有温度", "怕再失去任何人"],
            "core_belief": "守住这家店",
            "motivation": "亡妻的遗愿——守住这家店",
            "flaw": "未详",
            "speech_style": "长句唠叨但有温度，语速快爱抢话",
            "catchphrases": ["你是我的人。", "我跟你说。", "你听我的。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "老板→大哥→合伙人，气脉健身第一个投资人"},
        ],
        "character_arc": {
            "initial_state": "快倒闭的小健身房老板",
            "turning_points": [],
            "final_state": "气脉健身第一个投资人"
        }
    })

    # 陈胖
    characters.append({
        "character_id": "chen-pang",
        "name": "陈胖",
        "alias": ["陈大勇"],
        "gender": "男",
        "age": 30,
        "occupation": "上班族",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "偏胖→逐渐变瘦",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["说话小声", "走路低头"]
        },
        "personality": {
            "traits": ["最软的外壳+最硬的决心", "说话小声", "最忠诚"],
            "core_belief": "能扛得住",
            "motivation": "被前女友甩后重建自己",
            "flaw": "过度道歉",
            "speech_style": "试探式，说半句停半句",
            "catchphrases": ["对不起", "谢谢", "江教练……你还有没有别的？"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "师徒", "description": "学员→第一个'徒弟'→叫'师父'，从头到尾没离开"},
        ],
        "character_arc": {
            "initial_state": "被前女友甩的普通上班族",
            "turning_points": [],
            "final_state": "气脉健身基础板块教练，最忠诚的徒弟"
        }
    })

    # 程渡
    characters.append({
        "character_id": "cheng-du",
        "name": "程渡",
        "alias": [],
        "gender": "男",
        "age": 32,
        "occupation": "设计公司老板",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "有品位",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["表面玩世不恭", "内心最认真", "嘴碎爱笑"],
            "core_belief": "在乎一个人不需要回报",
            "motivation": "帮助江临渊",
            "flaw": "未详",
            "speech_style": "反问+调侃，语速快但会停",
            "catchphrases": ["啧。", "行吧。", "妈的，白教你用手机了。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "暗恋", "description": "喜欢→被拒绝→选择继续帮助，每次回复都是'说。'"},
            {"target": "gu-changfeng", "type": "利用", "description": "表面配合实际摸底，替江临渊暗中斡旋"},
        ],
        "character_arc": {
            "initial_state": "健身房高级会员，注意到江临渊",
            "turning_points": [],
            "final_state": "每次江临渊需要帮忙，他的回复永远是'说。'"
        }
    })

    # 张扬
    characters.append({
        "character_id": "zhang-yang",
        "name": "张扬",
        "alias": [],
        "gender": "男",
        "age": 28,
        "occupation": "健身教练",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["相信科班", "不是坏人", "规则捍卫者"],
            "core_belief": "科学规范才是对的",
            "motivation": "证明自己",
            "flaw": "看不起'野路子'",
            "speech_style": "断言式，中速",
            "catchphrases": ["你不懂。", "科学来说……"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "竞争", "description": "从对手到被数据说服，'你可以教我站桩'"},
        ],
        "character_arc": {
            "initial_state": "科班出身的老员工，看不起江临渊",
            "turning_points": [],
            "final_state": "气脉健身教学主管"
        }
    })

    # 刘雨桐
    characters.append({
        "character_id": "liu-yutong",
        "name": "刘雨桐",
        "alias": [],
        "gender": "女",
        "age": 26,
        "occupation": "退役运动员",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "强壮",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["膝盖有旧伤"]
        },
        "personality": {
            "traits": ["最强壮的体格+最脆弱的自我价值", "不服输", "只对自己狠"],
            "core_belief": "我可以",
            "motivation": "证明自己还能运动",
            "flaw": "脆弱的自我价值",
            "speech_style": "命令式（对自己），语速快",
            "catchphrases": ["我可以。", "再来。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "师徒", "description": "第一个真正的徒弟，运动康复板块继承者"},
        ],
        "character_arc": {
            "initial_state": "退役运动员，膝盖旧伤被判'不能运动'",
            "turning_points": [],
            "final_state": "气脉健身的康复师"
        }
    })

    # 赵一帆
    characters.append({
        "character_id": "zhao-yifan",
        "name": "赵一帆",
        "alias": [],
        "gender": "男",
        "age": 23,
        "occupation": "待业",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "瘦",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": ["低着头", "手指在裤缝上搓"]
        },
        "personality": {
            "traits": ["极度内向", "社恐", "网上能正常说话"],
            "core_belief": "未详",
            "motivation": "克服焦虑症",
            "flaw": "极度内向",
            "speech_style": "试探式，声音小",
            "catchphrases": []
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "师徒", "description": "呼吸法板块继承者"},
        ],
        "character_arc": {
            "initial_state": "社恐宅男，焦虑症",
            "turning_points": [],
            "final_state": "气脉健身的呼吸/冥想教练"
        }
    })

    # 苏姐
    characters.append({
        "character_id": "su-jie",
        "name": "苏姐",
        "alias": [],
        "gender": "女",
        "age": 37,
        "occupation": "中年离异女性",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["表面柔弱", "内心有刚", "三十七岁第一次进健身房"],
            "core_belief": "不变应万变",
            "motivation": "重建自己",
            "flaw": "从未坚持过任何东西",
            "speech_style": "未详",
            "catchphrases": ["我这辈子没有坚持过任何东西。这次——我想试试。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "师徒", "description": "心态/定力板块继承者"},
        ],
        "character_arc": {
            "initial_state": "中年离异女性",
            "turning_points": [],
            "final_state": "气脉健身最受欢迎的教练——专门带四十岁以上女性学员"
        }
    })

    # 乔宇（乔教练Joe）
    characters.append({
        "character_id": "qiao-yu",
        "name": "乔宇",
        "alias": ["乔教练Joe"],
        "gender": "男",
        "age": 30,
        "occupation": "健身博主",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "运动服",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["自信到傲慢", "对自己的学员确实负责", "不是坏人"],
            "core_belief": "健身不是玄学，需要规范",
            "motivation": "保护学员",
            "flaw": "不接受不规范",
            "speech_style": "未详",
            "catchphrases": ["健身不是玄学。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "竞争", "description": "从质疑到'和而不同'，不打架了"},
        ],
        "character_arc": {
            "initial_state": "百万粉健身博主，成都有三家连锁健身房",
            "turning_points": [],
            "final_state": "和江临渊达成'互不打扰'的默契"
        }
    })

    # 顾长风
    characters.append({
        "character_id": "gu-changfeng",
        "name": "顾长风",
        "alias": [],
        "gender": "男",
        "age": 28,
        "occupation": "连锁武馆老板",
        "role": "第四卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["逻辑自洽", "选择用武功在新世界称王", "不是纯粹的恶"],
            "core_belief": "既然穿越了，武功就是我们的优势",
            "motivation": "用武功称王",
            "flaw": "永远用三百年前的方式看人",
            "speech_style": "长句，自问自答，慢而有压迫感，把挑衅包装成'为你好'",
            "catchphrases": ["你还不明白吗。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "敌对", "description": "死敌→招揽→商业打压→擂台对决→告别"},
            {"target": "lu-chen", "type": "合作", "description": "同盟——天牢计划的合作者"},
            {"target": "cheng-du", "type": "利用", "description": "想通过程渡商业网搞江临渊"},
        ],
        "character_arc": {
            "initial_state": "同穿越者，江临渊在武侠世界的死敌",
            "turning_points": [],
            "final_state": "离开成都，两人最后一面——不是和解，是承认"
        }
    })

    # 老王（体育局）
    characters.append({
        "character_id": "lao-wang",
        "name": "老王",
        "alias": [],
        "gender": "男",
        "age": 45,
        "occupation": "体育局官员",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "戴眼镜",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["体制内的谨慎", "个人的真诚"],
            "core_belief": "你是真的",
            "motivation": "在规则内帮忙",
            "flaw": "不能公开挺",
            "speech_style": "说话慢，每一句都像在掂量",
            "catchphrases": ["我没办法公开挺你。但你的方法——能给我看看吗？"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "系统内第一个盟友，私下认可但不方便公开"},
        ],
        "character_arc": {
            "initial_state": "体育局负责健身教练资格认证的中年人",
            "turning_points": [],
            "final_state": "替江临渊在规则内找到合法空间"
        }
    })

    # 小何
    characters.append({
        "character_id": "xiao-he",
        "name": "小何",
        "alias": [],
        "gender": "女",
        "age": 22,
        "occupation": "抖音运营",
        "role": "第三卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["专业", "喜剧感"],
            "core_belief": "定位决定一切",
            "motivation": "帮江临渊做品牌",
            "flaw": "未详",
            "speech_style": "未详",
            "catchphrases": ["江老师你的定位是什么？"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "程渡介绍来的抖音运营"},
        ],
        "character_arc": {
            "initial_state": "程渡介绍的抖音运营",
            "turning_points": [],
            "final_state": "气脉健身品牌运营"
        }
    })

    # 小杨
    characters.append({
        "character_id": "yang-yang",
        "name": "小杨",
        "alias": [],
        "gender": "女",
        "age": 21,
        "occupation": "健身房前台",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["嘴快", "天然友好", "对喜欢的人好对讨厌的人翻白眼"],
            "core_belief": "未详",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "嘴快",
            "catchphrases": []
        },
        "relationships": [],
        "character_arc": {
            "initial_state": "健身房前台",
            "turning_points": [],
            "final_state": "未详"
        }
    })

    # 高姐
    characters.append({
        "character_id": "gao-jie",
        "name": "高姐",
        "alias": [],
        "gender": "女",
        "age": 50,
        "occupation": "学员",
        "role": "第二卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["想靠自己站起来"],
            "core_belief": "不给孩子添负担",
            "motivation": "靠自己站起来",
            "flaw": "未详",
            "speech_style": "未详",
            "catchphrases": ["我想靠自己站起来。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "崇拜", "description": "学员，和江临渊一样想靠自己"},
        ],
        "character_arc": {
            "initial_state": "五十岁学员，膝盖不好",
            "turning_points": [],
            "final_state": "未详"
        }
    })

    # 许曼
    characters.append({
        "character_id": "xu-man",
        "name": "许曼",
        "alias": [],
        "gender": "女",
        "age": 30,
        "occupation": "媒体记者",
        "role": "第四卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["不站队", "追问到底"],
            "core_belief": "真相",
            "motivation": "追问",
            "flaw": "未详",
            "speech_style": "未详",
            "catchphrases": []
        },
        "relationships": [],
        "character_arc": {
            "initial_state": "本地媒体记者",
            "turning_points": [],
            "final_state": "未详"
        }
    })

    # 孟姐
    characters.append({
        "character_id": "meng-jie",
        "name": "孟姐",
        "alias": [],
        "gender": "女",
        "age": 35,
        "occupation": "律师",
        "role": "第四卷角色",
        "status": "active",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["干练", "直接"],
            "core_belief": "规则之内保护人",
            "motivation": "帮程渡的朋友",
            "flaw": "未详",
            "speech_style": "直接",
            "catchphrases": ["你这人太容易信别人了。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "发现顾长风的合同陷阱"},
        ],
        "character_arc": {
            "initial_state": "律师，程渡介绍来的",
            "turning_points": [],
            "final_state": "未详"
        }
    })

    # 投资人陈总
    characters.append({
        "character_id": "chen-zong",
        "name": "陈总",
        "alias": [],
        "gender": "男",
        "age": 42,
        "occupation": "投资人",
        "role": "第三卷角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "定制西装",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["自信", "商业思维"],
            "core_belief": "品牌需要包装",
            "motivation": "投资",
            "flaw": "看不到品牌之外的东西",
            "speech_style": "未详",
            "catchphrases": []
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "利用", "description": "想投资但要改名包装，被拒绝"},
        ],
        "character_arc": {
            "initial_state": "成都本地投资人",
            "turning_points": [],
            "final_state": "被拒绝——'你这种人我见过'"
        }
    })

    # 阿星
    characters.append({
        "character_id": "a-xing",
        "name": "阿星",
        "alias": [],
        "gender": "未详",
        "age": 28,
        "occupation": "直播主持人",
        "role": "第五卷角色",
        "status": "planned",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["会做效果", "不失人情"],
            "core_belief": "未详",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "未详",
            "catchphrases": []
        },
        "relationships": [],
        "character_arc": {
            "initial_state": "直播主持人",
            "turning_points": [],
            "final_state": "被江临渊的诚实打乱了准备好的问题"
        }
    })

    # 流浪汉
    characters.append({
        "character_id": "liulanghan",
        "name": "流浪汉",
        "alias": [],
        "gender": "男",
        "age": "未知",
        "occupation": "流浪者",
        "role": "第一卷角色",
        "status": "inactive",
        "appearance": {
            "height": "未详",
            "build": "未详",
            "hair": "未详",
            "eyes": "未详",
            "clothing_style": "未详",
            "distinctive_features": []
        },
        "personality": {
            "traits": ["善良"],
            "core_belief": "未详",
            "motivation": "未详",
            "flaw": "未详",
            "speech_style": "未详",
            "catchphrases": ["你也是没地方去的吧。"]
        },
        "relationships": [
            {"target": "jiang-linyuan", "type": "合作", "description": "给了江临渊半个馒头——全书第一个对他好的人"},
        ],
        "character_arc": {
            "initial_state": "流浪汉",
            "turning_points": [],
            "final_state": "仅一场戏"
        }
    })

    return characters


# ============================================================
# 构建 world_setting
# ============================================================

def build_world_setting():
    return {
        "era": "现代",
        "location": "成都",
        "power_system": {
            "name": "气脉健身法",
            "levels": [
                {
                    "rank": 1,
                    "name": "基础站桩",
                    "description": "膝盖微屈、重心下沉、姿势标准",
                    "typical_abilities": ["体态改善", "基础体能"]
                },
                {
                    "rank": 2,
                    "name": "气感觉醒",
                    "description": "丹田呼吸+脚底到头顶的气血感知",
                    "typical_abilities": ["疼痛缓解", "情绪稳定"]
                },
                {
                    "rank": 3,
                    "name": "内力转化",
                    "description": "将传统内力理论转化为现代运动康复",
                    "typical_abilities": ["运动康复", "呼吸法教学"]
                },
                {
                    "rank": 4,
                    "name": "气脉贯通",
                    "description": "丹田→核心稳定、经络→筋膜链、内力→气脉的完整体系",
                    "typical_abilities": ["全体系教学", "他人指导"]
                }
            ]
        },
        "terms": {
            "气脉健身": "江临渊创立的健身方法，融合传统武术站桩、经络理论和现代运动康复",
            "降龙掌": "传统武功绝技，十八掌，现代世界无人知晓",
            "百鸟朝凤剑法": "传统剑法",
            "水泥哥": "江临渊在工地扛水泥时的外号，后来成为抖音账号名",
            "长风武馆": "顾长风在成都开的连锁武馆，共四家分馆",
            "气脉": "丹田到脚底的那条线，站桩时能感觉到的气血流动"
        },
        "rules": [
            "衡量人的标准：财富、学历、关系、稳定",
            "武功在现代是'负债'不是资产",
            "健身教练需要资格证才能合法教学",
            "这个世界唯一能转化的武侠能力：经络/身体知识→运动康复"
        ]
    }


# ============================================================
# 构建大纲 outline
# ============================================================

def build_outline(all_chapter_outlines):
    """构建 outline 结构"""
    outline = {
        "template": "custom",
        "main_storyline": {
            "protagonist_goal": "被需要——想用自己的能力证明价值",
            "core_conflict": "现代社会不需要功夫。衡量人的标准是钱、学历、社交——他全没有",
            "character_arc": "从天牢死囚到工地水泥工到健身教练到气脉健身创始人——重建尊严的过程",
            "stakes": "失败不会死——变成'没用的人'，比死更难受"
        },
        "acts": [
            {
                "act_number": 0,
                "title": "序章",
                "chapter_range": [1, 2],
                "summary": "盟主巅峰+背叛入狱+天牢穿越",
                "purpose": "建立'有'和'失'——让读者理解失去一切是什么感觉"
            },
            {
                "act_number": 1,
                "title": "坠落",
                "chapter_range": [3, 12],
                "summary": "穿越+扛水泥/送快递+短视频走红+进健身房",
                "purpose": "从最底层开始——被时代抛弃的感觉"
            },
            {
                "act_number": 2,
                "title": "求存",
                "chapter_range": [13, 32],
                "summary": "当教练+考证+第一个学员蜕变+被叫'师父'",
                "purpose": "在规则内找到位置——'被需要'的第一次实现"
            },
            {
                "act_number": 3,
                "title": "破土",
                "chapter_range": [33, 52],
                "summary": "气脉健身法+收三徒+行业认可+不打而胜",
                "purpose": "从一个人到一个体系——'不必处处在场'"
            },
            {
                "act_number": 4,
                "title": "对决",
                "chapter_range": [53, 82],
                "summary": "旧敌出现+商业打压+擂台对决+身份暴露+陆沉真相",
                "purpose": "过去的真相追上来——能不能不靠拳头面对"
            },
            {
                "act_number": 5,
                "title": "立派",
                "chapter_range": [83, 102],
                "summary": "风暴+直播承认+传承+新'门派'落定",
                "purpose": "传承不靠一个人——门派自己会运转"
            }
        ],
        "chapters": []
    }

    # 已有大纲的章节（1-52）
    for num in range(1, 53):
        if num in all_chapter_outlines:
            ch_data = all_chapter_outlines[num]
            outline["chapters"].append({
                "chapter_number": num,
                "title": ch_data.get("title", f"第{num}章"),
                "goal": ch_data.get("goal", ""),
                "key_events": ch_data.get("key_events", []),
                "involved_characters": ch_data.get("involved_characters", []),
                "chapter_type": ch_data.get("chapter_type", "setup"),
                "mood": ch_data.get("mood", "过渡/蓄力"),
                "estimated_words": ch_data.get("estimated_words", 2500),
                "chapter_summary": ch_data.get("chapter_summary", ""),
                "storyline_progress": ch_data.get("storyline_progress", ""),
            })
        else:
            outline["chapters"].append({
                "chapter_number": num,
                "title": f"第{num}章",
                "goal": "",
                "key_events": [],
                "involved_characters": [],
                "chapter_type": "setup",
                "mood": "过渡/蓄力",
                "estimated_words": 2500,
                "chapter_summary": "",
                "storyline_progress": "",
            })

    # 占位大纲（53-102）
    placeholder_titles_53_82 = [
        "未知号码", "追踪", "记忆碎片", "许曼追问", "暗流再起",
        "陆沉", "旧事", "合同陷阱", "孟姐出手", "顾长风的棋",
        "身份危机", "他不是这个时代的人", "舆论风暴", "学员表态",
        "站队", "三徒回应", "老王斡旋", "规则之内", "擂台之前",
        "老钟", "擂台（一）", "擂台（二）", "擂台（三）", "降龙掌",
        "最后一式", "收拳", "真相（上）", "真相（下）", "陆沉的真相",
        "余震"
    ]
    placeholder_titles_83_102 = [
        "风暴前夕", "选择", "直播（一）", "直播（二）", "直播（三）",
        "只是教深蹲的教练", "余波", "芭蕾女生", "程序员", "退伍兵",
        "新门徒", "自然运转", "老周的老婆", "传承", "旗舰店",
        "叫教练", "开业", "门派", "盟主", "落定"
    ]

    for i, title in enumerate(placeholder_titles_53_82):
        num = 53 + i
        outline["chapters"].append({
            "chapter_number": num,
            "title": title,
            "goal": "",
            "key_events": [],
            "involved_characters": [],
            "chapter_type": "setup",
            "mood": "过渡/蓄力",
            "estimated_words": 2500,
            "chapter_summary": "（规划中，未写）",
            "storyline_progress": "第四卷——对决",
        })

    for i, title in enumerate(placeholder_titles_83_102):
        num = 83 + i
        outline["chapters"].append({
            "chapter_number": num,
            "title": title,
            "goal": "",
            "key_events": [],
            "involved_characters": [],
            "chapter_type": "setup",
            "mood": "过渡/蓄力",
            "estimated_words": 2500,
            "chapter_summary": "（规划中，未写）",
            "storyline_progress": "第五卷——立派",
        })

    return outline


# ============================================================
# 构建 volumes
# ============================================================

def build_volumes():
    volumes_data = [
        {
            "volume_number": 1,
            "title": "坠落",
            "chapter_range": [3, 12],
            "summary": "从穿越到进健身房——扛水泥、送快递、短视频走红、告别工地",
            "status": "completed",
            "volume_goal": "在底层活下来，被看见",
            "themes": ["被时代抛弃", "底层生存", "体力劳动", "被看见"]
        },
        {
            "volume_number": 2,
            "title": "求存",
            "chapter_range": [13, 32],
            "summary": "当教练+考证+第一个学员蜕变+被叫'师父'+气脉健身法命名",
            "status": "completed",
            "volume_goal": "在规则内找到位置，'被需要'的第一次实现",
            "themes": ["规则之内", "数据说话", "被需要", "体系雏形"]
        },
        {
            "volume_number": 3,
            "title": "破土",
            "chapter_range": [33, 52],
            "summary": "气脉健身法+收三徒+行业认可+不打而胜+拒绝投资",
            "status": "completed",
            "volume_goal": "从一个人到一个体系——'不必处处在场'",
            "themes": ["教别人教别人", "三徒格局", "行业认可", "品牌定位"]
        },
        {
            "volume_number": 4,
            "title": "对决",
            "chapter_range": [53, 82],
            "summary": "旧敌出现+商业打压+擂台对决+身份暴露+陆沉真相",
            "status": "planned",
            "volume_goal": "面对过去的真相——能不能不靠拳头",
            "themes": ["真相追来", "身份暴露", "擂台对决", "陆沉"]
        },
        {
            "volume_number": 5,
            "title": "立派",
            "chapter_range": [83, 102],
            "summary": "风暴+直播承认+传承+新'门派'落定",
            "status": "planned",
            "volume_goal": "传承不靠一个人——门派自己会运转",
            "themes": ["直播承认", "传承", "自然运转", "门派落定"]
        }
    ]
    # 生成 chapters 和 volume_outline 列表
    for v in volumes_data:
        start, end = v["chapter_range"]
        ch_list = list(range(start, end + 1))
        v["chapters"] = ch_list
        v["volume_outline"] = ch_list
        # 删除非标准字段
        del v["chapter_range"]
        del v["summary"]
        del v["themes"]
    return volumes_data


# ============================================================
# 处理章节文件（正文 + 元数据JSON）
# ============================================================

def process_chapter_files(all_chapter_outlines, chapters_dir):
    """读取所有已有的章节 markdown 文件，生成 txt 和 json"""
    drafts_dir = os.path.join(BASE_DIR, "drafts")
    results = []

    # 收集所有章节文件并按编号排序
    chapter_files = []
    for fname in sorted(os.listdir(drafts_dir)):
        if fname.startswith("chapter-") and fname.endswith(".md"):
            num = chapter_file_to_number(fname)
            chapter_files.append((num, fname))

    chapter_files.sort(key=lambda x: x[0])

    now_iso = datetime.now(timezone(timedelta(hours=8))).isoformat()

    for num, fname in chapter_files:
        filepath = os.path.join(drafts_dir, fname)
        md_content = read_md(filepath)

        # 提取正文（去掉 # 标题标记）
        text = extract_text(md_content)

        # 统计字数
        word_count = count_words(text)

        # 提取标题
        title = extract_title(md_content)

        # 查找对应大纲信息
        outline_info = all_chapter_outlines.get(num, {})

        # 生成 txt 文件
        txt_filename = f"chapter_{num:03d}.txt"
        txt_path = os.path.join(chapters_dir, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        # 生成 json 元数据文件
        json_filename = f"chapter_{num:03d}.json"
        json_path = os.path.join(chapters_dir, json_filename)

        chapter_json = {
            "chapter_id": str(uuid.uuid4()),
            "chapter_number": num,
            "title": title,
            "word_count": word_count,
            "chapter_type": outline_info.get("chapter_type", "setup"),
            "target_words": 2500,
            "status": "finalized",
            "revision_count": 0,
            "generated_at": now_iso,
            "outline": {
                "goal": outline_info.get("goal", ""),
                "key_events": outline_info.get("key_events", []),
                "involved_characters": outline_info.get("involved_characters", []),
                "mood": outline_info.get("mood", "过渡/蓄力"),
                "chapter_summary": outline_info.get("chapter_summary", ""),
                "storyline_progress": outline_info.get("storyline_progress", ""),
            }
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(chapter_json, f, ensure_ascii=False, indent=2)

        results.append({
            "chapter_number": num,
            "title": title,
            "word_count": word_count,
            "txt_file": txt_filename,
            "json_file": json_filename,
        })

    return results


# ============================================================
# 构建 novel.json
# ============================================================

def build_novel_json(all_chapter_outlines):
    now_iso = datetime.now(timezone(timedelta(hours=8))).isoformat()

    characters = build_characters()
    world_setting = build_world_setting()
    outline = build_outline(all_chapter_outlines)
    volumes = build_volumes()

    novel = {
        "novel_id": "mengzhu-fitness-001",
        "title": "盟主穿越当健身教练",
        "genre": "都市",
        "theme": "穿越者如何在不需要自己的世界找到位置",
        "target_words": 500000,
        "style_name": "webnovel.shuangwen",
        "custom_style_reference": "第一人称、短句直给、不解释不煽情、极简对话、情绪靠身体反应不靠心理描写、冷幽默式荒诞",
        "outline": outline,
        "volumes": volumes,
        "world_setting": world_setting,
        "characters": characters,
        "status": "writing",
        "current_chapter": 53,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    return novel


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("盟主穿越当健身教练 — AI_novel 格式转换")
    print("=" * 60)

    # 创建输出目录结构
    chapters_dir = os.path.join(OUTPUT_DIR, "chapters")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(chapters_dir, exist_ok=True)
    print(f"\n[1] 创建输出目录: {OUTPUT_DIR}")
    print(f"    chapters/: {chapters_dir}")

    # 解析所有大纲
    print("\n[2] 解析章节大纲...")
    all_chapter_outlines = parse_outline_outlines([])
    print(f"    已解析 {len(all_chapter_outlines)} 章大纲 (编号 1-52)")

    # 处理章节文件
    print("\n[3] 转换章节文件 (md -> txt + json)...")
    results = process_chapter_files(all_chapter_outlines, chapters_dir)
    total_words = sum(r["word_count"] for r in results)
    print(f"    已转换 {len(results)} 个章节文件")
    print(f"    总字数: {total_words}")
    for r in results:
        print(f"    chapter_{r['chapter_number']:03d}: {r['title']} ({r['word_count']}字)")

    # 构建 novel.json
    print("\n[4] 构建 novel.json...")
    novel = build_novel_json(all_chapter_outlines)
    novel_json_path = os.path.join(OUTPUT_DIR, "novel.json")
    with open(novel_json_path, "w", encoding="utf-8") as f:
        json.dump(novel, f, ensure_ascii=False, indent=2)
    print(f"    保存: {novel_json_path}")
    print(f"    小说ID: {novel['novel_id']}")
    print(f"    角色: {len(novel['characters'])} 个")
    print(f"    章节大纲: {len(novel['outline']['chapters'])} 个 (含占位)")
    print(f"    卷: {len(novel['volumes'])} 卷")

    # 后处理：修正角色关系字段名以符合 AI_novel CharacterProfile 模型
    print("\n[5] 后处理：修正角色关系字段...")
    INTENSITY_MAP = {
        "师徒": 9, "暗恋": 7, "敌对": 9, "竞争": 6, "合作": 5,
        "背叛": 8, "利用": 4, "友好": 5, "崇拜": 7, "依赖": 6,
        "畏惧": 3, "亲属": 9, "暧昧": 6, "仇杀": 10, "陌生": 1,
    }
    for char in novel["characters"]:
        fixed_rels = []
        for rel in char.get("relationships", []):
            if "target" in rel:
                rel_type = rel.get("type", "合作")
                fixed_rels.append({
                    "target_character_id": rel["target"],
                    "current_type": rel_type,
                    "description": rel.get("description", ""),
                    "intensity": INTENSITY_MAP.get(rel_type, 5),
                    "history": []
                })
            else:
                # 已经是正确格式
                fixed_rels.append(rel)
        char["relationships"] = fixed_rels
    # 重新保存
    with open(novel_json_path, "w", encoding="utf-8") as f:
        json.dump(novel, f, ensure_ascii=False, indent=2)
    print(f"    已修正 {sum(len(c.get('relationships',[])) for c in novel['characters'])} 条关系记录")

    # 验证 JSON 格式
    print("\n[6] 验证 JSON 格式...")
    with open(novel_json_path, "r", encoding="utf-8") as f:
        json.load(f)  # 如果格式有问题会抛出异常
    print("    novel.json 格式验证通过")

    # 验证章节 JSON
    error_count = 0
    for r in results:
        json_path = os.path.join(chapters_dir, r["json_file"])
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"    ERROR: {r['json_file']} 格式错误: {e}")
            error_count += 1

    if error_count == 0:
        print(f"    所有 {len(results)} 个章节 JSON 格式验证通过")
    else:
        print(f"    {error_count} 个章节 JSON 格式错误!")

    print("\n" + "=" * 60)
    print("转换完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"  novel.json       — 根项目文件")
    print(f"  chapters/        — {len(results)} 个章节 (txt + json)")
    print("=" * 60)


if __name__ == "__main__":
    main()
