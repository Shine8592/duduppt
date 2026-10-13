#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duduppt MCP 服务：把 QA 三件套 + 编辑 + 图表 + 画幅 暴露成 MCP 工具。

为什么有这个（竞品对比 v3 的 P2 升级）：
  把 duduppt 的护城河（证据链 QA）从「脚本」升级成「平台」——
  别的 Skill / Agent 也能通过 MCP 调用 duduppt 的 QA 能力，
  而不必复制脚本。这是差异化定位的长期价值所在。

暴露的工具（12 个）：
    ppt_capabilities     查看本服务支持哪些动作
    ppt_qa_check         机械检查（11 项 lint）
    ppt_qa_report        生成质量审计报告
    ppt_trace_claims     断言溯源（数字 ↔ 证据）
    ppt_qa_compare       盲读一致性对比
    ppt_snapshot_save    归档版本快照
    ppt_snapshot_list    列出历史版本
    ppt_canvas_formats   查询支持的画幅
    ppt_native_chart     生成原生图表（v3.2 新增）
    ppt_edit_text        编辑既有 PPTX 的文字（v3.2 新增）
    ppt_list_text        列出某页文本（v3.2 新增）
    ppt_retemplate       全篇换风格（v3.2 新增）

全部操作已工具化（v3.2 完成）：此前保留为脚本的
native-charts / edit-deck / omml-formula 现已可通过 MCP 调用，
仅 omml-formula 因需精确页码与公式参数仍建议脚本方式。

启动：
    python scripts/mcp_server.py

挂载到 MCP 客户端：
    {
      "mcp": {
        "duduppt": {
          "type": "local",
          "command": ["python", "-u", "scripts/mcp_server.py"]
        }
      }
    }
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = Path(__file__).resolve().parent

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    print("缺少 mcp 依赖：pip install 'mcp>=2.0.0'")
    raise SystemExit(2)

mcp = MCPServer("duduppt")

SERVER_VERSION = "3.1.0"


def _run_node(script: str, *args: str, timeout: int = 300, env: dict | None = None) -> dict:
    """调用 Node 脚本（pptxgenjs 生成引擎走 Node，不能用 sys.executable）。"""
    p = SKILL_DIR / script
    if not p.exists():
        return {"ok": False, "error": f"脚本不存在: {script}"}
    import os

    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    try:
        r = subprocess.run(
            ["node", str(p), *args],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, cwd=str(SKILL_DIR.parent),
            env=run_env,
        )
        out = r.stdout or ""
        try:
            return {"ok": r.returncode == 0, "exit_code": r.returncode,
                    "data": json.loads(out)}
        except json.JSONDecodeError:
            return {"ok": r.returncode == 0, "exit_code": r.returncode,
                    "text": out, "stderr": (r.stderr or "")[:500]}
    except FileNotFoundError:
        return {"ok": False, "error": "未找到 node，请先安装 Node.js 18+（pptxgenjs 生成引擎依赖）"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"脚本超时（{timeout}s）: {script}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def _run(script: str, *args: str, timeout: int = 180) -> dict:
    """调用同级 Python 脚本，返回结构化结果。"""
    p = SKILL_DIR / script
    if not p.exists():
        return {"ok": False, "error": f"脚本不存在: {script}"}
    try:
        r = subprocess.run(
            [sys.executable, str(p), *args],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, cwd=str(SKILL_DIR.parent),
        )
        out = r.stdout or ""
        # 尝试解析 JSON，否则返回原文
        try:
            return {"ok": r.returncode == 0, "exit_code": r.returncode,
                    "data": json.loads(out)}
        except json.JSONDecodeError:
            return {"ok": r.returncode == 0, "exit_code": r.returncode,
                    "text": out, "stderr": (r.stderr or "")[:500]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"脚本超时（{timeout}s）: {script}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


@mcp.tool()
def ppt_capabilities() -> dict:
    """查看 duduppt MCP 服务支持哪些动作，以及哪些仍以脚本方式调用。

    用途：开始操作前先调用，确认某动作是否可用，避免对着不支持的动作反复失败。

    返回：MCP 工具清单、脚本清单、以及"为什么有些操作没做成工具"的说明。
    """
    return {
        "ok": True,
        "server": "duduppt-mcp",
        "version": SERVER_VERSION,
        "mcp_tools": [
            {"name": "ppt_capabilities", "purpose": "查看支持的动作"},
            {"name": "ppt_qa_check", "purpose": "机械检查（11 项 lint）"},
            {"name": "ppt_qa_report", "purpose": "生成质量审计报告"},
            {"name": "ppt_trace_claims", "purpose": "断言溯源（数字 ↔ 证据）"},
            {"name": "ppt_qa_compare", "purpose": "盲读一致性对比"},
            {"name": "ppt_snapshot_save", "purpose": "归档版本快照"},
            {"name": "ppt_snapshot_list", "purpose": "列出历史版本"},
            {"name": "ppt_canvas_formats", "purpose": "查询支持的画幅"},
            {"name": "ppt_native_chart", "purpose": "生成原生图表（带编辑数据）"},
            {"name": "ppt_list_text", "purpose": "列出某页文本"},
            {"name": "ppt_edit_text", "purpose": "替换某页文字（改字不重建）"},
            {"name": "ppt_retemplate", "purpose": "全篇换风格"},
            {"name": "ppt_build_master", "purpose": "编译风格模板（真 sldLayout）"},
            # v3.2 新增：生成层工具（Phase 3 全流程）
            {"name": "ppt_generate_sample", "purpose": "生成示例 PPTX（验证链路）"},
            {"name": "ppt_editable_preview", "purpose": "生成可编辑 HTML 预览页"},
            {"name": "ppt_apply_changes", "purpose": "把 changes.json 写回 PPTX"},
            {"name": "ppt_omml_formula", "purpose": "写入原生 OMML 公式（可编辑）"},
            {"name": "ppt_snapshot_restore", "purpose": "回滚到指定版本"},
            {"name": "ppt_snapshot_diff", "purpose": "对比两个版本差异"},
        ],
        "script_only": [
            {"name": "omml-formula.py", "purpose": "写入 OMML 原生公式"},
            {"name": "generate-sample.js", "purpose": "示例 PPTX 生成（Node/pptxgenjs）"},
        ],
        "why_script_only": (
            "omml-formula 需要精确的页码与公式参数（分数/根号/上下标），"
            "脚本形式便于逐步确认；generate-sample.js 依赖 Node 环境。"
        ),
    }


@mcp.tool()
def ppt_qa_check(deck: str, min_font: float = 6.5) -> dict:
    """对 PPTX 做机械检查（11 项 lint），能靠 lint 秒判的绝不用渲染。

    参数：
    - deck：PPTX 文件路径
    - min_font：最小字号（pt），默认 6.5

    检查项：结构完整 / 占位文案 / 图表 / 中文字体 / 字体白名单 / 语言元数据 /
            整页大图 / 字号 / 文本溢出 / 元素遮挡 / 对比度

    返回：passes / warnings / failures 三份清单与统计。
    """
    r = _run("qa-check.py", "--deck", deck, "--min-font", str(min_font),
             "--format", "json")
    return r


@mcp.tool()
def ppt_qa_report(deck: str, evidence: str = "", blind: str = "",
                  manifest: str = "", prev: str = "") -> dict:
    """生成《质量审计报告》，把证据链 QA 变成可见的交付物。

    参数：
    - deck：PPTX 路径
    - evidence：证据表 JSON（断言溯源用，可选）
    - blind：盲读答复 JSON（可选）
    - manifest：slide_manifest.json（可选）
    - prev：上一版 PPTX（版本对比用，可选）

    返回：报告路径（JSON + Markdown）与整体评级 PASS/WARN/FAIL。
    """
    args = ["--deck", deck]
    if evidence:
        args += ["--evidence", evidence]
    if blind:
        args += ["--blind", blind]
    if manifest:
        args += ["--manifest", manifest]
    if prev:
        args += ["--prev", prev]
    return _run("qa-report.py", *args)


@mcp.tool()
def ppt_trace_claims(deck: str, evidence: str) -> dict:
    """断言溯源：检查 PPT 里的数字是否都能在证据表中找到来源。

    防 AI 编数 —— 这是 duduppt 的核心差异能力。

    参数：
    - deck：PPTX 路径
    - evidence：证据表 JSON 路径
    """
    return _run("trace-claims.py", "--deck", deck, "--evidence", evidence)


@mcp.tool()
def ppt_qa_compare(blind: str, manifest: str) -> dict:
    """盲读一致性对比：盲读答复 vs slide_manifest 的逐页一致性。

    参数：
    - blind：盲读答复 JSON
    - manifest：slide_manifest.json
    """
    return _run("qa-compare.py", "--blind", blind, "--manifest", manifest)


@mcp.tool()
def ppt_snapshot_save(deck: str, note: str = "", manifest: str = "") -> dict:
    """归档当前版本快照（每次反馈迭代后调用，便于后续回溯）。

    参数：
    - deck：PPTX 路径
    - note：版本备注（如"初稿"、"改了配色"）
    - manifest：一并归档的 slide_manifest.json（可选）
    """
    args = ["save", "--deck", deck]
    if note:
        args += ["--note", note]
    if manifest:
        args += ["--manifest", manifest]
    return _run("snapshot.py", *args)


@mcp.tool()
def ppt_snapshot_list(deck: str) -> dict:
    """列出某 PPTX 的所有历史版本快照。

    参数：
    - deck：PPTX 路径（用于定位归档目录）
    """
    return _run("snapshot.py", "list", "--deck", deck)


@mcp.tool()
def ppt_canvas_formats(name: str = "") -> dict:
    """查询支持的画幅（画布尺寸）。

    参数：
    - name：指定画幅 key 则显示详情；留空则列出全部

    可用画幅：ppt169 / ppt43 / xhs34(小红书3:4) / xhs11 / wx916(公众号9:16) /
             wx235 / a4 / a4l / banners
    """
    args = ["--list", "--format", "json"]
    if name:
        args = ["--show", name]
    return _run("canvas-formats.py", *args)


@mcp.tool()
def ppt_native_chart(deck: str, chart_type: str, categories: str,
                     series: list[str], out: str = "",
                     title: str = "", slide: int = 0) -> dict:
    """生成 PowerPoint 原生图表（带「编辑数据」按钮的真 Chart 对象）。

    参数：
    - deck：PPTX 路径（提供则在指定页叠加；留空则新建）
    - chart_type：bar / bar_h / line / pie / stacked / area
    - categories：类别，逗号分隔，如 "Q1,Q2,Q3,Q4"
    - series：系列列表，每项格式 "名称:v1,v2,..."，可多个
    - out：输出文件路径
    - title：图表标题
    - slide：叠加到 deck 的第几页（1 起；0 或省略则新建 deck）

    依赖 python-pptx。
    """
    args = ["--type", chart_type, "--categories", categories]
    for s in series:
        args += ["--series", s]
    if deck:
        args += ["--deck", deck]
        if slide and slide > 0:
            args += ["--slide", str(slide)]
    if out:
        args += ["--out", out]
    if title:
        args += ["--title", title]
    return _run("native-charts.py", *args)


@mcp.tool()
def ppt_list_text(deck: str, slide: int) -> dict:
    """列出指定页的所有文本（用于定位要改什么）。

    参数：
    - deck：PPTX 路径
    - slide：页码（1 起）
    """
    return _run("edit-deck.py", "--deck", deck,
                "list-text", "--slide", str(slide))


@mcp.tool()
def ppt_edit_text(deck: str, slide: int, find: str, replace: str,
                  out: str = "") -> dict:
    """替换指定页的文字（改字不重建，保留原设计与未改动页）。

    参数：
    - deck：PPTX 路径
    - slide：页码（1 起）
    - find：要找的原文
    - replace：替换为
    - out：输出文件（留空则 <原名>-edited.pptx，不覆盖原稿）
    """
    args = ["--deck", deck]
    if out:
        args += ["--out", out]
    args += ["set-text", "--slide", str(slide),
             "--find", find, "--replace", replace]
    return _run("edit-deck.py", *args)


@mcp.tool()
def ppt_retemplate(deck: str, style: str, out: str = "") -> dict:
    """把整份 deck 换成另一种风格（全篇配色 + 字体一起变）。

    参数：
    - deck：PPTX 路径
    - style：目标风格编号或名称（如 "05" 或 "浅灰白"）
    - out：输出文件（留空则 <原名>-<编号>.pptx）
    """
    args = ["--deck", deck, "--style", style]
    if out:
        args += ["--out", out]
    return _run("retemplate.py", *args)


@mcp.tool()
def ppt_build_master(style: str = "", out: str = "",
                     all_styles: bool = False, out_dir: str = "") -> dict:
    """编译风格模板（带真 sldLayout + 占位符）。

    参数：
    - style：单个风格编号/名称（与 all_styles 二选一）
    - out：单风格时的输出文件路径
    - all_styles：True 则批量编译全部 16 种风格
    - out_dir：批量时的输出目录

    注意：这不等价于 PowerPoint 的「改母版全篇自动跟随」，
          全篇换风格请用 ppt_retemplate。
    """
    args = []
    if all_styles:
        args += ["--all"]
        if out_dir:
            args += ["--dir", out_dir]
    else:
        if not style:
            return {"ok": False, "error": "需要 style 或 all_styles=True"}
        args += ["--style", style]
        if out:
            args += ["--out", out]
    return _run("build-master.py", *args)


@mcp.tool()
def ppt_generate_sample(out: str = "") -> dict:
    """生成 duduppt 示例 PPTX（5 页咨询风：封面/市场格局/核心瓶颈/解决方案/行动建议）。

    用途：验证链路是否正常（pptxgenjs 引擎 + 中文字体修正全跑通）。
    注意：这是**固定内容的示例**，不是按用户材料生成。
    真正的内容生成由 Skill 的四阶段流程编排（Agent 读 SKILL.md 自行组装 pptxgenjs 调用）。

    参数：
    - out：输出路径（留空则输出到 skill 的 examples/duduppt-sample.pptx）
    """
    env = {"DUDUPPT_OUT": out} if out else None
    return _run_node("generate-sample.js", env=env)


@mcp.tool()
def ppt_editable_preview(deck: str, out: str = "") -> dict:
    """生成**可编辑**的 HTML 预览页（浏览器打开后可直接在页面上改文字）。

    用途：可视化改字 —— 打开页面 → 点着改 → 导出 changes.json → 用 ppt_apply_changes 写回。
    比命令行 ppt_edit_text（需知道页码+原文）直观得多。

    参数：
    - deck：PPTX 路径
    - out：输出 HTML 路径（留空则 <原名>-editable.html）
    """
    args = ["--deck", deck]
    if out:
        args += ["--out", out]
    return _run("edit-html.py", *args)


@mcp.tool()
def ppt_apply_changes(changes: str, deck: str, out: str = "", inplace: bool = False) -> dict:
    """把 ppt_editable_preview 导出的 changes.json 写回 PPTX。

    参数：
    - changes：changes.json 路径（包含 slide/find/replace 列表）
    - deck：目标 PPTX
    - out：输出文件（留空则 <原名>-edited.pptx）
    - inplace：True 则就地修改并自动备份 .bak
    """
    args = ["--apply", changes, "--deck", deck]
    if out:
        args += ["--out", out]
    if inplace:
        args += ["--inplace"]
    return _run("edit-html.py", *args)


@mcp.tool()
def ppt_omml_formula(deck: str, slide: int, formula_type: str,
                     num: str = "", den: str = "", radicand: str = "",
                     base: str = "", exp: str = "", sub: str = "", text: str = "",
                     x: float = 1.0, y: float = 3.0, w: float = 4.0, h: float = 1.2,
                     out: str = "", inplace: bool = False) -> dict:
    """写入 PowerPoint 原生 OMML 公式（可双击编辑，不是图片）。

    参数：
    - deck：PPTX 路径
    - slide：页码（1 起）
    - formula_type：frac(分数) / sqrt(根号) / power(上标) / sub(下标) / plain(纯文本)
    - num/den：分数用（分子/分母）
    - radicand：根号用（被开方式）
    - base/exp/sub：power/sub 用（底数/指数/下标）
    - text：plain 用（如 "E = mc^2"）
    - x/y/w/h：位置尺寸（英寸）
    - out：输出文件（留空则 <原名>-formula.pptx）
    - inplace：就地修改并备份
    """
    args = ["--deck", deck, "--slide", str(slide), "--type", formula_type]
    for flag, val in (("--num", num), ("--den", den), ("--radicand", radicand),
                      ("--base", base), ("--exp", exp), ("--sub", sub), ("--text", text)):
        if val:
            args += [flag, val]
    args += ["--x", str(x), "--y", str(y), "--w", str(w), "--h", str(h)]
    if out:
        args += ["--out", out]
    if inplace:
        args += ["--inplace"]
    return _run("omml-formula.py", *args)


@mcp.tool()
def ppt_snapshot_restore(deck: str, version: str, to: str = "") -> dict:
    """回滚到指定版本快照（写操作不可撤销时用）。

    参数：
    - deck：PPTX 路径（用于定位归档目录）
    - version：版本名（用 ppt_snapshot_list 查看）
    - to：输出路径（留空则覆盖原 deck，会自动备份 .bak）
    """
    args = ["restore", "--deck", deck, "--version", version]
    if to:
        args += ["--to", to]
    return _run("snapshot.py", *args)


@mcp.tool()
def ppt_snapshot_diff(a: str, b: str) -> dict:
    """对比两个版本的差异（文件级：新增/删除/变更）。"""
    return _run("snapshot.py", "diff", "--a", a, "--b", b)


def main() -> None:
    print(f"[duduppt] MCP 服务启动 v{SERVER_VERSION}", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
