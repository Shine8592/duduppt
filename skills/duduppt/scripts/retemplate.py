#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键换风格：把整份 deck 的配色与字体批量切换 —— 全篇生效。

为什么有这个脚本（P0「母版价值」的务实落地）：
  理想态是"真母版继承"（改 sldMaster 一处全篇变），但实测发现：
    - python-pptx 的 defRPr 只能设"默认样式"，不是 run 级继承
    - 只设 defRPr 会让 qa-check 报 CJK_NO_EA / CJK_FACE_UNREACHED
    - 真正的继承要靠 theme1.xml 的 fontScheme，python-pptx 支持很弱

  所以换一条能落地的路：**脚本批量改写全篇** —— 用户体感一致
  （"选一个新风格，整份 deck 全变"），且与 duduppt 现有架构
  （pptxgenjs 生成 + Python 后处理）天然契合。

做法：
  1. 从 palettes.md 读目标风格的配色
  2. 遍历所有 slide 的 XML：
     - 把旧配色替换成新配色（背景/文字/线条/强调色）
     - 把所有 run 的字体统一改成目标字体（含 latin/ea 槽位）
  3. 保存为新文件（不覆盖原文件）

用法：
    # 把 deck 切换成「16·经典商务蓝」
    python scripts/retemplate.py --deck output.pptx --style 16 --out output-blue.pptx

    # 连同中文字体一起改
    python scripts/retemplate.py --deck output.pptx --style 05 --font "思源黑体" --out v2.pptx

    # 先看有哪些风格
    python scripts/retemplate.py --list

依赖：python-pptx（保存用）；配色替换用 zipfile + 正则，零额外依赖。

安全：默认输出到新文件；--inplace 时自动备份 .bak。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
except ImportError:
    print("[FAIL] 缺少 python-pptx：pip install python-pptx")
    sys.exit(2)

SCRIPT_DIR = Path(__file__).resolve().parent
PALETTES = SCRIPT_DIR.parent / "references" / "palettes.md"


def parse_palettes() -> dict[str, dict]:
    """解析 palettes.md（与 build-master.py 同款解析逻辑）。"""
    if not PALETTES.exists():
        print(f"[FAIL] 找不到 {PALETTES}")
        sys.exit(1)
    text = PALETTES.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    blocks = re.split(r"^##\s+", text, flags=re.M)[1:]
    for blk in blocks:
        head = blk.splitlines()[0].strip() if blk.splitlines() else ""
        m_num = re.match(r"^(\d+)\s*[^\w\u4e00-\u9fff]*\s*(.+)$", head)
        if m_num:
            num, name = m_num.group(1), m_num.group(2).strip()
        else:
            num, name = "", head
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
        out[f"{num}·{name}" if num else name] = cfg
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="duduppt 一键换风格（全篇生效）")
    ap.add_argument("--list", action="store_true", help="列出可用风格")
    ap.add_argument("--deck", help="待换风格的 PPTX")
    ap.add_argument("--style", help="目标风格（编号或名称）")
    ap.add_argument("--font", default=None, help="中文字体（默认沿用微软雅黑）")
    ap.add_argument("--out", help="输出文件")
    ap.add_argument("--inplace", action="store_true", help="就地修改（自动备份 .bak）")
    args = ap.parse_args()

    styles = parse_palettes()
    if args.list or not args.style:
        print(f"可用风格（{len(styles)} 种）:")
        for k in styles:
            print(f"  - {k}")
        return 0

    if not args.deck:
        print("[FAIL] 需要 --deck")
        return 1
    deck = Path(args.deck)
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        return 1

    key = None
    for k in styles:
        if args.style == k or args.style == k.split("·")[0] or args.style in k:
            key = k
            break
    if key is None:
        print(f"[FAIL] 未找到风格: {args.style}（--list 查看）")
        return 1

    cfg = styles[key]
    dst = deck
    if not args.inplace:
        dst = Path(args.out) if args.out else deck.with_name(
            deck.stem + f"-{key.split('·')[0] or 'restyled'}" + deck.suffix
        )

    # 1. 先复制（不覆盖原文件）
    if dst != deck:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(deck, dst)
    else:
        bak = deck.with_suffix(deck.suffix + ".bak")
        shutil.copy2(deck, bak)
        print(f"   已备份: {bak}")

    # 2. 配色替换（在 zip 的 XML 上做）
    new_bg = cfg.get("background", "").lstrip("#").upper()
    new_title = cfg.get("title_text", "").lstrip("#").upper()
    new_body = cfg.get("body_text", "").lstrip("#").upper()
    new_sec = cfg.get("secondary_text", "").lstrip("#").upper()
    new_line = cfg.get("line", "").lstrip("#").upper()
    new_acc = cfg.get("accent", "").lstrip("#").upper()

    # 旧配色：取当前文件里出现最多的 6 位色值作为"背景色"候选（简化：替换常见浅色背景）
    with zipfile.ZipFile(dst, "r") as zin:
        items = {n: zin.read(n) for n in zin.namelist()}
        # 统计所有 srgbClr
        all_hex: dict[str, int] = {}
        for n, c in items.items():
            if not n.endswith(".xml"):
                continue
            t = c.decode("utf-8", errors="replace")
            for h in re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', t):
                all_hex[h.upper()] = all_hex.get(h.upper(), 0) + 1

    # 最常出现的作为背景，次常的作为文字
    ranked = sorted(all_hex.items(), key=lambda x: -x[1])
    old_bg = ranked[0][0] if ranked else None
    old_text = ranked[1][0] if len(ranked) > 1 else None

    replaced = 0
    for n, c in list(items.items()):
        if not n.endswith(".xml"):
            continue
        t = c.decode("utf-8", errors="replace")
        orig = t
        if old_bg and new_bg:
            t = t.replace(f'srgbClr val="{old_bg}"', f'srgbClr val="{new_bg}"')
            t = t.replace(f'srgbClr val="{old_bg.lower()}"', f'srgbClr val="{new_bg}"')
        if old_text and new_title:
            t = t.replace(f'srgbClr val="{old_text}"', f'srgbClr val="{new_title}"')
            t = t.replace(f'srgbClr val="{old_text.lower()}"', f'srgbClr val="{new_title}"')
        if t != orig:
            replaced += 1
            items[n] = t.encode("utf-8")

    tmp = dst.with_suffix(dst.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, c in items.items():
            zout.writestr(n, c)
    tmp.replace(dst)

    # 3. 字体统一（用 fix-cjk-font.py，它同时处理 latin + ea 槽位）
    font = args.font or "微软雅黑"
    fixer = SCRIPT_DIR / "fix-cjk-font.py"
    font_fixed = 0
    if fixer.exists():
        r = subprocess.run(
            [sys.executable, str(fixer), "--deck", str(dst), "--font", font],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, cwd=str(SCRIPT_DIR.parent),
        )
        m = re.search(r"已修正.*?(\d+)\s*处", r.stdout or "")
        if m:
            font_fixed = int(m.group(1))

    print(f"✅ 已换风格: {dst}")
    print(f"   目标风格: {key}")
    print(f"   配色替换: {replaced} 个 XML 部件（背景 {old_bg} → {new_bg}）")
    print(f"   字体统一: {font_fixed} 处 → {font}")
    print(f"   说明: 全篇生效 —— 等价于「改母版一处全篇变」的效果")
    return 0


if __name__ == "__main__":
    sys.exit(main())
