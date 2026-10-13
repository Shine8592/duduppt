#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duduppt 命令行工具。

用途：把包内的 Agent Skill 安装到各 Agent 的 skills 目录，
让 Agent 能识别并加载 duduppt。

子命令：
    install    安装 Skill（默认自动探测已安装的 Agent）
    path       打印包内 Skill 路径
    version    打印版本

用法：
    duduppt install
    duduppt install --agent claude
    duduppt path
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from duduppt import __version__, skill_path  # noqa: E402

# 各 Agent 的 skills 根目录（用户级）
AGENT_DIRS = {
    "claude": "~/.claude/skills",
    "codex": "~/.codex/skills",
    "cursor": "~/.cursor/skills",
    "opencode": "~/.config/opencode/skills",
    "hermes": "~/.hermes/skills",
}


def detect_agents() -> list[str]:
    """探测本机已安装（目录存在）的 Agent。"""
    found = []
    for name, pat in AGENT_DIRS.items():
        d = Path(pat).expanduser()
        if d.exists():
            found.append(name)
    return found


def install(agent: str | None, dest: str | None, force: bool) -> int:
    """安装 Skill 到目标目录。"""
    src = skill_path()
    # ⚠️ 修复：skill_name 不能取 src.name（包内目录名固定是 "skill"，
    # 会导致安装到 xxx/skill/ 而不是 xxx/duduppt/，实测踩过）。
    # 正确来源：包名。pip 安装的包一定叫 duduppt。
    import duduppt as _pkg
    skill_name = _pkg.__name__  # "duduppt"

    if dest:
        target = Path(dest).expanduser() / skill_name
        print(f"目标（显式指定）: {target}")
    elif agent:
        if agent not in AGENT_DIRS:
            print(f"[FAIL] 未知 agent: {agent}。可用：{', '.join(AGENT_DIRS)}")
            return 1
        base = Path(AGENT_DIRS[agent]).expanduser()
        target = base / skill_name
        print(f"目标 agent: {agent} -> {target}")
    else:
        found = detect_agents()
        if not found:
            print("[WARN] 未探测到已知 Agent 的 skills 目录。")
            print("       可用 --dest 显式指定，例如：")
            print("       duduppt install --dest ~/.claude/skills")
            return 1
        print(f"探测到 Agent: {', '.join(found)}")
        ok = True
        for a in found:
            ok = install(a, None, force) == 0 and ok
        return 0 if ok else 1

    if target.exists():
        if not force:
            print(f"[SKIP] 已存在，跳过：{target}（加 --force 覆盖）")
            return 0
        print(f"       已存在，--force 覆盖: {target}")
        shutil.rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    print(f"✅ 已安装 Skill -> {target}")
    print(f"   （{len(list(target.rglob('*')))} 个文件）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="duduppt",
        description="duduppt — 咨询级 PPTX 生成 Skill 安装器",
    )
    sub = ap.add_subparsers(dest="cmd")

    p_inst = sub.add_parser("install", help="安装 Skill 到 Agent 的 skills 目录")
    p_inst.add_argument("--agent", choices=sorted(AGENT_DIRS), help="指定 agent")
    p_inst.add_argument("--dest", help="显式指定目标父目录")
    p_inst.add_argument("--force", action="store_true", help="已存在时覆盖")

    sub.add_parser("path", help="打印包内 Skill 路径")
    sub.add_parser("version", help="打印版本")

    args = ap.parse_args()

    if args.cmd == "install":
        return install(args.agent, args.dest, args.force)
    if args.cmd == "path":
        print(skill_path())
        return 0
    if args.cmd == "version":
        print(f"duduppt {__version__}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
