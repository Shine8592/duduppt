#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duduppt MCP 服务：把 QA 三件套 + 编辑 + 图表 + 画幅 暴露成 MCP 工具。

为什么有这个（竞品对比 v3 的 P2 升级）：
  把 duduppt 的护城河（证据链 QA）从「脚本」升级成「平台」——
  别的 Skill / Agent 也能通过 MCP 调用 duduppt 的 QA 能力，
  而不必复制脚本。这是差异化定位的长期价值所在。

暴露的工具（8 个）：
    ppt_capabilities    查看本服务支持哪些动作
    ppt_qa_check        机械检查（11 项 lint）
    ppt_qa_report       生成质量审计报告
    ppt_trace_claims    断言溯源（数字 ↔ 证据）
    ppt_qa_compare      盲读一致性对比
    ppt_snapshot_save   归档版本快照
    ppt_snapshot_list   列出历史版本
    ppt_canvas_formats  查询支持的画幅

未做成 MCP 工具的操作（需要人参与或依赖 python-pptx 环境）：
    native-charts / edit-deck / omml-formula —— 仍以脚本方式调用，
    因为它们通常需要人工确认改动位置（页码、原文），且 python-pptx
    在 MCP 环境下未必安装。

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


def _run(script: str, *args: str, timeout: int = 180) -> dict:
    """调用同级脚本，返回结构化结果。"""
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
            {"name": "ppt_qa_check", "purpose": "机械检查（11 项 lint）"},
            {"name": "ppt_qa_report", "purpose": "生成质量审计报告"},
            {"name": "ppt_trace_claims", "purpose": "断言溯源（数字 ↔ 证据）"},
            {"name": "ppt_qa_compare", "purpose": "盲读一致性对比"},
            {"name": "ppt_snapshot_save", "purpose": "归档版本快照"},
            {"name": "ppt_snapshot_list", "purpose": "列出历史版本"},
            {"name": "ppt_canvas_formats", "purpose": "查询支持的画幅"},
        ],
        "script_only": [
            {"name": "native-charts.py", "purpose": "生成原生图表（带编辑数据）"},
            {"name": "edit-deck.py", "purpose": "编辑既有 PPTX（改字不重建）"},
            {"name": "omml-formula.py", "purpose": "写入 OMML 原生公式"},
            {"name": "generate-sample.js", "purpose": "示例 PPTX 生成（Node/pptxgenjs）"},
        ],
        "why_script_only": (
            "这些操作通常需要人工确认改动位置（页码、原文、图表序号），"
            "且依赖 python-pptx，在 MCP 环境下未必安装；"
            "做成脚本便于人工逐步确认，比自动化更稳妥。"
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


def main() -> None:
    print(f"[duduppt] MCP 服务启动 v{SERVER_VERSION}", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
