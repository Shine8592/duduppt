# 🚀 快速开始

> 5 分钟跑通 duduppt。本文档面向**第一次使用**的人。

---

## 一、这是什么

duduppt 是一个 **Agent Skill** —— 它不是可执行程序，而是一份**给 AI 助手看的说明书 + 配套脚本**。

装上之后，你对 AI 说"帮我做个 PPT"，它就会按 duduppt 的**四阶段方法论**来做：

```
Phase 0  深度调研    -> 材料不全时自动补证据
Phase 1  分析        -> 证据表 + 故事线 + 逐页大纲   [确认门]
Phase 2  视觉蓝图    -> 风格 + 布局 + 配图规划        [确认门]
Phase 3  生成 + QA   -> 逐页生成、逐页验收、合并交付
```

**核心特点**：输出的是**原生可编辑 PPTX**（能在 PowerPoint 里改每个字），
不是 HTML 幻灯片、不是截图。

---

## 二、安装

### 2.1 装到哪里

根据你的 AI 客户端选择目录：

| 客户端 | 技能目录 |
|---|---|
| Claude Code | `~/.claude/skills/duduppt/` 或项目内 `.claude/skills/duduppt/` |
| opencode | `~/.config/opencode/skills/duduppt/` |
| 其他支持 Agent Skills 的客户端 | 按其约定（通常是 `skills/duduppt/`） |

### 2.2 复制文件

```bash
# 以 Claude Code 为例
git clone https://github.com/Shine8592/duduppt.git /tmp/duduppt
cp -r /tmp/duduppt ~/.claude/skills/duduppt
```

目录结构应该是：

```
~/.claude/skills/duduppt/
├── SKILL.md                 <-- 入口（AI 读这个）
├── references/              <-- 按需加载的方法论文档
├── scripts/                 <-- 配套脚本
├── assets/                  <-- 风格样张
└── examples/                <-- 示例输出
```

### 2.3 环境依赖（按需）

**必需**：无。SKILL.md 是纯文档，AI 读了就能用。

**推荐安装**（用到对应能力时才需要）：

| 依赖 | 用途 | 安装 |
|---|---|---|
| **Node.js ≥18 + pptxgenjs** | 生成高保真 PPTX | `npm install pptxgenjs` |
| **LibreOffice** | 渲染 QA（导出 PNG 检查排版）| [下载](https://www.libreoffice.org/download/download/) |
| **python-pptx** | 快速出稿 / 编辑模板 | `pip install python-pptx` |
| 图库 API key（可选）| 搜索照片素材 | Pexels/Unsplash/Pixabay 免费注册 |

> 💡 **只装 Node.js + pptxgenjs 就能出活**。LibreOffice 只影响 QA 方式
> （没有它就用零依赖的结构检查兜底）。

---

## 三、第一次使用

对你的 AI 说：

```
帮我做一个关于「中国财富管理市场 2026」的汇报 PPT，给高管的
```

它会：
1. 先做**设计访谈**（问你 5 个问题：受众 / 场景 / 色调 / 图文比 / 参考）
2. 建**证据表**（每个数据带来源和置信度，缺的标"需验证"不编造）
3. 出**逐页大纲** → **等你确认**
4. 选**风格 + 布局** → **等你确认**
5. **逐页生成 + 逐页 QA + 逐页确认**
6. 合并交付 `.pptx`

---

## 四、用配套脚本单独跑

有些脚本可以独立使用（不依赖 AI 对话）：

```bash
cd ~/.claude/skills/duduppt

# 1) 深度调研（补证据）
python3 scripts/research-topic.py --topic "中国财富管理市场 2026" --depth deep

# 2) 搜索图片素材
python3 scripts/search-image.py --query "business meeting" --source pexels --count 3

# 3) 从参考 PPTX 学风格
python3 scripts/learn-from-pptx.py --input reference.pptx --compare

# 4) 从 Logo 提取配色
python3 scripts/extract-palette.py --input brand-logo.png --format json
```

### QA 相关（生成后）

```bash
# 机械检查（零依赖，秒级）—— 每次必跑
python3 scripts/qa-check.py --deck output.pptx

# 修正中文字体东亚槽位（重要！pptxgenjs 的坑）
python3 scripts/fix-cjk-font.py --deck output.pptx

# 数字溯源（防止编造数据）
python3 scripts/trace-claims.py --deck output.pptx --evidence evidence.json

# 图片来源与授权登记
python3 scripts/collect-credits.py --manifest slide_manifest.json

# 导出 HTML 预览（可选）
python3 scripts/export-html.py --deck output.pptx
```

---

## 五、看示例

`examples/duduppt-sample.pptx` 是一份**完整的 5 页示例**，可以直接打开看效果。

想快速看它的内容而不用 PowerPoint：

```bash
python3 scripts/export-html.py --deck examples/duduppt-sample.pptx --mode text
# 用浏览器打开生成的 .html
```

---

## 六、常见问题

**Q：生成的 PPT 文字不能编辑？**
A：检查是否"把文字烘焙进了图片"。duduppt 的**红线**禁止这样做。
跑 `python3 scripts/qa-check.py --deck output.pptx` 会检测整页大图。

**Q：中文在某些电脑上显示异常？**
A：中文字体问题。跑 `python3 scripts/fix-cjk-font.py --deck output.pptx`
修正东亚字体槽位，并把"本 deck 依赖『微软雅黑』"告知收件人。

**Q：图表是空白的？**
A：pptxgenjs 的经典坑 —— `addChart('column', ...)` 会产出空白页。
必须用 `addChart('bar', ..., {barDir: 'col'})`。
`qa-check.py` 会自动检测 `barDir`。详见 `references/chart-type-anatomy.md`。

**Q：想确认数据没编造？**
A：把证据表存成 JSON，跑 `trace-claims.py`，它会列出"页面上有但证据表里查不到"的数字。

**Q：没有 LibreOffice 能用吗？**
A：能。QA 的**机械项**（结构/字体/barDir/占位符）零依赖，永远可跑；
只有**视觉项**（文字溢出、重叠）需要渲染，此时退化为人工看图。

---

## 七、下一步

- 完整方法论 → [`SKILL.md`](../SKILL.md)
- 配色与风格 → [`references/palettes.md`](../references/palettes.md)
- 图表坑 → [`references/chart-type-anatomy.md`](../references/chart-type-anatomy.md)
- 中文字体与合并 → [`references/merge-and-qa.md`](../references/merge-and-qa.md)
- 变更历史 → [`CHANGELOG.md`](../CHANGELOG.md)
