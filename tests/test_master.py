#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
母版与换风格脚本的自检（零额外依赖，仅需 python-pptx；缺失则跳过）。

检查项：
  1. build-master.py 能列出 16 种风格
  2. 编译出的模板：有母版、版式数 >= 11、qa-check 无 FAIL
  3. retemplate.py 换风格后：全篇背景色被替换（证明"全篇生效"）

原则（防"蹦"）：python-pptx 缺失时优雅跳过并返回 0，
      不让可选依赖把构建变红 —— 与 test_mcp_e2e.py 同一策略。
"""

import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "duduppt"
SCRIPTS = SKILL / "scripts"
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail if not cond else ''}")
    if cond:
        PASS += 1
    else:
        FAIL += 1


def run(script, *args, timeout=180):
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, cwd=str(SKILL),
    )
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def main_colors(pptx: Path) -> list[str]:
    """返回出现最多的前 3 个颜色（大写 hex，不带 #）。"""
    cnt: Counter = Counter()
    with zipfile.ZipFile(pptx) as z:
        for n in z.namelist():
            if not n.endswith(".xml"):
                continue
            t = z.read(n).decode("utf-8", errors="replace")
            for h in re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', t):
                cnt[h.upper()] += 1
    return [h for h, _ in cnt.most_common(3)]


def main() -> int:
    print("=" * 60)
    print(" duduppt 母版 / 换风格 自检")
    print("=" * 60)

    try:
        from pptx import Presentation  # noqa: F401
    except ImportError:
        print("\n[SKIP] 未安装 python-pptx，跳过本测试")
        print("       本地如需测试：pip install python-pptx")
        return 0

    # 1. 列出风格
    code, out, _ = run("build-master.py", "--list")
    styles = [l.strip("- ").strip() for l in out.splitlines() if l.strip().startswith("-")]
    check("能列出 16 种风格", len(styles) == 16, f"got={len(styles)}")

    # 2. 编译模板
    tmp_dir = SKILL / "examples" / "_t"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tpl = tmp_dir / "t.pptx"
    code, out, err = run("build-master.py", "--style", "01", "--out", str(tpl))
    check("build-master.py 编译成功", code == 0 and tpl.exists(), (err or out)[:200])

    if tpl.exists():
        from pptx import Presentation as P
        prs = P(str(tpl))
        check("模板有母版", len(prs.slide_masters) >= 1)
        check("版式数 >= 11", len(prs.slide_masters[0].slide_layouts) >= 11,
              f"got={len(prs.slide_masters[0].slide_layouts)}")

        # qa-check 必须通过（内建后处理生效）
        code, qout, _ = run("qa-check.py", "--deck", str(tpl), "--format", "json")
        try:
            d = json.loads(qout)
            check("模板通过 qa-check（0 FAIL）", len(d.get("failures", [])) == 0,
                  f"failures={d.get('failures')}")
        except Exception as e:
            check("模板通过 qa-check（0 FAIL）", False, str(e)[:80])

    # 3. retemplate 全篇换色
    src = SKILL / "examples" / "duduppt-sample.pptx"
    if src.exists():
        before = main_colors(src)
        dst = tmp_dir / "r.pptx"
        code, out, err = run("retemplate.py", "--deck", str(src), "--style", "05",
                             "--out", str(dst))
        check("retemplate.py 执行成功", code == 0 and dst.exists(), (err or out)[:200])
        if dst.exists():
            after = main_colors(dst)
            print(f"     换前主色: {before}")
            print(f"     换后主色: {after}")
            check("全篇背景色被替换（证明全篇生效）",
                  bool(before) and bool(after) and before[0] != after[0],
                  f"{before[0]} -> {after[0]}")
            code, qout, _ = run("qa-check.py", "--deck", str(dst), "--format", "json")
            try:
                d = json.loads(qout)
                check("换风格后 qa-check 0 FAIL", len(d.get("failures", [])) == 0,
                      f"failures={d.get('failures')}")
            except Exception:
                check("换风格后 qa-check 0 FAIL", False)

    # 清理
    try:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print(f"结果：{PASS} 通过 / {FAIL} 失败")
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
