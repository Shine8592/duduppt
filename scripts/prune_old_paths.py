#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""删除远程仓库中的旧路径残留（v3 重构后 scripts/ references/ assets/ examples/ 已移入 skills/duduppt/）。

用法：
    set GITHUB_TOKEN=...
    python scripts/prune_old_paths.py
"""

import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOKEN = (os.environ.get("GITHUB_TOKEN") or "").strip()
REPO = "Shine8592/duduppt"
BRANCH = "main"

if not TOKEN:
    print("缺少 GITHUB_TOKEN")
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
    ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    base_sha = ref["object"]["sha"]
    commit = api("GET", f"/repos/{REPO}/git/commits/{base_sha}")
    base_tree = commit["tree"]["sha"]
    print(f"base: {base_sha[:12]}")

    tree = api("GET", f"/repos/{REPO}/git/trees/{BRANCH}?recursive=1")
    old = [
        t["path"]
        for t in tree.get("tree", [])
        if t["type"] == "blob"
        and t["path"].startswith(("scripts/", "references/", "assets/", "examples/"))
    ]
    print(f"旧路径残留 {len(old)} 个文件待删除")
    if not old:
        print("无需清理")
        return 0

    # 用 sha=null 的 tree item 删除文件
    items = [{"path": p, "mode": "100644", "type": "blob", "sha": None} for p in old]
    new_tree = api(
        "POST", f"/repos/{REPO}/git/trees",
        {"base_tree": base_tree, "tree": items},
    )
    new_commit = api(
        "POST", f"/repos/{REPO}/git/commits",
        {
            "message": "chore: 清理 v3 重构后的旧路径残留（已移入 skills/duduppt/）",
            "tree": new_tree["sha"],
            "parents": [base_sha],
        },
    )
    api(
        "PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}",
        {"sha": new_commit["sha"]},
    )
    print(f"[OK] 已删除 {len(old)} 个旧文件，commit {new_commit['sha'][:12]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:400]}")
        raise SystemExit(1)
