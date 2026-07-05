# 🎯 duduppt

> 把文档、数据和想法变成咨询风格的高密度 PPTX — Hermes Agent 技能

**duduppt** 是一个 Hermes Agent 技能，基于 [CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) 的三阶段方法论（证据分析 → SCR 叙事 → 视觉蓝图 → 工程化生产），把源材料转化为有证据链、结论先行、可编辑的咨询式演示文稿。

## ✨ 核心能力

- **三阶段流水线**：分析（证据表 + SCR 故事线）→ 蓝图（8 种风格 + 逐页蓝图）→ PPTX（可编辑高保真）
- **15 级 Typography Scale**：C0-T14 完整字体层级体系，源自 MBB 咨询标准
- **8 种视觉风格**：从经典深红咨询风到冷白灰 + 深紫，覆盖战略/科技/财务/消费等场景
- **双硬门槛**：主要文字可编辑 + 视觉语义高保真，不得二选一
- **13 项 QA 检查**：渲染验证、文字可编辑性、字体层级、溢出检测全涵盖
- **逐页验收**：一页做完确认再下一页，不做一次性批量生成

## 📦 适用场景

| 适合 | 不适合 |
|------|--------|
| 行业研究 | 字少/低密度演讲 |
| 战略分析 | 个人观点分享 |
| 品牌策略/电商分析 | 叙事性 PPT |
| 用户研究 / 高管汇报 | — |
| 客户提案 / 项目复盘 | — |

## 🚀 快速开始

### 安装依赖

```bash
# pptxgenjs — 主生成引擎
npm install -g pptxgenjs

# python-pptx — 备选/QA
pip install python-pptx

# LibreOffice — 渲染导出（可选）
apt install librecore libreoffice-impress
```

### 环境变量

```bash
# pptxgenjs 全局安装后需要设置 NODE_PATH
export NODE_PATH=$(npm root -g)
```

### 安装技能

```bash
# 克隆到 Hermes skills 目录
git clone https://github.com/Shine8592/duduppt.git ~/.hermes/skills/creative/duduppt

# 或直接复制 SKILL.md 到你的 skills 目录
cp duduppt/SKILL.md ~/.hermes/skills/creative/duduppt/
```

## 🧱 工作流程

```
Phase 1: 分析
  源材料 → 证据表 → 2-3 条故事线脑暴 → SCR 收敛 → 逐页大纲
  └── 🚪 第一次确认

Phase 2: 蓝图
  8 选 1 视觉风格 → 锁定字体层级 → 逐页布局描述
  └── 🚪 第二次确认

Phase 3: PPTX 生成
  逐页生成 (pptxgenjs) → QA 检查 → 渲染验证 → 合并交付
  └── 🚪 最终确认
```

## 🎨 8 种视觉风格

| # | 名称 | 色板 | 场景 |
|---|------|------|------|
| 01 | 经典深红咨询风 | `#F3F4EF` + `#8B1E1E` | 战略、竞品、行业研究 |
| 02 | 冷灰 + 勃艮第红 | `#F5F5F2` + `#7A1F2B` | 财务、投研、风险 |
| 03 | 暖象牙白 + 暗酒红 | `#F4F1EA` + `#8A1538` | 品牌、消费品、电商 |
| 04 | 象牙白 + 深蓝强调 | `#F7F6F0` + `#12355B` | 科技、SaaS、AI |
| 05 | 浅灰白 + 墨绿 | `#F2F3EF` + `#1F5B4D` | 可持续、增长 |
| 06 | 纸张米色 + 铜棕 | `#F4F0E8` + `#9A5A2E` | 消费、零售、奢侈品 |
| 07 | 纯净浅灰 + 黑金 | `#F6F6F4` + `#A87932` | 高管汇报、融资、董事会 |
| 08 | 冷白灰 + 深紫 | `#F4F5F6` + `#4B2E83` | AI、技术、创新 |

## 📐 Typography Scale

15 级固定字体层级，全篇统一，不得发明新层级：

| 层级 | 用途 | 字号 |
|------|------|------|
| C0 | 封面/章节标题 | 32-44pt |
| T1 | 页码/章节徽章 | 14-18pt |
| T2 | 页面主标题 | 22-28pt |
| T3 | 副标题 | 10-12pt |
| T4 | 模块/图表标题 | 11-14pt |
| T5 | 证据编号标签 | 7.5-8.5pt |
| T6 | 小节标题 | 11-13pt |
| T7 | 正文段落 | 9.5-11pt |
| T8 | 结论条文字 | 10-12pt |
| T9 | SO WHAT 标签 | 10-12pt |
| T10 | SO WHAT 正文 | 9.5-11pt |
| T11 | 图例/轴/刻度 | 7.5-9pt |
| T12 | 数据标签 | 8.5-11pt |
| T13 | KPI 大数字 | 18-28pt |
| T14 | 注释/来源/页脚 | 6.5-8pt |

## 🚫 红线

| 禁止 | 原因 |
|------|------|
| 编造数据 | 违反咨询基本诚信 |
| 整页截图当 PPT 背景 | 不可编辑 |
| 文字烘焙进图片 | 破坏可编辑性 |
| 为可编辑简化图表语义 | 视觉降级 |
| 一次性批量生成终版（≥3 页） | 质量失控 |
| 跳过 SO WHAT | 咨询 PPT 必须有含义 |

## 📁 项目结构

```
duduppt/
├── SKILL.md                     # Hermes 技能文件
├── README.md                    # 本文件
├── references/
│   ├── palettes.md              # 8 种色板配色代码
│   └── typography-scale.md      # C0/T1-T14 字体层级
├── assets/palette-samples/
│   ├── palette-01.png ~ 08.png  # 视觉风格样张
├── scripts/
│   └── generate-sample.js       # 示例生成脚本
└── examples/
    └── duduppt-sample.pptx       # 示例输出
```

## 📜 许可

MIT

## 🙏 致谢

- [CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) — 三阶段方法论和门禁体系的理论来源
- [pptxgenjs](https://github.com/gitbrent/PptxGenJS) — Node.js PPTX 生成引擎
- [python-pptx](https://github.com/scanny/python-pptx) — Python PPTX 库
