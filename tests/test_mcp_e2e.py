#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duduppt MCP 端到端烟雾测试：真实拉起 stdio server 走完整协议。

要点：用单独线程读 stdout，主线程带超时等待；
      发完消息后关闭 stdin 让 server 自然退出并 flush 输出。
"""

import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "skills" / "duduppt" / "scripts" / "mcp_server.py"
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
    print("=" * 60)
    print(" duduppt MCP 端到端烟雾测试")
    print("=" * 60)

    # mcp 是可选依赖：CI 环境未必安装，缺则优雅跳过（不失败）
    try:
        import mcp  # noqa: F401
    except ImportError:
        print("\n[SKIP] 未安装 mcp 包，跳过 MCP 端到端测试")
        print("       本地如需测试：pip install 'mcp>=2.0.0'")
        return 0

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "-u", str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", cwd=str(ROOT), env=env,
    )

    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "smoke", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "ppt_capabilities", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "ppt_canvas_formats", "arguments": {}}},
    ]

    # 线程读 stdout，避免主线程阻塞
    q: queue.Queue = queue.Queue()

    def reader():
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    q.put(json.loads(line))
                except ValueError:
                    pass
        except Exception:
            pass

    threading.Thread(target=reader, daemon=True).start()

    # 主线程写消息（每条间隔，确保被处理）
    for m in msgs:
        try:
            proc.stdin.write(json.dumps(m) + "\n")
            proc.stdin.flush()
        except Exception:
            break
        time.sleep(0.3)

    # 收集响应（最多等 25 秒）
    responses = []
    deadline = time.time() + 25
    while time.time() < deadline and len(responses) < len(msgs) - 1:
        try:
            responses.append(q.get(timeout=1.0))
        except queue.Empty:
            continue

    # 关 stdin 让 server 退出
    try:
        proc.stdin.close()
    except Exception:
        pass
    try:
        proc.wait(timeout=8)
    except Exception:
        proc.kill()

    by_id = {r.get("id"): r for r in responses if "id" in r}
    print(f"  收到响应 {len(responses)} 条（id: {sorted(k for k in by_id if k)}）")

    init = by_id.get(1, {})
    check("initialize 成功", "result" in init)
    si = (init.get("result") or {}).get("serverInfo") or {}
    check("serverInfo.name = duduppt", si.get("name") == "duduppt", f"got={si}")

    tools = ((by_id.get(2, {}).get("result") or {}).get("tools")) or []
    names = sorted(t["name"] for t in tools)
    expected = sorted([
        "ppt_apply_changes", "ppt_build_master", "ppt_canvas_formats",
        "ppt_capabilities", "ppt_edit_text", "ppt_editable_preview",
        "ppt_generate_sample", "ppt_list_text", "ppt_native_chart",
        "ppt_omml_formula", "ppt_qa_check", "ppt_qa_compare", "ppt_qa_report",
        "ppt_retemplate", "ppt_snapshot_diff", "ppt_snapshot_list",
        "ppt_snapshot_restore", "ppt_snapshot_save", "ppt_trace_claims",
    ])
    check("19 个工具全部注册", names == expected, f"got={names}")
    check("无内部函数泄漏", not any(n.startswith("_") for n in names))
    no_desc = [t["name"] for t in tools if not (t.get("description") or "").strip()]
    check("所有工具有描述", not no_desc, f"缺={no_desc}")

    cap = by_id.get(3, {})
    check("ppt_capabilities 可调用", "result" in cap and "error" not in cap)
    cap_txt = json.dumps(cap.get("result") or {}, ensure_ascii=False)
    check("capabilities 含 MCP 工具清单", "mcp_tools" in cap_txt)
    check("capabilities 含 script_only 说明", "script_only" in cap_txt)

    cf = by_id.get(4, {})
    check("ppt_canvas_formats 可调用", "result" in cf and "error" not in cf)
    cf_txt = json.dumps(cf.get("result") or {}, ensure_ascii=False)
    check("含小红书画幅 xhs34", "xhs34" in cf_txt)

    print("\n" + "=" * 60)
    print(f"结果：{PASS} 通过 / {FAIL} 失败")
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
