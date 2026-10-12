#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可编辑 HTML 预览页：在浏览器里看着版式改文字，改完导出改动写回 PPTX。

为什么有这个脚本（P1 升级 —— 对标 dashi-ppt-skill 的「产物即编辑器」）：
  此前的 export-html.py 只是**静态文本预览**，footer 还写着
  「请使用原始 PPTX 文件」—— 它只能看，不能改。
  而 dashi-ppt-skill 的杀手锏正是：生成的东西本身就是一个编辑器。

  本脚本把预览页升级为**可编辑**：
    - 按幻灯片版式渲染（标题 / 正文分层）
    - 每段文字可直接在页面上点着改（contenteditable）
    - 一键导出改动（JSON：页码 + 原文 + 新文）
    - 配合 edit-deck.py 把改动批量写回 PPTX

用法：
    # 1. 生成可编辑预览页
    python scripts/edit-html.py --deck output.pptx --out preview.html

    # 2. 浏览器打开 preview.html，点着改，然后点「导出改动」下载 changes.json

    # 3. 把改动写回 PPTX（生成新文件，原文件不动）
    python scripts/edit-html.py --apply changes.json --deck output.pptx \\
        --out output-edited.pptx

依赖：零（仅标准库 zipfile + 正则）。写回阶段复用 edit-deck.py 的能力。

安全：
    - 写回默认输出到新文件，不覆盖原稿
    - 预览页不上传任何数据，纯本地 HTML
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SCRIPT_DIR = Path(__file__).resolve().parent


def extract_slides(pptx: Path) -> list[tuple[int, list[str]]]:
    """按页提取文本（与 export-html.py 同款）。"""
    out: list[tuple[int, list[str]]] = []
    with zipfile.ZipFile(pptx) as z:
        names = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda n: int(re.search(r"(\d+)", n).group(1)),
        )
        for n in names:
            xml = z.read(n).decode("utf-8", "ignore")
            texts = [t.strip() for t in re.findall(r"<a:t>([^<]*)</a:t>", xml) if t.strip()]
            out.append((int(re.search(r"(\d+)", n).group(1)), texts))
    return out


def build_editable_html(pptx: Path, slides: list[tuple[int, list[str]]]) -> str:
    """构造可编辑预览页。"""
    blocks = []
    for n, texts in slides:
        if not texts:
            paras = '<div class="line" contenteditable="true" data-idx="0">(空白页)</div>'
        else:
            paras = "".join(
                f'<div class="line{" title" if i == 0 else ""}" '
                f'contenteditable="true" data-idx="{i}">{html.escape(t)}</div>'
                for i, t in enumerate(texts)
            )
        blocks.append(
            f'<section class="slide" data-slide="{n}">'
            f'<div class="num">{n}</div>'
            f'<div class="canvas">{paras}</div>'
            f'</section>'
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(pptx.stem)} — 可编辑预览</title>
<style>
  :root {{ --accent:#8B1E1E; --bg:#F3F4EF; --ink:#1a1a1a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif; }}
  header {{ padding:20px 28px; background:#fff; border-bottom:1px solid #ddd;
            position:sticky; top:0; z-index:10; display:flex; align-items:center;
            gap:16px; flex-wrap:wrap; }}
  header h1 {{ margin:0; font-size:18px; }}
  header .meta {{ font-size:12px; color:#777; }}
  header .spacer {{ flex:1; }}
  button {{ background:var(--accent); color:#fff; border:0; padding:8px 16px;
            border-radius:6px; cursor:pointer; font-size:13px; }}
  button:hover {{ opacity:.9; }}
  button.ghost {{ background:#fff; color:var(--accent);
                  border:1px solid var(--accent); }}
  main {{ max-width:940px; margin:0 auto; padding:24px 16px 80px; }}
  .slide {{ position:relative; background:#fff; border:1px solid #e3e3e3;
            border-radius:8px; margin:0 0 18px; overflow:hidden; }}
  .num {{ position:absolute; left:14px; top:14px; width:26px; height:26px;
          border-radius:50%; background:var(--accent); color:#fff;
          font-size:12px; display:flex; align-items:center;
          justify-content:center; z-index:2; }}
  .canvas {{ padding:24px 28px 24px 56px; min-height:120px; }}
  .line {{ margin:6px 0; line-height:1.6; font-size:14px; padding:3px 6px;
           border-radius:4px; outline:none; }}
  .line:hover {{ background:#fafafa; }}
  .line:focus {{ background:#fff8e6; box-shadow:0 0 0 2px #f0d9a0; }}
  .line.title {{ font-weight:700; font-size:17px; }}
  footer {{ position:fixed; bottom:0; left:0; right:0; background:#fff;
            border-top:1px solid #ddd; text-align:center; font-size:12px;
            color:#888; padding:10px; }}
  .changed {{ background:#e8f5e9; }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(pptx.stem)}</h1>
  <div class="meta">{len(slides)} 页 · 可直接点着改文字</div>
  <div class="spacer"></div>
  <button onclick="exportChanges()">导出改动 (changes.json)</button>
  <button class="ghost" onclick="resetAll()">还原</button>
</header>
<main>
{chr(10).join(blocks)}
</main>
<footer>
  改动导出后，用
  <code>python scripts/edit-html.py --apply changes.json --deck {html.escape(pptx.name)} --out 新文件.pptx</code>
  写回 PPTX
</footer>
<script>
const ORIG = {{}};
document.querySelectorAll('.line').forEach(el => {{
  ORIG[el.closest('.slide').dataset.slide + ':' + el.dataset.idx] = el.textContent;
}});
function collect() {{
  const changes = [];
  document.querySelectorAll('.line').forEach(el => {{
    const key = el.closest('.slide').dataset.slide + ':' + el.dataset.idx;
    const now = el.textContent;
    if (now !== ORIG[key]) {{
      changes.push({{
        slide: parseInt(el.closest('.slide').dataset.slide, 10),
        idx: parseInt(el.dataset.idx, 10),
        find: ORIG[key],
        replace: now
      }});
    }} else {{
      el.classList.remove('changed');
    }}
    if (now !== ORIG[key]) el.classList.add('changed');
  }});
  return changes;
}}
function exportChanges() {{
  const changes = collect();
  if (!changes.length) {{ alert('没有改动'); return; }}
  const blob = new Blob([JSON.stringify({{changes}}, null, 2)],
                        {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'changes.json';
  a.click();
  alert('已导出 ' + changes.length + ' 处改动');
}}
function resetAll() {{
  document.querySelectorAll('.line').forEach(el => {{
    const key = el.closest('.slide').dataset.slide + ':' + el.dataset.idx;
    el.textContent = ORIG[key];
    el.classList.remove('changed');
  }});
}}
</script>
</body>
</html>"""


def apply_changes(deck: Path, changes_file: Path, out: Path | None, inplace: bool) -> int:
    """把 changes.json 的改动写回 PPTX（复用 edit-deck.py）。"""
    # 用 utf-8-sig 读取：容错 Windows 记事本 / PowerShell 保存时加的 BOM。
    # 实测 PowerShell 的 Set-Content -Encoding UTF8 会写 BOM，
    # 用 utf-8 解析会直接抛 JSONDecodeError，故这里必须带 -sig。
    raw = changes_file.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[FAIL] changes.json 解析失败: {e}")
        return 1
    changes = data.get("changes") or []
    if not changes:
        print("没有改动需要应用")
        return 0

    edit_deck = SCRIPT_DIR / "edit-deck.py"
    if not edit_deck.exists():
        print("[FAIL] 找不到 edit-deck.py")
        return 1

    dst = out if out else deck.with_name(deck.stem + "-edited" + deck.suffix)
    # 先复制一份作为工作副本（不覆盖原稿）
    work = dst
    import shutil
    work.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(deck, work)

    # 逐条应用：调用 edit-deck.py 的 set-text（inplace 模式，它会自动备份 .bak）
    applied = 0
    failed = 0
    for c in changes:
        # 注意：--inplace 是 edit-deck.py 的**顶层参数**，必须放在子命令之前
        # （放子命令后会报 unrecognized arguments，实测踩过）
        args = [
            "--deck", str(work), "--inplace", "set-text",
            "--slide", str(c["slide"]),
            "--find", str(c["find"]),
            "--replace", str(c["replace"]),
        ]
        r = subprocess.run(
            [sys.executable, str(edit_deck), *args],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(SCRIPT_DIR.parent),
        )
        if r.returncode == 0 and "已就地保存" in (r.stdout or ""):
            applied += 1
        else:
            failed += 1
            print(f"   ⚠️ 第 {c['slide']} 页改动失败: "
                  f"{(r.stdout or r.stderr or '')[:120]}")
    print(f"\n✅ 改动写回完成: {work}")
    print(f"   应用 {applied} 处 / 失败 {failed} 处")
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="duduppt 可编辑 HTML 预览")
    ap.add_argument("--deck", help="PPTX 路径（生成预览或应用改动时需要）")
    ap.add_argument("--out", help="输出 HTML（生成模式）或 PPTX（应用模式）")
    ap.add_argument("--apply", help="应用 changes.json 到 PPTX")
    ap.add_argument("--inplace", action="store_true", help="应用时就地修改（自动备份）")
    args = ap.parse_args()

    if args.apply:
        if not args.deck:
            print("[FAIL] --apply 需要同时给 --deck")
            return 1
        return apply_changes(
            Path(args.deck), Path(args.apply),
            Path(args.out) if args.out else None, args.inplace,
        )

    if not args.deck:
        print("[FAIL] 需要 --deck（或用 --apply 应用改动）")
        return 1
    deck = Path(args.deck)
    if not deck.exists():
        print(f"[FAIL] 文件不存在: {deck}")
        return 1

    slides = extract_slides(deck)
    out_html = Path(args.out) if args.out else deck.with_name(
        deck.stem + "-editable.html"
    )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(build_editable_html(deck, slides), encoding="utf-8")

    print(f"✅ 已生成可编辑预览: {out_html}")
    print(f"   {len(slides)} 页 · 可直接点着改文字")
    print()
    print("   下一步：")
    print(f"   1. 浏览器打开 {out_html.name}")
    print("   2. 点着改文字 → 点「导出改动」得到 changes.json")
    print(f"   3. python scripts/edit-html.py --apply changes.json \\")
    print(f"          --deck {deck.name} --out 新文件.pptx")
    return 0


if __name__ == "__main__":
    sys.exit(main())
