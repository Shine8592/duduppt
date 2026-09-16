#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duduppt 结构自检（零依赖，CI 与本地均可跑）。

检查项：
1. SKILL.md frontmatter 合法（name/description 符合 Agent Skill 规范）
2. SKILL.md 里引用的所有文件**真实存在**（防止失效引用）
3. package.json 是合法 JSON 且关键字段正确
4. 所有 Python 脚本可编译
5. 所有 JS 脚本语法正确（需 node）
6. 中文字体检查逻辑的单测（用构造数据验证 ea/latin 槽位判定）

用法：
    python tests/test_structure.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FAILED: list[str] = []


def check(name: str, cond: bool, extra: str = "") -> None:
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f"  -> {extra}" if extra else ""))
    if not cond:
        FAILED.append(name)


# ---------------------------------------------------------------------------
# 1. SKILL.md frontmatter
# ---------------------------------------------------------------------------
def test_skill_frontmatter() -> None:
    p = ROOT / "SKILL.md"
    if not p.exists():
        check("SKILL.md 存在", False)
        return
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        check("SKILL.md 有 frontmatter", False)
        return
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)

    check("frontmatter 含 name", name is not None)
    check("frontmatter 含 description", desc is not None)

    if name:
        n = name.group(1).strip().strip('"').strip("'")
        # Agent Skill 规范：小写字母/数字/连字符，≤64 字符
        ok = bool(re.fullmatch(r"[a-z0-9-]{1,64}", n))
        check("name 符合规范（小写/数字/连字符，≤64）", ok, f"name={n}")

    if desc:
        d = desc.group(1).strip().strip('"').strip("'")
        check("description ≤1024 字符", len(d) <= 1024, f"长度={len(d)}")


# ---------------------------------------------------------------------------
# 2. 引用完整性（防失效引用）
# ---------------------------------------------------------------------------
def test_referenced_files_exist() -> None:
    """SKILL.md 中出现的 `scripts/xxx` `references/xxx` 路径必须真实存在。"""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    # 抓反引号里的相对路径
    refs = set(re.findall(r"`((?:scripts|references|assets|examples)/[^`\s]+)`", text))
    missing = []
    for r in sorted(refs):
        if not (ROOT / r).exists():
            missing.append(r)
    check("SKILL.md 引用的文件都存在", not missing,
          f"缺失 {missing}" if missing else f"检查 {len(refs)} 个引用")


# ---------------------------------------------------------------------------
# 3. package.json
# ---------------------------------------------------------------------------
def test_package_json() -> None:
    p = ROOT / "package.json"
    if not p.exists():
        check("package.json 存在", False)
        return
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        check("package.json 是合法 JSON", True)
    except Exception as e:
        check("package.json 是合法 JSON", False, str(e))
        return

    check("license 字段为 MIT", d.get("license") == "MIT", f"license={d.get('license')}")
    desc = d.get("description", "")
    # 只检测真正的 HTML 标签（<tag> / </tag>），不要把 "->" 之类的箭头误判
    has_html_tag = bool(re.search(r"</?[a-zA-Z][^>]*>", desc))
    check("description 未含 HTML 标签", not has_html_tag, f"长度={len(desc)}")
    check("keywords 非空", bool(d.get("keywords")))
    check("dependencies 含 pptxgenjs", "pptxgenjs" in d.get("dependencies", {}))


# ---------------------------------------------------------------------------
# 4. Python 脚本可编译
# ---------------------------------------------------------------------------
def test_python_scripts_compile() -> None:
    import py_compile
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    check("存在 Python 脚本", len(scripts) > 0, f"{len(scripts)} 个")
    bad = []
    for s in scripts:
        try:
            py_compile.compile(str(s), doraise=True)
        except Exception as e:
            bad.append(f"{s.name}: {e}")
    check("所有 Python 脚本可编译", not bad, f"失败 {bad}" if bad else "")


# ---------------------------------------------------------------------------
# 5. JS 脚本语法（需 node）
# ---------------------------------------------------------------------------
def test_js_scripts_syntax() -> None:
    scripts = sorted((ROOT / "scripts").glob("*.js"))
    if not scripts:
        check("存在 JS 脚本", False)
        return
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=20, check=True)
    except Exception:
        print("[SKIP] 未安装 node，跳过 JS 语法检查")
        return
    bad = []
    for s in scripts:
        r = subprocess.run(["node", "--check", str(s)], capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            bad.append(f"{s.name}: {r.stderr.strip()[:80]}")
    check("所有 JS 脚本语法正确", not bad, f"失败 {bad}" if bad else f"{len(scripts)} 个")


# ---------------------------------------------------------------------------
# 6. 中文字体检查逻辑单测（用构造 XML 验证判定正确）
# ---------------------------------------------------------------------------
CJK_FONTS = {"微软雅黑", "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC",
             "思源黑体", "Hiragino Sans GB", "PingFang SC", "宋体", "SimSun"}


def analyze_cjk_fonts(xml: str) -> dict:
    """从 slide XML 分析中文字体绑定情况（与 SKILL.md 中的检查逻辑一致）。"""
    ea = set(re.findall(r'<a:ea typeface="([^"]+)"', xml))
    latin = set(re.findall(r'<a:latin typeface="([^"]+)"', xml))
    has_cjk = bool(re.search(r"<a:t>[^<]*[\u4e00-\u9fff]", xml))
    problems = []
    if has_cjk and not ea:
        problems.append("CJK_NO_EA")
    if (latin & CJK_FONTS) and not ea:
        problems.append("CJK_FACE_UNREACHED")
    return {"ea": ea, "latin": latin, "has_cjk": has_cjk, "problems": problems}


def test_cjk_font_logic() -> None:
    # 场景 A：中文 + 正确设置 ea 槽位 -> 无问题
    a = analyze_cjk_fonts(
        '<a:rPr><a:latin typeface="Arial"/><a:ea typeface="Microsoft YaHei"/></a:rPr>'
        '<a:t>中文标题</a:t>'
    )
    check("CJK 正确绑定 ea -> 无问题", not a["problems"], str(a["problems"]))

    # 场景 B：中文但无 ea 槽位 -> CJK_NO_EA
    b = analyze_cjk_fonts(
        '<a:rPr><a:latin typeface="Arial"/></a:rPr><a:t>中文标题</a:t>'
    )
    check("中文缺 ea 槽位 -> 报 CJK_NO_EA", "CJK_NO_EA" in b["problems"], str(b["problems"]))

    # 场景 C：中文字体写在 latin 槽位（静默失效）-> CJK_FACE_UNREACHED
    c = analyze_cjk_fonts(
        '<a:rPr><a:latin typeface="微软雅黑"/></a:rPr><a:t>中文标题</a:t>'
    )
    check("中文字体写在 latin 槽位 -> 报 CJK_FACE_UNREACHED",
          "CJK_FACE_UNREACHED" in c["problems"], str(c["problems"]))

    # 场景 D：纯英文无中文 -> 不报错（避免误报）
    d = analyze_cjk_fonts(
        '<a:rPr><a:latin typeface="Arial"/></a:rPr><a:t>Hello World</a:t>'
    )
    check("纯英文不误报", not d["problems"], str(d["problems"]))


# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 60)
    print(" duduppt 结构自检")
    print("=" * 60)
    for fn in (test_skill_frontmatter, test_referenced_files_exist, test_package_json,
               test_python_scripts_compile, test_js_scripts_syntax, test_cjk_font_logic):
        print(f"\n--- {fn.__name__} ---")
        fn()
    print("\n" + "=" * 60)
    if FAILED:
        print(f" 失败 {len(FAILED)} 项: {FAILED}")
        print("=" * 60)
        return 1
    print(" 全部通过")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
