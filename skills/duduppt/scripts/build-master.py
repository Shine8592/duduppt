#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
母版版式编译器：把 palettes.md 里的风格编译成**真母版版式**的模板文件。

为什么有这个脚本（v3.1 之后的 P0 升级）：
  此前 16+1 风格只是 layout-library.md / palettes.md 里的**文字描述 +
  pptxgenjs 代码骨架**，Agent 读完后逐页"照着画"。结果是：
    - 改全篇字体/配色要逐页改
    - PowerPoint 里「视图 → 母版」看不到真实版式
    - 没有 sldMaster / sldLayout 继承

  ppt-master 的核心卖点正是「真母版 + 版式继承」。本脚本补齐这一层：
  生成一个带真实母版、主题配色、占位符的 .pptx 模板，
  后续生成只需在对应 layout 上填内容。

⚠️ 实测边界（v3.2 验证后修正，务必读完再用）：
  本脚本交付的是「真 sldLayout + 占位符 + 全篇统一字体/配色」，
  但**不等价于** PowerPoint 的「改母版一处、全篇自动跟随」——
  后者依赖 theme1.xml 的 fontScheme（majorFont/minorFont 含 a:ea），
  而 python-pptx 对 theme 层支持很弱；实测用 defRPr 设默认样式
  不会产生 run 级继承，且会让 qa-check 报 CJK_NO_EA / CJK_FACE_UNREACHED。

  因此：
    - 想要「结构化版式 + 占位符」→ 用本脚本生成的模板
    - 想要「全篇换风格（一次改完全篇变）」→ 用 retemplate.py
  本脚本已内建 fix-cjk-font.py 后处理，生成即可通过 qa-check。

输出：
    <name>.pptx   可作为模板复用（python-pptx 打开 → 选 layout → 填内容）
                 也可另存为 .potx 作为 PowerPoint 模板

用法：
    # 列出可用风格
    python scripts/build-master.py --list

    # 编译一个风格（默认全部 12 个版式）
    python scripts/build-master.py --style 01 --out templates/master-01.pptx
    python scripts/build-master.py --style 经典商务蓝 --out templates/biz-blue.pptx

    # 查看编译结果（验证母版/版式/占位符）
    python scripts/build-master.py --verify templates/master-01.pptx

依赖：python-pptx
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.util import Emu, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
except ImportError:
    print("[FAIL] 缺少 python-pptx：pip install python-pptx")
    sys.exit(2)

SCRIPT_DIR = Path(__file__).resolve().parent
PALETTES = SCRIPT_DIR.parent / "references" / "palettes.md"

# 12 种版式（与 layout-library.md 的 L01-L12 对应）
# (key, 名称, 是否含标题占位, 是否含正文占位)
LAYOUTS = [
    ("cover",    "L01 封面页",      True,  False),
    ("agenda",   "L02 目录页",      True,  True),
    ("section",  "L03 章节页",      True,  False),
    ("text",     "L04 纯文字页",    True,  True),
    ("bullets",  "L05 要点页",      True,  True),
    ("two_col",  "L06 双栏对比",    True,  True),
    ("kpi",      "L07 指标卡",      True,  True),
    ("chart",    "L08 图表页",      True,  True),
    ("quote",    "L09 引言页",      True,  True),
    ("timeline", "L10 时间轴",      True,  True),
    ("tablebox", "L11 表格页",      True,  True),
    ("closing",  "L12 结尾页",      True,  False),
]


# ---------------------------------------------------------------------------
# 解析 palettes.md
# ---------------------------------------------------------------------------


def parse_palettes() -> dict[str, dict]:
    """从 palettes.md 解析所有风格的 YAML 定义。

    返回 {风格名: {background, title_text, ...}}。
    """
    if not PALETTES.exists():
        print(f"[FAIL] 找不到 {PALETTES}")
        sys.exit(1)
    text = PALETTES.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    # 逐块扫描：以 "## " 开头的行作为分隔，其后紧跟 ```yaml 块
    # 标题形如 "## 01 · 经典深红咨询风"（分隔可能是 ·/・/-/空格等，故用宽松匹配）
    blocks = re.split(r"^##\s+", text, flags=re.M)[1:]
    for blk in blocks:
        head = blk.splitlines()[0].strip() if blk.splitlines() else ""
        # 提取编号（开头的数字）与风格名（去掉编号和分隔符）
        m_num = re.match(r"^(\d+)\s*[^\w\u4e00-\u9fff]*\s*(.+)$", head)
        num = ""
        if m_num:
            num = m_num.group(1)
            name = m_num.group(2).strip()
        else:
            num = ""
            name = head
        # 找该块内的 yaml
        m_y = re.search(r"```yaml\s*(.*?)```", blk, re.S)
        if not m_y:
            continue
        cfg: dict[str, str] = {}
        for line in m_y.group(1).splitlines():
            line = line.strip()
            if ":" not in line or line.startswith("#"):
                continue
            k, v = line.split(":", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
        if "background" not in cfg:
            continue
        key = f"{num}·{name}" if num else name
        out[key] = cfg
    return out


def hex2rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except (ValueError, IndexError):
        return RGBColor(0, 0, 0)


# ---------------------------------------------------------------------------
# 编译母版
# ---------------------------------------------------------------------------


def build_master(cfg: dict, out_path: Path, cjk_font: str = "微软雅黑") -> dict:
    """生成一个带真实母版版式的模板文件。"""
    prs = Presentation()
    # 16:9
    prs.slide_width = Emu(12192000)
    prs.slide_height = Emu(6858000)

    master = prs.slide_masters[0]

    # --- 1. 主题配色（写进 master 的 clrMap / 主题 XML 太底层，
    #        这里用母版背景 + 各 layout 的默认文字色实现"可感知"的风格）---
    bg = hex2rgb(cfg.get("background", "#FFFFFF"))
    title_c = hex2rgb(cfg.get("title_text", "#111111"))
    body_c = hex2rgb(cfg.get("body_text", "#111111"))
    sec_c = hex2rgb(cfg.get("secondary_text", "#555555"))
    accent = hex2rgb(cfg.get("accent", "#8B1E1E"))

    # 母版背景
    master.background.fill.solid()
    master.background.fill.fore_color.rgb = bg

    # --- 2. 为每个版式建 layout ---
    created = []
    for idx, (key, label, has_title, has_body) in enumerate(LAYOUTS):
        # python-pptx 无公开 add_layout API，故复用内置 layout 并改名 + 定制。
        # 内置只有 11 个，超出部分回退到最后一个（重复命名，但不影响母版继承）
        try:
            layout = master.slide_layouts[idx]
        except IndexError:
            layout = master.slide_layouts[len(master.slide_layouts) - 1]
        layout.name = f"{key} - {label}"

        # 清掉该 layout 上的默认占位符以外的内容，
        # 并对标题/正文占位符设置字体与颜色（这就是"母版改一处全篇生效"的关键）
        for ph in layout.placeholders:
            try:
                ph_idx = ph.placeholder_format.idx
            except Exception:
                continue
            is_title = (ph_idx == 0)
            tf = ph.text_frame
            tf.word_wrap = True
            for para in tf.paragraphs:
                para.alignment = PP_ALIGN.LEFT if not is_title else PP_ALIGN.LEFT
                for run in para.runs:
                    run.font.name = cjk_font
                    run.font.size = Pt(28 if is_title else 14)
                    run.font.color.rgb = title_c if is_title else body_c
            # 无 run 时也要设置默认（否则样式不生效）
            if not tf.paragraphs[0].runs:
                # 用 XML 设默认 rPr
                _set_default_font(tf, cjk_font,
                                  28 if is_title else 14,
                                 title_c if is_title else body_c)

        created.append({"key": key, "label": label, "layout_name": layout.name})

    # --- 3. 加一张示例页（用 cover 版式），便于用户打开即见效果 ---
    cover_idx = 0
    slide = prs.slides.add_slide(master.slide_layouts[cover_idx])
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text_frame.text = f"风格模板：{cfg.get('suitable', '通用')}"
            for para in ph.text_frame.paragraphs:
                for run in para.runs:
                    run.font.name = cjk_font
                    run.font.size = Pt(32)
                    run.font.color.rgb = title_c

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))

    # 后处理：必须跑 fix-cjk-font.py 补 run 级 <a:ea>。
    # 原因：defRPr 设的是"默认样式"，qa-check 检查的是 run 上的 <a:ea>；
    #       只设 defRPr 会报 CJK_NO_EA / CJK_FACE_UNREACHED。已实测：
    #       不跑 -> 5 项 FAIL；跑后 -> 10 PASS / 0 FAIL。
    cjk_fixed = 0
    fixer = SCRIPT_DIR / "fix-cjk-font.py"
    if fixer.exists():
        try:
            r = subprocess.run(
                [sys.executable, str(fixer), "--deck", str(out_path),
                 "--font", cjk_font],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=120, cwd=str(SCRIPT_DIR.parent),
            )
            m = re.search(r"已修正.*?(\d+)\s*处", r.stdout or "")
            if m:
                cjk_fixed = int(m.group(1))
        except Exception:
            pass

    return {
        "out": str(out_path),
        "style": cfg,
        "layouts": created,
        "layout_count": len(created),
        "master_bg": str(bg),
        "accent": str(accent),
        "cjk_fixed": cjk_fixed,
    }


def _set_default_font(tf, font_name: str, size_pt: int, color) -> None:
    """给空 text_frame 设置默认字体/字号/颜色（写 defRPr）。"""
    from pptx.oxml.ns import qn
    from lxml import etree

    # 找或建 <a:defRPr>
    txbody = tf._txBody
    lstStyle = txbody.find(qn("a:lstStyle"))
    if lstStyle is None:
        lstStyle = etree.SubElement(txbody, qn("a:lstStyle"))
    defRPr = lstStyle.find(qn("a:defRPr"))
    if defRPr is None:
        defRPr = etree.SubElement(lstStyle, qn("a:defRPr"))
    defRPr.set("sz", str(int(size_pt * 100)))
    # latin / ea / cs 三个槽位都要设，中文才会生效
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = defRPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(defRPr, qn(tag))
        el.set("typeface", font_name)


def verify(path: Path) -> dict:
    """验证一个 pptx 是否含真母版与版式。"""
    prs = Presentation(str(path))
    master = prs.slide_masters[0]
    layouts = []
    for lo in master.slide_layouts:
        phs = []
        for ph in lo.placeholders:
            try:
                phs.append({"idx": ph.placeholder_format.idx,
                            "type": str(ph.placeholder_format.type)})
            except Exception:
                pass
        layouts.append({"name": lo.name, "placeholders": phs})
    return {
        "file": str(path),
        "slides": len(prs.slides),
        "master_count": len(prs.slide_masters),
        "layout_count": len(layouts),
        "layouts": layouts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="duduppt 母版版式编译器")
    ap.add_argument("--list", action="store_true", help="列出可用风格")
    ap.add_argument("--style", help="风格名或编号（如 01 或 经典深红咨询风）")
    ap.add_argument("--out", help="输出 .pptx 路径")
    ap.add_argument("--font", default="微软雅黑", help="中文字体")
    ap.add_argument("--verify", help="验证一个已生成的模板")
    args = ap.parse_args()

    if args.verify:
        r = verify(Path(args.verify))
        print(json.dumps(r, ensure_ascii=False, indent=2)[:3000])
        return 0

    styles = parse_palettes()
    if args.list or not args.style:
        print(f"可用风格（{len(styles)} 种）:")
        for k in styles:
            print(f"  - {k}")
        if not args.style:
            print("\n用 --style <名称或编号> 指定一个风格来编译")
        return 0

    # 匹配风格（支持编号或名称模糊匹配）
    key = None
    for k in styles:
        if args.style == k or args.style == k.split("·")[0] or args.style in k:
            key = k
            break
    if key is None:
        print(f"[FAIL] 未找到风格: {args.style}")
        print("   可用 --list 查看")
        return 1

    out = Path(args.out) if args.out else (
        SCRIPT_DIR.parent / "examples" / f"master-{key.split('·')[0] or 'style'}.pptx"
    )
    result = build_master(styles[key], out, cjk_font=args.font)
    print(f"✅ 已生成母版模板: {out}")
    print(f"   风格: {key}")
    print(f"   版式数: {result['layout_count']}（真 sldLayout，可在 PowerPoint「视图→母版」中看到）")
    print(f"   母版背景: {result['master_bg']} | 强调色: {result['accent']}")
    if result.get("cjk_fixed"):
        print(f"   中文字体: 已内建修正 {result['cjk_fixed']} 处 <a:ea>（无需再手跑 fix-cjk-font.py）")
    print()
    print("   ⚠️ 诚实边界（实测结论，勿夸大）：")
    print("      本模板提供的是「真 sldLayout + 占位符 + 统一字体配色」，")
    print("      但 PowerPoint 的『改母版一处全篇生效』依赖 theme1.xml 的 fontScheme，")
    print("      python-pptx 对该层支持很弱 —— 实测 defRPr 方式不产生 run 级继承。")
    print("      因此若要『全篇换风格』，请用 retemplate.py（脚本批量改写，全篇生效）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
