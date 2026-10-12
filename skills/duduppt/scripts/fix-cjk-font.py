#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体后处理：修正 pptx 里中文 run 的东亚字体槽位（<a:ea>）。

## 为什么需要它

OOXML 里每个 run 的字体分两个槽位：

    <a:rPr>
      <a:latin typeface="Arial"/>          <- 拉丁/数字
      <a:ea   typeface="Arial" charset="-122"/>   <- 中文（East Asian）
    </a:rPr>

**pptxgenjs 的 `fontFace` 只会写这两个槽位为同一个值**。所以当你写
`fontFace: 'Arial'` 生成中文内容时，中文槽位也是 Arial ——
而 Arial 没有中文字形，中文会静默回退到系统默认字体。

本脚本在生成后把 `<a:ea>` 槽位改成真正的中文字体（默认「微软雅黑」），
并可选择同时把 `<a:latin>` 也换掉（英文数字也跟着变，视需求）。

## 用法

    # 只修 ea 槽位（拉丁保持原样）—— 推荐
    python scripts/fix-cjk-font.py --deck output.pptx

    # 同时把 latin 也换成中文字体
    python scripts/fix-cjk-font.py --deck output.pptx --latin-too

    # 指定字体
    python scripts/fix-cjk-font.py --deck output.pptx --font "Noto Sans CJK SC"

    # 只检查不修改
    python scripts/fix-cjk-font.py --deck output.pptx --dry-run

零依赖（仅标准库）。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 推荐的跨平台中文字体（按覆盖率排序）
DEFAULT_CJK_FONT = "微软雅黑"

CJK_SAFE = {
    "微软雅黑", "Microsoft YaHei",
    "Noto Sans CJK SC", "Source Han Sans SC", "思源黑体",
    "Hiragino Sans GB", "PingFang SC",
    "宋体", "SimSun", "黑体", "SimHei",
}


def _fix_slide_xml(xml: str, cjk_font: str, latin_too: bool, latin_font: str) -> tuple[str, int, int]:
    """修正单个 slide 的字体槽位，返回 (新xml, ea修正数, latin修正数)。"""
    ea_fixed = 0
    latin_fixed = 0

    # 1) <a:ea .../> —— 自闭合
    def repl_ea_self(m: re.Match) -> str:
        nonlocal ea_fixed
        tf = m.group(1)
        if tf in CJK_SAFE:
            return m.group(0)
        ea_fixed += 1
        # 保留其他属性（如 charset），只换 typeface
        rest = m.group(2) or ""
        return f'<a:ea typeface="{cjk_font}"{rest}/>'

    xml = re.sub(r'<a:ea typeface="([^"]*)"([^>]*)/>', repl_ea_self, xml)

    # 2) <a:ea ...></a:ea> —— 成对
    def repl_ea_pair(m: re.Match) -> str:
        nonlocal ea_fixed
        tf = m.group(1)
        if tf in CJK_SAFE:
            return m.group(0)
        ea_fixed += 1
        rest = m.group(2) or ""
        return f'<a:ea typeface="{cjk_font}"{rest}></a:ea>'

    xml = re.sub(r'<a:ea typeface="([^"]*)"([^>]*)></a:ea>', repl_ea_pair, xml)

    # 3) 若完全没有 <a:ea>，则为含中文的 rPr 补一个
    if "<a:ea" not in xml and re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", xml):
        def add_ea(m: re.Match) -> str:
            nonlocal ea_fixed
            block = m.group(0)
            if re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", block) and "<a:ea" not in block:
                ea_fixed += 1
                # 插到 <a:latin .../> 之后；没有 latin 就插到 rPr 开头后
                if "<a:latin" in block:
                    return re.sub(r"(<a:latin[^>]*/>)",
                                  r'\1' + f'<a:ea typeface="{cjk_font}"/>', block, count=1)
                return re.sub(r"(<a:rPr[^>]*>)", r'\1' + f'<a:ea typeface="{cjk_font}"/>', block, count=1)
            return block

        # 以 <a:r>...</a:r> 为单位处理
        xml = re.sub(r"<a:r>.*?</a:r>", add_ea, xml, flags=re.S)

    # 4) 可选：latin 也换
    if latin_too:
        def repl_latin(m: re.Match) -> str:
            nonlocal latin_fixed
            tf = m.group(1)
            if tf == latin_font:
                return m.group(0)
            latin_fixed += 1
            rest = m.group(2) or ""
            return f'<a:latin typeface="{latin_font}"{rest}/>'

        xml = re.sub(r'<a:latin typeface="([^"]*)"([^>]*)/>', repl_latin, xml)

    return xml, ea_fixed, latin_fixed


def main() -> int:
    ap = argparse.ArgumentParser(description="修正 pptx 中文东亚字体槽位（<a:ea>）")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--font", default=DEFAULT_CJK_FONT, help=f"中文字体（默认 {DEFAULT_CJK_FONT}）")
    ap.add_argument("--latin-too", action="store_true", help="同时替换 <a:latin>（英文数字也变）")
    ap.add_argument("--latin-font", default=None, help="latin 槽位目标字体（默认与 --font 相同）")
    ap.add_argument("--dry-run", action="store_true", help="只报告不修改")
    args = ap.parse_args()

    p = Path(args.deck)
    if not p.exists():
        print(f"[FAIL] 文件不存在: {p}")
        return 1
    if p.suffix.lower() not in (".pptx", ".pptm"):
        print(f"[FAIL] 仅支持 .pptx/.pptm: {p}")
        return 1

    cjk_font = args.font
    latin_font = args.latin_font or args.font
    if cjk_font not in CJK_SAFE:
        print(f"[WARN] '{cjk_font}' 不在推荐列表中；若收件人未安装该字体，中文仍会回退。")
        print(f"       推荐: {sorted(CJK_SAFE)[:4]}")

    tmp = p.with_suffix(p.suffix + ".tmp")
    total_ea = total_latin = 0

    with zipfile.ZipFile(p) as zin:
        slide_names = [n for n in zin.namelist()
                       if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        # 检查是否本来就没有中文
        has_cjk = any(
            re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", zin.read(n).decode("utf-8", "ignore"))
            for n in slide_names
        )
        if not has_cjk:
            print("该 deck 未检测到中文内容，无需修改。")
            return 0

        if args.dry_run:
            for n in slide_names:
                xml = zin.read(n).decode("utf-8", "ignore")
                _, ea, latin = _fix_slide_xml(xml, cjk_font, args.latin_too, latin_font)
                total_ea += ea
                total_latin += latin
                if ea:
                    print(f"  {n.split('/')[-1]}: 需修 ea {ea} 处")
            print(f"\n[DRY-RUN] 共需修 <a:ea> {total_ea} 处"
                  + (f"，<a:latin> {total_latin} 处" if args.latin_too else ""))
            return 0

        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in slide_names:
                    xml, ea, latin = _fix_slide_xml(
                        data.decode("utf-8", "ignore"), cjk_font, args.latin_too, latin_font)
                    total_ea += ea
                    total_latin += latin
                    data = xml.encode("utf-8")
                zout.writestr(item, data)

    shutil.move(str(tmp), str(p))
    print(f"[OK] 已修正 <a:ea> {total_ea} 处 -> {cjk_font}"
          + (f"；<a:latin> {total_latin} 处 -> {latin_font}" if args.latin_too else ""))
    print(f"     ⚠️ 交付时告知用户：本 deck 依赖「{cjk_font}」，收件人需安装")
    return 0


if __name__ == "__main__":
    sys.exit(main())
