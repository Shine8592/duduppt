#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
溯源校验：找出 deck 上「证据表里查不到」的数字。

背景：duduppt 的证据表要求每个数字标注来源，但此前**没有任何机械手段**
验证「页面上的数字是否真的在证据表里」—— 全靠模型自觉。本脚本把它变成可计算的。

用法：
    # 1. 先把证据表存成机器可读的 JSON（evidence.json）：
    #    [{"id": "E1", "claim": "市场规模", "value": 1234, "unit": "亿元",
    #      "period": "2025", "source": "报告XX P12", "confidence": "高"}, ...]
    #
    # 2. 对 deck 跑溯源（支持 .pptx，或纯文本大纲）
    python scripts/trace-claims.py --deck output.pptx --evidence evidence.json

    # 也支持只检查大纲 markdown
    python scripts/trace-claims.py --text outline.md --evidence evidence.json

输出：
    UNTRACED 行 = 页面上出现但证据表中找不到的数字（必须逐条解释或改稿）
    退出码 1 表示存在 UNTRACED（可用于 CI 门禁）

零依赖（.pptx 用标准库 zipfile + 正则解析）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 数字匹配：整数/小数/千分位/百分数/带单位
NUM_RE = re.compile(r"\d[\d,]*\.?\d*\s*%?")
# 忽略的"非数据数字"：纯年份、页码、序号等（可通过 --keep-years 关闭）
YEAR_RE = re.compile(r"^(19|20)\d{2}$")


def extract_numbers(text: str) -> set[str]:
    """从文本里抽取数字（归一化：去千分位逗号、去空格）。"""
    out = set()
    for m in NUM_RE.finditer(text):
        s = m.group(0).strip()
        # 归一化
        s = s.replace(",", "").replace(" ", "")
        if not s:
            continue
        # 去掉纯 "0" 之类的噪声
        if s in ("0", "0.", "0%"):
            continue
        out.add(s)
    return out


def numbers_from_ppt(pptx: Path) -> dict[str, set[str]]:
    """从 pptx 每个 slide 抽取数字，返回 {slide 名: 数字集合}。"""
    result = {}
    with zipfile.ZipFile(pptx) as z:
        slides = sorted(
            [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda x: int(re.search(r"(\d+)", x).group(1)),
        )
        for n in slides:
            xml = z.read(n).decode("utf-8", "ignore")
            # 只取可见文本 <a:t>
            texts = re.findall(r"<a:t>([^<]*)</a:t>", xml)
            joined = " ".join(texts)
            result[n.split("/")[-1]] = extract_numbers(joined)
    return result


def numbers_from_text(p: Path) -> dict[str, set[str]]:
    """从纯文本/大纲抽取数字（按 markdown 标题分块）。"""
    text = p.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n(?=#{1,3}\s)", text)
    result = {}
    for i, b in enumerate(blocks, 1):
        title = b.strip().split("\n")[0][:40] if b.strip() else f"block{i}"
        result[f"block{i}: {title}"] = extract_numbers(b)
    return result


def evidence_numbers(evidence: list[dict]) -> tuple[set[str], dict[str, str]]:
    """从证据表提取所有合法数字，并给出 值->来源 的映射。"""
    nums: set[str] = set()
    origin: dict[str, str] = {}
    for e in evidence:
        raw_fields = [e.get("value"), e.get("数值"), e.get("text"), e.get("claim")]
        # 也支持 evidence 里直接给一串数值
        for extra in (e.get("values") or []):
            raw_fields.append(extra)
        for v in raw_fields:
            if v is None:
                continue
            for s in extract_numbers(str(v)):
                nums.add(s)
                origin.setdefault(s, f"{e.get('id', '?')} ({e.get('source', '?')})")
                # 百分数：0.15 与 15% 互为等价表示
                if s.endswith("%"):
                    base = s.rstrip("%")
                    try:
                        nums.add(base)
                        origin.setdefault(base, origin[s])
                    except Exception:
                        pass
    return nums, origin


def main() -> int:
    ap = argparse.ArgumentParser(description="溯源校验：页面数字是否都在证据表里")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--deck", help=".pptx 文件")
    src.add_argument("--text", help="纯文本/大纲文件（.md/.txt）")
    ap.add_argument("--evidence", required=True, help="证据表 JSON")
    ap.add_argument("--keep-years", action="store_true", help="把年份也算作需溯源的数字")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    ev_path = Path(args.evidence)
    if not ev_path.exists():
        print(f"[FAIL] 证据表不存在: {ev_path}")
        return 1
    try:
        evidence = json.loads(ev_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] 证据表不是合法 JSON: {e}")
        return 1
    if isinstance(evidence, dict):
        evidence = evidence.get("evidence") or evidence.get("items") or []
    if not isinstance(evidence, list):
        print("[FAIL] 证据表格式应为数组，或含 evidence/items 字段的对象")
        return 1
    if not evidence:
        print("[WARN] 证据表为空 —— 此时任何数字都会被判为 UNTRACED")

    known, origin = evidence_numbers(evidence)
    print(f"证据表提供 {len(known)} 个可溯源数字")

    if args.deck:
        p = Path(args.deck)
        if not p.exists():
            print(f"[FAIL] deck 不存在: {p}")
            return 1
        if p.suffix.lower() not in (".pptx", ".pptm"):
            print(f"[FAIL] 仅支持 .pptx：{p}")
            return 1
        slide_nums = numbers_from_ppt(p)
    else:
        slide_nums = numbers_from_text(Path(args.text))

    # 逐个 slide 比对
    untraced: list[tuple[str, str]] = []
    for name, nums in slide_nums.items():
        for s in sorted(nums):
            if YEAR_RE.match(s) and not args.keep_years:
                continue
            if s not in known:
                untraced.append((name, s))

    if args.format == "json":
        print(json.dumps({
            "evidence_numbers": len(known),
            "slides_checked": len(slide_nums),
            "untraced_count": len(untraced),
            "untraced": [{"page": p, "number": n} for p, n in untraced],
        }, ensure_ascii=False, indent=2))
    else:
        if untraced:
            print(f"\n发现 {len(untraced)} 个 UNTRACED 数字（页面上有，证据表里查不到）：")
            for page, num in untraced:
                print(f"  UNTRACED: {page}  \"{num}\"")
            print("\n处理要求（二选一）：")
            print("  1) 补进证据表（附来源），再重跑本脚本")
            print("  2) 从页面删除该数字")
            print("\n⚠️ 不要把本报告当作'已解释'——必须真的改稿或补来源。")
            return 1
        print(f"\n全部溯源通过（检查了 {len(slide_nums)} 页）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
