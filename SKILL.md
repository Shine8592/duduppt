---
name: cyber-ppt
description: "主人说'做个PPT'时用这个技能。把文档/数据/想法转成咨询风格高密度PPTX。三阶段：证据分析→视觉蓝图→PPTX生成+QA。不是套模板，是流水线式生产。来源：CyberPPT项目(crazyykhllc-bit/CyberPPT)方法论。"
---

# 🎯 嘟嘟的咨询风PPT流水线

> 来源：CyberPPT（crazyykhllc-bit/CyberPPT）三阶段方法论
> 适配为嘟嘟可执行的 Hermes 技能

## 触发条件

主人说类似以下的话时加载本技能：
- "帮我做个PPT"
- "把这份材料做成演示文稿"
- "需要一份关于XX的汇报材料"
- "做份deck"
- 任何涉及 .pptx 生成的需求

## 核心原则（记牢）

1. **结论先行** — 每页必须有可被证据挑战的强标题，不能只放图表
2. **双硬门槛** — 主要文字必须可编辑 + 视觉必须高保真，二选一就是不合格
3. **SO WHAT 必在** — 每页必须有业务含义/行动建议，咨询PPT不只有数据
4. **逐页验收** — 一页做完确认再下一页，不要一次性批量生成
5. **先确认再过门** — 三阶段各有确认门，未经用户批准不得进入下一阶段

---

## 三阶段执行流程

### 📋 阶段一：分析（产出：证据表 + 故事线 + 逐页大纲）

**目标：把源材料变成可审计的证据和清晰的故事线**

#### 步骤 1.1 — 读材料，建证据表

```
| ID | 论点/数据 | 数值 | 单位 | 期间 | 来源 | 置信度 | Caveat | 含义 | 推荐视觉 |
```

规则：
- 区分事实 vs 解释 vs 建议
- 缺失数据标记 `未提供`/`仅方向性判断`/`需外部验证`，不编造
- 数据冲突时保留两个值并说明差异原因

#### 步骤 1.2 — 内容脑暴（2-3 条故事线）

证据表完成后不要直接出大纲。先脑暴 2-3 个可选方向：
- 每条的核心结论是什么
- 依赖哪些关键证据
- 最大的数据缺口/风险是什么
- 适合什么受众场景

#### 步骤 1.3 — SCR 收敛

选一个故事线，按 **Situation → Complication → Resolution** 展开全篇论证。

| 要素 | 说明 |
|------|------|
| Situation | 受众已接受的背景 |
| Complication | 需要决策的变化/风险/机会 |
| Resolution | 证据支持的行动/选择 |

**结论标题测试标准：** 弱标题如"市场概览"❌ → 强标题如"市场增长在修复，但价值正向结构性优势赛道转移"✅

#### 步骤 1.4 — 逐页大纲

每页明确：角色、结论标题、论证、证据ID、Caveat、视觉类型、图表计划、SO WHAT、承接关系

**👉 出完后向主人汇报，等第一次确认再进阶段二**

---

### 🎨 阶段二：视觉蓝图（产出：风格选择 + 逐页蓝图描述）

**目标：确定视觉方向，规划每页的布局和视觉元素**

#### 步骤 2.1 — 选风格（8选1）

无品牌/模板时从以下选，有品牌/模板时直接沿用：

```
01 — 经典深红咨询风  #F3F4EF + #8B1E1E    → 战略/竞品/行业研究
02 — 冷灰+勃艮第红   #F5F5F2 + #7A1F2B    → 财务/投研/风险
03 — 暖象牙+暗酒红   #F4F1EA + #8A1538    → 品牌/消费品/电商
04 — 象牙白+深蓝     #F7F6F0 + #12355B    → 科技/SaaS/AI
05 — 浅灰白+墨绿     #F2F3EF + #1F5B4D    → 可持续/增长
06 — 纸张米色+铜棕   #F4F0E8 + #9A5A2E    → 消费/零售/奢侈品
07 — 纯净浅灰+黑金   #F6F6F4 + #A87932    → 高管汇报/融资/董事会
08 — 冷白灰+深紫     #F4F5F6 + #4B2E83    → AI/技术/创新
```

选定后整份PPT锁定同一视觉系统。

#### 步骤 2.2 — 固定字体层级

全篇用 15 级 Typography Scale，不要发明新层级：

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

#### 步骤 2.3 — 逐页蓝图描述

为每页生成蓝图描述，包含：
- 页面标题和结论
- 布局类型（上结论下图表 / 左图表右解读 / 矩阵 / 流程 / 时间线 等）
- 每个区域的视觉元素、颜色比例
- 图表类型和数据来源
- 哪些区域需要保留为图片（复杂插画/照片/Logo）

**👉 出完后向主人汇报，等第二次确认再进阶段三**

---

### 🛠 阶段三：PPTX 生成 + QA（产出：可编辑高保真 PPTX）

**目标：逐页生成、逐页QA、逐页确认，最终合并交付**

#### 步骤 3.1 — 选工具 + 环境准备

| 场景 | 工具 |
|------|------|
| 高视觉保真、复杂布局 | `pptxgenjs`（Node.js） |
| 快速出稿、模板编辑 | `python-pptx` |
| 渲染QA | `LibreOffice` → PDF → PNG（优先）或 python-pptx 结构检查（备选） |

**环境坑（已验证解决）：**
```bash
# pptxgenjs 全局安装后需要设置 NODE_PATH
export NODE_PATH=/root/.hermes/node/lib/node_modules
# 或用本地安装：
npm install pptxgenjs --save
```

**核心策略：** 复杂视觉（照片/Logo/插画/纹理）可保留为图片，但主要文字、标题、数字、标签、来源必须原生可编辑。

#### 步骤 3.2 — QA 流程（含 Fallback）

**优先 QA：LibreOffice 渲染**
```bash
# 杀残留进程 + 转换 PDF
killall -9 soffice.bin 2>/dev/null; sleep 1
libreoffice --headless --convert-to pdf output.pptx

# PDF → PNG
pdftoppm -jpeg -r 150 output.pdf slide
```

**Fallback QA（LibreOffice 不可用时）：python-pptx 结构检查**
```python
from pptx import Presentation
from pptx.util import Emu

prs = Presentation('output.pptx')
print(f'Slides: {len(prs.slides)}')
w_in = prs.slide_width / 914400
h_in = prs.slide_height / 914400
print(f'Size: {w_in:.3f} x {h_in:.3f} inches (16:9={1.75 <= w_in/h_in <= 1.79})')

for i, slide in enumerate(prs.slides):
    texts = []
    pics = 0
    for s in slide.shapes:
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                if p.text.strip(): texts.append(p.text.strip()[:60])
        if s.shape_type == 13: pics += 1
    print(f'Slide {i+1}: {len(slide.shapes)} shapes, {pics} pics')
    print(f'  Text preview: {texts[0] if texts else "(empty)"}')
    print(f'  Pics: {\"⚠️\" if pics else \"✅\"} ({pics} pictures)')
```

#### 步骤 3.2 — 逐页生成流程

每页执行顺序：
1. 写蓝图 → 换算坐标（px → inch）
2. 写 slide_manifest.json（记录该页文字、图片、组件、QA期望）
3. 生成单页 PPTX
4. PowerPoint/LibreOffice 渲染导出 PNG
5. 视觉 QA 检查
6. 用户确认 → 再进下一页

#### 步骤 3.3 — QA 检查清单

**严格检查以下每一项：**

```
□ 所有页面都存在
□ 标题匹配已确认故事线
□ 数字匹配证据表
□ 主要文字可编辑（鼠标能选中修改）
□ 简单图表已原生重建（不是图片）
□ 视觉风格一致（没漂移）
□ 无占位文案残留（Lorem ipsum / xxxx / 单击此处添加）
□ 每页有 SO WHAT / 含义块
□ 文字没溢出容器（卡片、表格、结论条）
□ 字体层级符合 C0/T1-T14
□ 标签没压住图标/节点/曲线
□ 无语言元数据残留在页面（如 target_language）
□ 无整页蓝图截图当背景
```

**QA 命令：**
```bash
# PPTX → PDF → PNG 渲染
python -m scripts.office.soffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide

# 内容检查
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|todo"
```

#### 步骤 3.4 — 最终合并

逐页通过后，合并单页 PPTX 为完整 deck。合并后做全篇回归验证：
- 所有页面存在
- 背景/主题一致
- 无页面偏移/变形
- 字体无变化

**👉 最终交付：PPTX + QA 报告**

---

## 🚫 红线

| 绝对禁止 | 原因 |
|----------|------|
| 编造数据/市场规模/调研结果 | 违反咨询基本诚信 |
| 用整页截图当PPT背景 | 不可编辑 |
| 把文字烘焙进图片 | 不可编辑 |
| 为可编辑把复杂图表简化成默认图形 | 视觉降级 |
| 一次性生成≥3页终版 | 质量失控 |
| 跳过SO WHAT只放图表 | 咨询PPT必须有含义 |
| 跳过用户确认门 | 流程失控 |

## ⚙️ 关键技术参数（源码沉淀）

```python
# 容差
P0容差 = 3px（最大6px）    # 标题/主图/SO WHAT/页脚/关键数字
P1容差 = 4px（最大8px）    # 卡片/图标/标签/箭头/表格
P2容差 = 6px（最大12px）   # 装饰线/纹理/背景纹样

# 图片检测阈值
LARGE_IMAGE_RATIO = 0.40   # >40%页面面积=大图风险
FULL_SLIDE_IMAGE_RATIO = 0.90  # >90%=整页背景风险

# 曲线
CORE_CURVE_MIN_POINTS = 16  # 核心曲线最少采样点

# 字体
GLOBAL_MIN_FONT_PT = 6.5    # 任何文字不得小于此值

# 像素对比
PIXEL_DIFF_TOLERANCE = 18   # 蓝图vs渲染的mean abs diff容差
```

## 🎨 设计原则

- 不要默认蓝色 — 颜色要反映主题
- 不要素色白底+默认圆点 — 每页都要有视觉元素
- 不要用accent lines装饰标题 — AI生成PPT的典型标志
- 先渲染QA再交付 — 永远假设第一版有问题
- 用子代理做视觉检查 — 自己盯着看会漏问题

## 📚 参考

CyberPPT（crazyykhllc-bit/CyberPPT）：SCR论证、Typography Scale C0-T14、15道门禁体系、精确追踪原则、8种视觉风格。
