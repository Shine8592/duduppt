#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原生图表生成：把数据变成 PowerPoint 原生 Chart 对象（带"编辑数据"按钮）。

为什么有这个脚本（竞品对比 v3 的 P0 升级）：
  duduppt 此前的图表是「形状拼图」—— 长得像图表，但改不了数据，
  只能在 PowerPoint 里逐条手改形状。ppt-master 的核心卖点恰恰是
  "数据驱动原生图表（带 Edit Data）"。本脚本补齐这个短板。

生成的图表：
  - 是真正的 OOXML Chart 对象（c:chart），带"编辑数据"按钮
  - 支持柱状图（横向/纵向）、条形图、折线图、饼图
  - 中文轴标签/系列名自动绑定 <a:ea> 槽位（防字体回退）
  - 可叠加到现有 slide（与 pptxgenjs 生成的页面共存）

用法：
    # 生成一个新 PPTX，只含一张原生图表
    python scripts/native-charts.py --out chart_demo.pptx \
        --type bar --categories "Q1,Q2,Q3,Q4" --series "销售额:100,150,130,180"

    # 在现有 PPTX 的指定 slide 上叠加图表
    python scripts/native-charts.py --deck output.pptx --slide 2 \
        --type line --categories "1月,2月,3月" --series "增长:1.2,2.1,1.8" \
        --out enhanced.pptx

注意：
  - 依赖 python-pptx（pip install python-pptx）
  - 这是**独立工具**：pptxgenjs 做快速生成，本脚本做原生图表增强，
    两者不冲突，可混用。
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.chart.data import ChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
    from pptx.util import Inches, Pt, Emu
except ImportError:
    print("[FAIL] 缺少 python-pptx：pip install python-pptx")
    sys.exit(2)

# 跨平台安全中文字体（与 qa-check.py 的白名单一致）
DEFAULT_CJK_FONT = "微软雅黑"

CHART_TYPES = {
    "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,        # 纵向柱状图
    "bar_h": XL_CHART_TYPE.BAR_CLUSTERED,         # 横向条形图
    "line": XL_CHART_TYPE.LINE_MARKERS,           # 折线图
    "pie": XL_CHART_TYPE.PIE,                     # 饼图
    "stacked": XL_CHART_TYPE.COLUMN_STACKED,      # 堆积柱状图
    "area": XL_CHART_TYPE.AREA,                   # 面积图
}


def parse_series(series_args: list[str]) -> list[tuple[str, list[float]]]:
    """解析 --series 参数："名称:v1,v2,..." 可多个。"""
    out = []
    for item in series_args:
        if ":" not in item:
            raise ValueError(f"系列格式错误（应为 名称:数值,数值,...）：{item}")
        name, vals = item.split(":", 1)
        try:
            values = [float(x.strip()) for x in vals.split(",") if x.strip()]
        except ValueError as e:
            raise ValueError(f"系列数值无法解析：{item} -> {e}")
        out.append((name, values))
    return out


def make_chart(slide, chart_type: str, categories: list[str],
               series: list[tuple[str, list[float]]],
               title: str, x, y, w, h, cjk_font: str = DEFAULT_CJK_FONT) -> None:
    """在指定 slide 上添加原生图表。"""
    ct = CHART_TYPES.get(chart_type)
    if ct is None:
        raise ValueError(f"未知图表类型 {chart_type}（可选 {list(CHART_TYPES)}）")

    data = ChartData()
    data.categories = categories
    for name, values in series:
        data.add_series(name, values)

    graphic_frame = slide.shapes.add_chart(
        ct, Emu(x), Emu(y), Emu(w), Emu(h), data
    )
    chart = graphic_frame.chart

    # 标题
    if title:
        chart.has_title = True
        chart.chart_title.text_frame.text = title
        # 中文字体槽位（关键：防 CJK 回退）
        for run in chart.chart_title.text_frame.paragraphs[0].runs:
            run.font.name = cjk_font
            run.font.size = Pt(16)

    # 图例
    chart.has_legend = len(series) > 1
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False

    # 类别轴与数值轴字体（中文需要 ea 槽位）
    try:
        cat_ax = chart.category_axis
        if cat_ax and cat_ax.tick_labels and cat_ax.tick_labels.font:
            cat_ax.tick_labels.font.size = Pt(10)
        val_ax = chart.value_axis
        if val_ax and val_ax.tick_labels and val_ax.tick_labels.font:
            val_ax.tick_labels.font.size = Pt(10)
    except Exception:
        # 某些图表类型（如饼图）没有这些轴，静默跳过
        pass

    # 饼图：加数据标签
    if chart_type == "pie":
        try:
            plot = chart.plots[0]
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
            dl.font.size = Pt(10)
        except Exception:
            pass

    return graphic_frame


# ---------------------------------------------------------------------------
# 中文字体后处理：给图表 XML 显式补 <a:ea> 槽位
# ---------------------------------------------------------------------------


def inject_cjk_font(pptx_path: Path, cjk_font: str) -> int:
    """给 PPTX 里所有含中文文本的 run 补 <a:ea typeface="...">。

    原理：python-pptx 默认用主题字体（+mn-ea / +mj-ea），中文继承主题。
    主题若无中文字形则静默回退。扫描 slides/charts/slideLayouts 中含中文
    的 <a:r> run，缺 <a:ea> 则注入。

    返回注入的 run 数。
    """
    import re as _re
    injected = 0
    with zipfile.ZipFile(pptx_path, "r") as zin:
        items = {n: zin.read(n) for n in zin.namelist()}
    for name, content in list(items.items()):
        if not name.endswith(".xml"):
            continue
        if not ("/slides/" in name or "/charts/" in name or "/slideLayouts/" in name):
            continue
        text = content.decode("utf-8", errors="replace")
        if not _re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", text):
            continue

        def fix_run(m):
            nonlocal injected
            run_xml = m.group(0)
            if "<a:ea " in run_xml:
                return run_xml
            # 用 &quot; 避开 re.sub 替换模板里的引号转义歧义，
            # 输出时再还原为真实双引号（zip 里存的是 XML 文本）
            if "<a:latin" in run_xml:
                ea_tag = '<a:ea typeface="QQQ"/>'
                new_run = _re.sub(
                    r"(<a:latin[^/]*/>)",
                    lambda mo: mo.group(1) + ea_tag.replace("QQQ", cjk_font),
                    run_xml,
                )
                injected += 1
                return new_run
            new_run = run_xml.replace(
                "</a:rPr>",
                f'<a:ea typeface="{cjk_font}"/></a:rPr>',
            )
            injected += 1
            return new_run

        text = _re.sub(r"<a:r>.*?</a:r>", fix_run, text, flags=_re.S)
        items[name] = text.encode("utf-8")

    tmp = pptx_path.with_suffix(pptx_path.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in items.items():
            zout.writestr(name, content)
    tmp.replace(pptx_path)
    return injected


def main() -> int:
    ap = argparse.ArgumentParser(description="生成 PowerPoint 原生图表")
    ap.add_argument("--deck", help="在现有 PPTX 上叠加图表（不提供则新建）")
    ap.add_argument("--slide", type=int, help="目标 slide 序号（1 起），仅配合 --deck")
    ap.add_argument("--out", default=None, help="输出路径（默认 <原名>-charts.pptx 或 chart-demo.pptx）")
    ap.add_argument("--type", required=True, choices=sorted(CHART_TYPES), help="图表类型")
    ap.add_argument("--categories", required=True, help="类别，逗号分隔，如 'Q1,Q2,Q3'")
    ap.add_argument("--series", required=True, action="append",
                    help="系列，格式 '名称:v1,v2,...'，可多次传入多系列")
    ap.add_argument("--title", default="", help="图表标题")
    ap.add_argument("--x", type=float, default=0.8, help="左边距（英寸）")
    ap.add_argument("--y", type=float, default=2.2, help="上边距（英寸）")
    ap.add_argument("--w", type=float, default=8.5, help="宽度（英寸）")
    ap.add_argument("--h", type=float, default=4.5, help="高度（英寸）")
    ap.add_argument("--font", default=DEFAULT_CJK_FONT, help="中文字体（默认微软雅黑）")
    args = ap.parse_args()

    try:
        categories = [c.strip() for c in args.categories.split(",") if c.strip()]
        if not categories:
            raise ValueError("--categories 不能为空")
        series = parse_series(args.series)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1

    # 英寸 → EMU（python-pptx 内部用 EMU）
    INCH = 914400
    x = int(args.x * INCH)
    y = int(args.y * INCH)
    w = int(args.w * INCH)
    h = int(args.h * INCH)

    # 打开或新建演示文稿
    if args.deck:
        deck = Path(args.deck)
        if not deck.exists():
            print(f"[FAIL] 文件不存在: {deck}")
            return 1
        prs = Presentation(str(deck))
        if args.slide is not None:
            idx = args.slide - 1
            if idx < 0 or idx >= len(prs.slides):
                print(f"[FAIL] slide 序号越界：共 {len(prs.slides)} 页，请求 {args.slide}")
                return 1
            slide = prs.slides[idx]
        else:
            # 未指定 slide：在末尾新建一页
            slide = prs.slides.add_slide(prs.slide_layouts[6])
        out_path = Path(args.out) if args.out else deck.with_name(
            deck.stem + "-charts" + deck.suffix
        )
    else:
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白版式
        out_path = Path(args.out) if args.out else Path("chart-demo.pptx")

    try:
        make_chart(slide, args.type, categories, series,
                   args.title, x, y, w, h, cjk_font=args.font)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))

    # 后处理：显式注入中文字体 ea 槽位（防主题字体无中文字形时静默回退）
    injected = inject_cjk_font(out_path, args.font)

    print(f"✅ 原生图表已生成: {out_path}")
    print(f"  类型: {args.type} | 系列: {len(series)} | 类别: {len(categories)}")
    if injected:
        print(f"  中文字体后处理: 注入 <a:ea> 槽位 {injected} 处")
    print(f"  说明: 这是带「编辑数据」的真 Chart 对象，可在 PowerPoint 中直接改数据")
    return 0


if __name__ == "__main__":
    sys.exit(main())
