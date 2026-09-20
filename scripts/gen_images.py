#!/usr/bin/env python3
"""《云桌面 AI Agent「桌面记忆」方案》配图 — 浅色明亮商务风，纯 PIL 绘制，无 emoji。
内容依据 OUTLINE.md（产品经理导图逐字校订版），禁止引入导图外数字。
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
os.makedirs(OUT, exist_ok=True)

# ---- palette（浅色明亮商务）----
BG = (247, 249, 252)        # 浅灰白底
PANEL = (255, 255, 255)     # 卡片白
SOFT = (233, 239, 247)      # 浅蓝灰面板
LINE = (205, 216, 231)      # 边线
INK = (21, 38, 64)          # 深蓝墨
INK2 = (86, 105, 133)       # 次级文字
BLUE = (31, 90, 190)        # 主色
SKY = (104, 168, 240)       # 浅蓝
ORANGE = (232, 122, 54)     # 强调色（问题/警示）
RED = (203, 78, 78)         # 缺陷标记
GREEN = (43, 140, 100)      # 改造后

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def fb(size):
    return ImageFont.truetype(FONT_BOLD, size)


def fr(size):
    return ImageFont.truetype(FONT_REG, size)


def canvas(w, h):
    img = Image.new("RGB", (w, h), BG)
    return img, ImageDraw.Draw(img, "RGBA")


def card(d, box, rad=18, fill=PANEL, outline=LINE, width=2):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


def arrow(d, x1, y1, x2, y2, color=BLUE, w=4):
    d.line([x1, y1, x2, y2], fill=color, width=w)
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 16
    for s in (-1, 1):
        a = ang + math.pi + s * 0.45
        d.line([x2, y2, x2 + L * math.cos(a), y2 + L * math.sin(a)], fill=color, width=w)


def chip(d, cx, cy, text, fnt, fill=PANEL, outline=LINE, tcol=INK, padx=18, pady=10, width=2):
    tw = d.textlength(text, font=fnt)
    box = [cx - tw / 2 - padx, cy - (fnt.size // 2) - pady, cx + tw / 2 + padx, cy + (fnt.size // 2) + pady]
    d.rounded_rectangle(box, radius=(fnt.size // 2) + pady, fill=fill, outline=outline, width=width)
    d.text((cx, cy), text, font=fnt, fill=tcol, anchor="mm")
    return box


# =====================================================================
# 1. cover.png — 封面：桌面记忆概念图（浅色）
# =====================================================================
def cover():
    W, H = 1080, 1150
    img, d = canvas(W, H)
    cx, cy = W // 2, 430
    # 光晕
    for r, a in [(300, 16), (250, 22), (200, 30)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SKY + (a,))
    # 同心环
    for r, col, wdt in [(235, LINE, 2), (185, (150, 180, 220), 2), (135, BLUE, 3)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=wdt)
    # 中心节点
    d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=BLUE)
    d.text((cx, cy - 22), "桌面记忆", font=fb(42), fill=(255, 255, 255), anchor="mm")
    d.text((cx, cy + 30), "个人上下文", font=fb(28), fill=(214, 230, 250), anchor="mm")

    # 记忆条目（沿环分布）
    items = ["岗位", "工作边界", "写作偏好", "常用文档", "沟通对象", "桌面操作"]
    n = len(items)
    for i, it in enumerate(items):
        ang = -math.pi / 2 + i * (2 * math.pi / n)
        px = cx + 185 * math.cos(ang)
        py = cy + 185 * math.sin(ang)
        fillc = SOFT if i % 2 == 0 else PANEL
        chip(d, px, py, it, fr(25), fill=fillc + (250,), outline=(150, 180, 220), tcol=INK)
        # 连线到中心
        ix = cx + 92 * math.cos(ang)
        iy = cy + 92 * math.sin(ang)
        ox = px - 70 * math.cos(ang)
        oy = py - 26 * math.sin(ang)
        d.line([ix, iy, ox, oy], fill=(170, 195, 225), width=2)

    # 底部：三台显示器（文档/沟通/浏览）
    sw, sh, ys = 210, 132, 830
    xs = [90, 435, 780]
    labels = ["文档", "沟通", "浏览"]
    for i, x in enumerate(xs):
        card(d, [x, ys, x + sw, ys + sh], 14, fill=PANEL, outline=LINE, width=2)
        d.rectangle([x + 12, ys + 12, x + sw - 12, ys + 40], fill=SOFT)
        for r in range(3):
            d.rounded_rectangle([x + 16, ys + 54 + r * 24, x + sw - 26 - (r % 3) * 45, ys + 54 + r * 24 + 11],
                                5, fill=(214, 226, 242))
        d.rectangle([x + sw // 2 - 12, ys + sh, x + sw // 2 + 12, ys + sh + 16], fill=LINE)
        d.rectangle([x + sw // 2 - 45, ys + sh + 16, x + sw // 2 + 45, ys + sh + 22], fill=LINE)
        d.text((x + 12 + (sw - 24) / 2, ys + 26), labels[i], font=fr(20), fill=INK2, anchor="mm")
        # 上行数据流
        sx = x + sw // 2
        for k in range(14):
            t = k / 13
            px = sx + (cx - sx) * t + math.sin(t * 4.5) * 30 * math.sin(t * math.pi)
            py = ys - 8 + (cy + 130 - ys) * t
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=SKY + (int(190 * (1 - t * 0.35)),))

    chip(d, W // 2, H - 56, "VDI 云桌面 · 本地闭环", fb(24), fill=SOFT, outline=BLUE, tcol=BLUE, padx=26)
    img = img.filter(ImageFilter.GaussianBlur(0.3))
    img.save(os.path.join(OUT, "cover.png"))
    print("cover.png", img.size)


# =====================================================================
# 2. split.png — P2：对话框记忆 vs 桌面记忆的割裂
# =====================================================================
def split():
    W, H = 1150, 640
    img, d = canvas(W, H)
    # 左：Agent 只知道对话框
    card(d, [60, 120, 480, 470], 20)
    d.text((270, 170), "Agent 的记忆范围", font=fb(28), fill=INK, anchor="mm")
    card(d, [100, 210, 440, 300], 14, fill=SOFT, outline=BLUE, width=2)
    d.text((270, 236), "对话框", font=fb(26), fill=BLUE, anchor="mm")
    d.text((270, 272), "你说过的每一句话", font=fr(21), fill=INK2, anchor="mm")
    card(d, [100, 320, 440, 430], 14, fill=(250, 240, 238), outline=(226, 170, 160), width=2)
    d.text((270, 348), "桌面", font=fb(26), fill=RED, anchor="mm")
    d.text((270, 384), "看过哪些文件、和谁协作——", font=fr(21), fill=INK2, anchor="mm")
    d.text((270, 410), "一概不知", font=fb(21), fill=RED, anchor="mm")
    # 右：桌面发生的事
    card(d, [670, 120, 1090, 470], 20)
    d.text((880, 170), "用户的真实办公", font=fb(28), fill=INK, anchor="mm")
    rows = ["昨天张三发来的 PPT", "昨天输出的需求文档格式", "岗位：云桌面产品经理", "文档习惯与常用词"]
    for i, r in enumerate(rows):
        yy = 220 + i * 62
        card(d, [710, yy, 1050, yy + 46], 10, fill=SOFT, outline=(150, 180, 220), width=1)
        d.text((730, yy + 23), r, font=fr(22), fill=INK, anchor="lm")
    # 中间断层
    d.line([500, 295, 645, 295], fill=RED, width=6)
    for qx, qy, fs in [(572, 258, 40), (540, 320, 26), (606, 330, 22)]:
        d.text((qx, qy), "?", font=fb(fs), fill=RED, anchor="mm")
    d.text((572, 392), "记忆断层", font=fb(26), fill=RED, anchor="mm")
    d.text((572, 430), "Agent 与你的记忆不一致", font=fr(20), fill=INK2, anchor="mm")
    # 顶部雨点问句
    qs = [("昨天的文档什么格式？", 200), ("张三在哪发的 PPT？", 575), ("这个名词什么意思？", 950)]
    for t, x in qs:
        chip(d, x, 60, t, fr(21), fill=PANEL, outline=(226, 170, 160), tcol=RED)
    img.save(os.path.join(OUT, "split.png"))
    print("split.png", img.size)


# =====================================================================
# 3. gacha.png — P3：抽卡比喻（浅色版）
# =====================================================================
def gacha():
    W, H = 1150, 620
    img, d = canvas(W, H)
    cx = W // 2
    # 机器
    card(d, [cx - 150, 110, cx + 150, 470], 26, fill=PANEL, outline=LINE, width=3)
    # 玻璃球
    d.ellipse([cx - 116, 140, cx + 116, 372], fill=SOFT, outline=SKY, width=3)
    balls = [(cx - 55, 250), (cx + 45, 228), (cx - 5, 300), (cx + 62, 305), (cx - 68, 312)]
    for bx, by in balls:
        d.ellipse([bx - 30, by - 30, bx + 30, by + 30], fill=PANEL, outline=(150, 180, 220), width=2)
        d.text((bx, by), "?", font=fb(28), fill=BLUE, anchor="mm")
    # 出卡口
    card(d, [cx - 48, 390, cx + 48, 470], 12, fill=SOFT, outline=LINE, width=2)
    d.text((cx, 415), "输出", font=fr(20), fill=INK2, anchor="mm")
    d.text((cx, 448), "▼", font=fr(20), fill=INK2, anchor="mm")
    d.text((cx, 545), "不「懂你」的 Agent，输出只能靠抽卡", font=fb(30), fill=INK, anchor="mm")
    # 左右标注
    card(d, [80, 190, 400, 300], 16, fill=PANEL, outline=LINE, width=2)
    d.text((240, 226), "很多提示词", font=fb(26), fill=INK, anchor="mm")
    d.text((240, 266), "也拦不住随机性", font=fr(21), fill=INK2, anchor="mm")
    arrow(d, 406, 245, cx - 158, 250, INK2, 3)
    card(d, [750, 190, 1070, 300], 16, fill=PANEL, outline=LINE, width=2)
    d.text((910, 226), "输出看运气", font=fb(26), fill=INK, anchor="mm")
    d.text((910, 266), "成功率时高时低", font=fr(21), fill=INK2, anchor="mm")
    arrow(d, cx + 158, 250, 744, 245, INK2, 3)
    img.save(os.path.join(OUT, "gacha.png"))
    print("gacha.png", img.size)


# =====================================================================
# 4. flow3.png — P4：三步流程（桌面记录→形成记忆→形成个人上下文）
# =====================================================================
def flow3():
    W, H = 1180, 1080
    img, d = canvas(W, H)
    d.text((W // 2, 52), "一套桌面操作数据 · 两种增强产出", font=fb(32), fill=INK, anchor="mm")
    # 顶部：VDI 桌面
    card(d, [W // 2 - 320, 100, W // 2 + 320, 208], 18, fill=SOFT, outline=BLUE, width=3)
    d.text((W // 2, 136), "VDI 云桌面 · 用户正常办公", font=fb(30), fill=INK, anchor="mm")
    d.text((W // 2, 180), "启用桌面记忆，采集桌面中的操作信息", font=fr(22), fill=INK2, anchor="mm")
    arrow(d, W // 2, 212, W // 2, 296, BLUE, 5)
    d.text((W // 2 + 108, 254), "滚动记录", font=fr(22), fill=INK2, anchor="lm")
    # 中部：桌面记录数据库
    card(d, [W // 2 - 250, 302, W // 2 + 250, 420], 18, fill=PANEL, outline=BLUE, width=3)
    chip(d, W // 2 - 158, 316, "① 桌面记录", fb(20), fill=BLUE, outline=BLUE, tcol=(255, 255, 255), pady=7)
    d.text((W // 2, 358), "桌面操作信息 · 数据库记录", font=fb(30), fill=INK, anchor="mm")
    d.text((W // 2, 400), "文件往来 · 沟通对象 · 文档习惯 · 操作轨迹", font=fr(22), fill=INK2, anchor="mm")
    # 分叉
    arrow(d, W // 2 - 252, 348, 300, 500, BLUE, 4)
    arrow(d, W // 2 + 252, 348, 880, 500, BLUE, 4)
    # 左产出：形成记忆
    card(d, [70, 506, 530, 742], 20, fill=PANEL, outline=BLUE, width=3)
    chip(d, 300, 556, "② 形成记忆", fb(26), fill=BLUE, outline=BLUE, tcol=(255, 255, 255))
    d.text((300, 620), "数据可被用户的 Agent 调用", font=fb(25), fill=INK, anchor="mm")
    d.text((300, 660), "Agent 具备桌面中的「记忆」", font=fr(23), fill=INK, anchor="mm")
    d.text((300, 700), "桌面里发生的事，Agent 知道", font=fr(23), fill=INK2, anchor="mm")
    # 右产出：形成个人上下文
    card(d, [650, 506, 1110, 742], 20, fill=PANEL, outline=BLUE, width=3)
    chip(d, 880, 556, "③ 形成个人上下文", fb(26), fill=BLUE, outline=BLUE, tcol=(255, 255, 255))
    d.text((880, 620), "借助模型能力整理为用户上下文", font=fb(25), fill=INK, anchor="mm")
    d.text((880, 664), "当前用户的岗位 · 工作边界", font=fr(23), fill=INK, anchor="mm")
    d.text((880, 700), "写作偏好", font=fr(23), fill=INK2, anchor="mm")
    # 底部价值条
    card(d, [70, 800, 1110, 920], 18, fill=SOFT, outline=BLUE, width=2)
    d.text((590, 846), "Agent 回答成功率大幅提升（不再「抽卡」）", font=fb(27), fill=INK, anchor="mm")
    d.text((590, 890), "模糊指令也可达成目标", font=fb(27), fill=BLUE, anchor="mm")
    d.text((W // 2, 990), "全程在云桌面内完成 · 数据不出域", font=fr(24), fill=INK2, anchor="mm")
    img.save(os.path.join(OUT, "flow3.png"))
    print("flow3.png", img.size)


# =====================================================================
# 5. cases.png — B1 分支页：两个案例「现在 vs 改造后」
# =====================================================================
def cases():
    W, H = 1180, 1120
    img, d = canvas(W, H)
    # 案例一
    card(d, [50, 60, 1130, 520], 22, fill=PANEL, outline=LINE, width=2)
    d.text((90, 118), "案例一 · 提示词很详细，输出仍然较差", font=fb(29), fill=INK, anchor="lm")
    chip(d, 950, 118, "问题 1", fb(22), fill=(250, 240, 238), outline=(226, 170, 160), tcol=RED)
    card(d, [90, 160, 1090, 240], 12, fill=SOFT, outline=LINE, width=1)
    d.text((110, 200), "「写一个 VDI 需求文档，针对 xx 客户提出的 xxx 移动端的问题」（描述得很详细）",
           font=fr(22), fill=INK, anchor="lm")
    # 现在列
    d.text((300, 286), "现在", font=fb(24), fill=RED, anchor="mm")
    now1 = ["内容比较空", "专业名词理解偏差", "格式不是想要的", "超出工作边界"]
    for i, t in enumerate(now1):
        yy = 318 + i * 46
        card(d, [100, yy, 500, yy + 36], 8, fill=(250, 240, 238), outline=(226, 170, 160), width=1)
        d.text((120, yy + 18), "✗ " + t, font=fr(21), fill=RED, anchor="lm")
    # 改造后列
    d.text((860, 286), "改造后", font=fb(24), fill=GREEN, anchor="mm")
    aft1 = ["知道你的岗位与项目背景", "按你的文档格式习惯输出", "名词对齐你的常用词", "守住你的工作边界"]
    for i, t in enumerate(aft1):
        yy = 318 + i * 46
        card(d, [620, yy, 1090, yy + 36], 8, fill=(236, 246, 240), outline=(150, 200, 175), width=1)
        d.text((640, yy + 18), "✓ " + t, font=fr(21), fill=GREEN, anchor="lm")
    d.text((590, 420), "→", font=fb(34), fill=BLUE, anchor="mm")

    # 案例二
    card(d, [50, 560, 1130, 1060], 22, fill=PANEL, outline=LINE, width=2)
    d.text((90, 618), "案例二 · 模糊指令，直接达成", font=fb(29), fill=INK, anchor="lm")
    chip(d, 950, 618, "问题 2", fb(22), fill=(250, 240, 238), outline=(226, 170, 160), tcol=RED)
    card(d, [90, 660, 1090, 762], 12, fill=SOFT, outline=LINE, width=1)
    d.text((110, 694), "「昨天张三发了我一个 PPT，名字好像是“什么什么 云桌面 xx 方案”，", font=fr(22), fill=INK, anchor="lm")
    d.text((110, 730), "请使用这个数据帮我生成一份需求文档，就按照我昨天输出的那个需求文档格式来」", font=fr(22), fill=INK, anchor="lm")
    d.text((300, 806), "现在", font=fb(24), fill=RED, anchor="mm")
    now2 = ["昨天的需求文档是什么格式？", "昨天张三是在哪里发的这个 PPT？"]
    for i, t in enumerate(now2):
        yy = 838 + i * 46
        card(d, [100, yy, 560, yy + 36], 8, fill=(250, 240, 238), outline=(226, 170, 160), width=1)
        d.text((120, yy + 18), "? " + t, font=fr(21), fill=RED, anchor="lm")
    d.text((860, 806), "改造后", font=fb(24), fill=GREEN, anchor="mm")
    aft2 = ["从桌面记忆定位：张三 · 昨天 · PPT", "对齐你昨天的需求文档格式直接生成"]
    for i, t in enumerate(aft2):
        yy = 838 + i * 46
        card(d, [620, yy, 1090, yy + 36], 8, fill=(236, 246, 240), outline=(150, 200, 175), width=1)
        d.text((640, yy + 18), "✓ " + t, font=fr(21), fill=GREEN, anchor="lm")
    d.text((590, 940), "→", font=fb(34), fill=BLUE, anchor="mm")
    d.text((W // 2, 1085), "Agent 具备和你一样的桌面记忆 · 模糊指令也可达成", font=fb(25), fill=BLUE, anchor="mm")
    img.save(os.path.join(OUT, "cases.png"))
    print("cases.png", img.size)


# =====================================================================
# 6. custom.png — P6：自定义功能举例卡片图
# =====================================================================
def custom():
    W, H = 1150, 620
    img, d = canvas(W, H)
    # 两条来源路径
    card(d, [70, 90, 540, 210], 16, fill=PANEL, outline=BLUE, width=2)
    d.text((305, 132), "用户二次开发", font=fb(27), fill=INK, anchor="mm")
    d.text((305, 174), "使用自然语言即可", font=fr(22), fill=INK2, anchor="mm")
    card(d, [610, 90, 1080, 210], 16, fill=PANEL, outline=BLUE, width=2)
    d.text((845, 132), "管理员统一下发", font=fb(27), fill=INK, anchor="mm")
    d.text((845, 174), "应用方式由管理员配置", font=fr(22), fill=INK2, anchor="mm")
    arrow(d, 305, 216, 400, 300, BLUE, 4)
    arrow(d, 845, 216, 750, 300, BLUE, 4)
    # 中间枢纽
    card(d, [370, 306, 780, 400], 18, fill=SOFT, outline=BLUE, width=3)
    d.text((575, 352), "桌面记忆 · 二次开发", font=fb(28), fill=INK, anchor="mm")
    # 三个举例卡
    exs = [("识别提效点", "识别工作过程中", "可以通过 AI 提效的点"), ("生成日报 / 周报", "按你的格式与口径", "自动整理成稿"),
           ("生成待办事项", "从桌面工作轨迹中", "提取待办与提醒")]
    for i, (t, l1, l2) in enumerate(exs):
        x = 70 + i * 370
        card(d, [x, 460, x + 330, 590], 18, fill=PANEL, outline=LINE, width=2)
        chip(d, x + 165, 502, t, fb(24), fill=SOFT, outline=(150, 180, 220), tcol=BLUE, pady=8)
        d.text((x + 165, 550), l1, font=fr(21), fill=INK2, anchor="mm")
        d.text((x + 165, 578), l2, font=fr(21), fill=INK2, anchor="mm")
        arrow(d, 575, 404, x + 165, 454, BLUE, 3)
    img.save(os.path.join(OUT, "custom.png"))
    print("custom.png", img.size)


# =====================================================================
# 7. value.png — P7：价值总结四象限
# =====================================================================
def value():
    W, H = 1180, 900
    img, d = canvas(W, H)
    cards = [
        ("数据属于企业", "企业新上的 Agent、更换 Agent、多 Agent 并存，都即刻获得个人上下文", "更换 Agent，个人上下文不丢", True),
        ("提升 Agent 成功率", "Agent 更懂用户是谁、用户偏好、工作边界", "输出符合个性化要求", False),
        ("模糊指令也可达成", "桌面级记忆，上下文不局限于对话框", "说清目标即可，不必描述路径", False),
        ("更多自定义功能", "识别可 AI 提效的任务 · 生成日报 / 周报 · 生成待办事项", "能力持续生长", False),
    ]
    for i, (t, s1, s2, hl) in enumerate(cards):
        x = 60 + (i % 2) * 545
        y = 70 + (i // 2) * 380
        card(d, [x, y, x + 520, y + 350], 22, fill=SOFT if hl else PANEL, outline=BLUE if hl else LINE, width=3 if hl else 2)
        chip(d, x + 66, y + 62, f"{i+1}", fb(26), fill=BLUE, outline=BLUE, tcol=(255, 255, 255), padx=14)
        d.text((x + 110, y + 62), t, font=fb(31), fill=INK, anchor="lm")
        # 手动换行：把 s1 按 ~22 字切
        seg, lines, cur = s1, [], ""
        for chn in seg:
            cur += chn
            if len(cur) >= 21:
                lines.append(cur)
                cur = ""
        if cur:
            lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            d.text((x + 40, y + 130 + j * 40), ln, font=fr(24), fill=INK2, anchor="lm")
        d.text((x + 40, y + 236), s2, font=fb(25), fill=BLUE, anchor="lm")
        if hl:
            chip(d, x + 300, y + 298, "重点", fb(20), fill=BLUE, outline=BLUE, tcol=(255, 255, 255), padx=14, pady=6)
    img.save(os.path.join(OUT, "value.png"))
    print("value.png", img.size)


if __name__ == "__main__":
    cover()
    split()
    gacha()
    flow3()
    cases()
    custom()
    value()
    print("ALL DONE ->", OUT)
