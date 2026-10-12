#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA 审计报告外化：把盲读/溯源/机械检查/版本对比汇总成一份随交付的《质量审计报告》。

设计意图（竞品对比 v3 的第一步升级）：
  duduppt 的差异是「证据链 QA」，但此前这些能力藏在脚本里，用户感知不到。
  本脚本把它变成一份**可见的、可随 PPTX 一起交付的报告** ——
  把技术壁垒变成产品卖点。

输出两份文件：
  1. qa-report.json   —— 机器可读（可进 CI / 流水线门禁）
  2. qa-report.md     —— 人可读的《质量审计报告》，随 PPTX 一起交付

整合的检查项：
  - 机械检查（qa-check.py 的 8 项 lint）
  - 断言溯源（trace-claims.py：PPT 里的数字 ↔ 证据表）
  - 盲读对比（qa-compare.py：盲读答复 ↔ slide_manifest）
  - 版本对比（可选：与上一版快照 diff）

用法：
    python scripts/qa-report.py --deck output.pptx \
        [--evidence evidence.json] [--blind blind_read.json] \
        [--manifest slide_manifest.json] [--prev old.pptx] \
        [--out-dir out/qa-report]

退出码：存在 FAIL 级问题返回 1，否则 0（可进交付门禁）。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SCRIPT_DIR = Path(__file__).resolve().parent


def run_script(name: str, *args: str, timeout: int = 120) -> tuple[int, str, str]:
    """调用同级脚本，返回 (退出码, stdout, stderr)。"""
    script = SCRIPT_DIR / name
    if not script.exists():
        return 2, "", f"脚本不存在: {script}"
    r = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, cwd=str(SCRIPT_DIR.parent),
    )
    return r.returncode, r.stdout or "", r.stderr or ""


# ---------------------------------------------------------------------------
# 1. 机械检查（qa-check.py --format json）
# ---------------------------------------------------------------------------


def collect_mechanical(deck: Path) -> dict:
    code, out, err = run_script(
        "qa-check.py", "--deck", str(deck), "--format", "json"
    )
    try:
        d = json.loads(out)
        # 归一化为报告字段（qa-check 原生格式：passes/warnings/failures）
        passes = d.get("passes") or []
        warnings = d.get("warnings") or []
        failures = d.get("failures") or []
        return {
            "passed": len(passes),
            "failed": len(failures),
            "warned": len(warnings),
            "pass_list": passes,
            "fail_list": failures,
            "warn_list": warnings,
            "raw_exit": code,
        }
    except json.JSONDecodeError:
        # qa-check 非 JSON 输出时兜底：解析 [PASS]/[FAIL]/[WARN] 文本
        pass_items = re.findall(r"\[PASS\] (.+)", out)
        fail_items = re.findall(r"\[FAIL\] (.+)", out)
        warn_items = re.findall(r"\[WARN\] (.+)", out)
        return {
            "passed": len(pass_items),
            "failed": len(fail_items),
            "warned": len(warn_items),
            "pass_list": pass_items,
            "fail_list": fail_items,
            "warn_list": warn_items,
            "raw_exit": code,
            "parse_fallback": True,
        }


# ---------------------------------------------------------------------------
# 2. 断言溯源（trace-claims.py）
# ---------------------------------------------------------------------------


def collect_trace(deck: Path, evidence: Path | None) -> dict | None:
    if evidence is None:
        return None
    if not evidence.exists():
        return {"available": False, "error": f"证据文件不存在: {evidence}"}
    code, out, err = run_script(
        "trace-claims.py", "--deck", str(deck), "--evidence", str(evidence)
    )
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # 解析文本形式
        lines = [l for l in out.splitlines() if l.strip()]
        return {
            "available": True,
            "parse_fallback": True,
            "exit_code": code,
            "output_lines": lines[:30],
        }


# ---------------------------------------------------------------------------
# 3. 盲读对比（qa-compare.py）
# ---------------------------------------------------------------------------


def collect_blind_compare(blind: Path | None, manifest: Path | None) -> dict | None:
    if blind is None or manifest is None:
        return None
    if not blind.exists() or not manifest.exists():
        return {"available": False, "error": "盲读/manifest 文件缺失"}
    code, out, err = run_script(
        "qa-compare.py", "--blind", str(blind), "--manifest", str(manifest)
    )
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        lines = [l for l in out.splitlines() if l.strip()]
        return {
            "available": True,
            "parse_fallback": True,
            "exit_code": code,
            "output_lines": lines[:30],
        }


# ---------------------------------------------------------------------------
# 4. 版本对比（与上一版快照）
# ---------------------------------------------------------------------------


def collect_diff(deck: Path, prev: Path | None) -> dict | None:
    if prev is None or not prev.exists():
        return None
    changed = []
    try:
        with zipfile.ZipFile(deck) as z_new, zipfile.ZipFile(prev) as z_old:
            new_files = set(z_new.namelist())
            old_files = set(z_old.namelist())
            added = sorted(new_files - old_files)
            removed = sorted(old_files - new_files)
            common = sorted(new_files & old_files)
            for f in common:
                if z_new.read(f) != z_old.read(f):
                    changed.append(f)
            return {
                "prev": str(prev),
                "files_added": added,
                "files_removed": removed,
                "files_changed": changed,
                "changed_count": len(changed),
            }
    except zipfile.BadZipFile:
        return {"available": False, "error": "对比文件不是有效 pptx"}


# ---------------------------------------------------------------------------
# 汇总与分级
# ---------------------------------------------------------------------------

SEVERITY = {"INFO": 0, "WARN": 1, "FAIL": 2}


def grade(report: dict) -> str:
    """根据各检查项汇总整体评级：PASS / WARN / FAIL。"""
    worst = 0
    mech = report.get("mechanical") or {}
    if isinstance(mech.get("failed"), int):
        worst = max(worst, 2 if mech["failed"] > 0 else 0)
    if mech.get("raw_exit") == 1:
        worst = max(worst, 2)

    for key in ("trace", "blind_compare", "diff"):
        sub = report.get(key)
        if not sub or not sub.get("available", True):
            continue
        # 子项里 fail/issue/error 计数
        for probe in ("fail", "issue", "error", "unmatched"):
            v = sub.get(probe)
            if isinstance(v, int) and v > 0:
                worst = max(worst, 2)
        # trace 未匹配的断言（如果文本形式）
        for line in sub.get("output_lines", []):
            if "FAIL" in line or "未匹配" in line or "溯源失败" in line:
                worst = max(worst, 2)

    return ["PASS", "WARN", "FAIL"][worst]


# ---------------------------------------------------------------------------
# 生成 Markdown 报告（人可读）
# ---------------------------------------------------------------------------


def to_markdown(report: dict) -> str:
    g = report["grade"]
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[g]
    lines = [
        f"# duduppt 质量审计报告",
        "",
        f"> 本报告由 duduppt 的「证据链 QA」自动生成，随 PPTX 一起交付。",
        "",
        f"**整体评级：{icon} {g}**",
        "",
        f"- 交付物：`{report['deck']}`",
        f"- 生成时间：{report['generated_at']}",
        f"- 生成器：duduppt qa-report v1",
        "",
        "---",
        "",
    ]

    mech = report.get("mechanical") or {}
    if mech:
        lines.append("## 一、机械检查（8 项 lint）")
        lines.append("")
        if mech.get("failed") is not None:
            lines.append(f"- 通过：**{mech.get('passed', 0)}** 项")
            lines.append(f"- 警告：**{mech.get('warned', 0)}** 项")
            lines.append(f"- 失败：**{mech.get('failed', 0)}** 项")
            if mech.get("fail_list"):
                lines.append("")
                lines.append("### 失败明细")
                lines.append("")
                for item in mech["fail_list"]:
                    lines.append(f"- ❌ {item}")
            if mech.get("warn_list"):
                lines.append("")
                lines.append("### 警告明细")
                lines.append("")
                for item in mech["warn_list"]:
                    lines.append(f"- ⚠️ {item}")
        else:
            lines.append(f"- 原始输出已记录（详见 JSON）")
        lines.append("")

    trace = report.get("trace")
    if trace:
        lines.append("## 二、断言溯源（数字 ↔ 证据）")
        lines.append("")
        if not trace.get("available", True):
            lines.append(f"- ⚠️ 不可用：{trace.get('error', '解析失败')}")
        else:
            if "output_lines" in trace:
                lines.append("")
                lines.extend(f"  {l}" for l in trace["output_lines"][:20])
            else:
                lines.append("- 详见 JSON 原始数据")
        lines.append("")

    blind = report.get("blind_compare")
    if blind:
        lines.append("## 三、盲读一致性（不看原稿只看成品）")
        lines.append("")
        if not blind.get("available", True):
            lines.append(f"- ⚠️ 不可用：{blind.get('error', '解析失败')}")
        else:
            if "output_lines" in blind:
                lines.extend(f"  {l}" for l in blind["output_lines"][:20])
            else:
                lines.append("- 详见 JSON 原始数据")
        lines.append("")

    diff = report.get("diff")
    if diff:
        lines.append("## 四、版本对比（与上一版快照）")
        lines.append("")
        lines.append(f"- 上一版：`{diff.get('prev')}`")
        lines.append(f"- 新增文件：{len(diff.get('files_added', []))}")
        lines.append(f"- 删除文件：{len(diff.get('files_removed', []))}")
        lines.append(f"- 变更文件：**{diff.get('changed_count', 0)}**")
        if diff.get("files_changed"):
            lines.append("")
            lines.append("### 变更明细（前 10）")
            lines.append("")
            for f in diff["files_changed"][:10]:
                lines.append(f"  - {f}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 若评级为 FAIL，请先处理上述失败项再交付。")
    lines.append("> 报告由 duduppt 生成 —— 唯一带证据链审计的咨询级 PPT 生成器。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="生成 duduppt 质量审计报告")
    ap.add_argument("--deck", required=True, help="待审计的 PPTX 路径")
    ap.add_argument("--evidence", help="证据表 JSON（断言溯源用）")
    ap.add_argument("--blind", help="盲读答复 JSON（盲读对比用）")
    ap.add_argument("--manifest", help="slide_manifest.json（盲读对比用）")
    ap.add_argument("--prev", help="上一版 PPTX 快照（版本对比用）")
    ap.add_argument("--out-dir", default=None, help="报告输出目录（默认与 deck 同级的 qa-report/）")
    args = ap.parse_args()

    deck = Path(args.deck)
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        return 1

    out_dir = Path(args.out_dir) if args.out_dir else deck.parent / "qa-report"
    out_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "deck": str(deck),
        "deck_name": deck.name,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mechanical": collect_mechanical(deck),
        "trace": collect_trace(deck, Path(args.evidence) if args.evidence else None),
        "blind_compare": collect_blind_compare(
            Path(args.blind) if args.blind else None,
            Path(args.manifest) if args.manifest else None,
        ),
        "diff": collect_diff(deck, Path(args.prev) if args.prev else None),
    }
    report["grade"] = grade(report)

    # JSON 报告
    json_path = out_dir / "qa-report.json"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Markdown 报告
    md_path = out_dir / "qa-report.md"
    md_path.write_text(to_markdown(report), encoding="utf-8")

    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[report["grade"]]
    print(f"{icon} 审计评级: {report['grade']}")
    print(f"  JSON: {json_path}")
    print(f"  报告: {md_path}")

    return 1 if report["grade"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
