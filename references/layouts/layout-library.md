# duduppt 布局模板库

> 用途：蓝图阶段从"文字描述布局"升级为"选模板 + 微调"
> 每个模板包含：适用场景、布局比例描述、pptxgenjs 代码骨架

---

## L01 — 封面页（Cover）

**适用：** 首页 / 章节封面
**特点：** 视觉冲击力强，大面积背景图 + 居中/左对齐标题

```
┌──────────────────────────────────────┐
│                                      │
│   ██████████████████████████████████ │  ← 背景图/渐变 80% 高度
│   ██                                │
│   ██  主标题 32-44pt                 │
│   ██  副标题 14-18pt                 │
│   ██  日期/作者 10-12pt              │
│   ██                                │
│   ██████████████████████████████████ │
│                                      │
│   底部装饰线 / Logo                   │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 底部色块装饰
slide.addShape('rect', { x: 0, y: 5.3, w: 10, h: 1.7, fill: { color: C.accent } });
slide.addText('主标题', { x: 0.8, y: 1.5, w: 8.4, h: 1.2, fontSize: 36, fontFace: FONT, color: C.text, bold: true });
slide.addText('副标题说明文字', { x: 0.8, y: 2.9, w: 8.4, h: 0.6, fontSize: 16, fontFace: FONT, color: C.accentDark });
slide.addText('2026年7月', { x: 0.8, y: 3.7, w: 3, h: 0.4, fontSize: 11, fontFace: FONT, color: C.muted });
```

---

## L02 — 目录页（TOC / Agenda）

**适用：** 展示章节结构
**特点：** 2列或3列网格，大数字编号 + 章节标题

```
┌──────────────────────────────────────┐
│  目录 CONTENTS                       │
│                                      │
│  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │  01  │  │  02  │  │  03  │       │
│  │市场  │  │竞争  │  │策略  │       │
│  │概况  │  │分析  │  │建议  │       │
│  └──────┘  └──────┘  └──────┘       │
│                                      │
│  ┌──────┐  ┌──────┐                 │
│  │  04  │  │  05  │                 │
│  │执行  │  │风险  │                 │
│  │计划  │  │管控  │                 │
│  └──────┘  └──────┘                 │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
const items = [
  { num: '01', title: '市场概况', sub: '行业规模与趋势' },
  { num: '02', title: '竞争分析', sub: '主要玩家格局' },
  { num: '03', title: '策略建议', sub: '核心增长路径' },
];
items.forEach((item, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.6 + col * 3.1;
  const y = 1.8 + row * 1.8;
  slide.addShape('roundRect', { x, y, w: 2.8, h: 1.4, fill: { color: C.light }, line: { color: C.divider } });
  slide.addText(item.num, { x, y: y + 0.1, w: 2.8, h: 0.6, fontSize: 24, fontFace: FONT, color: C.accent, bold: true, align: 'center' });
  slide.addText(item.title, { x, y: y + 0.6, w: 2.8, h: 0.4, fontSize: 14, fontFace: FONT, color: C.text, bold: true, align: 'center' });
  slide.addText(item.sub, { x, y: y + 1.0, w: 2.8, h: 0.3, fontSize: 10, fontFace: FONT, color: C.muted, align: 'center' });
});
```

---

## L03 — 章节标题页（Section Divider）

**适用：** 切换新章节时的过渡页
**特点：** 大数字 + 简洁文字，视觉留白

```
┌──────────────────────────────────────┐
│                                      │
│                                      │
│          02                          │  ← 巨大数字 72-96pt
│                                      │
│     竞争格局分析                      │  ← 章节标题 28-32pt
│                                      │
│     本章将分析主要竞争对手...         │  ← 章节简介 12-14pt
│                                      │
│                                      │
│   ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬              │  ← 装饰线
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 大数字
slide.addText('02', { x: 0.8, y: 1.0, w: 4, h: 2.0, fontSize: 72, fontFace: FONT, color: C.accent, bold: true });
// 章节标题
slide.addText('竞争格局分析', { x: 0.8, y: 2.8, w: 8, h: 0.8, fontSize: 28, fontFace: FONT, color: C.text, bold: true });
// 装饰线
slide.addShape('rect', { x: 0.8, y: 3.8, w: 2, h: 0.04, fill: { color: C.accent } });
// 简介
slide.addText('本章将分析主要竞争对手的市场份额、核心优势与战略动向', { x: 0.8, y: 4.0, w: 8, h: 0.5, fontSize: 13, fontFace: FONT, color: C.muted });
```

---

## L04 — 结论先行页（Claim + Evidence）

**适用：** 核心论点展示，每页一个强结论
**特点：** 顶部强标题 + 下方证据 + 底部 SO WHAT

```
┌──────────────────────────────────────┐
│  市场增长在修复，但价值正向结构性    │  ← 强结论标题 (T2)
│  优势赛道转移                        │
│──────────────────────────────────────│  ← 装饰线
│                                      │
│  ┌─────────┐  ┌─────────┐           │
│  │ 数据/   │  │ 图表/   │           │
│  │ 证据A   │  │ 证据B   │           │
│  │ +15%    │  │ 28.6%   │           │
│  └─────────┘  └─────────┘           │
│                                      │
│  ── SO WHAT: 建议聚焦赛道 A 和 B    │  ← 行动建议 (T10)
│  来源: XX 报告 2026                  │  ← 注脚 (T14)
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 强结论标题（色块背景）
slide.addShape('rect', { x: 0, y: 0, w: 10, h: 0.9, fill: { color: C.accent } });
slide.addText('市场增长在修复，但价值正向结构性优势赛道转移', {
  x: 0.5, y: 0.1, w: 9, h: 0.7, fontSize: 20, fontFace: FONT, color: 'FFFFFF', bold: true
});
// 证据卡片
slide.addShape('roundRect', { x: 0.5, y: 1.2, w: 4.2, h: 2.5, fill: { color: C.card }, line: { color: C.divider }, shadow: { type: 'outer', blur: 4, offset: 2 } });
slide.addText('+15%', { x: 0.7, y: 1.4, w: 3.8, h: 0.8, fontSize: 36, fontFace: FONT, color: C.accent, bold: true });
slide.addText('高端市场年增长率', { x: 0.7, y: 2.2, w: 3.8, h: 0.4, fontSize: 12, fontFace: FONT, color: C.text });
slide.addShape('roundRect', { x: 5.3, y: 1.2, w: 4.2, h: 2.5, fill: { color: C.card }, line: { color: C.divider }, shadow: { type: 'outer', blur: 4, offset: 2 } });
slide.addText('28.6%', { x: 5.5, y: 1.4, w: 3.8, h: 0.8, fontSize: 36, fontFace: FONT, color: C.gold, bold: true });
slide.addText('结构性赛道占比提升', { x: 5.5, y: 2.2, w: 3.8, h: 0.4, fontSize: 12, fontFace: FONT, color: C.text });
// SO WHAT
slide.addShape('rect', { x: 0.5, y: 4.2, w: 9, h: 0.6, fill: { color: C.light } });
slide.addText('▶ SO WHAT: 建议聚焦赛道 A 和 B，放弃低毛利赛道 C', {
  x: 0.7, y: 4.25, w: 8.6, h: 0.5, fontSize: 12, fontFace: FONT, color: C.accentDark, bold: true
});
// 注脚
slide.addText('来源: XX 行业报告 2026 | 数据截至 Q2 2026', {
  x: 0.5, y: 5.0, w: 9, h: 0.3, fontSize: 8, fontFace: FONT, color: C.muted
});
```

---

## L05 — 左文右图（Text + Image）

**适用：** 产品介绍、案例分析、概念解释
**特点：** 左 40% 文字 + 右 60% 图片

```
┌──────────────────────────────────────┐
│                                      │
│  ┌─────────┐  ┌──────────────────┐  │
│  │ 标题    │  │                  │  │
│  │         │  │   图片 / 图表    │  │
│  │ 正文    │  │                  │  │
│  │ 描述    │  │                  │  │
│  │         │  │                  │  │
│  │ SO WHAT │  │                  │  │
│  └─────────┘  └──────────────────┘  │
│                                      │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 左侧文字
slide.addText('左栏标题', { x: 0.5, y: 0.5, w: 3.5, h: 0.6, fontSize: 22, fontFace: FONT, color: C.text, bold: true });
slide.addText('描述文字段落...', { x: 0.5, y: 1.3, w: 3.5, h: 2.5, fontSize: 12, fontFace: FONT, color: C.text, valign: 'top' });
// 右侧图片占位（边框示意）
slide.addShape('roundRect', { x: 4.5, y: 0.5, w: 5, h: 4.5, fill: { color: C.light }, line: { color: C.divider, dashType: 'dash' } });
slide.addText('🖼️ 图片区域', { x: 4.5, y: 2.0, w: 5, h: 0.5, fontSize: 14, fontFace: FONT, color: C.muted, align: 'center' });
// SO WHAT 在底部
slide.addShape('rect', { x: 0.5, y: 5.3, w: 9, h: 0.5, fill: { color: C.light } });
slide.addText('SO WHAT: 核心启示', { x: 0.7, y: 5.35, w: 8.6, h: 0.4, fontSize: 11, fontFace: FONT, color: C.accentDark });
```

---

## L06 — 数据图表页（Data Page）

**适用：** KPI 展示 + 趋势图表 + 关键解读
**特点：** 顶部 KPI 大数字 + 中部图表 + 底部解读

```
┌──────────────────────────────────────┐
│  $2.4B      +18%      32.5%         │  ← KPI 大数字 (T13)
│  总营收    同比增长   毛利率         │
│──────────────────────────────────────│
│                                      │
│        📊 柱状图/折线图              │  ← 图表主体
│        (barDir:'col')                │
│                                      │
│──────────────────────────────────────│
│  ▶ 关键发现: 营收增长主要由 X 驱动  │  ← 解读 (T10)
│  来源: 公司财报 Q2 2026             │  ← 注脚 (T14)
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// KPI 行 — 三个大数字
const kpis = [
  { num: '$2.4B', label: '总营收', color: C.accent },
  { num: '+18%', label: '同比增长', color: C.gold },
  { num: '32.5%', label: '毛利率', color: C.accentDark },
];
kpis.forEach((kpi, i) => {
  const x = 0.5 + i * 3.2;
  slide.addText(kpi.num, { x, y: 0.3, w: 2.8, h: 0.7, fontSize: 28, fontFace: FONT, color: kpi.color, bold: true, align: 'center' });
  slide.addText(kpi.label, { x, y: 1.0, w: 2.8, h: 0.3, fontSize: 10, fontFace: FONT, color: C.muted, align: 'center' });
});
// 图表（注意 barDir 修复）
slide.addChart('bar', chartData, { x: 0.5, y: 1.5, w: 9, h: 3.0, barDir: 'col', showLegend: true, showValue: true, chartColors: [C.accent, C.gold, C.light] });
// 关键发现
slide.addShape('rect', { x: 0.5, y: 4.8, w: 9, h: 0.5, fill: { color: C.light } });
slide.addText('▶ 关键发现: 营收增长主要由 X 业务线驱动，Y 市场贡献增量', { x: 0.7, y: 4.85, w: 8.6, h: 0.4, fontSize: 11, fontFace: FONT, color: C.accentDark });
slide.addText('来源: 公司财报 Q2 2026', { x: 0.5, y: 5.4, w: 9, h: 0.3, fontSize: 8, fontFace: FONT, color: C.muted });
```

---

## L07 — 对比页（Comparison）

**适用：** 前后对比 / 竞品对比 / 方案对比 / 优缺点
**特点：** 左右两栏 + 表头 + 对比元素

```
┌──────────────────────────────────────┐
│        方案 A        vs    方案 B    │  ← 对比标题
│──────────────────────────────────────│
│  ┌──────────┐       ┌──────────┐    │
│  │ 优势1    │       │ 优势1    │    │
│  │ 优势2    │       │ 优势2    │    │
│  │ 优势3    │       │ 优势3    │    │
│  │          │       │          │    │
│  │ ⚠️ 风险  │       │ ⚠️ 风险  │    │
│  └──────────┘       └──────────┘    │
│                                      │
│  建议: 综合考量推荐方案 A            │  ← 结论
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 标题
slide.addText('方案对比：自建 vs 采购', { x: 0.5, y: 0.3, w: 9, h: 0.6, fontSize: 20, fontFace: FONT, color: C.text, bold: true });
// A 列
slide.addShape('roundRect', { x: 0.5, y: 1.2, w: 4.2, h: 3.5, fill: { color: C.card }, line: { color: C.accent } });
slide.addText('方案 A：自建团队', { x: 0.7, y: 1.3, w: 3.8, h: 0.5, fontSize: 14, fontFace: FONT, color: C.accent, bold: true });
slide.addText('• 完全可控\n• 长期成本低\n• 定制化程度高\n\n⚠️ 周期 6-12 个月\n⚠️ 团队招聘难度高', {
  x: 0.7, y: 1.9, w: 3.8, h: 2.6, fontSize: 11, fontFace: FONT, color: C.text, valign: 'top', lineSpacing: 18
});
// B 列
slide.addShape('roundRect', { x: 5.3, y: 1.2, w: 4.2, h: 3.5, fill: { color: C.card }, line: { color: C.gold } });
slide.addText('方案 B：外部采购', { x: 5.5, y: 1.3, w: 3.8, h: 0.5, fontSize: 14, fontFace: FONT, color: C.gold, bold: true });
slide.addText('• 快速上线 1-2 个月\n• 低初期投入\n• 运维外包\n\n⚠️ 供应商锁定\n⚠️ 长期成本高', {
  x: 5.5, y: 1.9, w: 3.8, h: 2.6, fontSize: 11, fontFace: FONT, color: C.text, valign: 'top', lineSpacing: 18
});
// 结论
slide.addShape('rect', { x: 0.5, y: 5.0, w: 9, h: 0.6, fill: { color: C.accent } });
slide.addText('建议：综合考量推荐方案 A，但建议分阶段实施以控制风险', { x: 0.7, y: 5.05, w: 8.6, h: 0.5, fontSize: 12, fontFace: FONT, color: 'FFFFFF', bold: true });
```

---

## L08 — 时间线（Timeline）

**适用：** 项目里程碑、发展历程、实施计划
**特点：** 横向时间轴 + 关键节点 + 说明

```
┌──────────────────────────────────────┐
│  项目实施路线图                      │
│                                      │
│  ●───────●───────●───────●───────●  │  ← 时间轴
│  Q1      Q2      Q3      Q4      Q5 │
│  调研    开发    测试    上线    优化 │
│  ┌───┐   ┌───┐   ┌───┐            │
│  │详 │   │MVP│   │UAT│            │
│  │情 │   │   │   │   │            │
│  └───┘   └───┘   └───┘            │
│                                      │
│  当前阶段: Q2 开发中                 │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
slide.addText('项目实施路线图', { x: 0.5, y: 0.3, w: 9, h: 0.6, fontSize: 22, fontFace: FONT, color: C.text, bold: true });
// 时间轴
const phases = [
  { label: 'Q1', title: '需求调研', desc: '业务需求收集\n流程梳理', active: false },
  { label: 'Q2', title: 'MVP 开发', desc: '核心功能开发\n迭代测试', active: true },
  { label: 'Q3', title: '用户测试', desc: 'UAT 验收\n反馈收集', active: false },
  { label: 'Q4', title: '正式上线', desc: '生产部署\n培训切换', active: false },
];
const startX = 0.5, spacing = 2.3, axisY = 2.5;
// 轴线
slide.addShape('rect', { x: startX, y: axisY, w: spacing * (phases.length - 1) + 0.3, h: 0.04, fill: { color: C.divider } });
phases.forEach((p, i) => {
  const cx = startX + i * spacing;
  const isActive = p.active;
  // 圆点
  slide.addShape('ellipse', {
    x: cx - 0.12, y: axisY - 0.12, w: 0.24, h: 0.24,
    fill: { color: isActive ? C.accent : C.divider }
  });
  // 标签
  slide.addText(p.label, { x: cx - 0.5, y: axisY + 0.3, w: 1, h: 0.3, fontSize: 10, fontFace: FONT, color: isActive ? C.accent : C.muted, align: 'center', bold: isActive });
  // 标题
  slide.addText(p.title, { x: cx - 0.8, y: axisY - 1.2, w: 1.6, h: 0.4, fontSize: 12, fontFace: FONT, color: isActive ? C.accent : C.text, align: 'center', bold: isActive });
  // 卡片描述
  if (isActive) {
    slide.addShape('roundRect', { x: cx - 0.8, y: axisY - 1.8, w: 1.6, h: 0.5, fill: { color: C.accent } });
    slide.addText('当前阶段', { x: cx - 0.8, y: axisY - 1.8, w: 1.6, h: 0.5, fontSize: 9, fontFace: FONT, color: 'FFFFFF', align: 'center' });
  }
});
```

---

## L09 — 流程页（Process Flow）

**适用：** 业务流程、系统架构、方法论步骤
**特点：** 水平/垂直流程 + 箭头连接 + 步骤说明

```
┌──────────────────────────────────────┐
│                                      │
│  ┌──────┐   ┌──────┐   ┌──────┐    │
│  │ 步骤1 │ → │ 步骤2 │ → │ 步骤3 │    │
│  │ 输入  │   │ 处理  │   │ 输出  │    │
│  └──────┘   └──────┘   └──────┘    │
│              │                       │
│              ↓                       │
│          ┌──────┐                    │
│          │ 步骤4 │ ← 异常处理        │
│          │ 反馈  │                   │
│          └──────┘                    │
│                                      │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
slide.addText('业务流程设计', { x: 0.5, y: 0.3, w: 9, h: 0.6, fontSize: 22, fontFace: FONT, color: C.text, bold: true });
// 主流程
const steps = ['数据采集', '清洗处理', '分析建模', '结果输出'];
const arrowW = 0.6;
const stepW = 1.8, stepH = 1.2;
const totalW = steps.length * stepW + (steps.length - 1) * arrowW;
const startX2 = (10 - totalW) / 2;
steps.forEach((s, i) => {
  const sx = startX2 + i * (stepW + arrowW);
  slide.addShape('roundRect', { x: sx, y: 1.5, w: stepW, h: stepH, fill: { color: i === 2 ? C.accent : C.card }, line: { color: C.accent } });
  slide.addText(s, { x: sx, y: 1.7, w: stepW, h: 0.8, fontSize: 12, fontFace: FONT, color: i === 2 ? 'FFFFFF' : C.accent, align: 'center', bold: true });
  // 箭头
  if (i < steps.length - 1) {
    slide.addText('→', { x: sx + stepW, y: 1.9, w: arrowW, h: 0.4, fontSize: 18, fontFace: FONT, color: C.muted, align: 'center' });
  }
});
// 底部说明
slide.addText('流程说明：核心环节为分析建模，数据质量直接影响最终结果', {
  x: 0.5, y: 3.2, w: 9, h: 0.4, fontSize: 10, fontFace: FONT, color: C.muted
});
```

---

## L10 — 矩阵/象限页（Matrix / 2x2）

**适用：** 战略定位、竞争力评估、优先级矩阵
**特点：** 2x2 四象限 + 各象限标签 + 项目分布

```
┌──────────────────────────────────────┐
│     高                              │
│  ┌──────────┬──────────┐            │
│  │ 维持     │ 优先投资 │            │
│  │ Keep     │ Priority │            │
│  │          │          │            │
│  ├──────────┼──────────┤  重要性   │
│  │ 低优先   │ 长期观察 │            │
│  │ Low      │ Watch    │            │
│  │          │          │            │
│  └──────────┴──────────┘            │
│                 → 可行性      低    │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
slide.addText('战略优先级矩阵', { x: 0.5, y: 0.2, w: 9, h: 0.5, fontSize: 20, fontFace: FONT, color: C.text, bold: true });
// 四象限
const quads = [
  { x: 0.5, y: 1.0, label: '维持 Keep', color: C.muted, items: '项目 A\n项目 B' },
  { x: 5.2, y: 1.0, label: '优先投资 Priority', color: C.accent, items: '项目 C (重点)\n项目 D' },
  { x: 0.5, y: 3.2, label: '低优先 Low', color: C.divider, items: '项目 E' },
  { x: 5.2, y: 3.2, label: '长期观察 Watch', color: C.gold, items: '项目 F\n项目 G' },
];
quads.forEach(q => {
  slide.addShape('rect', { x: q.x, y: q.y, w: 4.2, h: 1.8, fill: { color: C.card }, line: { color: C.divider } });
  slide.addText(q.label, { x: q.x + 0.2, y: q.y + 0.1, w: 3.8, h: 0.4, fontSize: 13, fontFace: FONT, color: q.color, bold: true });
  slide.addText(q.items, { x: q.x + 0.2, y: q.y + 0.6, w: 3.8, h: 1.0, fontSize: 10, fontFace: FONT, color: C.text });
});
// 坐标轴标签
slide.addText('可行性 →', { x: 5.2, y: 5.3, w: 1.5, h: 0.3, fontSize: 9, fontFace: FONT, color: C.muted });
slide.addText('↑ 重要性', { x: 0.1, y: 1.5, w: 0.5, h: 2.5, fontSize: 9, fontFace: FONT, color: C.muted, align: 'center', valign: 'middle' });
```

---

## L11 — 引用/案例页（Quote / Case Study）

**适用：** 客户案例、专家引用、数据背书
**特点：** 大号引用文字 + 来源 + Logo/人物

```
┌──────────────────────────────────────┐
│                                      │
│  "                                  │
│  实施该项目后，运营效率提升了 40%， │
│  年度成本节约超过 500 万元，         │
│  远超预期目标。                      │  ← 大号引用 18-22pt
│  "                                  │
│                                      │
│  ── 某客户 CTO，2026年6月            │  ← 来源
│                                      │
│  [客户 Logo]  [客户 Logo]            │
└──────────────────────────────────────┘
```

**pptxgenjs 骨架：**
```js
slide.background = { color: C.bg };
// 引用标记 — 大号引号
slide.addText('"', { x: 0.8, y: 0.5, w: 1, h: 1.0, fontSize: 48, fontFace: FONT, color: C.accent, bold: true });
// 引用正文
slide.addText('实施该项目后，运营效率提升了 40%，\n年度成本节约超过 500 万元，\n远超预期目标。', {
  x: 1.5, y: 0.8, w: 7.5, h: 2.5, fontSize: 20, fontFace: FONT, color: C.text, valign: 'top'
});
// 引号闭合
slide.addText('"', { x: 7.5, y: 2.5, w: 1, h: 1.0, fontSize: 48, fontFace: FONT, color: C.accent, bold: true, align: 'right' });
// 来源
slide.addShape('rect', { x: 0.8, y: 3.8, w: 1.5, h: 0.02, fill: { color: C.accent } });
slide.addText('某知名客户 CTO，2026 年 6 月', { x: 0.8, y: 3.9, w: 5, h: 0.4, fontSize: 12, fontFace: FONT, color: C.muted });
// Logo 占位
slide.addText('[客户 Logo]    [客户 Logo]', { x: 0.8, y: 4.6, w: 5, h: 0.5, fontSize: 10, fontFace: FONT, color: C.muted });
```

---

## L12 — 数据表格页（Table）

**适用：** 明细数据展示、对比表格
**特点：** 表格 + 表头高亮 + 行条纹 + 数据解读

```
┌──────────────────────────────────────┐
│  指标       2024    2025    2026E   │  ← 表头（深色背景）
│──────────────────────────────────────│
│  营收 ($M)   1,200   1,450   1,720  │  ← 数据行（条纹交替）
│  毛利率       28%     32%     35%   │
│  YoY 增长     —       +21%    +19%  │
│  EBITDA       340     420     510   │
│──────────────────────────────────────│
│  ▶ 趋势: 营收稳健增长，利润率改善   │  ← 解读
└──────────────────────────────────────┘
```

**pptxgenjs 骨架（纯 shapes 模拟，避免表格兼容性问题）：**
```js
slide.background = { color: C.bg };
slide.addText('财务指标概览', { x: 0.5, y: 0.2, w: 9, h: 0.5, fontSize: 20, fontFace: FONT, color: C.text, bold: true });
const headers = ['指标', '2024', '2025', '2026E'];
const rows = [
  ['营收 ($M)', '1,200', '1,450', '1,720'],
  ['毛利率', '28%', '32%', '35%'],
  ['YoY 增长', '—', '+21%', '+19%'],
  ['EBITDA ($M)', '340', '420', '510'],
];
const colW = [2.5, 2.0, 2.0, 2.0];
const rowH = 0.5;
const startY = 1.0;
// 表头
let cx = 0.5;
headers.forEach((h, i) => {
  slide.addShape('rect', { x: cx, y: startY, w: colW[i], h: rowH, fill: { color: C.accent } });
  slide.addText(h, { x: cx, y: startY, w: colW[i], h: rowH, fontSize: 11, fontFace: FONT, color: 'FFFFFF', align: 'center', valign: 'middle', bold: true });
  cx += colW[i];
});
// 数据行
rows.forEach((row, ri) => {
  const ry = startY + (ri + 1) * rowH;
  const bgColor = ri % 2 === 0 ? C.card : C.light;
  let rx = 0.5;
  row.forEach((cell, ci) => {
    slide.addShape('rect', { x: rx, y: ry, w: colW[ci], h: rowH, fill: { color: bgColor } });
    slide.addText(cell, { x: rx, y: ry, w: colW[ci], h: rowH, fontSize: 10, fontFace: FONT, color: ci === 0 ? C.accentDark : C.text, align: ci === 0 ? 'left' : 'center', valign: 'middle', bold: ci === 0 });
    rx += colW[ci];
  });
});
// 解读
slide.addShape('rect', { x: 0.5, y: startY + (rows.length + 1) * rowH + 0.2, w: 8.5, h: 0.4, fill: { color: C.light } });
slide.addText('▶ 趋势: 营收稳健增长，利润率持续改善，EBITDA 增速领先', { x: 0.7, y: startY + (rows.length + 1) * rowH + 0.25, w: 8.1, h: 0.3, fontSize: 10, fontFace: FONT, color: C.accentDark });
```

---

## 模板选择指南

| 模板 | 编号 | 最佳场景 | 复杂度 |
|------|------|---------|--------|
| 封面页 | L01 | PPT 首页 / 章节封面 | ⭐ |
| 目录页 | L02 | 内容导航 / 议程 | ⭐⭐ |
| 章节标题页 | L03 | 章节切换过渡 | ⭐ |
| 结论先行页 | L04 | 核心论点 / 关键发现 | ⭐⭐⭐ |
| 左文右图 | L05 | 产品介绍 / 案例 | ⭐⭐ |
| 数据图表页 | L06 | KPI 汇报 / 数据分析 | ⭐⭐⭐ |
| 对比页 | L07 | 竞品对比 / 方案评估 | ⭐⭐ |
| 时间线 | L08 | 项目计划 / 里程碑 | ⭐⭐⭐ |
| 流程页 | L09 | 业务流程 / 方法论 | ⭐⭐ |
| 矩阵象限 | L10 | 战略定位 / 优先级 | ⭐⭐⭐ |
| 引用案例 | L11 | 客户背书 / 数据引用 | ⭐ |
| 数据表格 | L12 | 明细数据 / 财报 | ⭐⭐ |

**使用原则：**
1. 同一份 PPT 中尽量使用 3-4 种不同布局轮换，保持视觉多样性
2. 每次选模板后做微调：配色、边距、字体大小按实际内容适配
3. 复杂页（L04/L06/L10）优先逐页确认
