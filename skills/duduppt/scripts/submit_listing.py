#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""向 datawhalechina/ai-skills-for-everyone 提交 duduppt 收录 PR。

流程：在已 fork 的仓库里建分支 → 加卡片文件 → 开 PR 到上游。
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOKEN = (os.environ.get("GITHUB_TOKEN") or "").strip()
UPSTREAM = "datawhalechina/ai-skills-for-everyone"
FORK = "Shine8592/ai-skills-for-everyone"
CARD_SRC = Path(r"C:\Users\yaner\AppData\Local\Temp\opencode\duduppt-card.md")
CARD_PATH = "catalog/writing-and-office/duduppt.md"
BRANCH = "add-duduppt-skill"

if not TOKEN:
    print("缺少 GITHUB_TOKEN")
    raise SystemExit(2)

H = {"Authorization": f"token {TOKEN}", "User-Agent": "ps",
     "Accept": "application/vnd.github+json"}
OP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def api(method, path, body=None, repo=FORK):
    url = f"https://api.github.com/repos/{repo}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=H, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with OP.open(req, timeout=60) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw.strip() else {}


def main():
    # 1. fork 的 main HEAD
    ref = api("GET", "/git/ref/heads/main")
    base_sha = ref["object"]["sha"]
    print(f"fork main: {base_sha[:12]}")

    # 2. 创建分支（已存在则忽略）
    try:
        api("POST", "/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": base_sha})
        print(f"分支已创建: {BRANCH}")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"分支已存在: {BRANCH}")
        else:
            raise

    # 3. 写卡片文件
    content = CARD_SRC.read_text(encoding="utf-8")
    body = {
        "message": "docs: 收录 duduppt（证据链可审计的咨询风 PPT 生成 Skill）",
        "content": base64.b64encode(content.encode("utf-8")).decode(),
        "branch": BRANCH,
    }
    try:
        api("PUT", f"/contents/{CARD_PATH}", body)
        print(f"卡片已写入: {CARD_PATH}")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            # 已存在，需要提供 sha 更新
            cur = api("GET", f"/contents/{CARD_PATH}?ref={BRANCH}")
            body["sha"] = cur["sha"]
            api("PUT", f"/contents/{CARD_PATH}", body)
            print(f"卡片已更新: {CARD_PATH}")
        else:
            raise

    # 4. 开 PR 到上游
    pr_body = """## 收录申请：duduppt

**来源**：https://github.com/Shine8592/duduppt
**许可证**：MIT
**分类**：写作与办公 / PPT 生成

### 一句话说明

duduppt 是强调「证据链可审计」的咨询风格 PPT 生成 Skill：不只排页面，还会对每页结论做盲读验收、把 PPT 里的数字追溯到证据来源，并输出一份质量审计报告。

### 为什么值得收录

- **差异点明确**：同类工具（如已收录的 ppt-master）重点在原生对象模型深度；duduppt 重点在「生成结果可信、可追溯、可审计」——盲读验收、断言溯源、质量审计报告，这三项组合在同类里少见。
- **QA 能力完整**：机械检查 11 项（结构/占位文案/图表/中文字体/字体白名单/语言元数据/整页大图/字号/文本溢出/元素遮挡/对比度），零依赖秒级返回。
- **中文场景扎实**：内置中文字体东亚槽位 `<a:ea>` 修正，解决 pptxgenjs 中文静默回退问题；支持小红书 3:4、公众号 9:16 等中文投放画幅。
- **解决真实痛点**：支持编辑既有 PPTX（改字不重建），命中「改一个字等于重做一遍」的行业痛点。
- **MIT + Skill 形态**：可 `npx skills add Shine8592/duduppt` 一键安装，文档完整。

### 如实说明限制

- 星标数为 0，是 2026-07 创建的新项目，社区规模远小于同类头部（卡片中已如实标注，未虚报）。
- 依赖 Python 3.10+ 与 Node.js（pptxgenjs），非纯网页工具。
- 复杂动画、转场、SmartArt 未支持。

### 已核对

- [x] 来源公开可访问
- [x] 许可证清楚（MIT）
- [x] 项目在维护（最近更新 2026-10-12）
- [x] README / SKILL.md 说明了用法
- [x] 解决具体任务，非泛泛提示词
- [x] 无隐私、版权、账号安全风险

卡片内容按 `templates/skill-card-template.md` 填写，放在 `catalog/writing-and-office/`。
"""
    try:
        pr = api("POST", "/pulls", {
            "title": "收录 duduppt：证据链可审计的咨询风 PPT 生成 Skill",
            "head": f"Shine8592:{BRANCH}",
            "base": "main",
            "body": pr_body,
        }, repo=UPSTREAM)
        print(f"\n[OK] PR 已创建: {pr['html_url']}")
        print(f"    #{pr['number']}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        if e.code == 422 and "already exists" in detail:
            print("PR 已存在（可能之前开过）")
        else:
            print(f"PR 创建失败 HTTP {e.code}: {detail}")
            raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
