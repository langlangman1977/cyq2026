#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中联永信企业宣传视频 — 电影级字幕效果
逐词高亮 · 底部居中 · 暗色渐变底条 · 同步 TTS
"""
import os, sys, codecs, textwrap, asyncio, subprocess, re
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
os.environ["FFMPEG_BINARY"] = imageio_ffmpeg.get_ffmpeg_exe()
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
import edge_tts

VIDEO_DIR  = r"C:\Users\Administrator\Videos\中联永信"
FRAME_DIR  = os.path.join(VIDEO_DIR, "frames")
WORK_DIR   = os.path.join(FRAME_DIR, "work")
for d in [VIDEO_DIR, FRAME_DIR, WORK_DIR]: os.makedirs(d, exist_ok=True)

W, H = 1920, 1080
FPS = 24

# ── 色彩 ──
BG    = (8, 13, 26)
GOLD  = (212, 175, 55)
WARM  = (255, 220, 50)
WHITE = (240, 242, 248)
GREY  = (140, 150, 170)
DIM   = (80, 90, 110)

# ── 字体 ──
FONT_REG  = None; FONT_BOLD = None; FONT_LIGHT = None
def load_fonts():
    global FONT_REG, FONT_BOLD, FONT_LIGHT
    base = "C:/Windows/Fonts"
    for ttf in [f"{base}/msyh.ttc", f"{base}/simhei.ttf", f"{base}/simsun.ttc"]:
        if os.path.exists(ttf):
            FONT_REG   = ImageFont.truetype(ttf, 44)
            FONT_BOLD  = ImageFont.truetype(ttf, 52)
            FONT_LIGHT = ImageFont.truetype(ttf, 36)
            return
    FONT_REG = FONT_BOLD = FONT_LIGHT = ImageFont.load_default()
load_fonts()

# ════════════════════════════════════════════════════════
# 文案：每个场景 = (背景图类型, 旁白文本)
# ════════════════════════════════════════════════════════
SCENES = [
    ("title",  "跨越千里的信任。广西某工业项目，造价编制工作纪实。"),
    ("scene",  "上周一，上午九点。电话来自广西——四个单体，工业项目，时间非常紧。"),
    ("scene",  "造价行业有一条铁律：不看完图纸，绝不报价。十七个压缩包，两百多张图纸，层层叠叠。"),
    ("scene",  "四个单体工程——两栋破碎楼，单层层高超十二米，大型破碎设备基础，振动筛平台。两栋转运站，最高超过四十米，皮带机通廊，卸料斗，钢桁架。"),
    ("scene",  "图纸存在多处矛盾。建筑图和结构图的轴线对不上，设备基础位置前后不一致。节点详图缺失，标注错误。造价圈的说法：这就是地雷阵。"),
    ("scene",  "我们接了。客户的工期不等人，信任跨越一千公里来到河南。二十年造价，这种硬仗，我们打过的。"),
    ("scene",  "三个人，一个技术负责人，两个注册造价工程师。第一步，图纸梳理——逐张分类编号，建立交叉索引，出具图纸问题清单。当天就发给了客户和设计方。"),
    ("scene",  "破碎楼的挑战。两台大型颚式破碎机，单台自重超三十吨。基础是复合结构体——底板、侧墙、顶板、减振层、预埋螺栓群。每一个数据，都要从图纸上找到准确依据。"),
    ("scene",  "转运站的难度。高和险——最高处超四十米。钢桁架通廊，一根一根算弦杆、腹杆、节点板。卸料斗是非标设备，没有现成定额可套，分解，组价，一项一项找到最接近的子目。"),
    ("scene",  "五天，将近一百个小时。白天在屏幕前伏案算量，晚上在灯光下核对图纸。饿了是外卖，困了是咖啡。办公室的灯，至少亮到晚上十一点。"),
    ("scene",  "造价，是翻译——把图纸上的线条和符号，翻译成精确的数字和定额。造价，是预判——价格波动的风险，工艺变更的可能，都要在编制阶段做出预案。造价，是博弈——经得起审计，对得起甲方，不脱离市场。造价，是良知——每一个数字，终将被时间检验。"),
    ("scene",  "董事长常说：造价这事，糊弄不得。差一点，不是差一点钱，是差一份良心。所以，我们选择了最笨也最稳妥的做法——逐张核对，逐项确认，逐条核算。"),
    ("scene",  "最终造价，两千一百一十七万元。这是四个单体的土建、钢构、机电全部子目，逐一计算、逐一核实、逐一套价后的结果。三道审查——自检、互审、抽审——全部通过，我们才敢发给客户。"),
    ("scene",  "昨天下午，客户的尾款到账了。款项不大，但意义很重。这是客户对我们专业能力的最终确认——你们做的，我认。"),
    ("scene",  "造价，是在混沌中建立秩序。一堆杂乱的图纸，无数交叉的信息，从中找到一条清晰的逻辑线索，最终锚定在最合理的数字上。"),
    ("highlight", "造价，是一种信任的交付。客户交出来的不仅是几百张图纸，更是一份沉甸甸的信任。这份信任，是我们在这个行业里坚持了二十年最大的动力。"),
    ("closing", "中联永信工程管理河南有限公司。以精算筑价值，以诚信赢天下。匠心二十载，期待与您同行。"),
]


# ════════════════════════════════════════════════════════
# 逐词拆分
# ════════════════════════════════════════════════════════
def split_words(text):
    """中文按标点/空格拆词，保留标点"""
    tokens = []
    current = ""
    for ch in text:
        if ch in "，。、；：！？\"\"''（）()  \n":
            if current:
                tokens.append(("word", current))
                current = ""
            tokens.append(("punct", ch))
        else:
            current += ch
    if current:
        tokens.append(("word", current))
    return tokens


# ════════════════════════════════════════════════════════
# 逐场景生成 TTS，记录每句音频时长
# ════════════════════════════════════════════════════════
def get_duration(path):
    try:
        r = subprocess.run([os.environ["FFMPEG_BINARY"], "-i", path],
                           capture_output=True, text=True)
        for line in r.stderr.split("\n"):
            if "Duration" in line:
                h, m, s = line.split("Duration: ")[1].split(",")[0].split(":")
                return float(h)*3600 + float(m)*60 + float(s)
    except: pass
    return max(2.0, os.path.getsize(path) / 16000)


async def gen_tts():
    audio_dir = os.path.join(WORK_DIR, "tts")
    os.makedirs(audio_dir, exist_ok=True)
    combined = b""
    durations = []
    for i, (_, text) in enumerate(SCENES):
        path = os.path.join(audio_dir, f"{i:02d}.mp3")
        for attempt in range(5):
            try:
                c = edge_tts.Communicate(text=text, voice="zh-CN-YunxiNeural", rate="+5%")
                await c.save(path)
                break
            except:
                await asyncio.sleep((attempt+1)*3)
        dur = max(2.5, get_duration(path))
        durations.append(dur)
        with open(path, "rb") as f: combined += f.read()
        print(f"  ✓ {i+1:2d}/{len(SCENES)} {dur:.1f}s  {text[:18]}…")
        await asyncio.sleep(1)
    mp3 = os.path.join(WORK_DIR, "all.mp3")
    with open(mp3, "wb") as f: f.write(combined)
    ts = []; off = 0.0
    for i, d in enumerate(durations):
        ts.append({"idx": i, "start": off, "end": off+d})
        off += d
    return mp3, ts, off


# ════════════════════════════════════════════════════════
# 电影级字幕渲染
# ════════════════════════════════════════════════════════
def draw_gradient_bar(draw, y0, y1, w):
    """底部渐变条 — 从透明到深黑"""
    for row in range(y0, y1):
        alpha = (row - y0) / (y1 - y0)
        c = int(8 * (1 - alpha))
        draw.rectangle([0, row, w, row+1], fill=(c, c, c))

def draw_subtitle_bar(draw, y_top, bar_h):
    """半透明黑底条"""
    for row in range(y_top, y_top + bar_h):
        ratio = (row - y_top) / bar_h
        a = int(0.75 + 0.1 * (1 - abs(2*ratio - 1)))  # 中间更不透明
        c = int(5 * a)
        draw.rectangle([0, row, W, row+1], fill=(c, c+3, c+8))

def render_movie_frame(scene_idx, progress, total_scenes):
    """
    progress: 0.0 ~ 1.0 — 当前场景朗读进度
    电影效果：
    - 背景：深色工业风渐变
    - 底部：半透明黑条 + 字幕逐词高亮
    - 顶部：淡色品牌条
    """
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    stype, text = SCENES[scene_idx]

    # ── 背景氛围 ──
    # 顶部渐变光源
    for y in range(0, 350):
        a = 1 - y/350
        c = int(20 + 8 * a)
        draw.rectangle([0, y, W, y+1], fill=(c, c+4, c+16))

    # 装饰线
    draw.rectangle([80, 45, W-80, 47], fill=GOLD)

    # 品牌标识
    draw.text((80, 16), "中联永信", font=FONT_LIGHT, fill=GOLD)
    draw.text((260, 16), "工程管理（河南）有限公司", font=FONT_LIGHT, fill=GREY)

    # 右上角 — 项目标签
    tag = "广西工业项目 · 造价编制纪实"
    tw = draw.textbbox((0,0), tag, font=FONT_LIGHT)[2]
    draw.text((W - tw - 80, 16), tag, font=FONT_LIGHT, fill=DIM)

    # ── 场景标题 (顶部淡色) ──
    titles = {
        0: "跨越千里的信任", 1: "千里之外，一纸委托",
        2: "不看完图纸，绝不报价", 3: "四个单体工程",
        4: "地雷阵", 5: "我们接了",
        6: "灯火通明的夜晚", 7: "破碎楼的挑战",
        8: "转运站的难度", 9: "五天，将近一百个小时",
        10: "数字背后的温度", 11: "董事长的话",
        12: "两千一百一十七万的重量", 13: "客户的尾款到账了",
        14: "为什么选择造价", 15: "信任的交付",
        16: "匠心二十载",
    }
    title = titles.get(scene_idx, "")
    if title and stype not in ("title", "closing"):
        draw.text((100, 100), title, font=FONT_BOLD, fill=GOLD)

    # ── 电影级底部字幕 ──
    subtitle_y = H - 200
    bar_h = 160
    draw_subtitle_bar(draw, subtitle_y, bar_h)

    # 逐词渲染
    words = [t for t in split_words(text) if t[0] == "word"]
    total_words = len(words)

    # 每行最多 N 个词
    lines = []; current_line = []
    for w, _ in words:
        current_line.append(w)
        if len("".join(current_line)) > 14:
            lines.append(current_line)
            current_line = []
    if current_line:
        lines.append(current_line)

    # 计算当前该高亮到第几个词
    highlighted_idx = int(progress * total_words)

    # 渲染每一行
    font_sub = FONT_REG
    font_hl  = FONT_BOLD
    line_h = 50
    total_h = len(lines) * line_h
    start_y = subtitle_y + (bar_h - total_h) // 2 + 5

    global_word_idx = 0
    for li, line_words in enumerate(lines):
        # 计算这一行所有词的宽度
        parts = []
        for w in line_words:
            is_hl = global_word_idx <= highlighted_idx
            parts.append((w, is_hl))
            global_word_idx += 1

        # 居中
        total_w = 0
        gaps = 0
        for w, hl in parts:
            f = font_hl if hl else font_sub
            total_w += draw.textbbox((0,0), w, font=f)[2] - draw.textbbox((0,0), w, font=f)[0]
            gaps += 1
        total_w += (gaps - 1) * 12  # 间距

        x = (W - total_w) // 2
        y = start_y + li * line_h

        for w, hl in parts:
            f = font_hl if hl else font_sub
            color = WARM if hl else WHITE
            # 电影字幕描边
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                draw.text((x+dx, y+dy), w, font=f, fill=(0,0,0))
            draw.text((x, y), w, font=f, fill=color)
            x += draw.textbbox((0,0), w, font=f)[2] - draw.textbbox((0,0), w, font=f)[0] + 12

    # ── 底部信息 ──
    foot = "工程造价咨询  ·  工程预结算  ·  竣工结算审计  ·  二十年专注"
    fw = draw.textbbox((0,0), foot, font=FONT_LIGHT)[2]
    draw.text(((W-fw)//2, H-36), foot, font=FONT_LIGHT, fill=DIM)

    draw.rectangle([80, H-50, W-80, H-48], fill=GOLD)

    return img


# ════════════════════════════════════════════════════════
# 主流程
# ════════════════════════════════════════════════════════
async def main():
    N = len(SCENES)
    print(f"中联永信 · 电影级字幕视频  ({N} 场景)")

    # —— TTS ——
    print(f"\n[1/3] TTS…")
    audio_path, timestamps, total_dur = await gen_tts()
    print(f"总时长: {total_dur:.0f}s")

    # —— 渲染逐词帧 ——
    print(f"\n[2/3] 渲染逐词高亮帧…")
    # 每个场景渲染多帧，帧间隔 = 场景时长 / (词数 * 2)
    all_frames = []  # (fpath, start_time, duration)

    for i, ts in enumerate(timestamps):
        stype, text = SCENES[i]
        scene_dur = ts["end"] - ts["start"]
        words = [t for t in split_words(text) if t[0] == "word"]
        n_steps = max(len(words) * 2, 24)  # 每个词至少 2 帧步进
        step_dur = scene_dur / n_steps

        for step in range(n_steps):
            progress = (step + 1) / n_steps
            img = render_movie_frame(i, progress, N)
            fname = f"f_{i:02d}_{step:03d}.png"
            fpath = os.path.join(WORK_DIR, fname)
            img.save(fpath)
            all_frames.append({
                "path": fpath,
                "start": ts["start"] + step * step_dur,
                "dur": step_dur,
            })
        print(f"  ✓ {i+1:2d} {scene_dur:.1f}s  {n_steps} 帧  [{text[:20]}…]")

    # —— 合成 ——
    print(f"\n[3/3] 合成 {len(all_frames)} 帧…")
    clips = []
    for f in all_frames:
        c = ImageClip(f["path"], duration=f["dur"])
        c = c.with_start(f["start"])
        clips.append(c)

    video = CompositeVideoClip(clips, size=(W, H))
    audio = AudioFileClip(audio_path)
    final_dur = min(all_frames[-1]["start"] + all_frames[-1]["dur"], audio.duration)
    video = video.subclipped(0, final_dur)
    video = video.with_audio(audio.subclipped(0, final_dur))

    out = os.path.join(VIDEO_DIR, "广西项目纪实.mp4")
    video.write_videofile(out, fps=FPS, codec="libx264",
                          audio_codec="aac", threads=4, preset="medium", logger=None)
    video.close(); audio.close()

    # 桌面快捷方式
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    with open(os.path.join(desktop, "中联永信宣传片-广西项目.url"), "w") as f:
        f.write(f"[InternetShortcut]\nURL=file:///{out.replace(chr(92), '/')}\n")

    sz = os.path.getsize(out)/1024/1024
    print(f"\n✅ {out}")
    print(f"   {sz:.1f} MB · 1920x1080 · {final_dur:.0f}s · 电影字幕")
    print(f"✅ 桌面快捷方式已更新")


if __name__ == "__main__":
    asyncio.run(main())
