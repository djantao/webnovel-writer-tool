#!/usr/bin/env python3
"""Chapter generation via external API. Supports batch generation.

Usage:
  python generate_chapter.py 5                          # Single chapter
  python generate_chapter.py 5-14                       # Batch chapters 5-14
  python generate_chapter.py 5 --model deepseek-chat    # Specific model
"""

import json, sys, os, argparse
from openai import OpenAI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

PROVIDERS = {
    "deepseek": {
        "api_base": "https://api.deepseek.com/v1",
        "api_key": "",
    }
}

CHAPTER_OUTLINES = {
    5: {
        "title": "地宫之门",
        "context": "萧寒追到地宫入口，假助手正逼小雀以血开门。地宫「认血不认人」。萧寒与假助手战斗。",
        "outline": """写第5章「地宫之门」(约3000字)。

开场：萧寒跑到地宫入口。看清地宫是一整块沙岩被切开，门上刻满暗红纹路，和骨片裂纹一样。门缝渗出千年陈气。

假助手站在门前按着小雀肩膀，割破她手指涂血开门。小雀血渗进纹路——亮了但很快暗了。不够。假助手发出气音：「不对……不是你……还有一个人……」

萧寒出手。假助手脸上是铁老助手长相但眼睛不会转。萧寒挥刀砍进去没有血只有黑烟。他用骨片挡住假助手手指，暗红纹路蔓延过去，假助手手指被烫缩回。

小雀：「哥，门在叫我。」萧寒把手掌按在门纹上——骨片狂跳，门纹全亮。地宫认的是骨印不是血。

门开。千年尘埃涌出。门内是大殿。

假助手发出尖啸叫天玄宗的人。萧寒拉小雀冲进门内，门缓缓合上。最后一刻从门缝看到远处沙丘线十几道人影。""",
    },
    6: {
        "title": "荒殿回响",
        "context": "萧寒和小雀进入地宫。寻找荒血传承和萧无极遗言。",
        "outline": """写第6章「荒殿回响」(约3000字)。

开场：地宫内。柱子被灵刃削断，断面残留千年灵力。地上散落战斗姿态骸骨。正面墙壁刻满手指写的字：「荒殿第三百七十代守殿人留书。后来者，你若身怀荒血——跪。」

萧寒跪下，骨片一烫，墙上字亮暗红光。刻字讲述荒殿最后时刻——灵修联盟围攻，弟子战至最后。守殿人将完整修炼法门上墙：炼皮→淬骨→换血→开窍→凝魂→荒古圣体。

角落找到与骨片共鸣的骸骨——萧无极。手边玉简留给后来者，提到萧母是他妹妹。

小雀盯着墙上字——看得懂字之间「空隙」里的内容，那是写给血种看的。

结尾：萧寒得到完整传承。地宫深处传来震动——天玄宗在破门。""",
    },
    7: {
        "title": "血种",
        "context": "天玄宗破门。萧寒带小雀逃离。小雀血种觉醒。",
        "outline": """写第7章「血种」(约3000字)。

开场：地宫震动碎石掉落。萧寒拉小雀往后方跑，但小雀不走，盯着墙念话——不是念，是被人借着嘴说话：「地宫不是关着的，是守着的。」

她脉搏太快像鸟的心跳。瞳孔有暗红芒——看到字句间还有字：荒殿不是被屠灭的，是主动放弃的。灵修联盟攻进来时人已撤空。

萧寒震惊。

大殿后墙翻转露出向下通道。壁上刻字越走越新，到最后是萧母手迹：「如果你是我肚子里的孩子——往前走。如果不是——滚。」

小雀血种初步觉醒——能看见荒血残留的信息记忆。

结尾断章：秘道尽头有风声。但身后破门声停了——不是天玄宗放弃，是他们进来了。""",
    },
    8: {
        "title": "沙下",
        "context": "萧寒带小雀从秘道逃出地宫，决定赴约霍七。小雀状态异常。",
        "outline": """写第8章「沙下」(约3000字)。

开场：秘道很长，空气变湿地底凉。小雀安静得不正常——在听什么。身后通道传来声音——地宫在塌，天玄宗触动了机关。

秘道尽头石门一行字：「用自己的血就能开。」萧寒割手按上去，门开。出口在沙坑底部，已经走出三四里。

小雀蹲在沙坑角落用手指在地上画东西——画的是一扇门。不是地宫的门是另一扇。「哥，门后面还有人。」

萧寒决定去黑风口赴约霍七。还没走到就看到远处沙丘上站着一个人——霍七在等他们。""",
    },
    9: {
        "title": "黑风口之约",
        "context": "萧寒带小雀到黑风口。霍七教萧寒荒血实战。天玄宗灵材车队将至。",
        "outline": """写第9章「黑风口之约」(约3000字)。

开场：霍七站在沙丘上，看萧寒带小雀来：「这丫头不对劲。」

训练：霍七把萧寒带到沙窝低地，要他荒血对打。萧寒第一次主动用荒血战斗——动作笨拙释放断断续续。霍七用弯刀逼他在压力下学会释放。荒血需要用「念头」引——想着掌心里有一团火血就过去了。荒血最大优势是「隐」——灵力波动能被探测，荒血不能。

小雀在边上用手指在沙子画东西，霍七看到脸色变了——认出那是荒殿图腾。

傍晚探子来报——天玄宗灵材车从北边来。霍七：「练了一下午，试试真家伙？」

萧寒+霍七设伏。萧寒第一次荒血实战——藏气息接近成功放倒三品灵修。霍七对付领队。

结尾反转：劫车成功，但车厢里装的是石头——空的。诱饵。远处火光一盏接一盏亮起——包围圈。""",
    },
    10: {
        "title": "包围",
        "context": "灵材车是诱饵。天玄宗包围圈已形成。三人被困。",
        "outline": """写第10章「包围」(约3000字)。

开场：火光连成一条线——每隔五十步一盏灵灯从东到西连了三四里。天玄宗用围猎阵势。

霍七判断：包围圈半圆，留西边缺口——但西边是流沙区。「他在赶我们往死路上走。」

小雀开口指着西边：「那边能走。沙子下面有路。」萧寒信她。三人往西走。天玄宗不急着收拢——像是知道西边是死路。

流沙区边缘追兵到——七品灵修，搜风部副统领。认出萧寒。萧寒用刚学技巧交手——差距大只能自保。霍七偷袭打断节奏，三人趁乱冲进流沙区。

小雀带路——她看得到沙子下面的石板路，荒殿铺的。

结尾：走过流沙区，天玄宗没追——领队站在边缘嘴角动了一下。那是猎物按计划走进陷阱的表情。""",
    },
    11: {
        "title": "荒路",
        "context": "三人穿过流沙区发现荒殿古道。小雀持续异变。",
        "outline": """写第11章「荒路」(约3000字)。

开场：流沙区后地形变成沙砾平原硬土层。每隔几十步有凸起石板排成线——霍七认出是荒殿驿道。他爷爷说千年前漠北有绿洲，灵修联盟屠灭荒殿后用灵术改变气候把绿洲变沙漠。

三人沿古道走看到废墟。萧寒想到荒殿是主动撤走的——人撤到哪里去了？

小雀在衣服边缘画东西——从荒殿图腾变成另一种符号。萧寒认出那是「荒血不灭」。

「他们在叫我们。」

结尾：古道尽头出现建筑轮廓——立着的，塌了一半但主体还在。霍七：「这是荒殿前哨。」小雀：「哥，有人在里面等我们。」""",
    },
    12: {
        "title": "前哨",
        "context": "三人到达荒殿前哨站。有活物在等他们。天玄宗绕过流沙区逼近。",
        "outline": """写第12章「前哨」(约3000字)。

开场：前哨站大门敞着像在等人。正厅地上坐着一具骸骨——老死的。墙上挂着漠北全图：有红线从地宫连到前哨站再往西到「荒殿」。

一只背有暗红纹路的沙蜥绕萧寒脚转一圈，带路到地下密室——有修炼药材灵材和一封信。信说淬骨需要大量气血之力，天玄宗灵材能转化。劫车不是霍七主意——是荒殿计划。

小雀越来越安静，手指在空中划——像跟着谁学写字。

结尾：萧寒获得修炼资源。霍七喊天玄宗追兵到了——不止搜风部，还有穿白袍的。萧母遗物里有一幅画画着穿白袍的人。""",
    },
    13: {
        "title": "淬骨",
        "context": "天玄宗追兵到，白袍神秘人出现。萧寒必须在战斗中淬骨突破。",
        "outline": """写第13章「淬骨」(约3500字)。

开场：白袍人站在最前面打量前哨站。萧寒从哨塔看他——骨片缩了一下。不是跳，是缩。

天玄宗三路包抄。萧寒到地下密室服用灵材冲击淬骨。

淬骨过程：服下灵材引导荒血运转。骨头裂开重组再裂开——疼到咬自己手背。但听到地面战斗声——霍七在一个人扛。

淬骨成功。骨片和掌骨融为一体。萧寒能感觉到自己每一根骨头。

重返战场：对上七品领队——之前只能自保，现在一拳打碎灵盾。领队后退三步。

结尾反转断章：萧寒正要追击——白袍人一步出现在面前，手按在他肩上。荒血遇到白袍人像水遇烧红的铁——蒸发了。白袍人：「你娘没告诉过你——荒血不是无敌的吗。」""",
    },
    14: {
        "title": "旧识",
        "context": "白袍人一招压制萧寒。他认识萧母，是天道观的人。",
        "outline": """写第14章「旧识」(约3500字)。

开场：白袍人手按萧寒肩上，萧寒动不了。不是灵力压制是更高规则——荒血像被冻住。第一次遇到能直接克制荒血的东西。

白袍人摘兜帽——中年，瞳孔淡金色。「你长得像你娘。」他叫陆沉，天道观的人。千年前荒殿和天道观有约定——荒血对他「不设防」是契约。他带来萧母留给萧寒的玉简。

小雀走出来看到陆沉——瞳孔暗红大盛。陆沉皱眉：「血种觉醒这么深了？」

玉简里是萧母的话：荒殿不是被灭的是主动撤走的，因为殿主「看到了什么」。荒血传承者留在漠北是为了守一个东西——不是地宫，是地宫下面的东西。

结尾断章：陆沉突然看向远处——天玄宗大批援军到，领头八品灵修。陆沉：「你娘留给你的任务不是让你死的。自己选——跟我走，或者自己活过今晚。」""",
    },
}


def load_config(args):
    cfg_path = os.path.join(SCRIPT_DIR, "api_config.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if args.provider:
        if args.provider not in PROVIDERS:
            print(f"未知 provider: {args.provider}. 可用: {list(PROVIDERS.keys())}")
            sys.exit(1)
        prov = PROVIDERS[args.provider]
        cfg["api_base"] = prov["api_base"]
        cfg["api_key"] = prov["api_key"]
    if args.model:
        cfg["model"] = args.model
    key = cfg["api_key"]
    if key.startswith("$"):
        cfg["api_key"] = os.environ.get(key[1:], key)
    return cfg


def load_file(rel_path):
    path = os.path.join(PROJECT_DIR, rel_path)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_chapter_range(arg):
    arg = arg.strip()
    if "-" in arg:
        parts = arg.split("-")
        return int(parts[0]), int(parts[1])
    return int(arg), int(arg)


def build_prompt(chapter_num, outline_info):
    memory = load_file("memory/novel-memory.md")
    prev_content = ""
    for c in range(chapter_num - 1, max(0, chapter_num - 4), -1):
        pc = load_file(f"chapters/chapter-{c:02d}.md")
        if pc:
            prev_content = pc
            break
    chapters_summary = []
    for c in range(max(1, chapter_num - 5), chapter_num):
        pc = load_file(f"chapters/chapter-{c:02d}.md")
        if pc:
            title = f"第{c}章"
            for line in pc.strip().split("\n"):
                if line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break
            tail = pc.strip()[-200:] if len(pc) > 200 else pc
            chapters_summary.append(f"第{c}章「{title}」: ...{tail[:100]}...")
    earlier = ("## 前情提要\n" + "\n".join(chapters_summary[-4:])) if chapters_summary else ""

    system_prompt = f"""你是专业网文写手，创作玄幻小说《风起漠北》。这是第{chapter_num}章「{outline_info['title']}」。

## 上下文背景
{outline_info['context']}

## 硬约束
1. 开头承接上一章结尾——不能凭空开始
2. 每500字至少2处非视觉感官描写（听觉、嗅觉、触觉、味觉）
3. 连续3句不能出现相同句式结构。禁止排比式并列
4. 每段对话必须有潜台词
5. 重大事件后必须用至少2句写主角情绪反应
6. "然而""与此同时""不仅如此""总之"不用或极少用
7. 情绪用身体反应写，不写"他很愤怒"
8. 章尾必须断章/升级/反转，禁用总结句

## 世界观速查
- 灵脉分九品天生不可改。漠北人天生灵脉残缺
- 荒血：古老修炼体系（炼皮→淬骨→换血→开窍→凝魂→荒古圣体）。荒血克制灵力
- 千年前灵修联盟屠灭荒殿。天玄宗追杀荒血者
- 萧寒：零品灵脉，荒血初醒（骨片融入骨髓可碎灵刃感知灵力反制灵力）。第13章淬骨成功
- 萧小雀：「血种」共生者，可感知荒血残留信息
- 霍七：血沙匪头目，被萧寒荒血反震后成为盟友
- 天玄宗搜风部：正在追杀。罗盘核心被毁精度下降
- 天道观：千年前与荒殿有约定。陆沉已出场

## 记忆上下文
{memory[:1500]}

{earlier}

## 上一章结尾
{prev_content[-800:] if prev_content else ''}

## 本章大纲（必须严格遵循）
{outline_info['outline']}"""

    user_prompt = f"""按以上大纲写第{chapter_num}章「{outline_info['title']}」。

要求：
- 字数目标：约3000字
- 只输出正文，不要额外说明
- 对话用「」引号
- 节奏快，不拖泥带水
- 开头直接进入剧情，不要环境描写铺垫
- 结尾必须是推法"""

    return system_prompt, user_prompt


def call_api(system_prompt, user_prompt, config, retries=5):
    client = OpenAI(
        base_url=config["api_base"],
        api_key=config["api_key"],
        timeout=180.0
    )
    extra_body = {}
    if "thinking" in config:
        extra_body["chat_template_kwargs"] = {"thinking": config["thinking"]}
    print(f"  Provider: {config['api_base']}")
    print(f"  模型: {config['model']}")
    print(f"  Prompt: {len(system_prompt)+len(user_prompt)} 字符")
    for attempt in range(retries):
        try:
            kwargs = {
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": config.get("temperature", 0.85),
                "max_tokens": config.get("max_tokens", 8192),
                "stream": False
            }
            if "top_p" in config:
                kwargs["top_p"] = config["top_p"]
            if extra_body:
                kwargs["extra_body"] = extra_body
            completion = client.chat.completions.create(**kwargs)
            content = completion.choices[0].message.content
            usage = completion.usage
            print(f"  Token: {usage.prompt_tokens}→{usage.completion_tokens}")
            return content
        except Exception as e:
            err_str = str(e)
            wait = 3
            if "429" in err_str:
                wait = (attempt + 1) * 15
                print(f"  限流，等待{wait}秒...")
            elif "connection" in err_str.lower():
                wait = (attempt + 1) * 5
                print(f"  连接失败，等待{wait}秒...")
            else:
                print(f"  错误: {err_str[:100]}...")
            if attempt < retries - 1:
                import time
                time.sleep(wait)
            else:
                raise


def main():
    parser = argparse.ArgumentParser(description="Generate novel chapter via API")
    parser.add_argument("chapter", type=str, help="Chapter number or range (e.g. 5 or 5-14)")
    parser.add_argument("--model", type=str, help="Model name override")
    parser.add_argument("--provider", type=str, choices=["deepseek"], help="API provider")
    args = parser.parse_args()
    config = load_config(args)
    start_ch, end_ch = parse_chapter_range(args.chapter)

    for chapter_num in range(start_ch, end_ch + 1):
        if chapter_num not in CHAPTER_OUTLINES:
            print(f"\n跳过第{chapter_num}章：无大纲")
            continue
        info = CHAPTER_OUTLINES[chapter_num]
        if info.get("note") == "skip":
            print(f"\n跳过第{chapter_num}章")
            continue
        path = os.path.join(PROJECT_DIR, "chapters", f"chapter-{chapter_num:02d}.md")
        if os.path.exists(path):
            print(f"\n覆盖: {path}")
        print(f"\n=== 第{chapter_num}章「{info['title']}」 ===")
        system_prompt, user_prompt = build_prompt(chapter_num, info)
        content = call_api(system_prompt, user_prompt, config)
        if not content:
            print("  失败，跳过")
            continue
        if not content.strip().startswith("#"):
            content = f"# 第 {chapter_num} 章\n\n" + content
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        cn = sum(1 for c in content if '一' <= c <= '鿿')
        total_cn = sum(
            sum(1 for c in (load_file(f"chapters/chapter-{n:02d}.md") or '') if '一' <= c <= '鿿')
            for n in range(1, chapter_num)
        )
        print(f"  保存 | 中文字数: {cn} | 累计: {total_cn + cn}")

    print(f"\n=== 完成！章节 {start_ch}-{end_ch} ===")


if __name__ == "__main__":
    main()