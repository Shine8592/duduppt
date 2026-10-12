#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 README / README_EN 中所有相对链接是否指向真实存在的文件。"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail if not cond else ''}")
    if cond:
        PASS += 1
    else:
        FAIL += 1


def main() -> int:
    print("=" * 58)
    print(" README 链接有效性检查")
    print("=" * 58)
    for f in ("README.md", "README_EN.md"):
        p = ROOT / f
        if not p.exists():
            check(f"{f} 存在", False)
            continue
        text = p.read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)#\s]+)\)", text)
        rel = [l for l in links if not l.startswith("http")]
        missing = [l for l in sorted(set(rel)) if not (ROOT / l).exists()]
        check(f"{f}: {len(set(rel))} 个相对链接全部有效", not missing, f"缺失={missing}")
    print("\n" + "=" * 58)
    print(f" 结果：{PASS} 通过 / {FAIL} 失败")
    print("=" * 58)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
