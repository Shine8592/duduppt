#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画幅（画布尺寸）定义与换算：一套内容，多种投放尺寸。

为什么有这个脚本（竞品对比 v3 的 P1 升级）：
  ppt-master 已支持 10+ 画布格式。中文场景里，同一份内容常常
  既要出 PPT 汇报（16:9），又要出小红书图文（3:4）、公众号封面（2.35:1）、
  竖版短视频（9:16）。手工重排成本极高 —— 本脚本把画幅变成参数。

支持的画幅（ppt-master 的 canvas-formats 思路 + 中文平台补充）：
    ppt169        PowerPoint 16:9        1920x1080   汇报/路演
    ppt43         PowerPoint 4:3         1024x768    老式投影
    xhs34         小红书 3:4             1080x1440   小红书图文
    xhs11         小红书 1:1             1080x1080   小红书方图
    wx916         公众号/视频号 9:16      1080x1920   竖版短视频
    wx235         公众号封面 2.35:1       900x383     公众号头图
    a4            A4 纵向                 2480x3508   打印/PDF
    a4l           A4 横向                 3508x2480   打印/PDF
    banners       横幅 3:1                1500x500    网站横幅

两种用法：
  1. 查询：python scripts/canvas-formats.py --list
           python scripts/canvas-formats.py --show xhs34
  2. 换算：把某个画幅的 EMU 尺寸输出到 JSON，供生成脚本使用
           python scripts/canvas-formats.py --get xhs34 --unit emu

依赖：无（纯计算，零依赖）。实际改 PPTX 尺寸请用 edit-deck.py。
"""
from __future__ import annotations

import argparse
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EMU_PER_PX = 9525        # OOXML: 1 px = 9525 EMU（96 DPI）
EMU_PER_INCH = 914400    # 1 英寸 = 914400 EMU

# name -> (label, 宽px, 高px, 场景)
FORMATS: dict[str, tuple[str, int, int, str]] = {
    "ppt169": ("PowerPoint 16:9", 1920, 1080, "汇报 / 路演 / 线上会议"),
    "ppt43":  ("PowerPoint 4:3", 1024, 768, "老式投影 / 传统课件"),
    "xhs34":  ("小红书 3:4", 1080, 1440, "小红书图文笔记（最常用）"),
    "xhs11":  ("小红书 1:1", 1080, 1080, "小红书方图 / 头像封面"),
    "wx916":  ("公众号·视频号 9:16", 1080, 1920, "竖版短视频 / 视频号"),
    "wx235":  ("公众号封面 2.35:1", 900, 383, "公众号头图"),
    "a4":     ("A4 纵向", 2480, 3508, "打印 / 导出 PDF"),
    "a4l":    ("A4 横向", 3508, 2480, "打印 / 导出 PDF"),
    "banners": ("横幅 3:1", 1500, 500, "网站 / 落地页横幅"),
}


def to_emu(px: int) -> int:
    return int(px * EMU_PER_PX)


def to_inches(px: int) -> float:
    return round(px / 96.0, 3)


def ratio(w: int, h: int) -> str:
    from math import gcd
    g = gcd(w, h)
    return f"{w // g}:{h // g}"


def main() -> int:
    ap = argparse.ArgumentParser(description="duduppt 画幅定义与换算")
    ap.add_argument("--list", action="store_true", help="列出所有画幅")
    ap.add_argument("--show", help="显示指定画幅的详情")
    ap.add_argument("--get", help="输出指定画幅的尺寸数据")
    ap.add_argument("--unit", choices=["px", "emu", "inch"], default="px",
                    help="--get 的输出单位")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    if args.list or (not args.show and not args.get):
        rows = []
        for key, (label, w, h, scene) in FORMATS.items():
            rows.append({
                "key": key, "label": label, "w": w, "h": h,
                "ratio": ratio(w, h), "scene": scene,
            })
        if args.format == "json":
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(f"{'key':<9}{'画幅':<22}{'尺寸':<14}{'比例':<10}适用场景")
            print("-" * 78)
            for r in rows:
                print(f"{r['key']:<9}{r['label']:<22}"
                      f"{r['w']}x{r['h']:<8}{r['ratio']:<10}{r['scene']}")
        return 0

    if args.show:
        if args.show not in FORMATS:
            print(f"[FAIL] 未知画幅: {args.show}（可用 --list 查看）")
            return 1
        label, w, h, scene = FORMATS[args.show]
        d = {
            "key": args.show, "label": label, "w_px": w, "h_px": h,
            "ratio": ratio(w, h), "scene": scene,
            "w_emu": to_emu(w), "h_emu": to_emu(h),
            "w_inch": to_inches(w), "h_inch": to_inches(h),
        }
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0

    if args.get:
        if args.get not in FORMATS:
            print(f"[FAIL] 未知画幅: {args.get}")
            return 1
        label, w, h, _ = FORMATS[args.get]
        if args.unit == "px":
            print(f"{w} {h}")
        elif args.unit == "emu":
            print(f"{to_emu(w)} {to_emu(h)}")
        else:
            print(f"{to_inches(w)} {to_inches(h)}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
