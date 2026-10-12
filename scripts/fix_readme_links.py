#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正根 README 中 skill 内部相对链接，并验证全部相对链接有效。"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent


def main():
    p = ROOT / "README.md"
    t = p.read_text(encoding="utf-8")

    n1 = sum(
        t.count(f"({d}/") for d in ("references", "scripts", "assets", "examples")
    )
    n2 = sum(
        t.count(f"`{d}/") for d in ("references", "scripts", "assets", "examples")
    )
    t = re.sub(
        r"\((references/|scripts/|assets/|examples/)", r"(skills/duduppt/\1", t
    )
    t = re.sub(
        r"`(references/|scripts/|assets/|examples/)", r"`skills/duduppt/\1", t
    )
    p.write_text(t, encoding="utf-8")
    print(f"markdown links fixed: {n1}, backtick paths fixed: {n2}")

    # 验证
    t2 = p.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)#\s]+)\)", t2)
    missing = [
        l
        for l in sorted(set(links))
        if not l.startswith("http") and not (ROOT / l).exists()
    ]
    print(f"links: {len(set(links))}, missing: {missing if missing else 'none'}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
