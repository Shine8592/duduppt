#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duduppt API 推送：把本地已提交内容同步到 GitHub（绕过 git 直连不稳）。

用法：
    set GITHUB_TOKEN=...   （必填）
    python scripts/push_via_api.py          # 推送 HEAD commit 的全部变更
"""

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOKEN = (os.environ.get("GITHUB_TOKEN") or "").strip()
REPO = os.environ.get("DUDUPPT_REPO", "Shine8592/duduppt")
BRANCH = "main"
ROOT = Path(__file__).resolve().parent.parent

if not TOKEN:
    print("缺少 GITHUB_TOKEN 环境变量")
    raise SystemExit(2)

H = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "ps",
    "Accept": "application/vnd.github+json",
}
OP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def api(method, path, body=None):
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=H, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with OP.open(req, timeout=60) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw.strip() else {}


def main():
    # 1. 本地 HEAD 与变更文件清单（相对仓库根，git 会输出统一格式）
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    changed = subprocess.run(
        ["git", "diff", "--name-only", "origin/main..HEAD", "--diff-filter=ACMR"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.split()
    # 优先用 HEAD~1..HEAD（本次提交），失败则退回与远程比较
    if not changed:
        changed = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD", "--diff-filter=ACMR"],
            cwd=ROOT, capture_output=True, text=True,
        ).stdout.split()
    print(f"local HEAD: {head[:12]}")
    print(f"待推送文件: {len(changed)}")

    if not changed:
        print("没有文件要推送")
        return 0

    # 2. 远程 HEAD
    ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    base_sha = ref["object"]["sha"]
    print(f"remote base: {base_sha[:12]}")
    commit = api("GET", f"/repos/{REPO}/git/commits/{base_sha}")
    base_tree = commit["tree"]["sha"]

    # 3. 逐文件建 blob
    tree_items = []
    for rel in sorted(changed):
        p = ROOT / rel
        if not p.is_file():
            print(f"  [SKIP] 本地不存在: {rel}")
            continue
        raw = p.read_bytes()
        blob = api(
            "POST",
            f"/repos/{REPO}/git/blobs",
            {
                "content": base64.b64encode(raw).decode(),
                "encoding": "base64",
            },
        )
        tree_items.append({
            "path": rel,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print(f"  [BLOB] {rel} ({len(raw)}B)")

    if not tree_items:
        print("无可推送内容")
        return 1

    # 4. 建 tree / commit / 更新 ref
    tree = api(
        "POST", f"/repos/{REPO}/git/trees",
        {"base_tree": base_tree, "tree": tree_items},
    )
    msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8",
    ).stdout.strip()
    new_commit = api(
        "POST", f"/repos/{REPO}/git/commits",
        {"message": msg, "tree": tree["sha"], "parents": [base_sha]},
    )
    api(
        "PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}",
        {"sha": new_commit["sha"]},
    )
    print(f"\n[OK] 已推送 {len(tree_items)} 个文件，commit {new_commit['sha'][:12]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:400]}")
        raise SystemExit(1)
