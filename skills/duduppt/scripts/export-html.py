#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPTX → HTML 预览导出（可选能力，供快速预览与非 PPT 场景分享）。

## 为什么需要它

PPTX 有两个场景不适合：
1. **快速预览**：只想看排版对不对，不想装 PowerPoint
2. **网页分享**：发给别人看，对方不一定有 Office

本脚本把 deck 转成**单文件 HTML**（零依赖，图片内联为 base64），
可直接用浏览器打开、也可贴到任意静态托管。

> ⚠️ 定位说明：duduppt 的**主交付物永远是原生 PPTX**（可编辑是底线）。
> HTML 只是**预览/分享的副产品**，不替代 PPTX。

## 实现方式

优先用 LibreOffice 转（保真度最高）：
    soffice --headless --convert-to html deck.pptx

LibreOffice 不可用时，退化为**纯文本预览 HTML**（列出每页文字），
仍能快速核对内容与页序。

用法：
    python scripts/export-html.py --deck output.pptx
    python scripts/export-html.py --deck output.pptx --out preview.html
    python scripts/export-html.py --deck output.pptx --mode text   # 强制纯文本模式

零依赖（仅标准库；LibreOffice 可选）。
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_soffice() -> str | None:
    for name in ("soffice", "soffice.exe", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    for c in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
              "/usr/bin/soffice",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if Path(c).exists():
            return c
    return None


def extract_slides_text(pptx: Path) -> list[tuple[int, list[str]]]:
    """从 pptx 抽取每页文字（用于纯文本预览模式）。"""
    out: list[tuple[int, list[str]]] = []
    with zipfile.ZipFile(pptx) as z:
        names = sorted(
            [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda x: int(re.search(r"(\d+)", x).group(1)),
        )
        for n in names:
            xml = z.read(n).decode("utf-8", "ignore")
            texts = [t.strip() for t in re.findall(r"<a:t>([^<]*)</a:t>", xml) if t.strip()]
            out.append((int(re.search(r"(\d+)", n).group(1)), texts))
    return out


def build_text_html(pptx: Path, slides: list[tuple[int, list[str]]]) -> str:
    """构造纯文本预览 HTML。"""
    blocks = []
    for n, texts in slides:
        body = "".join(f"<p>{html.escape(t)}</p>" for t in texts) or "<p class=empty>(空白页)</p>"
        blocks.append(f'<section class="slide"><div class="num">{n}</div>{body}</section>')
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(pptx.stem)} — 文本预览</title>
<style>
  :root {{ --accent:#8B1E1E; --bg:#F3F4EF; --ink:#1a1a1a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif; }}
  header {{ padding:24px 32px; border-bottom:1px solid #ddd; background:#fff; }}
  header h1 {{ margin:0 0 6px; font-size:20px; }}
  header .meta {{ font-size:12px; color:#777; }}
  main {{ max-width:960px; margin:0 auto; padding:24px 16px 64px; }}
  .slide {{ position:relative; background:#fff; border:1px solid #e3e3e3; border-radius:8px;
            padding:20px 24px 20px 56px; margin:0 0 16px; }}
  .num {{ position:absolute; left:16px; top:20px; width:28px; height:28px; border-radius:50%;
          background:var(--accent); color:#fff; font-size:13px; display:flex;
          align-items:center; justify-content:center; }}
  .slide p {{ margin:6px 0; line-height:1.6; font-size:14px; }}
  .slide p:first-of-type {{ font-weight:700; font-size:16px; }}
  .empty {{ color:#bbb; font-style:italic; }}
  footer {{ text-align:center; font-size:12px; color:#999; padding:16px; }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(pptx.stem)}</h1>
  <div class="meta">{len(slides)} 页 · 文本预览模式（非最终排版）· 由 duduppt 导出</div>
</header>
<main>
{chr(10).join(blocks)}
</main>
<footer>正式交付请使用原生 PPTX 文件（可编辑）</footer>
</body>
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="PPTX -> HTML 预览导出")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--out", default=None, help="输出 HTML 路径（默认同名 .html）")
    ap.add_argument("--mode", choices=["auto", "text"], default="auto",
                    help="auto: 优先 LibreOffice；text: 强制纯文本预览")
    args = ap.parse_args()

    pptx = Path(args.deck)
    if not pptx.exists():
        print(f"[FAIL] 文件不存在: {pptx}")
        return 1
    if pptx.suffix.lower() not in (".pptx", ".pptm"):
        print(f"[FAIL] 仅支持 .pptx/.pptm: {pptx}")
        return 1

    out = Path(args.out) if args.out else pptx.with_suffix(".html")

    if args.mode == "auto":
        soffice = find_soffice()
        if soffice:
            print(f"使用 LibreOffice 转换（{soffice}）...")
            with tempfile.TemporaryDirectory() as td:
                try:
                    r = subprocess.run(
                        [soffice, "--headless", "--norestore",
                         "--convert-to", "html", "--outdir", td, str(pptx)],
                        capture_output=True, text=True, timeout=180,
                    )
                    produced = Path(td) / (pptx.stem + ".html")
                    if produced.exists():
                        shutil.copy(produced, out)
                        print(f"[OK] 已导出（LibreOffice，保真度较高）: {out}")
                        print("     注意：LibreOffice 导出的 HTML 可能带额外资源文件，"
                              "跨机分享请打包整个目录")
                        return 0
                    print(f"[WARN] LibreOffice 未产出 HTML（退出码 {r.returncode}），退化到文本模式")
                except Exception as e:
                    print(f"[WARN] LibreOffice 转换失败（{type(e).__name__}），退化到文本模式")
        else:
            print("[INFO] 未检测到 LibreOffice，使用纯文本预览模式")

    slides = extract_slides_text(pptx)
    out.write_text(build_text_html(pptx, slides), encoding="utf-8")
    print(f"[OK] 已导出文本预览: {out}")
    print(f"     {len(slides)} 页 · 可直接用浏览器打开")
    return 0


if __name__ == "__main__":
    sys.exit(main())
