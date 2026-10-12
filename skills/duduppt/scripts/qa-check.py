#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPTX 机械检查（QA 清单的"机械项"部分）。

设计原则（对标 addsumtech 的成本论断）：
  "Before spending a round on a defect class, ask whether a lint could decide it.
   A round spent finding what a lint could have decided is a round wasted."
即：能靠 lint 秒判的，绝不用渲染图去看。

检查项（全部零依赖，仅标准库 zipfile + 正则）：
  1. 结构完整性      ZIP 可读、slide 数量、[Content_Types] 完整
  2. 占位文案         Lorem ipsum / TODO / 单击此处 / xxxx 等
  3. 图表             barDir 正确（防空白柱状图）、有数据点、中文轴标签有字体
  4. 中文字体         <a:ea> 槽位是否绑定（不是只查 typeface 出现过）
  5. 字体白名单      是否用了可能"投递后不存在"的字体
  6. 语言元数据      中文 run 上是否残留 lang="en-US"
  7. 整页大图        是否存在 base64 塞满整页的图片（破坏可编辑性）
  8. 字号范围        是否低于全局最小字号 GLOBAL_MIN_FONT_PT
  9. 文本溢出        （v3 静态 Critic）估文本总宽是否超框
 10. 元素遮挡        （v3 静态 Critic）同页两元素重叠超 30%
 11. 对比度不足      （v3 静态 Critic）文字与背景色亮度差过小

用法：
    python scripts/qa-check.py --deck output.pptx
    python scripts/qa-check.py --deck output.pptx --min-font 6.5 --format json

退出码 1 表示存在 FAIL 项（可用于交付门禁）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 可配置项（与 SKILL.md 的「关键技术参数」保持一致）---------------------
GLOBAL_MIN_FONT_PT = 6.5
PLACEHOLDERS = ["Lorem", " ipsum", "TODO", "FIXME", "xxxx", "XXX",
                "单击此处", "点击编辑", "占位", "placeholder", "待补充", "TBD"]

# 跨平台安全的中文字体（Windows 优先）
CJK_SAFE_FONTS = {
    "微软雅黑", "Microsoft YaHei",          # Windows 自带，覆盖最广
    "Noto Sans CJK SC", "Source Han Sans SC", "思源黑体",  # 跨平台开源
    "Hiragino Sans GB", "PingFang SC",       # macOS
    "宋体", "SimSun", "黑体", "SimHei",
}
# 已知"开发机有、收件人常没有"的字体（投递风险）
CJK_RISKY_FONTS = {
    "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",  # Linux 发行版字体
    "Droid Sans Fallback", "AR PL UMing",
}

FAILS: list[str] = []
WARNS: list[str] = []
PASSES: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)


def warn(msg: str) -> None:
    WARNS.append(msg)


def ok(msg: str) -> None:
    PASSES.append(msg)


# ---------------------------------------------------------------------------
# 1. 结构完整性
# ---------------------------------------------------------------------------
def check_structure(z: zipfile.ZipFile) -> list[str]:
    names = z.namelist()
    if z.testzip() is not None:
        fail("ZIP 损坏")
    slides = sorted(
        [n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        key=lambda x: int(re.search(r"(\d+)", x).group(1)),
    )
    if not slides:
        fail("没有找到任何 slide")
    else:
        ok(f"slide 数量: {len(slides)}")
    if "[Content_Types].xml" not in names:
        fail("缺 [Content_Types].xml")
    else:
        ok("[Content_Types].xml 存在")
    return slides


# ---------------------------------------------------------------------------
# 2. 占位文案
# ---------------------------------------------------------------------------
def check_placeholders(z: zipfile.ZipFile, slides: list[str]) -> None:
    found = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        texts = " ".join(re.findall(r"<a:t>([^<]*)</a:t>", xml))
        for bad in PLACEHOLDERS:
            if bad in texts:
                found.append(f"{n.split('/')[-1]}: '{bad}'")
    if found:
        for f in found:
            fail(f"占位文案残留: {f}")
    else:
        ok("无占位文案残留")


# ---------------------------------------------------------------------------
# 3. 图表（barDir / 数据点 / 中文轴字体）
# ---------------------------------------------------------------------------
def check_charts(z: zipfile.ZipFile) -> None:
    charts = [n for n in z.namelist() if re.match(r"ppt/charts/chart\d+\.xml$", n)]
    if not charts:
        ok("无图表（跳过图表检查）")
        return
    for c in charts:
        cx = z.read(c).decode("utf-8", "ignore")
        name = c.split("/")[-1]

        # 柱状图必须有合法 barDir（否则空白页）
        if "<c:barChart>" in cx:
            m = re.search(r'<c:barDir val="(\w+)"/>', cx)
            if not m:
                fail(f"{name}: barChart 缺 barDir（pptxgenjs 'column' 会产出空白页）")
            elif m.group(1) not in ("col", "bar"):
                fail(f"{name}: barDir 非法值 '{m.group(1)}'")
            else:
                ok(f"{name}: barDir={m.group(1)}")

        # 必须有数据点
        pts = re.findall(r"<c:pt ", cx)
        if pts:
            ok(f"{name}: 数据点 {len(pts)} 个")
        else:
            fail(f"{name}: 图表无数据点（空的）")

        # 中文轴标签需指定中文字体
        if re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", cx):
            if not any(f in cx for f in CJK_SAFE_FONTS):
                fail(f"{name}: 中文轴标签未指定中文字体（可能乱码）")


# ---------------------------------------------------------------------------
# 4 & 5. 中文字体槽位 + 字体白名单
# ---------------------------------------------------------------------------
def check_fonts(z: zipfile.ZipFile, slides: list[str]) -> None:
    ea_all: set[str] = set()
    latin_all: set[str] = set()
    risky: set[str] = set()
    problems: list[str] = []

    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        ea = set(re.findall(r'<a:ea typeface="([^"]+)"', xml))
        latin = set(re.findall(r'<a:latin typeface="([^"]+)"', xml))
        ea_all |= ea
        latin_all |= latin
        risky |= (ea | latin) & CJK_RISKY_FONTS

        has_cjk = bool(re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", xml))
        if has_cjk and not ea:
            problems.append(f"{n.split('/')[-1]}: CJK_NO_EA（有中文但未设 <a:ea>）")
        if (latin & CJK_SAFE_FONTS) and not ea:
            problems.append(f"{n.split('/')[-1]}: CJK_FACE_UNREACHED（中文字体写在 latin 槽位，不生效）")

    if problems:
        for p in problems:
            fail(p)
    elif ea_all:
        # 有 ea 槽位还不够 —— 必须确认 ea 槽位绑的是「中文字体」而非 Arial 之类
        ea_is_cjk = ea_all & CJK_SAFE_FONTS
        if ea_is_cjk:
            ok(f"中文字体已绑定 <a:ea>: {sorted(ea_is_cjk)}")
        else:
            fail(f"<a:ea> 槽位存在但绑的不是中文字体: {sorted(ea_all)}"
                 f"（应设为 {sorted(CJK_SAFE_FONTS)[:3]} 等；"
                 f"否则中文仍会回退到系统默认字体）")
    else:
        # 没有中文就不报错
        has_any_cjk = any(
            re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", z.read(n).decode("utf-8", "ignore"))
            for n in slides
        )
        if has_any_cjk:
            fail("存在中文但完全没有 <a:ea> 槽位")
        else:
            ok("无中文内容（跳过中文字体检查）")

    if risky:
        warn(f"投递风险字体（开发机有但收件人常无）: {sorted(risky)}"
             " —— 建议改用「微软雅黑」等跨平台字体")

    # 语言元数据残留（中文 run 上的 lang="en-US"）
    lang_bad = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        for m in re.finditer(r'lang="en-US"[^>]*>', xml):
            seg = xml[max(0, m.start() - 200):m.start()]
            if re.search(r"[\u4e00-\u9fff]", seg):
                lang_bad.append(n.split("/")[-1])
                break
    if lang_bad:
        warn(f"中文 run 上残留 lang=\"en-US\": {sorted(set(lang_bad))}")


# ---------------------------------------------------------------------------
# 6. 字号范围
# ---------------------------------------------------------------------------
def check_font_sizes(z: zipfile.ZipFile, slides: list[str], min_pt: float) -> None:
    tiny = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        for m in re.finditer(r'sz="(\d+)"', xml):
            pt = int(m.group(1)) / 100.0   # OOXML 里 sz 是 1/100 pt
            if pt < min_pt:
                tiny.append(f"{n.split('/')[-1]}: {pt}pt")
    if tiny:
        for t in tiny[:10]:
            warn(f"字号低于 {min_pt}pt: {t}")
        if len(tiny) > 10:
            warn(f"...另有 {len(tiny) - 10} 处")
    else:
        ok(f"字号均 ≥ {min_pt}pt")


# ---------------------------------------------------------------------------
# 7. 整页大图（破坏可编辑性）
# ---------------------------------------------------------------------------
def check_full_page_images(z: zipfile.ZipFile, slides: list[str]) -> None:
    big = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        # 找图片形状的尺寸（cx/cy 单位 EMU），整页约 12192000 x 6858000 (16:9)
        for m in re.finditer(r"<a:ext cx=\"(\d+)\" cy=\"(\d+)\"", xml):
            cx, cy = int(m.group(1)), int(m.group(2))
            if cx >= 11_000_000 and cy >= 6_000_000:
                big.append(n.split("/")[-1])
                break
    if big:
        warn(f"存在接近整页尺寸的图片（检查是否为整页截图当背景）: {sorted(set(big))}")
    else:
        ok("无整页大图")


# ---------------------------------------------------------------------------
# 8. 静态 Critic：文本溢出风险（估宽度超框）
# ---------------------------------------------------------------------------
def check_text_overflow(z: zipfile.ZipFile, slides: list[str]) -> None:
    """估算文本框内文字总宽是否可能超出框宽。

    依据（学 paper-ppt-agent 的静态 Critic）：逐 run 累加
    （sz * len(text)）的宽度估计，与 <a:ext cx> 比较。
    中文按 1.0 宽、ASCII 按 0.6 宽估算，超出 110% 报 WARN。
    """
    issues = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        # 每个 sp 文本框：取它的 cx 与所有 run 的 sz+text
        for sp in re.finditer(
            r"<p:sp>.*?<a:ext cx=\"(\d+)\" cy=\"(\d+)\".*?</p:sp>", xml, re.S
        ):
            cx = int(sp.group(1))
            if cx < 1_000_000:  # 忽略过小的装饰框
                continue
            block = sp.group(0)
            total_w = 0.0
            for run in re.finditer(
                r"<a:r>.*?sz=\"(\d+)\".*?<a:t>([^<]+)</a:t>.*?</a:r>", block, re.S
            ):
                pt = int(run.group(1)) / 100.0
                text = run.group(2)
                cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
                ascii_ = len(text) - cjk
                # 宽度估计：pt(EMU/12700=px 基准) × 字符宽
                total_w += pt * (cjk * 1.0 + ascii_ * 0.6)
            # EMU: 1pt = 12700 EMU
            est_emu = total_w * 12700
            if cx > 0 and est_emu > cx * 1.10:
                slide_name = n.split("/")[-1]
                ratio = est_emu / cx
                issues.append(f"{slide_name}: 文本宽估计超框 {ratio:.0%}")
                break
    if issues:
        for t in issues[:5]:
            warn(f"文本溢出风险: {t}")
    else:
        ok("无文本溢出风险")


# ---------------------------------------------------------------------------
# 9. 静态 Critic：元素遮挡（重叠）
# ---------------------------------------------------------------------------
def check_overlap(z: zipfile.ZipFile, slides: list[str]) -> None:
    """检测同页内两个文本/形状框是否存在明显重叠。

    简化判定：两个 <a:off x y> + <a:ext cx cy> 的矩形相交面积
    占较小框面积 >30% 即报。忽略装饰性小元素（<20000 EMU 边长）
    和整页背景框（面积 > 页面 50% 的元素不参与遮挡判定）。
    """
    # 16:9 页面约 12192000 x 6858000 EMU
    PAGE_AREA = 12_192_000 * 6_858_000
    issues = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        boxes = []
        # 按 sp 分组取元素（同 sp 内的文本框与其背景矩形天然重叠，不算遮挡）
        for sp in re.finditer(r"<p:sp>.*?</p:sp>", xml, re.S):
            block = sp.group(0)
            # 该 sp 的 off/ext
            m = re.search(
                r"<a:off x=\"(-?\d+)\" y=\"(-?\d+)\"/><a:ext cx=\"(\d+)\" cy=\"(\d+)\"",
                block,
            )
            if not m:
                continue
            x, y, cx, cy = map(int, m.groups())
            area = cx * cy
            if cx > 50_000 and cy > 50_000 and area < PAGE_AREA * 0.5:
                boxes.append((x, y, x + cx, y + cy))
        # 两两比较
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
                iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
                inter = ix * iy
                if inter <= 0:
                    continue
                area_a = (a[2] - a[0]) * (a[3] - a[1])
                area_b = (b[2] - b[0]) * (b[3] - b[1])
                smaller = min(area_a, area_b)
                ratio = inter / smaller
                # 排除"完全包含"关系（大框完全套住小框不算遮挡）
                contains = (ix == min(a[2], b[2]) - max(a[0], b[0]) and
                            iy == min(a[3], b[3]) - max(a[1], b[1]) and
                            (ix == (a[2] - a[0]) or ix == (b[2] - b[0])) and
                            (iy == (a[3] - a[1]) or iy == (b[3] - b[1])))
                if contains:
                    continue
                # 只报部分重叠且占比较小框 >60% 的情况
                if smaller > 0 and ratio > 0.60:
                    issues.append(
                        f"{n.split('/')[-1]}: 两元素重叠 {ratio:.0%}"
                    )
                    break
            else:
                continue
            break
    if issues:
        for t in issues[:5]:
            warn(f"元素遮挡: {t}")
    else:
        ok("无元素遮挡")


# ---------------------------------------------------------------------------
# 10. 静态 Critic：对比度不足（前景色 vs 背景色）
# ---------------------------------------------------------------------------
def check_contrast(z: zipfile.ZipFile, slides: list[str]) -> None:
    """检测文字颜色与填充背景色是否对比不足。

    简化版：找 <a:solidFill><a:srgbClr val="RRGGBB"/> 的文本颜色，
    与同 sp 的背景 <a:solidFill> 比较相对亮度差 <1.5 即报。
    """
    def _lum(rgb: str) -> float:
        try:
            r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        except (ValueError, IndexError):
            return -1.0

    issues = []
    for n in slides:
        xml = z.read(n).decode("utf-8", "ignore")
        for sp in re.finditer(r"<p:sp>.*?</p:sp>", xml, re.S):
            block = sp.group(0)
            fills = re.findall(r"<a:solidFill><a:srgbClr val=\"([0-9a-fA-F]{6})\"", block)
            if len(fills) < 2:
                continue
            lums = [_lum(f) for f in fills if _lum(f) >= 0]
            if len(lums) < 2:
                continue
            # 同 sp 内文字与背景亮度差过小
            if max(lums) - min(lums) < 40:
                issues.append(f"{n.split('/')[-1]}: 文字与背景对比度不足")
                break
    if issues:
        for t in issues[:5]:
            warn(f"对比度风险: {t}")
    else:
        ok("无对比度风险")


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="PPTX 机械检查（QA 机械项）")
    ap.add_argument("--deck", required=True, help=".pptx 文件")
    ap.add_argument("--min-font", type=float, default=GLOBAL_MIN_FONT_PT)
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    p = Path(args.deck)
    if not p.exists():
        print(f"[FAIL] 文件不存在: {p}")
        return 1
    if p.suffix.lower() not in (".pptx", ".pptm"):
        print(f"[FAIL] 仅支持 .pptx/.pptm: {p}")
        return 1

    try:
        with zipfile.ZipFile(p) as z:
            slides = check_structure(z)
            if slides:
                check_placeholders(z, slides)
                check_charts(z)
                check_fonts(z, slides)
                check_font_sizes(z, slides, args.min_font)
                check_full_page_images(z, slides)
                # 静态 Critic（v3 新增）
                check_text_overflow(z, slides)
                check_overlap(z, slides)
                check_contrast(z, slides)
    except zipfile.BadZipFile:
        print(f"[FAIL] 不是有效的 pptx（zip）文件: {p}")
        return 1

    if args.format == "json":
        print(json.dumps({
            "file": str(p),
            "passes": PASSES, "warnings": WARNS, "failures": FAILS,
            "summary": {"pass": len(PASSES), "warn": len(WARNS), "fail": len(FAILS)},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"机械检查: {p.name}")
        print("=" * 56)
        for x in PASSES:
            print(f"  [PASS] {x}")
        for x in WARNS:
            print(f"  [WARN] {x}")
        for x in FAILS:
            print(f"  [FAIL] {x}")
        print("=" * 56)
        print(f"通过 {len(PASSES)} / 警告 {len(WARNS)} / 失败 {len(FAILS)}")
        if FAILS:
            print("\n⚠️ 存在 FAIL 项，必须修复后才能交付。")
        elif WARNS:
            print("\n有 WARN 项，建议复核（未必是问题）。")
        else:
            print("\n机械检查全部通过 —— 接下来只剩「视觉项」需要渲染验收。")

    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
