#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收集并校验 deck 中所有图片的来源与授权信息。

背景：图库图（Pexels / Unsplash / Pixabay）虽然免费，但多数要求**署名**；
AI 生图需要标注生成来源。缺失授权信息在正式交付（尤其客户/商业场景）中有合规风险。

用法：
    # 1. 扫描 manifest，列出图片与缺失的授权字段
    python scripts/collect-credits.py --manifest slide_manifest.json

    # 2. 生成「图片来源」页的 markdown（可粘到 deck 末页）
    python scripts/collect-credits.py --manifest slide_manifest.json --format markdown

manifest 中图片项应包含（建议）：
    {
      "type": "image",
      "source": "pexels",              # pexels / unsplash / pixabay / ai / brand / local
      "source_url": "https://...",     # 图库图必填
      "credit_text": "Photo by X",     # 图库图必填（署名）
      "license": "Pexels License",     # 授权类型
      "generated_by": "Agnes API",     # AI 生图必填
      "path": "images/cover.png"
    }

零依赖（仅标准库），无需安装任何包。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 各来源的必填字段与授权说明
SOURCE_RULES = {
    "pexels":   {"required": ["source_url", "credit_text"], "license": "Pexels License",
                 "note": "免费商用，建议署名摄影师"},
    "unsplash": {"required": ["source_url", "credit_text"], "license": "Unsplash License",
                 "note": "免费商用，强烈建议署名"},
    "pixabay":  {"required": ["source_url"], "license": "Pixabay License",
                 "note": "免费商用，无强制署名"},
    "ai":       {"required": ["generated_by"], "license": "AI Generated",
                 "note": "需标注由 AI 生成"},
    "agnes":    {"required": ["generated_by"], "license": "AI Generated",
                 "note": "需标注由 AI 生成"},
    "brand":    {"required": [], "license": "Brand Asset",
                 "note": "品牌素材，需确认使用授权"},
    "local":    {"required": [], "license": "Local",
                 "note": "本地素材，请自行确认版权"},
}


def iter_images(manifest: dict):
    """从 manifest 中取出所有图片项（兼容多种结构）。"""
    slides = manifest.get("slides") or manifest.get("pages") or []
    if isinstance(slides, dict):
        slides = list(slides.values())
    for idx, slide in enumerate(slides, 1):
        if not isinstance(slide, dict):
            continue
        # 可能叫 images / assets / pictures
        for key in ("images", "assets", "pictures"):
            items = slide.get(key)
            if not isinstance(items, list):
                continue
            for it in items:
                if isinstance(it, dict):
                    yield idx, it
        # 单图简写
        if slide.get("type") == "image" or "image_path" in slide:
            yield idx, slide


def audit(manifest: dict) -> tuple[list[dict], list[str]]:
    """返回 (图片清单, 问题列表)。"""
    images, problems = [], []
    for slide_no, img in iter_images(manifest):
        src = str(img.get("source", "")).strip().lower()
        rule = SOURCE_RULES.get(src)
        record = {
            "slide": slide_no,
            "path": img.get("path") or img.get("image_path") or "(未指定)",
            "source": src or "(未指定)",
            "license": (rule or {}).get("license", "(未知)"),
            "credit": img.get("credit_text", ""),
            "url": img.get("source_url", ""),
        }
        images.append(record)

        if rule is None:
            problems.append(f"slide {slide_no}: source 未指定或未知（'{src}'）-> 无法判断授权")
            continue
        for field in rule["required"]:
            if not img.get(field):
                problems.append(
                    f"slide {slide_no} ({record['path']}): 缺少 {field}（source={src}，规则：{rule['note']}）"
                )
    return images, problems


def to_markdown(images: list[dict]) -> str:
    """生成「图片来源」页内容。"""
    if not images:
        return "_本 deck 无外部图片_"
    lines = ["## 图片来源与授权", ""]
    seen = set()
    for r in images:
        key = (r["path"], r["url"])
        if key in seen:
            continue
        seen.add(key)
        parts = [f"- `{r['path']}`"]
        if r["source"] and r["source"] != "(未指定)":
            parts.append(f"来源: {r['source']}")
        if r["credit"]:
            parts.append(r["credit"])
        if r["license"] and r["license"] != "(未知)":
            parts.append(f"授权: {r['license']}")
        if r["url"]:
            parts.append(r["url"])
        lines.append("  ".join(parts))
    lines += ["", "> 免费图库素材使用时请遵循各自授权条款；AI 生成内容已标注。"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="收集/校验 deck 图片来源与授权")
    ap.add_argument("--manifest", required=True, help="slide_manifest.json 路径")
    ap.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    args = ap.parse_args()

    p = Path(args.manifest)
    if not p.exists():
        print(f"[FAIL] manifest 不存在: {p}")
        return 1
    try:
        manifest = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] manifest 不是合法 JSON: {e}")
        return 1

    images, problems = audit(manifest)

    if args.format == "json":
        print(json.dumps({"images": images, "problems": problems}, ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        print(to_markdown(images))
    else:
        print(f"共发现 {len(images)} 张图片")
        for r in images:
            print(f"  slide {r['slide']}: {r['path']}  [{r['source']}] {r['license']}")
        if problems:
            print(f"\n发现 {len(problems)} 个授权信息缺失：")
            for x in problems:
                print("  -", x)
            print("\n建议：补齐 manifest 中的 source_url / credit_text / generated_by 字段，"
                  "并在 deck 末页附「图片来源」页（--format markdown 可直接生成）")
            return 1
        print("\n授权信息完整。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
