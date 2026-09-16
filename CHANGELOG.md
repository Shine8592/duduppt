# Changelog

All notable changes to **duduppt**. Format follows [Keep a Changelog](https://keepachangelog.com/);
versioning follows [Semantic Versioning](https://semver.org/).

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
