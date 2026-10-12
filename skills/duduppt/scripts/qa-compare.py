#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盲读 QA 比对：把盲读子 agent 的回答与 slide_manifest.json 做机器比对。

设计理念（对标 addsumtech 的 blind-reader + 机器比对）：
  盲读者只看到图片、看不到设计意图，因此它能暴露"结论没传达出去"——
  而知情者会在图里脑补出意图，永远发现不了。

本脚本**不做主观判断**，只输出可复核的差异：
  1. claim 覆盖率：读者说出的"这一页想让记住什么"，与 manifest 的结论标题是否对得上
  2. about 重复：不同页被读成"关于同一件事" -> 页面冗余
  3. unreadable 非空：有元素读者看不清
  4. problems / any_blank / style_consistent：结构性问题

用法：
    python scripts/qa-compare.py --blind blind_read.json --manifest slide_manifest.json
    python scripts/qa-compare.py --blind blind_read.json --manifest slide_manifest.json --format json

退出码 1 表示存在需要响应的差异（可用于交付门禁）。

零依赖（仅标准库）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 判定"对得上"的相似度阈值（词集重合比例）
CLAIM_MATCH_THRESHOLD = 0.34


def _norm_tokens(text: str) -> set[str]:
    """归一化为词/字集合，用于粗略相似度（中英文混合友好）。"""
    if not text:
        return set()
    t = str(text).lower()
    # 英文词 + 中文单字
    words = set(re.findall(r"[a-z0-9]+", t))
    cjk = set(re.findall(r"[\u4e00-\u9fff]", t))
    return words | cjk


def _similar(a: str, b: str) -> float:
    """Jaccard 相似度（词集重合度）。"""
    ta, tb = _norm_tokens(a), _norm_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _manifest_claims(manifest: dict) -> dict[int, str]:
    """从 manifest 取每页的"应传达的结论"（兼容多种字段名）。"""
    out: dict[int, str] = {}
    slides = manifest.get("slides") or manifest.get("pages") or []
    if isinstance(slides, dict):
        slides = list(slides.values())
    for i, s in enumerate(slides, 1):
        if not isinstance(s, dict):
            continue
        for key in ("claim", "结论标题", "title", "headline", "assertion", "so_what"):
            v = s.get(key)
            if v and isinstance(v, str):
                out[i] = v.strip()
                break
    return out


def compare(blind: dict, manifest: dict) -> dict:
    """执行比对，返回结构化差异报告。"""
    slides = blind.get("slides") or []
    if not isinstance(slides, list):
        slides = []

    expected = _manifest_claims(manifest)

    claim_miss: list[dict] = []
    about_map: dict[str, list[int]] = {}
    unreadable_pages: list[dict] = []
    problem_pages: list[dict] = []

    for s in slides:
        if not isinstance(s, dict):
            continue
        n = s.get("n")
        claim = str(s.get("claim", "") or "").strip()
        about = str(s.get("about", "") or "").strip()

        # 1) claim 覆盖率
        if isinstance(n, int) and n in expected:
            sim = _similar(claim, expected[n])
            if sim < CLAIM_MATCH_THRESHOLD:
                claim_miss.append({
                    "slide": n,
                    "reader_said": claim[:80],
                    "manifest_claim": expected[n][:80],
                    "similarity": round(sim, 3),
                })

        # 2) about 重复
        if about:
            about_map.setdefault(about, []).append(n if isinstance(n, int) else 0)

        # 3) unreadable
        un = s.get("unreadable") or []
        if isinstance(un, list) and un:
            unreadable_pages.append({"slide": n, "items": un[:8]})

        # 4) problems
        pr = s.get("problems") or []
        if isinstance(pr, list) and pr:
            problem_pages.append({"slide": n, "problems": pr[:8]})

    dup_about = {k: v for k, v in about_map.items() if len(v) > 1}

    return {
        "slides_read": len(slides),
        "slides_in_manifest": len(expected),
        "claim_miss": claim_miss,
        "duplicate_about": dup_about,
        "unreadable_pages": unreadable_pages,
        "problem_pages": problem_pages,
        "any_blank": blind.get("any_blank") or [],
        "style_consistent": blind.get("style_consistent"),
    }


def report_text(r: dict) -> str:
    lines = []
    lines.append(f"盲读页数: {r['slides_read']}   manifest 页数: {r['slides_in_manifest']}")

    need_response = 0

    if r["slides_in_manifest"] and r["slides_read"] != r["slides_in_manifest"]:
        lines.append(f"\n⚠️ 页数不一致：读了 {r['slides_read']} 页，manifest 有 {r['slides_in_manifest']} 页")
        need_response += 1

    cm = r["claim_miss"]
    if cm:
        lines.append(f"\n【结论未传达】{len(cm)} 页 —— 读者说出的要点与预期结论对不上：")
        for x in cm:
            lines.append(f"  slide {x['slide']} (相似度 {x['similarity']})")
            lines.append(f"    读者说: {x['reader_said']}")
            lines.append(f"    预期:   {x['manifest_claim']}")
        need_response += len(cm)

    if r["duplicate_about"]:
        lines.append(f"\n【页面冗余】{len(r['duplicate_about'])} 组被读成'关于同一件事'：")
        for about, pages in r["duplicate_about"].items():
            lines.append(f"  \"{about}\" -> 页 {pages}")
        need_response += len(r["duplicate_about"])

    if r["unreadable_pages"]:
        lines.append(f"\n【元素看不清】{len(r['unreadable_pages'])} 页：")
        for x in r["unreadable_pages"]:
            lines.append(f"  slide {x['slide']}: {x['items']}")
        need_response += len(r["unreadable_pages"])

    if r["problem_pages"]:
        lines.append(f"\n【排版问题】{len(r['problem_pages'])} 页：")
        for x in r["problem_pages"]:
            lines.append(f"  slide {x['slide']}: {x['problems']}")
        need_response += len(r["problem_pages"])

    if r["any_blank"]:
        lines.append(f"\n【空白页】{r['any_blank']}")
        need_response += 1

    if r["style_consistent"] is False:
        lines.append("\n【风格不一致】盲读者认为整份 deck 不像同一个设计系统")
        need_response += 1

    if need_response == 0:
        lines.append("\n盲读比对通过：没有需要响应的差异。")
    else:
        lines.append(f"\n共 {need_response} 处需要响应。")
        lines.append("处理规则（不允许'看到了但忽略'）：")
        lines.append("  - 结论未传达 -> 改标题/内容，让要点真的出现在页面上")
        lines.append("  - 页面冗余   -> 合并或删页")
        lines.append("  - 元素看不清 -> 放大字号 / 提对比度 / 减信息量")
        lines.append("  - 排版问题   -> 修版面")
        lines.append("  - 若判定为盲读者误报，也必须书面说明理由")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="盲读 QA 比对")
    ap.add_argument("--blind", required=True, help="盲读输出 blind_read.json")
    ap.add_argument("--manifest", required=True, help="slide_manifest.json")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    for label, path in (("blind", args.blind), ("manifest", args.manifest)):
        if not Path(path).exists():
            print(f"[FAIL] {label} 不存在: {path}")
            return 1
    try:
        blind = json.loads(Path(args.blind).read_text(encoding="utf-8"))
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] JSON 解析失败: {e}")
        return 1

    r = compare(blind, manifest)

    if args.format == "json":
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(report_text(r))

    # 有需要响应的差异 -> 退出码 1
    has_diff = bool(
        r["claim_miss"] or r["duplicate_about"] or r["unreadable_pages"]
        or r["problem_pages"] or r["any_blank"] or r["style_consistent"] is False
    )
    return 1 if has_diff else 0


if __name__ == "__main__":
    sys.exit(main())
