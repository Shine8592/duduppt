# Changelog

All notable changes to **duduppt**. Format follows [Keep a Changelog](https://keepachangelog.com/);
versioning follows [Semantic Versioning](https://semver.org/).

---

## [3.2.0] — 2026-10-12

> 完整背景见 `competitive-analysis-v3.md`（GitHub PPT 项目全景对比）。

### Added — 分发（P0 前置）

- **Skill 本体移入 `skills/duduppt/`**，对齐主流 Skill 布局
- **支持 `npx skills add Shine8592/duduppt`** 一键安装（任何 Agent 通用）
- **Claude Code 插件市场元数据** `.claude-plugin/marketplace.json`
- **English README**（`README_EN.md`），中文 README 顶部互链
- 提交收录申请：`datawhalechina/ai-skills-for-everyone` PR #3

### Added — 证据链审计（护城河）

- `qa-report.py` 生成《质量审计报告》（JSON + Markdown），随 PPTX 一起交付
- `snapshot.py` 版本快照：save / list / restore / diff，回滚前自动备份
- `qa-check.py` 扩展至 **11 项 lint**：新增文本溢出 / 元素遮挡 / 对比度

### Added — 生成与编辑能力

- `native-charts.py` 原生 OOXML 图表（带「编辑数据」），支持 6 种类型
- `edit-deck.py` 编辑既有 PPTX：改字 / 改图表数据 / 增删页，未改动页保留
- `edit-html.py` **可编辑 HTML 预览页**：点着改 → 导出 → 写回 PPTX
- `canvas-formats.py` 9 种画幅（含小红书 3:4、公众号 9:16、A4、横幅）
- `omml-formula.py` 原生 OMML 公式（frac / sqrt / power / sub / plain）
- `build-master.py` 母版版式编译器，**16 种风格全部编译为带真 sldLayout 的模板**
- `retemplate.py` 一键换风格（全篇配色 + 字体一起变，实测 127 处替换）
- `mcp_server.py` MCP 服务，**13 个工具**（QA 能力平台化）

### Changed

- `qa-check` 遮挡检测排除整页背景框与完全包含关系（修复误报）
- `generate-sample.js` 输出路径改为相对定位（修复 Windows ENOENT）

### Fixed

- `generate-sample.js` 环境变量名 `DUDUPPt_OUT` 大小写错误（Linux 失效）
- `native-charts.py` XML 注入引号转义错误（反斜杠进入 XML）
- `edit-html.py` 读取 BOM JSON 失败（PowerShell 写入带 BOM）
- `edit-deck.py` `--out` / `--inplace` 为顶层参数，须置于子命令之前

### Changed — 诚实边界（重要）

- 文档明确：**「改母版一处全篇生效」不成立**。python-pptx 的 `defRPr` 不产生
  run 级继承，真正继承依赖 `theme1.xml` 的 `fontScheme`，python-pptx 支持很弱。
  全篇换风格请使用 `retemplate.py`。

---

## [2.1.0] — 2026-09-16

### Fixed

- Pexels API 403（User-Agent）
- Querit 端点 / 参数修正

---

## [2.0.0] — 2026-09

### Added

- **16+1 视觉风格库**（原 8 种 → 16 种 + 1 特选）：新增清新高客 / 电子杂志 / 瑞士数据 /
  极光渐变 / 黑胶唱片 / 莫兰迪 / 自然草木 / 经典商务蓝
- **设计访谈**（Phase 2 步骤 2.1）：选风格前先问 5 个问题（受众 / 场景 / 色调 / 图文比 / 参考）
- **配图管理体系**：统一的 `[图片-类型: 比例: 位置: 描述]` 标注语法 + 图文比例规则
  （叙事型 40–60% / 数据型 <20%）
- **演讲者备注自动生成**：每页 60–100 字口语化要点（非逐字稿），含生成规则与示例
- **`references/design-principles.md`**：10 条设计原则独立成篇
- **`references/prompt-templates.md`**：各阶段 system prompt 模板
- **`references/multi-model-guide.md`**：多模型选择指南（不同阶段配不同模型）
- **`references/layouts/layout-library.md`**：12 种布局模板库（562 行）
- **`scripts/learn-from-pptx.py`**：从参考 PPTX 自动提取配色/字体/布局并匹配预设风格
- **`scripts/research-topic.py`**：Deep Research 多引擎搜索（Tavily + Exa + Querit + SerpAPI + 兜底）
- **`scripts/search-image.py`**：多来源图库搜索（Pexels / Unsplash / Pixabay）

### Fixed

- Pexels API 403（缺 User-Agent）
- Querit 端点与参数修正
- `search-image.py`：零 API key 时给出明确提示 + Pexels 网页爬取 fallback

---

## [1.1.0] — 2026-08

### Added

- **Phase 0 Deep Research**：材料不全时自动搜索补证据（四阶段流程从此确立）
- **模板学习**：`learn-from-pptx.py` 从参考 PPTX 提取风格
- **布局库**：`references/layouts/`
- **多模型指南**：省钱方案（Research 用 Flash，蓝图用最强模型）
- **多图源**：AI 生图 + 免费图库

---

## [1.0.0] — 2026-07

### Added

- 初始版本：三阶段方法论（证据分析 → 视觉蓝图 → PPTX 生成 + QA）
- SCR 叙事框架（Situation → Complication → Resolution）
- 证据表驱动（ID / 数值 / 单位 / 期间 / 来源 / 置信度 / Caveat / 含义 / 推荐视觉）
- 8 种经典风格（继承 [CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT)）
- 15 级 Typography Scale（C0 / T1–T14）
- `scripts/generate-sample.js`：pptxgenjs 示例生成脚本
- 双硬门槛：主要文字可编辑 + 视觉高保真

---

## 设计来源

- 方法论基底：[CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) 的三阶段框架（SCR + 证据表）
- duduppt 的增量：16+1 风格库、四阶段流程、逐页确认门、配图管理、演讲者备注、
  中文字体检测、私人材料红线

## 同类项目参考

调研并借鉴（仅学习思路，未复制代码）：

| 项目 | 借鉴点 |
|---|---|
| `anthropics/skills` 的 `skills/pptx` | 任务路由表开篇、pptxgenjs 坑清单、QA 必做、字体「QA-safe / QA-unreliable」分级 |
| `Gabberflast/academic-pptx-skill` | 双层架构（本文件管内容 / 技术 skill 管生成）、子文件路由表 |
| `carnot-tech/consulting-pptx-skill` | 「规约是正典」、references 标注「何时读」 |
| `addsumtech/slides_maker` | 独立盲读 QA、CJK 双槽位（`<a:latin>` / `<a:ea>`）、成本分档 |
| `sbroenne/mcp-server-powerpoint` | 「Verify Visually 是差异化能力」、逐页导出图片验收 |
