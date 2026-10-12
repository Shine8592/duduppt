#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMML 原生公式：把数学公式写成 PowerPoint 可编辑的 OMML 对象。

为什么有这个脚本（竞品对比 v3 的 P2 升级）：
  ppt-master 支持 OMML 原生公式（PowerPoint 2010+ 可双击编辑）。
  学术 / 技术 / 金融建模场景刚需 —— 公式若是图片就改不了。

生成的公式：
  - 是真 OMML 对象（<m:oMath>），可在 PowerPoint 里双击编辑
  - 不是图片、不是 Unicode 拼凑

支持的输入（简化语法，够用即可）：
    frac        a/b                分数
    sqrt        sqrt(x)            根号
    power       x^2               上标
    sub         x_1               下标
    plain       纯文本/线性公式

用法：
    # 分数
    python scripts/omml-formula.py --deck out.pptx --slide 2 \
        --type frac --num "a" --den "b" --x 1 --y 3 --w 4 --h 1.5

    # 上标（x 的平方）
    python scripts/omml-formula.py --deck out.pptx --slide 2 \
        --type power --base "x" --exp "2"

    # 根号
    python scripts/omml-formula.py --deck out.pptx --slide 2 \
        --type sqrt --radicand "x+1"

    # 线性公式（直接写）
    python scripts/omml-formula.py --deck out.pptx --slide 2 \
        --type plain --text "E = mc^2"

说明：
  - 本脚本构造 OMML XML 并直接写入 slide 的 XML（python-pptx 不直接支持）
  - 依赖 python-pptx（用于打开/保存）
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:
    print("[FAIL] 缺少 python-pptx：pip install python-pptx")
    sys.exit(2)

# OMML 命名空间
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def esc(s: str) -> str:
    """XML 转义。"""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def run_text(t: str) -> str:
    """构造 OMML 的 <m:r><m:t> 文本 run。"""
    t = esc(t)
    if not t.strip():
        t = t.replace(" ", "&#160;")  # 空格保形
    return f'<m:r><m:t>{t}</m:t></m:r>'


def build_omml(kind: str, args) -> str:
    """按类型构造 OMML XML。"""
    if kind == "frac":
        num = args.num or ""
        den = args.den or ""
        return (
            f'<m:f><m:num>{run_text(num)}</m:num>'
            f'<m:den>{run_text(den)}</m:den></m:f>'
        )
    if kind == "sqrt":
        rad = args.radicand or ""
        return (
            f'<m:rad><m:deg>{run_text("")}</m:deg>'
            f'<m:e>{run_text(rad)}</m:e></m:rad>'
        )
    if kind == "power":
        base = args.base or ""
        exp = args.exp or ""
        return (
            f'<m:sSup><m:e>{run_text(base)}</m:e>'
            f'<m:sup>{run_text(exp)}</m:sup></m:sSup>'
        )
    if kind == "sub":
        base = args.base or ""
        sub = args.sub or ""
        return (
            f'<m:sSub><m:e>{run_text(base)}</m:e>'
            f'<m:sub>{run_text(sub)}</m:sub></m:sSub>'
        )
    if kind == "plain":
        return run_text(args.text or "")
    raise ValueError(f"未知公式类型: {kind}")


def wrap_omath(inner: str) -> str:
    """把内部 OMML 包成 <m:oMath> 段落。"""
    return (
        f'<m:oMathPara xmlns:m="{M}">'
        f'<m:oMath>{inner}</m:oMath>'
        f'</m:oMathPara>'
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="写入 PowerPoint 原生 OMML 公式")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--slide", type=int, required=True, help="页码（1 起）")
    ap.add_argument("--type", required=True,
                    choices=["frac", "sqrt", "power", "sub", "plain"])
    ap.add_argument("--num"), ap.add_argument("--den")
    ap.add_argument("--radicand")
    ap.add_argument("--base"), ap.add_argument("--exp"), ap.add_argument("--sub")
    ap.add_argument("--text")
    ap.add_argument("--x", type=float, default=1.0, help="左边距（英寸）")
    ap.add_argument("--y", type=float, default=3.0, help="上边距（英寸）")
    ap.add_argument("--w", type=float, default=4.0, help="宽度（英寸）")
    ap.add_argument("--h", type=float, default=1.2, help="高度（英寸）")
    ap.add_argument("--out", help="输出文件（默认 <原名>-formula.pptx）")
    ap.add_argument("--inplace", action="store_true", help="就地修改（自动备份）")
    args = ap.parse_args()

    # 校验必填参数
    need = {
        "frac": ["num", "den"], "sqrt": ["radicand"],
        "power": ["base", "exp"], "sub": ["base", "sub"],
        "plain": ["text"],
    }[args.type]
    missing = [k for k in need if not getattr(args, k, None)]
    if missing:
        print(f"[FAIL] --type {args.type} 需要参数: {', '.join('--' + m for m in missing)}")
        return 1

    deck = Path(args.deck)
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        return 1
    prs = Presentation(str(deck))
    if args.slide < 1 or args.slide > len(prs.slides):
        print(f"[FAIL] 页码越界：共 {len(prs.slides)} 页，请求 {args.slide}")
        return 1
    slide = prs.slides[args.slide - 1]

    try:
        inner = build_omml(args.type, args)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1
    omath = wrap_omath(inner)

    INCH = 914400
    x = int(args.x * INCH)
    y = int(args.y * INCH)
    w = int(args.w * INCH)
    h = int(args.h * INCH)

    # 用 python-pptx 加一个文本框，然后把它替换成 OMML
    # 做法：加文本框拿 shape，再直接改其 <a:txBody> 为 OMML 容器
    from pptx.util import Emu as _E
    shape = slide.shapes.add_textbox(_E(x), _E(y), _E(w), _E(h))
    tf = shape.text_frame
    tf.text = ""  # 清空

    # 把 OMML 注入到 txBody
    txbody = shape._element.find(
        "{http://schemas.openxmlformats.org/presentationml/2006/main}txBody"
    )
    if txbody is None:
        # 找不到 txBody（少见），用 spTree 直接追加
        print("[FAIL] 无法定位文本框的 txBody")
        return 1

    # 清空原有段落，插入 OMML
    for child in list(txbody):
        if child.tag.endswith("}p"):
            txbody.remove(child)

    from lxml import etree  # python-pptx 依赖 lxml
    ns_p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    # <a:p> 里放 <m:oMathPara>
    p_elem = etree.SubElement(txbody, f"{{{ns_a}}}p")
    omath_elem = etree.fromstring(omath.encode("utf-8"))
    p_elem.append(omath_elem)

    if args.inplace:
        bak = deck.with_suffix(deck.suffix + ".bak")
        shutil.copy2(deck, bak)
        prs.save(str(deck))
        print(f"✅ 已就地写入 OMML 公式: {deck}（备份 {bak}）")
    else:
        dst = Path(args.out) if args.out else deck.with_name(
            deck.stem + "-formula" + deck.suffix
        )
        dst.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(dst))
        print(f"✅ 已写入 OMML 公式: {dst}")
    print(f"   类型: {args.type} | 位置: 第 {args.slide} 页")
    print(f"   说明: 这是原生 OMML，可在 PowerPoint 中双击编辑")
    return 0


if __name__ == "__main__":
    sys.exit(main())
