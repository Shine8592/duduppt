#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑既有 PPTX：改文字 / 替换图表数据 / 增删页，保留原设计与未改动页面。

为什么有这个脚本（竞品对比 v3 的 P0 升级）：
  全行业最大痛点 —— 「改一个字 = 重新生成一遍」。ppt-master 凭
  "Edit Native PPTX（字节级保留设计）"拿下大量口碑。
  本脚本让 duduppt 也能：打开已有 PPTX → 只改指定内容 → 保存，
  未改动的页与原设计完全保留。

能力：
    set-text   按"页码+原文"替换文字（支持部分匹配）
    set-chart  按"页码+图表序号"替换图表数据
    list-text  列出指定页的所有文本（便于定位要改什么）
    list-chart 列出指定页的图表与系列
    add-slide  在末尾/指定位置新增一页（沿用已有版式）
    del-slide  删除指定页

用法：
    # 1. 先看第 2 页有哪些文字
    python scripts/edit-deck.py --deck output.pptx list-text --slide 2

    # 2. 改：把"2025年"改成"2026年"（第 2 页）
    python scripts/edit-deck.py --deck output.pptx set-text \
        --slide 2 --find "2025年" --replace "2026年" --out output_v2.pptx

    # 3. 改图表数据（第 3 页第 1 个图表）
    python scripts/edit-deck.py --deck output.pptx set-chart \
        --slide 3 --chart 1 --categories "Q1,Q2,Q3,Q4" \
        --series "销售额:120,160,140,190" --out output_v2.pptx

    # 4. 增删页
    python scripts/edit-deck.py --deck output.pptx add-slide --layout 6 --out v2.pptx
    python scripts/edit-deck.py --deck output.pptx del-slide --slide 4 --out v2.pptx

安全：
    - 默认输出到新文件（--out），不覆盖原文件；需覆盖用 --inplace
    - --inplace 时自动先备份 .bak
    - 依赖 python-pptx
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.chart.data import ChartData
except ImportError:
    print("[FAIL] 缺少 python-pptx：pip install python-pptx")
    sys.exit(2)


def load(deck: Path) -> Presentation:
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        sys.exit(1)
    return Presentation(str(deck))


def save(prs: Presentation, deck: Path, out: str | None, inplace: bool) -> None:
    if inplace:
        bak = deck.with_suffix(deck.suffix + ".bak")
        shutil.copy2(deck, bak)
        prs.save(str(deck))
        print(f"✅ 已就地保存: {deck}（备份: {bak}）")
    else:
        dst = Path(out) if out else deck.with_name(deck.stem + "-edited" + deck.suffix)
        dst.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(dst))
        print(f"✅ 已保存: {dst}")


def get_slide(prs: Presentation, idx1: int):
    """按 1 起的页码取 slide。"""
    i = idx1 - 1
    if i < 0 or i >= len(prs.slides):
        print(f"[FAIL] 页码越界：共 {len(prs.slides)} 页，请求 {idx1}")
        sys.exit(1)
    return prs.slides[i]


# ---------------------------------------------------------------------------


def cmd_list_text(prs: Presentation, a) -> None:
    slide = get_slide(prs, a.slide)
    print(f"第 {a.slide} 页文本（共 {len(slide.shapes)} 个形状）")
    print("=" * 60)
    n = 0
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            txt = "".join(r.text for r in para.runs).strip()
            if txt:
                n += 1
                print(f"  [{n}] {txt[:80]}")
    if n == 0:
        print("  （该页无文本）")


def cmd_set_text(prs: Presentation, a) -> None:
    slide = get_slide(prs, a.slide)
    hit = 0
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if a.find in run.text:
                    if not a.dry_run:
                        run.text = run.text.replace(a.find, a.replace)
                    hit += 1
                    print(f"  替换: {run.text[:60]}")
    if hit == 0:
        print(f"⚠️  第 {a.slide} 页未找到「{a.find}」")
        print("   可先用 list-text 查看该页实际文本")
    else:
        print(f"✅ 共替换 {hit} 处")
        if a.dry_run:
            print("   （dry-run，未实际写入）")


def cmd_list_chart(prs: Presentation, a) -> None:
    slide = get_slide(prs, a.slide)
    idx = 0
    for shape in slide.shapes:
        if not shape.has_chart:
            continue
        idx += 1
        chart = shape.chart
        ctype = str(chart.chart_type).split()[0] if chart.chart_type else "?"
        cats = list(chart.plots[0].categories) if chart.plots else []
        print(f"  图表 [{idx}] 类型={ctype}")
        print(f"     类别: {cats}")
        try:
            for s in chart.series:
                vals = list(s.values)
                print(f"     系列: {s.name} -> {vals[:8]}")
        except Exception:
            pass
    if idx == 0:
        print("  （该页无图表）")


def cmd_set_chart(prs: Presentation, a) -> None:
    slide = get_slide(prs, a.slide)
    charts = [s.chart for s in slide.shapes if s.has_chart]
    if not charts:
        print(f"[FAIL] 第 {a.slide} 页没有图表")
        sys.exit(1)
    if a.chart < 1 or a.chart > len(charts):
        print(f"[FAIL] 图表序号越界：共 {len(charts)} 个，请求 {a.chart}")
        sys.exit(1)
    chart = charts[a.chart - 1]

    cats = [c.strip() for c in a.categories.split(",") if c.strip()]
    series = []
    for item in a.series:
        if ":" not in item:
            print(f"[FAIL] 系列格式应为 名称:v1,v2,... -> {item}")
            sys.exit(1)
        name, vals = item.split(":", 1)
        try:
            series.append((name, [float(x) for x in vals.split(",") if x.strip()]))
        except ValueError as e:
            print(f"[FAIL] 数值解析失败: {item} -> {e}")
            sys.exit(1)

    data = ChartData()
    data.categories = cats
    for name, vals in series:
        data.add_series(name, vals)

    if a.dry_run:
        print(f"✅ dry-run：将把图表 {a.chart} 数据替换为 {len(cats)} 类别 / {len(series)} 系列")
        return

    chart.replace_data(data)
    print(f"✅ 已替换第 {a.slide} 页图表 {a.chart} 的数据")
    print(f"   {len(cats)} 类别 / {len(series)} 系列（图表样式与格式保留）")


def cmd_add_slide(prs: Presentation, a) -> None:
    layouts = prs.slide_layouts
    li = a.layout if a.layout is not None else 6
    if li < 0 or li >= len(layouts):
        print(f"[FAIL] 版式序号越界：共 {len(layouts)} 个，请求 {li}")
        sys.exit(1)
    prs.slides.add_slide(layouts[li])
    print(f"✅ 已新增一页（版式 {li}），当前共 {len(prs.slides)} 页")


def cmd_del_slide(prs: Presentation, a) -> None:
    idx = a.slide - 1
    if idx < 0 or idx >= len(prs.slides):
        print(f"[FAIL] 页码越界：共 {len(prs.slides)} 页，请求 {a.slide}")
        sys.exit(1)
    # python-pptx 删除 slide：操作 XML
    from pptx.util import Emu
    slide = prs.slides[idx]
    xml_slides = prs.slides._sldIdLst
    prs.part.drop_rel(slide.part.reltype if hasattr(slide.part, "reltype") else "")
    # 标准做法：删 sldId 元素
    for sldId in list(xml_slides):
        if sldId.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") == slide.part.related_parts and False:
            pass
    # 简化：直接用 rId 匹配
    rIds = {v: k for k, v in prs.part.rels.items()}
    slide_rId = None
    for rId, rel in prs.part.rels.items():
        if rel.target_part == slide.part:
            slide_rId = rId
            break
    if slide_rId is None:
        print("[FAIL] 无法定位要删除的页")
        sys.exit(1)
    for sldId in list(xml_slides):
        if sldId.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") == slide_rId:
            xml_slides.remove(sldId)
            break
    prs.part.drop_rel(slide_rId)
    print(f"✅ 已删除第 {a.slide} 页，剩余 {len(prs.slides)} 页")


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="编辑既有 PPTX（保留原设计）")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--out", help="输出文件（不指定则 <原名>-edited.pptx）")
    ap.add_argument("--inplace", action="store_true", help="就地修改（自动备份 .bak）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-text")
    p.add_argument("--slide", type=int, required=True)
    p.set_defaults(fn=cmd_list_text)

    p = sub.add_parser("set-text")
    p.add_argument("--slide", type=int, required=True)
    p.add_argument("--find", required=True)
    p.add_argument("--replace", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_set_text)

    p = sub.add_parser("list-chart")
    p.add_argument("--slide", type=int, required=True)
    p.set_defaults(fn=cmd_list_chart)

    p = sub.add_parser("set-chart")
    p.add_argument("--slide", type=int, required=True)
    p.add_argument("--chart", type=int, default=1)
    p.add_argument("--categories", required=True)
    p.add_argument("--series", required=True, action="append")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_set_chart)

    p = sub.add_parser("add-slide")
    p.add_argument("--layout", type=int, default=6)
    p.set_defaults(fn=cmd_add_slide)

    p = sub.add_parser("del-slide")
    p.add_argument("--slide", type=int, required=True)
    p.set_defaults(fn=cmd_del_slide)

    args = ap.parse_args()
    prs = load(Path(args.deck))
    args.fn(prs, args)

    # list-* 命令不保存
    if args.cmd.startswith("list-"):
        return 0
    if getattr(args, "dry_run", False):
        print("（dry-run，未保存）")
        return 0
    save(prs, Path(args.deck), args.out, args.inplace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
