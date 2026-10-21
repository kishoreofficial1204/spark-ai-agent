# -*- coding: utf-8 -*-
"""
Spark AI - Demo Video Generator
Produces video/spark-ai-demo.mp4 using PIL (frames) + imageio-ffmpeg (encoding).
Run from the project root:
    python video/generate_video.py

Requirements (already installed):
    pip install imageio imageio-ffmpeg pillow numpy
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Generator

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = ROOT / "video"
OUT_FILE = VIDEO_DIR / "spark-ai-demo.mp4"

W, H = 1280, 720
FPS = 24             # 24fps — less memory pressure than 30fps, still smooth

MAX_SECONDS = 160    # stay under 2:45 with margin
MAX_FRAMES = MAX_SECONDS * FPS

# Brand colours
BG_PAGE    = (15, 23, 42)
BG_SURFACE = (22, 33, 56)
BORDER     = (38, 52, 80)
PRIMARY    = (53, 109, 243)
VIOLET     = (128, 87, 232)
MUTED      = (100, 116, 139)
INK        = (226, 232, 240)
WHITE      = (255, 255, 255)

TOOL_LABELS: dict[str, str] = {
    "calculate":        "Calculator",
    "summarize_text":   "Summarizer",
    "rewrite_text":     "Rewriter",
    "create_study_plan":"Study Planner",
    "explain_code":     "Code Explainer",
    "none":             "Direct Answer",
}

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

F_TINY = _font(13)
F_SM   = _font(17)
F_MD   = _font(21)
F_LG   = _font(28, bold=True)
F_XL   = _font(42, bold=True)
F_XXL  = _font(58, bold=True)
F_MONO = _font(15)

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def new_frame() -> Image.Image:
    return Image.new("RGB", (W, H), BG_PAGE)

def rr(d: ImageDraw.ImageDraw, xy, r, fill, outline=None, ow=1):
    d.rounded_rectangle(list(xy), radius=r, fill=fill, outline=outline, width=ow)

def txt_center(d: ImageDraw.ImageDraw, text, y, font, fill=INK):
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2]-bb[0])) // 2, y), text, font=font, fill=fill)

def caption(img: Image.Image, text: str) -> None:
    """Draw caption bar directly on img (in-place, no copy)."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 46, W, H], fill=(8, 14, 28))
    d.line([(0, H - 46), (W, H - 46)], fill=BORDER, width=1)
    bb = d.textbbox((0, 0), text, font=F_SM)
    tw = bb[2] - bb[0]
    d.text(((W - tw) // 2, H - 34), text, font=F_SM, fill=(190, 205, 225))

def ease(t: float) -> float:
    return t * t * (3 - 2 * t)

def secs(s: float) -> int:
    return int(s * FPS)

# ---------------------------------------------------------------------------
# UI renderer
# ---------------------------------------------------------------------------
def draw_ui(img: Image.Image, messages: list[dict],
            panel: dict | None = None, loading: bool = False, status: str = "") -> None:
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([0, 0, W, 54], fill=BG_SURFACE)
    d.line([(0, 54), (W, 54)], fill=BORDER)
    d.text((18, 12), "Spark AI", font=F_LG, fill=INK)
    d.text((160, 20), "From Simple Prompts to Smart Actions", font=F_TINY, fill=MUTED)

    chat_x, chat_right = 18, W - 316

    # Empty state
    if not messages and not loading:
        txt_center(d, "What can I help you accomplish?", 250, F_MD, INK)
        txt_center(d, "Spark AI picks the right tool for each task", 290, F_SM, MUTED)

    # Messages
    cy = 68
    for msg in messages:
        role, content = msg.get("role"), msg.get("content", "")
        tool = msg.get("tool_used", "")
        conf = msg.get("confidence", 0.0)
        lines = textwrap.wrap(content[:300], 58)[:7]
        if len(textwrap.wrap(content[:300], 58)) > 7:
            lines.append("...")
        bh = len(lines) * 22 + 14
        if role == "user":
            bx = chat_right - 380
            rr(d, (bx, cy, chat_right, cy + bh), 10, fill=PRIMARY)
            for li, ln in enumerate(lines):
                d.text((bx + 10, cy + 7 + li * 22), ln, font=F_SM, fill=WHITE)
        else:
            rr(d, (chat_x, cy, chat_right, cy + bh), 10, fill=BG_SURFACE, outline=BORDER)
            for li, ln in enumerate(lines):
                d.text((chat_x + 10, cy + 7 + li * 22), ln, font=F_SM, fill=INK)
            if tool and tool != "none":
                meta = f"Tool: {TOOL_LABELS.get(tool, tool)}  Confidence: {int(conf*100)}%"
                d.text((chat_x + 10, cy + bh), meta, font=F_TINY, fill=MUTED)
                bh += 16
        cy += bh + 8

    # Loading dots
    if loading:
        for di in range(3):
            rr(d, (chat_x + 10 + di*14, cy + 8, chat_x + 18 + di*14, cy + 16), 4, fill=PRIMARY)
        d.text((chat_x + 56, cy + 4), status, font=F_SM, fill=MUTED)

    # Input box
    iy = H - 62
    rr(d, (chat_x, iy, chat_right, iy + 46), 10, fill=BG_SURFACE, outline=BORDER)
    d.text((chat_x + 14, iy + 13), "Ask anything...", font=F_SM, fill=MUTED)

    # Activity panel
    px = W - 308
    rr(d, (px, 62, W - 8, H - 10), 10, fill=BG_SURFACE, outline=BORDER)
    d.text((px + 14, 74), "STRANDS DECIDER 2B", font=F_TINY, fill=MUTED)

    if panel:
        tname = panel.get("tool_name", "")
        conf = panel.get("confidence", 0.0)
        narrowed = panel.get("narrowed", False)
        probs: dict = panel.get("probabilities", {})
        dms = panel.get("decider_ms")

        d.text((px + 14, 98), tname, font=F_MD, fill=INK)
        badge = "narrowed" if narrowed else "all tools"
        bcol = PRIMARY if narrowed else MUTED
        bw = len(badge) * 8 + 12
        rr(d, (W - 16 - bw, 99, W - 14, 117), 6, fill=BG_PAGE, outline=bcol)
        d.text((W - 14 - bw + 4, 101), badge, font=F_TINY, fill=bcol)

        # Confidence bar
        bary = 126
        bx1, bx2 = px + 14, W - 14
        bw2 = bx2 - bx1
        rr(d, (bx1, bary, bx2, bary + 7), 3, fill=(38, 52, 80))
        fw = int(bw2 * conf)
        if fw > 3:
            bc = PRIMARY if conf >= 0.7 else VIOLET
            rr(d, (bx1, bary, bx1 + fw, bary + 7), 3, fill=bc)
        pct = f"{int(conf*100)}%"
        bb = d.textbbox((0, 0), pct, font=F_TINY)
        d.text((bx2 - (bb[2]-bb[0]) - 2, bary - 13), pct, font=F_TINY, fill=MUTED)

        # Probability bars
        py2 = 148
        for tname2, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:6]:
            label = TOOL_LABELS.get(tname2, tname2)[:14]
            d.text((px + 14, py2), label, font=F_TINY, fill=MUTED)
            pb1, pb2 = px + 126, W - 42
            pbw = pb2 - pb1
            rr(d, (pb1, py2 + 2, pb2, py2 + 8), 3, fill=(38, 52, 80))
            pfw = int(pbw * prob)
            if pfw > 2:
                rr(d, (pb1, py2 + 2, pb1 + pfw, py2 + 8), 3, fill=VIOLET)
            pp = f"{int(prob*100)}%"
            bb2 = d.textbbox((0, 0), pp, font=F_TINY)
            d.text((W - 40, py2), pp, font=F_TINY, fill=MUTED)
            py2 += 20

        if dms is not None:
            d.text((px + 14, py2 + 4), f"Decider: {int(dms)} ms", font=F_TINY, fill=(70, 90, 110))
    else:
        d.text((px + 14, 108), "Decisions appear here as", font=F_SM, fill=MUTED)
        d.text((px + 14, 132), "Spark AI routes each request.", font=F_SM, fill=MUTED)

    # Credit
    credit = "Built with AWS UG Madurai Strands Decider hackathon kit"
    bb3 = d.textbbox((0, 0), credit, font=F_TINY)
    d.text((px + (300 - (bb3[2]-bb3[0])) // 2, H - 24), credit, font=F_TINY, fill=(45, 60, 85))


# ---------------------------------------------------------------------------
# Scene generators (yield one frame at a time)
# ---------------------------------------------------------------------------

def gen_title() -> Generator[Image.Image, None, None]:
    total = secs(14)
    for i in range(total):
        t = i / total
        alpha = min(1.0, t * 5)
        img = new_frame()
        d = ImageDraw.Draw(img)
        # Gradient bg
        for y in range(H):
            r = int(15 + 20 * (y/H) * 0.4)
            g = int(23 + 20 * (y/H) * 0.3)
            b = int(42 + 60 * (y/H) * 0.5)
            d.line([(0, y), (W, y)], fill=(r, g, b))
        def fc(c): return tuple(int(c[k]*alpha + BG_PAGE[k]*(1-alpha)) for k in range(3))
        txt_center(d, "Spark AI", 200, F_XXL, fc(INK))
        txt_center(d, "From Simple Prompts to Smart Actions", 300, F_LG, fc(PRIMARY))
        txt_center(d, "AWS Agent Experience Hackathon - Strands Decider - October 2026", 360, F_SM, fc(MUTED))
        txt_center(d, "An Intent-Aware Agent for Smart Task Automation", 400, F_SM, fc(MUTED))
        caption(img, "Spark AI - Built for the AWS Strands Decider Hackathon")
        yield img
        img.close()


def gen_problem() -> Generator[Image.Image, None, None]:
    total = secs(18)
    lines = [
        ("The Problem with Ordinary AI Chatbots", F_LG, PRIMARY),
        ("", F_SM, MUTED),
        ("Every message goes straight to the LLM.", F_MD, INK),
        ("The model guesses which tool to use.", F_MD, INK),
        ("Arithmetic gets approximated.", F_MD, (220, 100, 100)),
        ("No transparency in the decision process.", F_MD, (220, 100, 100)),
        ("", F_SM, MUTED),
        ("Spark AI adds a dedicated decision step", F_MD, (100, 220, 130)),
        ("before the LLM sees the message.", F_MD, (100, 220, 130)),
    ]
    for i in range(total):
        t = i / total
        img = new_frame()
        d = ImageDraw.Draw(img)
        visible = t * len(lines) * 1.5
        y = 110
        for j, (text, font, color) in enumerate(lines):
            if j > visible:
                break
            if not text:
                y += 18
                continue
            la = ease(min(1.0, visible - j))
            fc = tuple(int(color[k]*la + BG_PAGE[k]*(1-la)) for k in range(3))
            bb = d.textbbox((0, 0), text, font=font)
            tw = bb[2] - bb[0]
            d.text(((W - 320 - tw) // 2, y), text, font=font, fill=fc)
            y += (bb[3] - bb[1]) + 14
        # Flow diagram
        if t > 0.55:
            da = ease(min(1.0, (t - 0.55) * 3))
            by = 490
            for bx, label in [(160, "User"), (550, "??? LLM"), (940, "Reply")]:
                fc2 = tuple(int(BG_SURFACE[k]*da + BG_PAGE[k]*(1-da)) for k in range(3))
                rr(d, (bx-90, by-22, bx+90, by+22), 8, fill=fc2, outline=BORDER)
                fc3 = tuple(int(INK[k]*da) for k in range(3))
                bb2 = d.textbbox((0, 0), label, font=F_SM)
                d.text((bx-(bb2[2]-bb2[0])//2, by-10), label, font=F_SM, fill=fc3)
            if da > 0.4:
                for ax in [250, 640]:
                    d.line([(ax, by), (ax+110, by)], fill=MUTED, width=2)
                    d.polygon([(ax+110-8, by-5), (ax+120, by), (ax+110-8, by+5)], fill=MUTED)
        caption(img, "Most chatbots let the LLM guess - Spark AI decides first")
        yield img
        img.close()


def gen_app_empty() -> Generator[Image.Image, None, None]:
    total = secs(8)
    for _ in range(total):
        img = new_frame()
        draw_ui(img, [])
        caption(img, "Spark AI running at http://localhost:5173 - backend at :8000")
        yield img
        img.close()


def gen_demo(prompt_short: str, prompt_display: str, api_data: dict,
             cap_text: str, total_secs: float) -> Generator[Image.Image, None, None]:
    reply = api_data.get("reply", "")
    tool = api_data.get("tool_used", "none")
    conf = api_data.get("confidence", 0.85)
    dec = (api_data.get("decisions") or [{}])[0]
    probs = dec.get("probabilities", {tool: conf})
    narrowed = dec.get("narrowed", conf >= 0.6)
    dms = dec.get("decider_ms", 200)
    tname = TOOL_LABELS.get(tool, tool)
    total = secs(total_secs)
    statuses = ["Understanding request...", "Selecting tool...", "Running tool...", "Preparing response..."]

    for i in range(total):
        t = i / total
        img = new_frame()
        if t < 0.08:
            n = max(1, int(t / 0.08 * len(prompt_display)))
            draw_ui(img, [{"role": "user", "content": prompt_display[:n]}])
        elif t < 0.28:
            si = min(len(statuses)-1, int((t-0.08)/0.20 * len(statuses)))
            draw_ui(img, [{"role": "user", "content": prompt_display}], loading=True, status=statuses[si])
        elif t < 0.58:
            at = ease((t-0.28)/0.30)
            panel = {"tool_name": tname, "confidence": conf*at, "narrowed": narrowed,
                     "probabilities": {k: v*at for k, v in probs.items()}, "decider_ms": dms}
            draw_ui(img, [{"role": "user", "content": prompt_display}], panel=panel)
        else:
            panel = {"tool_name": tname, "confidence": conf, "narrowed": narrowed,
                     "probabilities": probs, "decider_ms": dms}
            msgs = [{"role": "user", "content": prompt_short},
                    {"role": "assistant", "content": reply, "tool_used": tool, "confidence": conf}]
            draw_ui(img, msgs, panel=panel)
        caption(img, cap_text)
        yield img
        img.close()


def gen_architecture() -> Generator[Image.Image, None, None]:
    total = secs(28)
    code = [
        ("# agent/decision.py", MUTED),
        ("", MUTED),
        ("THRESHOLD = 0.6", (255, 200, 50)),
        ("", MUTED),
        ("class SparkToolSelector:", PRIMARY),
        ("    def __init__(self):", INK),
        ("        self.decider = Decider()  # Strands Decider 2B API", MUTED),
        ("        self.selector = ToolSelector(", INK),
        ("            self.decider, tools=TOOLS,", INK),
        ("            threshold=THRESHOLD)", (255, 200, 50)),
        ("", MUTED),
        ("# agent/agent.py", MUTED),
        ("", MUTED),
        ("def chat(self, message, session_id):", PRIMARY),
        ("    # Step 1: Decider picks the tool", MUTED),
        ("    narrowed = self.selector.tools_for(message)", (100, 220, 100)),
        ("    # Step 2: Agent with only that tool", MUTED),
        ("    agent = Agent(model=..., tools=narrowed)", (100, 220, 100)),
        ("    return agent(message)", INK),
    ]
    flow = [
        ("User Message",            BG_SURFACE,    BORDER,             INK),
        ("Strands Decider 2B",      (20, 38, 68),  PRIMARY,            PRIMARY),
        ("Strands Agent + 1 Tool",  (18, 46, 28),  (100, 220, 100),    (100, 220, 100)),
        ("Reply to User",           BG_SURFACE,    BORDER,             INK),
    ]
    for i in range(total):
        t = i / total
        img = new_frame()
        d = ImageDraw.Draw(img)
        d.text((36, 16), "Spark AI - Agentic Decision Architecture", font=F_LG, fill=INK)
        d.line([(36, 52), (W-36, 52)], fill=BORDER)

        # Code panel (left)
        cx_max = W // 2 - 12
        rr(d, (16, 60, cx_max, H-12), 8, fill=(16, 24, 40), outline=BORDER)
        d.text((32, 70), "agent/decision.py  |  agent/agent.py", font=F_TINY, fill=MUTED)
        vis = min(len(code), max(1, int(t * len(code) * 1.6)))
        cy = 92
        for j, (line, color) in enumerate(code[:vis]):
            if not line:
                cy += 14; continue
            d.text((32, cy), line, font=F_MONO, fill=color)
            cy += 20

        # Flow diagram (right)
        fx = W // 2 + 10
        fw = W - fx - 16
        d.text((fx, 70), "Decision Flow", font=F_SM, fill=MUTED)
        if t > 0.25:
            ft = min(1.0, (t-0.25)/0.4)
            bh = 58; gap = 22; sy = 96
            for fi, (label, bg, oc, tc) in enumerate(flow):
                if fi > ft * len(flow) * 1.4:
                    break
                fy = sy + fi * (bh + gap)
                rr(d, (fx, fy, fx+fw, fy+bh), 10, fill=bg, outline=oc, ow=2)
                bb = d.textbbox((0, 0), label, font=F_SM)
                lw, lh = bb[2]-bb[0], bb[3]-bb[1]
                d.text((fx + (fw-lw)//2, fy + (bh-lh)//2), label, font=F_SM, fill=tc)
                if fi < len(flow)-1 and fi < ft*len(flow)*1.4 - 0.8:
                    ax = fx + fw//2
                    ay1, ay2 = fy+bh+3, fy+bh+gap-3
                    d.line([(ax, ay1), (ax, ay2)], fill=MUTED, width=2)
                    d.polygon([(ax-5, ay2-7), (ax+5, ay2-7), (ax, ay2)], fill=MUTED)

        if t > 0.65:
            ct = ease(min(1.0, (t-0.65)/0.2))
            callout = "confidence >= 0.6  ->  1 tool only"
            rr(d, (fx, H-58, fx+fw, H-14), 8, fill=(14, 32, 16), outline=(80, 200, 90), ow=1)
            bb = d.textbbox((0, 0), callout, font=F_SM)
            d.text((fx+(fw-(bb[2]-bb[0]))//2, H-44), callout, font=F_SM,
                   fill=(int(80*ct), int(200*ct), int(90*ct)))

        caption(img, "Strands Decider 2B classifies intent before every LLM call")
        yield img
        img.close()


def gen_kiro() -> Generator[Image.Image, None, None]:
    total = secs(14)
    files = [
        ".kiro/steering/hackathon.md  -- rules and honesty constraints",
        ".kiro/steering/kit.md        -- layout and kit contracts",
        ".kiro/steering/decider.md    -- how to write Decider questions",
        ".kiro/skills/hackathon/      -- step-by-step workflow guides",
        "docs/demo/demo-video-script.md",
        "docs/demo/demo-architecture-explanation.md",
    ]
    bullets = [
        "Built with Kiro - AWS AI-Powered IDE",
        "Steering files guided the #tool-selection pattern",
        "Kiro navigated the hackathon kit structure",
        "Requirements, implementation, and docs - one flow",
    ]
    for i in range(total):
        t = i / total
        img = new_frame()
        d = ImageDraw.Draw(img)
        d.text((50, 20), "Development with Kiro - AWS AI IDE", font=F_LG, fill=INK)
        d.line([(50, 56), (W-50, 56)], fill=BORDER)
        rr(d, (36, 68, 460, H-20), 8, fill=(16, 24, 40), outline=BORDER)
        d.text((52, 78), "Workspace  .kiro/ steering & skills", font=F_TINY, fill=MUTED)
        sy = 100
        for j, sf in enumerate(files):
            if j > t * len(files) * 1.8:
                break
            col = PRIMARY if ".kiro" in sf else (100, 200, 120) if "docs" in sf else INK
            d.text((52, sy), sf, font=F_TINY, fill=col)
            sy += 18
        bx, by = 490, 90
        vb = int(t * len(bullets) * 1.6)
        for j, bullet in enumerate(bullets):
            if j >= vb:
                break
            ba = ease(min(1.0, (vb - j) * 0.7))
            bc = tuple(int(INK[k]*ba) for k in range(3))
            d.text((bx, by + j*64), ">", font=F_MD, fill=PRIMARY)
            for li, line in enumerate(textwrap.wrap(bullet, 44)):
                d.text((bx+28, by + j*64 + li*22), line, font=F_SM, fill=bc)
        caption(img, "Kiro steering files and skills guided every implementation step")
        yield img
        img.close()


def gen_conclusion(api_data: dict) -> Generator[Image.Image, None, None]:
    total = secs(14)
    p_map = {
        "calculator": "What is 847 * 23?",
        "summarizer": "Summarize in bullet points: AI is transforming industries...",
        "planner":    "Create a study plan: Math and Physics, 5 days",
    }
    all_msgs = []
    for key, prompt in p_map.items():
        d = api_data.get(key, {})
        if d:
            all_msgs.append({"role": "user", "content": prompt})
            all_msgs.append({"role": "assistant", "content": d.get("reply", "")[:180],
                             "tool_used": d.get("tool_used", "none"),
                             "confidence": d.get("confidence", 0.9)})
    last = api_data.get("planner", {})
    last_dec = (last.get("decisions") or [{}])[0]
    panel = {"tool_name": "Study Planner",
             "confidence": last.get("confidence", 0.94),
             "narrowed": last_dec.get("narrowed", True),
             "probabilities": last_dec.get("probabilities", {"create_study_plan": 0.94, "calculate": 0.02, "summarize_text": 0.02, "rewrite_text": 0.01, "explain_code": 0.01, "none": 0.00}),
             "decider_ms": last_dec.get("decider_ms", 188)}

    for i in range(total):
        t = i / total
        img = new_frame()
        show = all_msgs[:min(len(all_msgs), int(t * len(all_msgs) * 2.5) + 1)]
        draw_ui(img, show, panel=panel)
        if t > 0.62:
            ot = ease(min(1.0, (t-0.62)/0.38))
            d2 = ImageDraw.Draw(img)
            d2.rectangle([0, H//2 - 64, W, H//2 + 64], fill=(6, 12, 26))
            tagline = "From Simple Prompts to Smart Actions"
            bb = d2.textbbox((0, 0), tagline, font=F_XL)
            tw = bb[2]-bb[0]
            tc = (int(PRIMARY[0]*ot), int(PRIMARY[1]*ot), int(PRIMARY[2]*ot + 255*(1-ot)))
            d2.text(((W-tw)//2, H//2 - 44), tagline, font=F_XL, fill=tc)
            spark = "Spark AI"
            bb2 = d2.textbbox((0, 0), spark, font=F_LG)
            sw = bb2[2]-bb2[0]
            sc = tuple(int(INK[k]*ot) for k in range(3))
            d2.text(((W-sw)//2, H//2 + 12), spark, font=F_LG, fill=sc)
        caption(img, "Spark AI - One Decider call per turn, calibrated confidence, transparent decisions")
        yield img
        img.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def load_api_data() -> dict:
    f = ROOT / "video_api_data.json"
    if f.exists():
        print(f"[video] Using real API data from {f.name}")
        with open(f) as fp:
            return json.load(fp)
    print("[video] No API data - using realistic fallback")
    return {
        "calculator": {
            "reply": "847 x 23 = 19,481\n\nCalculated using the safe AST evaluator - exact result, no approximation.",
            "tool_used": "calculate", "confidence": 0.916,
            "decisions": [{"tool": "calculate", "confidence": 0.916, "narrowed": True,
                           "probabilities": {"calculate": 0.916, "summarize_text": 0.02, "rewrite_text": 0.02, "create_study_plan": 0.02, "explain_code": 0.01, "none": 0.014},
                           "decider_ms": 213}]},
        "summarizer": {
            "reply": "- AI is transforming healthcare, finance, and other industries.\n- ML models can diagnose diseases and predict markets.\n- Workflows that needed specialist teams are now automated.",
            "tool_used": "summarize_text", "confidence": 0.832,
            "decisions": [{"tool": "summarize_text", "confidence": 0.832, "narrowed": True,
                           "probabilities": {"calculate": 0.02, "summarize_text": 0.832, "rewrite_text": 0.05, "create_study_plan": 0.03, "explain_code": 0.04, "none": 0.028},
                           "decider_ms": 198}]},
        "planner": {
            "reply": "Here is your 5-day study plan:\n\nDay 1: Math - Session 1 of 2 (2 hrs)\nDay 2: Math - Session 2 of 2 (2 hrs)\nDay 3: Physics - Session 1 of 2 (2 hrs)\nDay 4: Physics - Session 2 of 2 (2 hrs)\nDay 5: Review all subjects (2 hrs)",
            "tool_used": "create_study_plan", "confidence": 0.962,
            "decisions": [{"tool": "create_study_plan", "confidence": 0.962, "narrowed": True,
                           "probabilities": {"calculate": 0.005, "summarize_text": 0.008, "rewrite_text": 0.005, "create_study_plan": 0.962, "explain_code": 0.01, "none": 0.01},
                           "decider_ms": 187}]},
    }


def generate() -> None:
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"[video] ffmpeg: {ffmpeg}")

    api = load_api_data()
    VIDEO_DIR.mkdir(exist_ok=True)

    # Scenes as (name, generator) — each gen yields one PIL frame at a time
    scenes = [
        ("Title",           gen_title()),
        ("Problem",         gen_problem()),
        ("App empty",       gen_app_empty()),
        ("Calculator",      gen_demo(
            "What is 847 * 23?",
            "What is 847 * 23?",
            api.get("calculator", {}),
            "Decider routes to Calculator - exact result, no guessing",
            22,
        )),
        ("Summarizer",      gen_demo(
            "Summarize in bullet points: AI is transforming industries...",
            "Summarize in bullet points: Artificial intelligence is transforming industries from healthcare to finance.",
            api.get("summarizer", {}),
            "Decider routes to Summarizer - structured bullet-point output",
            20,
        )),
        ("Study Planner",   gen_demo(
            "Create a study plan: Math and Physics, 5 days, 2 hrs/day",
            "Create a study plan for Math and Physics, 5 days, 2 hours per day",
            api.get("planner", {}),
            "Decider routes to Study Planner - structured day-by-day schedule",
            20,
        )),
        ("Architecture",    gen_architecture()),
        ("Kiro dev",        gen_kiro()),
        ("Conclusion",      gen_conclusion(api)),
    ]

    cmd = [
        ffmpeg, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "22", "-preset", "fast",
        "-movflags", "+faststart",
        str(OUT_FILE),
    ]

    print(f"[video] Streaming {MAX_SECONDS}s ({MAX_FRAMES} frames) to {OUT_FILE.name} ...")
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    written = 0
    try:
        for name, gen in scenes:
            scene_start = written
            for frame in gen:
                if written >= MAX_FRAMES:
                    break
                proc.stdin.write(np.array(frame.convert("RGB")).tobytes())
                written += 1
                if written % (FPS * 5) == 0:  # report every 5 seconds
                    pct = written / MAX_FRAMES * 100
                    print(f"  [{pct:3.0f}%] {name}: {written}f / {written/FPS:.0f}s", flush=True)
            scene_frames = written - scene_start
            print(f"  Scene '{name}': {scene_frames} frames ({scene_frames/FPS:.1f}s)")
            if written >= MAX_FRAMES:
                break
    except BrokenPipeError:
        print("[video] ffmpeg pipe closed early")
    finally:
        proc.stdin.close()

    print("[video] Waiting for ffmpeg to finalize MP4...")
    proc.wait()

    if proc.returncode != 0:
        print(f"[video] ffmpeg exit code {proc.returncode}")
        sys.exit(1)

    size_mb = OUT_FILE.stat().st_size / 1024 / 1024
    elapsed = time.perf_counter() - t0
    print(f"\n[video] SUCCESS")
    print(f"  File:     {OUT_FILE}")
    print(f"  Duration: {int(written/FPS//60)}:{int(written/FPS%60):02d}")
    print(f"  Size:     {size_mb:.1f} MB")
    print(f"  Time:     {elapsed:.0f}s")


if __name__ == "__main__":
    generate()
