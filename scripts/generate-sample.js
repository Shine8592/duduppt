const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';

// Palette #04 — 象牙白+深蓝（科技风）
const BG = 'F7F6F0';
const TITLE = '101820';
const BODY = '303030';
const ACCENT = '12355B';
const LINE = 'C9CDD1';

// === Slide 1: 封面 ===
const slide1 = pptx.addSlide();
slide1.background = { color: ACCENT };

slide1.addText('AI Agent 开发现状与趋势', {
  x: 0.8, y: 2.0, w: 11.7, h: 1.5,
  fontSize: 40, fontFace: 'Arial',
  color: 'FFFFFF', bold: true
});
slide1.addText('从概念验证到生产部署的关键路径', {
  x: 0.8, y: 3.5, w: 11.7, h: 0.8,
  fontSize: 18, fontFace: 'Arial',
  color: 'C9CDD1'
});
slide1.addShape(pptx.ShapeType.rect, {
  x: 0.8, y: 4.5, w: 2.0, h: 0.06,
  fill: { color: 'A87932' }
});
slide1.addText('duduppt  |  2025', {
  x: 0.8, y: 6.5, w: 5, h: 0.5,
  fontSize: 12, fontFace: 'Arial', color: 'C9CDD1'
});

// === Slide 2: 市场格局 ===
const slide2 = pptx.addSlide();
slide2.background = { color: BG };

slide2.addText('市场格局', {
  x: 0.6, y: 0.3, w: 2, h: 0.5,
  fontSize: 14, fontFace: 'Arial', color: ACCENT, bold: true
});
slide2.addText('Agent 开发框架呈三强鼎立格局，生态尚未固化', {
  x: 0.6, y: 0.9, w: 12, h: 0.7,
  fontSize: 24, fontFace: 'Arial', color: TITLE, bold: true
});

// 市场份额数据
const data = [
  [{ text: '框架', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } },
   { text: '市占率', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } },
   { text: '核心优势', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } }],
  [{ text: 'LangChain', options: { fontSize: 11 } }, { text: '43%', options: { fontSize: 11, bold: true } }, { text: '生态最丰富，社区最大', options: { fontSize: 11 } }],
  [{ text: 'Semantic Kernel', options: { fontSize: 11 } }, { text: '28%', options: { fontSize: 11, bold: true } }, { text: '微软生态集成，企业级', options: { fontSize: 11 } }],
  [{ text: 'CrewAI', options: { fontSize: 11 } }, { text: '15%', options: { fontSize: 11, bold: true } }, { text: '多Agent编排简单', options: { fontSize: 11 } }],
  [{ text: '其他', options: { fontSize: 11 } }, { text: '14%', options: { fontSize: 11, bold: true } }, { text: 'AutoGPT、BabyAGI等', options: { fontSize: 11 } }],
];
slide2.addTable(data, {
  x: 0.6, y: 2.0, w: 8, h: 3.0,
  fontSize: 11, fontFace: 'Arial',
  border: { type: 'solid', pt: 0.5, color: LINE },
  colW: [3.0, 2.0, 3.0],
  rowH: [0.5, 0.5, 0.5, 0.5, 0.5],
});

// 结论条
slide2.addShape(pptx.ShapeType.rect, {
  x: 0.6, y: 5.5, w: 12, h: 0.8,
  fill: { color: 'E8EDF5' }
});
slide2.addText('SO WHAT: 生态尚未固化，框架选择窗口期仍在。建议以 LangChain 为主栈，同时关注 Semantic Kernel 的企业级进展。', {
  x: 0.8, y: 5.6, w: 11.6, h: 0.6,
  fontSize: 11, fontFace: 'Arial', color: BODY
});

// 页脚
slide2.addText('2  |  duduppt  |  Confidential', {
  x: 0.6, y: 7.0, w: 12, h: 0.3,
  fontSize: 8, fontFace: 'Arial', color: '999999'
});

// === Slide 3: 核心瓶颈 ===
const slide3 = pptx.addSlide();
slide3.background = { color: BG };

slide3.addText('核心瓶颈', {
  x: 0.6, y: 0.3, w: 2, h: 0.5,
  fontSize: 14, fontFace: 'Arial', color: ACCENT, bold: true
});
slide3.addText('可靠性、成本、安全构成规模化"铁三角"瓶颈', {
  x: 0.6, y: 0.9, w: 12, h: 0.7,
  fontSize: 24, fontFace: 'Arial', color: TITLE, bold: true
});

// 三个 KPI 卡片
const kpis = [
  { label: '工具调用失败率', value: '22%', desc: '复杂任务链中单步失败概率', x: 0.6 },
  { label: '单次任务成本', value: '$0.47', desc: '含 LLM 调用 + 工具执行', x: 4.8 },
  { label: '数据泄露风险', value: '32%', desc: '企业遇 Agent 相关数据泄露', x: 9.0 },
];
kpis.forEach(k => {
  slide3.addShape(pptx.ShapeType.roundRect, {
    x: k.x, y: 2.0, w: 3.6, h: 2.8,
    fill: { color: 'FFFFFF' },
    shadow: { type: 'outer', blur: 6, offset: 2, color: '000000', opacity: 0.1 }
  });
  slide3.addText(k.value, {
    x: k.x, y: 2.3, w: 3.6, h: 1.0,
    fontSize: 36, fontFace: 'Arial', color: ACCENT, bold: true, align: 'center'
  });
  slide3.addText(k.label, {
    x: k.x, y: 3.3, w: 3.6, h: 0.5,
    fontSize: 13, fontFace: 'Arial', color: TITLE, bold: true, align: 'center'
  });
  slide3.addText(k.desc, {
    x: k.x, y: 3.8, w: 3.6, h: 0.5,
    fontSize: 10, fontFace: 'Arial', color: '666666', align: 'center'
  });
});

slide3.addShape(pptx.ShapeType.rect, {
  x: 0.6, y: 5.5, w: 12, h: 0.8,
  fill: { color: 'E8EDF5' }
});
slide3.addText('SO WHAT: 三项瓶颈相互关联——降成本往往牺牲可靠性，提安全通常增加成本。需要组合方案而非单点优化。', {
  x: 0.8, y: 5.6, w: 11.6, h: 0.6,
  fontSize: 11, fontFace: 'Arial', color: BODY
});
slide3.addText('3  |  duduppt  |  Confidential', {
  x: 0.6, y: 7.0, w: 12, h: 0.3,
  fontSize: 8, fontFace: 'Arial', color: '999999'
});

// === Slide 4: 解决方案 ===
const slide4 = pptx.addSlide();
slide4.background = { color: BG };

slide4.addText('解决方案', {
  x: 0.6, y: 0.3, w: 2, h: 0.5,
  fontSize: 14, fontFace: 'Arial', color: ACCENT, bold: true
});
slide4.addText('MCP + Guardrails + Caching 组合方案已验证有效', {
  x: 0.6, y: 0.9, w: 12, h: 0.7,
  fontSize: 24, fontFace: 'Arial', color: TITLE, bold: true
});

// 三个方案对比表
const solData = [
  [{ text: '方案', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } },
   { text: '效果', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } },
   { text: '实现周期', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } },
   { text: '优先级', options: { bold: true, color: 'FFFFFF', fill: { color: ACCENT }, fontSize: 12 } }],
  [{ text: 'MCP 协议', options: { fontSize: 11 } }, { text: '↓ 40% 集成成本', options: { fontSize: 11 } }, { text: '1-2 个月', options: { fontSize: 11 } }, { text: 'P0', options: { fontSize: 11, bold: true, color: ACCENT } }],
  [{ text: 'Guardrails', options: { fontSize: 11 } }, { text: '拦 89% 异常', options: { fontSize: 11 } }, { text: '2-3 个月', options: { fontSize: 11 } }, { text: 'P0', options: { fontSize: 11, bold: true, color: ACCENT } }],
  [{ text: 'Caching', options: { fontSize: 11 } }, { text: '省 60% Token', options: { fontSize: 11 } }, { text: '0.5-1 个月', options: { fontSize: 11 } }, { text: 'P1', options: { fontSize: 11, bold: true } }],
];
slide4.addTable(solData, {
  x: 0.6, y: 2.0, w: 12, h: 2.5,
  fontSize: 11, fontFace: 'Arial',
  border: { type: 'solid', pt: 0.5, color: LINE },
  colW: [3.0, 3.0, 3.0, 3.0],
  rowH: [0.5, 0.5, 0.5, 0.5],
});

slide4.addShape(pptx.ShapeType.rect, {
  x: 0.6, y: 5.5, w: 12, h: 0.8,
  fill: { color: 'E8EDF5' }
});
slide4.addText('SO WHAT: 三项组合可在 3-6 个月内实现 ROI 转正。建议优先落地 MCP + Caching（低成本高回报），再上 Guardrails（安全保障）。', {
  x: 0.8, y: 5.6, w: 11.6, h: 0.6,
  fontSize: 11, fontFace: 'Arial', color: BODY
});
slide4.addText('4  |  duduppt  |  Confidential', {
  x: 0.6, y: 7.0, w: 12, h: 0.3,
  fontSize: 8, fontFace: 'Arial', color: '999999'
});

// === Slide 5: 行动建议 ===
const slide5 = pptx.addSlide();
slide5.background = { color: BG };

slide5.addText('行动建议', {
  x: 0.6, y: 0.3, w: 2, h: 0.5,
  fontSize: 14, fontFace: 'Arial', color: ACCENT, bold: true
});
slide5.addText('抓住窗口期，建立差异化 Agent 能力', {
  x: 0.6, y: 0.9, w: 12, h: 0.7,
  fontSize: 24, fontFace: 'Arial', color: TITLE, bold: true
});

// 时间线
slide5.addShape(pptx.ShapeType.rect, {
  x: 0.6, y: 2.0, w: 12, h: 0.04,
  fill: { color: LINE }
});
const milestones = [
  { label: 'Q3 启动 PoC', sub: '客服+内部工具', x: 1.0 },
  { label: 'Q4 试运行', sub: '扩展至 3-5 业务线', x: 5.0 },
  { label: 'Q1 规模化', sub: '全部门推广', x: 9.0 },
];
milestones.forEach(m => {
  slide5.addShape(pptx.ShapeType.ellipse, {
    x: m.x + 1.0, y: 1.8, w: 0.4, h: 0.4,
    fill: { color: ACCENT }
  });
  slide5.addText(m.label, {
    x: m.x, y: 2.5, w: 2.4, h: 0.4,
    fontSize: 13, fontFace: 'Arial', color: TITLE, bold: true, align: 'center'
  });
  slide5.addText(m.sub, {
    x: m.x, y: 2.9, w: 2.4, h: 0.4,
    fontSize: 10, fontFace: 'Arial', color: '666666', align: 'center'
  });
});

// 三张行动卡片
const actions = [
  { title: '选型', desc: '以 LangChain 为主栈\n评估 Semantic Kernel\n备选方案', x: 0.6 },
  { title: '基建', desc: '部署 MCP Server\n搭建 Guardrails\n配置 Caching Layer', x: 4.8 },
  { title: '团队', desc: '组建 3-5 人 Agent 团队\n设立效能度量体系\n每双周迭代', x: 9.0 },
];
actions.forEach(a => {
  slide5.addShape(pptx.ShapeType.roundRect, {
    x: a.x, y: 3.8, w: 3.6, h: 2.5,
    fill: { color: 'FFFFFF' },
    shadow: { type: 'outer', blur: 4, offset: 1, color: '000000', opacity: 0.08 }
  });
  slide5.addShape(pptx.ShapeType.rect, {
    x: a.x, y: 3.8, w: 3.6, h: 0.06,
    fill: { color: ACCENT }
  });
  slide5.addText(a.title, {
    x: a.x, y: 4.1, w: 3.6, h: 0.5,
    fontSize: 14, fontFace: 'Arial', color: ACCENT, bold: true, align: 'center'
  });
  slide5.addText(a.desc, {
    x: a.x + 0.3, y: 4.7, w: 3.0, h: 1.2,
    fontSize: 10, fontFace: 'Arial', color: BODY, align: 'center'
  });
});

slide5.addText('5  |  duduppt  |  Confidential', {
  x: 0.6, y: 7.0, w: 12, h: 0.3,
  fontSize: 8, fontFace: 'Arial', color: '999999'
});

// 输出
pptx.writeFile({ fileName: '/tmp/duduppt-rollout/duduppt-sample.pptx' })
  .then(() => console.log('✅ PPTX generated: /tmp/duduppt-rollout/duduppt-sample.pptx'))
  .catch(err => console.error(err));
