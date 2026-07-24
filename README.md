<div align="center">
  <h1>🎯 duduppt</h1>
  <p><strong>把文档、数据和想法变成咨询风格的高密度 PPTX</strong></p>
  <p>Hermes Agent 技能 · 四阶段方法论 · 原生可编辑 PPTX 输出</p>
  <p>
    <a href="https://github.com/Shine8592/duduppt/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <a href="https://github.com/Shine8592/duduppt"><img src="https://img.shields.io/github/stars/Shine8592/duduppt?style=flat" alt="Stars"></a>
  </p>
</div>

---

duduppt 是一个 **Hermes Agent 技能**，基于 [CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) 的三阶段方法论，把源材料转化为有证据链、结论先行、**PowerPoint 原生可编辑的 PPTX 文件**。

不是 HTML 幻灯片，不是网页截图，是真的 `.pptx`——能在 PowerPoint 中打开、选中、修改每一个字。

---

## ✨ 核心能力

| 能力 | 说明 |
|------|------|
| **SCR 叙事框架** | Situation → Complication → Resolution 咨询级论证结构 |
| **证据表驱动** | 每个论点带 ID/来源/置信度/Caveat，不编造数据 |
| **结论先行 + SO WHAT** | 每页一个可挑战的强标题 + 行动建议，咨询 PPT 标配 |
| **16+1 种视觉风格** | 从经典深红咨询风到清新高客风，覆盖全场景 |
| **15 级 Typography Scale** | C0-T14 完整字体层级体系，源自 MBB 咨询标准 |
| **12 种布局模板** | 封面/目录/对比/时间线/数据页等，即选即用 |
| **逐页交付** | 每页做完确认再下一页，不批量翻车 |
| **15 项 QA 检查** | 零依赖 zipfile 结构检查 + 中文字体绑定验证 |
| **Deep Research 自动补证据** | Tavily + Exa + Querit 三引擎搜索填补数据缺口 |
| **从参考 PPTX 学习风格** | 自动提取配色/字体/布局，匹配最接近的预设风格 |
| **配图自动规划** | 蓝图标注配图类型/比例/位置，统一管理 |
| **演讲者备注自动生成** | 每页 60-100 字口语化备注，现场直接讲 |
| **多来源图片** | AI 生图 + Pexels/Unsplash/Pixabay 免费图库 |
| **多模型适配** | 不同阶段用不同模型（省钱方案：Research 用 Flash，蓝图用最强） |
| **私人材料保护** | 红线机制阻止业务数据上传公开仓库 |

---

## 📦 适用场景

| 适合 | 不适合 |
|------|--------|
| 行业研究 / 战略分析 | 字少/低密度演讲 |
| 品牌策略 / 电商分析 | 个人观点分享 |
| 用户研究 / 高管汇报 | 纯叙事性 PPT（无数据支撑） |
| 客户提案 / 项目复盘 | — |
| 高客财富沙龙 / 家族信托 | — |
| 财务分析 / KPI 汇报 | — |

---

## 🚀 快速开始

### 前提条件

- Hermes Agent (或兼容 Claude Code / Codex 的环境)
- Node.js (pptxgenjs 生成引擎)
- Python 3 (辅助脚本)

### 安装依赖

```bash
# pptxgenjs — 主生成引擎
npm install -g pptxgenjs

# Python 辅助脚本依赖
pip install Pillow

# LibreOffice — 渲染 QA（可选但推荐）
apt install libreoffice-impress
```

### 设置环境变量

```bash
# 搜索 API key（Deep Research 用）
export TAVILY_API_KEY="tvly-xxx"      # https://app.tavily.com （免费额度）
export EXA_API_KEY="your-key"         # https://exa.ai （可选）
export QUERIT_API_KEY="your-key"      # https://querit.ai （可选）

# 图片生成 API key
export AGNES_API_KEY="sk-xxx"         # Agnes AI 生图
export PEXELS_API_KEY="your-key"      # Pexels 免费图库搜索（可选）
export UNSPLASH_ACCESS_KEY="your-key" # Unsplash 免费图库搜索（可选）

# pptxgenjs 全局安装路径
export NODE_PATH=$(npm root -g)
```

### 安装技能

```bash
# 克隆到 Hermes skills 目录
git clone https://github.com/Shine8592/duduppt.git ~/.hermes/skills/creative/duduppt

# 或复制 SKILL.md
cp duduppt/SKILL.md ~/.hermes/skills/creative/duduppt/
```

### 使用

在 Hermes 中说：

> "帮我做个关于中国财富管理市场的 PPT"
> "把这份报告改成演示文稿"
> "按这个参考 PPTX 的风格做一份 deck"

duduppt 会自动进入四阶段流程。

---

## 🧱 四阶段工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  🔍  Phase 0: Deep Research                                 │
│  自动搜索补充背景信息 → 多引擎搜索 → 结构化证据输入         │
│  └── 产出：数据缺口清单 + 关键发现                          │
├─────────────────────────────────────────────────────────────┤
│  📋  Phase 1: 分析（Analysis）                              │
│  读材料 → 建证据表 → 2-3 条故事线脑暴 → SCR 收敛 → 逐页大纲 │
│  └── 🚪 第一次确认                                           │
├─────────────────────────────────────────────────────────────┤
│  🎨  Phase 2: 视觉蓝图（Blueprint）                          │
│  设计访谈 → 16+1 选风格 → 锁定字体层级 → 选布局模板 → 配图规划│
│  └── 🚪 第二次确认                                           │
├─────────────────────────────────────────────────────────────┤
│  🛠  Phase 3: PPTX 生成 + QA                                 │
│  逐页生成 (pptxgenjs) → 演讲者备注 → QA 检查 → 合并交付      │
│  └── 🚪 最终确认                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 16+1 视觉风格

### 经典系列（CyberPPT 继承）

| # | 风格名 | 底色 | 强调色 | 最佳场景 |
|---|--------|------|--------|---------|
| 01 | 经典深红咨询风 | `#F3F4EF` | `#8B1E1E` | 战略、竞品、行业研究 |
| 02 | 冷灰 + 勃艮第红 | `#F5F5F2` | `#7A1F2B` | 财务、投研、风险 |
| 03 | 暖象牙白 + 暗酒红 | `#F4F1EA` | `#8A1538` | 品牌、消费品、电商 |
| 04 | 象牙白 + 深蓝强调 | `#F7F6F0` | `#12355B` | 科技、SaaS、AI |
| 05 | 浅灰白 + 墨绿 | `#F2F3EF` | `#1F5B4D` | 可持续、增长 |
| 06 | 纸张米色 + 铜棕 | `#F4F0E8` | `#9A5A2E` | 消费、零售、奢侈品 |
| 07 | 纯净浅灰 + 黑金 | `#F6F6F4` | `#A87932` | 高管汇报、融资、董事会 |
| 08 | 冷白灰 + 深紫 | `#F4F5F6` | `#4B2E83` | AI、技术、创新 |

### 新增系列（duduppt v2.0）

| # | 风格名 | 底色 | 强调色 | 最佳场景 |
|---|--------|------|--------|---------|
| **09** | **清新高客风** ⭐ | `#F8F9F7` | `#5B9B8A` | **高客沙龙、家族传承（特选）** |
| 10 | 电子杂志风 | `#FAFAF8` | `#C73E3A` | 叙事、案例、品牌故事 |
| 11 | 瑞士数据风 | `#FFFFFF` | `#E85D3A` | 数据、KPI、财务分析 |
| 12 | 极光渐变风 | `#0A0E27` | `#6C63FF` | AI、路演、创新 |
| 13 | 黑胶唱片风 | `#F5F0E8` | `#2C1810` | 文化、奢侈品、高端品牌 |
| 14 | 莫兰迪色风 | `#F2F0EC` | `#9E7E7A` | 设计、美学、生活方式 |
| 15 | 自然草木风 | `#F5F7F2` | `#4A7C59` | ESG、环保、农业 |
| 16 | 经典商务蓝 | `#F6F8FA` | `#1B5E8A` | 保险、银行、传统企业 |

> 完整色板代码见 [`references/palettes.md`](references/palettes.md)

---

## 📐 Typography Scale

15 级固定字体层级，全篇统一：

| 层级 | 用途 | 字号 |
|------|------|------|
| **C0** | 封面/章节标题 | 32-44pt |
| **T1** | 页码/章节徽章 | 14-18pt |
| **T2** | 页面主标题 | 22-28pt |
| **T3** | 副标题 | 10-12pt |
| **T4** | 模块/图表标题 | 11-14pt |
| **T5** | 证据编号标签 | 7.5-8.5pt |
| **T6** | 小节标题 | 11-13pt |
| **T7** | 正文段落 | 9.5-11pt |
| **T8** | 结论条文字 | 10-12pt |
| **T9** | SO WHAT 标签 | 10-12pt |
| **T10** | SO WHAT 正文 | 9.5-11pt |
| **T11** | 图例/轴/刻度 | 7.5-9pt |
| **T12** | 数据标签 | 8.5-11pt |
| **T13** | KPI 大数字 | 18-28pt |
| **T14** | 注释/来源/页脚 | 6.5-8pt |

---

## 🛠 脚本工具

| 脚本 | 用途 | 依赖 |
|------|------|------|
| [`scripts/research-topic.py`](scripts/research-topic.py) | Deep Research 多引擎搜索（Tavily+Exa+Querit+SerpAPI） | API keys |
| [`scripts/learn-from-pptx.py`](scripts/learn-from-pptx.py) | 从参考 PPTX 学习配色/字体/布局 | Pillow |
| [`scripts/extract-palette.py`](scripts/extract-palette.py) | 从图片提取配色，生成 PPT style config | Pillow |
| [`scripts/generate-image.js`](scripts/generate-image.js) | AI 生图（Agnes API），适配 16:9/4:3/1:1 | Agnes API key |
| [`scripts/search-image.py`](scripts/search-image.py) | 多来源免费图库搜索（Pexels/Unsplash/Pixabay） | API keys（可选） |
| [`scripts/generate-sample.js`](scripts/generate-sample.js) | 示例 PPT 生成脚本 | pptxgenjs |

---

## 📚 参考资料

| 文件 | 说明 |
|------|------|
| [`references/palettes.md`](references/palettes.md) | 16+1 种配色完整代码（YAML + CSS + JS 格式） |
| [`references/design-principles.md`](references/design-principles.md) | 10 条设计原则：PPTX 优先、结论先行、克制优于炫技 |
| [`references/layouts/layout-library.md`](references/layouts/layout-library.md) | 12 种布局模板 + pptxgenjs 代码骨架 |
| [`references/prompt-templates.md`](references/prompt-templates.md) | 各阶段 system prompt 模板 |
| [`references/multi-model-guide.md`](references/multi-model-guide.md) | 多模型选择指南：省钱方案 vs 顶配方案 |
| [`references/chart-type-anatomy.md`](references/chart-type-anatomy.md) | pptxgenjs chart 坑分析（barDir 修复） |
| [`references/merge-and-qa.md`](references/merge-and-qa.md) | 多 batch 合并脚本 + 中文 QA 兜底 |
| [`references/typography-scale.md`](references/typography-scale.md) | C0/T1-T14 字体层级详解 |
| [`assets/palette-samples/`](assets/palette-samples/) | 8 张风格样张 PNG |

---

## 🗺️ 路线图

| 版本 | 状态 | 核心内容 |
|------|------|---------|
| **v1.0** | ✅ 已发布 | 三阶段方法论 + 8 种风格 + C0-T14 + 13 项 QA |
| **v1.1** | ✅ 已发布 | Deep Research + 参考 PPTX 学习 + 布局库 + 多模型 + 多图源 |
| **v2.0** | ✅ **当前版本** | 16+1 风格库 + 设计访谈 + 配图管理 + 演讲者备注 + 设计原则 |
| **v2.1** | 📋 规划中 | Agent 自主配图（自动搜图+裁图+插入）、Mermaid 图表集成 |
| **v2.2** | 📋 规划中 | 多语言模板（英文/日文 PPTX 输出）、社区模板贡献机制 |

---

## 🚫 红线

| 绝对禁止 | 原因 |
|----------|------|
| 编造数据/市场规模/调研结果 | 违反咨询基本诚信 |
| 整页截图当 PPT 背景 | 不可编辑 |
| 文字烘焙进图片 | 破坏可编辑性 |
| 为可编辑简化图表语义 | 视觉降级 |
| 一次性生成 ≥3 页终版 | 质量失控 |
| 跳过 SO WHAT | 咨询 PPT 必须有含义 |
| 跳过用户确认门 | 流程失控 |
| 上传私人业务内容到公开仓库 | 隐私保护 |

> 反哺项目只沉淀**去内容化的方法论**（合并脚本、QA 流程、配色模块），绝不携带业务数据。

---

## 🆚 竞品对比

duduppt 定位独特：**PPTX 原生可编辑 × 咨询方法论 × Agent 原生**。

| 对比维度 | duduppt | guizang-ppt-skill (22k⭐) | Presenton (9k⭐) | PPTAgent (4.8k⭐) |
|----------|---------|--------------------------|-----------------|-------------------|
| 输出格式 | **PPTX** | HTML | Web + PPTX | PPTX |
| 叙事框架 | **SCR + 证据表** | 无 | 无 | 无 |
| 质量门禁 | **15 项 QA** | 瑞士校验器 | 无 | 反射式自评估 |
| 中文字体 | **原生支持** | 浏览器渲染 | 未知 | 有限支持 |
| 逐页确认 | **✅** | ❌ | ❌ | ❌ |
| 风格数量 | **16+1** | 5+4 | 基于模板 | Free-Form |
| 部署方式 | Agent 技能 | Agent 技能 | Web App | Docker |

---

## 📁 项目结构

```
duduppt/
├── SKILL.md                        # Hermes 技能文件（核心）
├── README.md                       # 本文件
├── COMMUNITY.md                    # 推广策略 + 实战踩坑
├── competitive-analysis.md         # 竞品深度对比（v1）
├── competitive-analysis-v2.md      # 竞品深度对比（v2，agent skill 类）
├── references/
│   ├── palettes.md                 # 16+1 种配色完整代码
│   ├── design-principles.md        # 10 条设计原则
│   ├── layouts/layout-library.md   # 12 种布局模板
│   ├── prompt-templates.md         # 8 套 system prompt 模板
│   ├── multi-model-guide.md        # 多模型选择指南
│   ├── chart-type-anatomy.md       # pptxgenjs chart 坑分析
│   ├── merge-and-qa.md             # 多 batch 合并 + 中文 QA
│   └── typography-scale.md         # C0/T1-T14 字体层级
├── assets/palette-samples/
│   └── palette-01.png ~ 08.png     # 视觉风格样张
├── scripts/
│   ├── learn-from-pptx.py          # 从参考 PPTX 学习模板风格
│   ├── research-topic.py           # Deep Research 多引擎搜索
│   ├── search-image.py             # 多来源免费图库搜索
│   ├── generate-image.js           # AI 生图（Agnes API）
│   ├── extract-palette.py          # 从图片提取配色
│   └── generate-sample.js          # 示例 PPT 生成脚本
└── examples/
    └── duduppt-sample.pptx          # 示例输出
```

---

## 📜 许可

MIT License. 详见 [LICENSE](LICENSE)。

## 🙏 致谢

- [CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) — 三阶段方法论和门禁体系的理论来源
- [pptxgenjs](https://github.com/gitbrent/PptxGenJS) — Node.js PPTX 生成引擎
- [python-pptx](https://github.com/scanny/python-pptx) — Python PPTX 库
- 竞品项目 guizang-ppt-skill / frontend-slides / visual-explainer / Presenton / PPTAgent — 设计思路参考

---

<div align="center">
  <sub>Made with ❤️ for 卢艳峰 Shine · 咨询风 PPT 流水线 · Hermes Agent Skill</sub>
</div>
