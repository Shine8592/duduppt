#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建 duduppt 的 sdist + wheel。

关键一步：把仓库里的 skills/duduppt/ 复制成包内 duduppt/skill/，
这样 pip install 后 duduppt.skill_path() 能找到 Skill 本体，
CLI 的 `duduppt install` 才有东西可装。

用法：
    python scripts/build_pypi.py          # 构建到 dist/
    python scripts/build_pypi.py --clean  # 先清理再构建
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SKILL_SRC = ROOT / "skills" / "duduppt"
PKG = ROOT / "duduppt"
SKILL_DST = PKG / "skill"


def sync_skill() -> int:
    """把 skills/duduppt 同步到 duduppt/skill（排除 __pycache__）。"""
    if not SKILL_SRC.exists():
        print(f"[FAIL] 源 Skill 目录不存在: {SKILL_SRC}")
        return 1

    # 先清空目标
    if SKILL_DST.exists():
        shutil.rmtree(SKILL_DST)
    SKILL_DST.mkdir(parents=True, exist_ok=True)

    n = 0
    for src_file in SKILL_SRC.rglob("*"):
        if src_file.is_dir():
            continue
        # 跳过 pycache / pyc
        if "__pycache__" in src_file.parts or src_file.suffix == ".pyc":
            continue
        rel = src_file.relative_to(SKILL_SRC)
        dst_file = SKILL_DST / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        n += 1

    print(f"✅ 已同步 Skill: {SKILL_SRC.name} -> duduppt/skill/  （{n} 个文件）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="构建 duduppt 发布包")
    ap.add_argument("--clean", action="store_true", help="构建前清理旧产物")
    args = ap.parse_args()

    if args.clean:
        for d in ("dist", "build"):
            p = ROOT / d
            if p.exists():
                shutil.rmtree(p)
                print(f"已清理 {d}/")
        # 清理包内残留（避免误把旧 skill 打进去）

    # 1. 同步 Skill 到包内
    if sync_skill() != 0:
        return 1

    # 2. build
    print("\n=== 构建 sdist + wheel ===")
    r = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=str(ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600,
    )
    tail = (r.stdout or "").strip().splitlines()[-6:]
    for line in tail:
        print("  " + line)
    if r.returncode != 0:
        print("\n[FAIL] 构建失败:")
        print((r.stderr or "")[:1500])
        return r.returncode

    print("\n=== dist 产物 ===")
    dist = ROOT / "dist"
    if dist.exists():
        for f in sorted(dist.iterdir()):
            print(f"  {f.name}  ({f.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
