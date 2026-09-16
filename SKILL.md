---
name: duduppt
description: "主人说'做个PPT'时用这个技能。把文档/数据/想法转成咨询风格高密度PPTX。三阶段：证据分析→视觉蓝图→PPTX生成+QA。GitHub: github.com/Shine8592/duduppt。"
---

# 🎯 duduppt — 嘟嘟的咨询风PPT流水线

> 来源：[CyberPPT](https://github.com/crazyykhllc-bit/CyberPPT) 三阶段方法论
> GitHub 项目：[duduppt](https://github.com/Shine8592/duduppt)
> 升级 v2.0：16+1 风格库 + 设计访谈 + 配图管理 + 演讲者备注

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

## 四阶段执行流程（v1.1 新增 Phase 0）

### 🔍 阶段 0：Deep Research（自动补证据）

> 当主人没有提供完整材料时，先自动搜索补充背景信息。

**目标：填补证据缺口，为 Phase 1 提供素材**

1. 确定搜索关键词（从任务描述中提取 3-5 个关键方向）
2. 运行多引擎搜索：
   ```bash
   python3 scripts/research-topic.py --topic "中国财富管理市场 2026" --depth deep --sources 8
   ```
3. 搜索结果整理为结构化证据输入：
   - 核心结论（3-5 条）
   - 关键数据点（含来源和置信度）
   - 数据缺口清单（标记"需人工验证"）
   - 建议进一步搜索方向

**搜索策略：** Tavily → Exa → Querit → SerpAPI → DuckDuckGo 逐级兜底，确保总有结果
（各引擎在 `scripts/research-topic.py` 内自动降级，无需手动切换）

**👉 将搜索结果喂给 Phase 1 证据表**

---

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

### 🎨 阶段二：视觉蓝图（产出：风格选择 + 逐页布局）

**目标：确定视觉方向，规划每页的布局和视觉元素**

#### 步骤 2.0 — 参考学习（可选）

如果主人说"按这个风格做"或提供了参考 PPTX：
```bash
python3 scripts/learn-from-pptx.py --input reference.pptx --compare
```
自动提取：配色方案、字体、布局特征 → 匹配最接近的 duduppt 预设风格

#### 步骤 2.1 — 设计访谈（先问再选，不盲目推荐）

在选风格之前，先问主人 5 个问题确定方向：

```
1. 受众是谁？        → 高管/客户/同行/公众？
2. 什么场景？        → 正式汇报/沙龙分享/内部沟通？
3. 色调偏好？        → 暖色/冷色/深色/浅色？有无品牌色？
4. 图文比例？        → 图多（叙事型）/文多（数据型）？
5. 参考风格？        → 有没有喜欢的 PPT 或品牌参考？
```

根据回答推荐最匹配的风格（见下方 16+1 风格库）。

#### 步骤 2.2 — 选风格（16+1 选 + 参考学习）

无品牌/模板时从以下选，有参考 PPTX 时用 `learn-from-pptx.py` 自动匹配：

**经典系列（CyberPPT 继承）：**
```
01 — 经典深红咨询风   #F3F4EF + #8B1E1E    → 战略/竞品/行业研究
02 — 冷灰+勃艮第红    #F5F5F2 + #7A1F2B    → 财务/投研/风险
03 — 暖象牙+暗酒红    #F4F1EA + #8A1538    → 品牌/消费品/电商
04 — 象牙白+深蓝      #F7F6F0 + #12355B    → 科技/SaaS/AI
05 — 浅灰白+墨绿      #F2F3EF + #1F5B4D    → 可持续/增长
06 — 纸张米色+铜棕    #F4F0E8 + #9A5A2E    → 消费/零售/奢侈品
07 — 纯净浅灰+黑金    #F6F6F4 + #A87932    → 高管汇报/融资/董事会
08 — 冷白灰+深紫      #F4F5F6 + #4B2E83    → AI/技术/创新
```

**新增系列（duduppt v2.0）：**
```
09 — 清新高客风       #F8F9F7 + #5B9B8A    → 沙龙/传承（特选）
10 — 电子杂志风       #FAFAF8 + #C73E3A    → 叙事/案例/品牌故事
11 — 瑞士数据风       #FFFFFF + #E85D3A    → 数据/KPI/财务分析
12 — 极光渐变风       #0A0E27 + #6C63FF    → AI/路演/创新
13 — 黑胶唱片风       #F5F0E8 + #2C1810    → 文化/奢侈品/高端品牌
14 — 莫兰迪色风       #F2F0EC + #9E7E7A    → 设计/美学/生活方式
15 — 自然草木风       #F5F7F2 + #4A7C59    → ESG/环保/农业
16 — 经典商务蓝       #F6F8FA + #1B5E8A    → 保险/银行/传统企业
```

选定后整份PPT锁定同一视觉系统。详细色板见 `references/palettes.md`。

#### 步骤 2.3 — 固定字体层级

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

#### 步骤 2.4 — 选布局模板

从布局模板库中选择（`references/layouts/layout-library.md`），不再从零描述：

| 模板 | 编号 | 最佳场景 |
|------|------|---------|
| 封面页 | L01 | PPT 首页/章节封面 |
| 目录页 | L02 | 内容导航/议程 |
| 章节标题页 | L03 | 章节切换过渡 |
| 结论先行页 | L04 | 核心论点/关键发现 |
| 左文右图 | L05 | 产品介绍/案例 |
| 数据图表页 | L06 | KPI 汇报/数据分析 |
| 对比页 | L07 | 竞品对比/方案评估 |
| 时间线 | L08 | 项目计划/里程碑 |
| 流程页 | L09 | 业务流程/方法论 |
| 矩阵象限 | L10 | 战略定位/优先级 |
| 引用案例 | L11 | 客户背书/数据引用 |
| 数据表格 | L12 | 明细数据/财报 |

选模板后做微调：配色、边距、字体大小按实际内容适配。同一份 PPT 用 3-4 种不同布局轮换。

#### 步骤 2.5 — 配图规划（v2.0 新增）

为每页规划配图需求，在蓝图描述中标注：

```
配图标注格式：
  [图片-类型: 比例: 位置: 描述]
  示例: [图片-摄影: 16:9: 背景: 商务会议场景]
  示例: [图片-图标: 1:1: 标题旁: 增长箭头]
  示例: [图片-插画: 4:3: 右侧: 数据流示意图]
```

类型分类：
- **摄影** — 真实照片（人物/场景/产品），用于封面、案例页
- **图标** — 简单图形符号，用于标题装饰、列表标记
- **插画** — 概念示意图/信息图，用于流程页、对比页
- **图表** — 数据可视化，用 PPTX 原生 chart，不用图片
- **Logo** — 品牌标识，需透明背景

配图原则：
- 叙事型页面（案例/故事）→ 配摄影图，占比 40-60%
- 数据型页面（KPI/分析）→ 配图表/图标，占比 <20%
- 同份 PPT 的图片风格必须统一（不要混用摄影和插画）
- 所有配图在蓝图阶段标注 → Phase 3 统一生成/搜索

**👉 出完后向主人汇报，等第二次确认再进阶段三**

---

## 🖼️ 图片能力（AI 生图 + 搜索 + 识图 + 配图）

### 图片从哪来

| 来源 | 能力 | 工具/脚本 |
|------|------|-----------|
| **AI 生成** | Agnes API 生图，适配 PPT 尺寸 | `scripts/generate-image.js` |
| **图库搜索** | Pexels / Unsplash / Pixabay 免费图库 | `scripts/search-image.py` |
| **已有图片** | vision_analyze 读取图片，识别颜色/布局/元素 | `vision_analyze` 工具 |
| **提取配色** | 从图片/Logo 提取主色，自动生成 PPT 色板 | `scripts/extract-palette.py` |
| **参考学习** | 从参考 PPTX 提取全套风格 | `scripts/learn-from-pptx.py` |
| **外部素材** | 品牌 Logo、产品截图、照片 | 直接插入 PPTX |

### 快速生图（AI）
```bash
node scripts/generate-image.js --prompt "科技蓝渐变背景" --style bg --out cover.png
```
支持 style: `bg` (16:9), `hero` (4:3), `icon` (1:1)

### 图库搜索（免费）
```bash
python3 scripts/search-image.py --query "business meeting" --source pexels --count 3
python3 scripts/search-image.py --query "city skyline" --download ./images/
```
自动尝试 Pexels → Unsplash → Pixabay，需要对应 API key（免费注册）。

### 从参考图提取配色
```bash
python3 scripts/extract-palette.py --input brand-logo.png --format json
```

### 从参考 PPTX 学习风格（v1.1 新增）
```bash
python3 scripts/learn-from-pptx.py --input reference.pptx --compare
```
输出 style config JSON + 匹配最接近的 duduppt 预设风格。

### 图片在 PPTX 中的使用原则
- **封面**：大面积 AI 生成图/高清照片做背景（配合深色遮罩 + 白字）
- **内容页**：小面积配图（图标、插画、图表背景），不影响文字可编辑性
- **图表**：柱状图/折线图/表格必须原生重建，不可用图片替代
- **Logo**：品牌 Logo 可以用图片，但要确保背景透明或匹配底色

### 图片红线

| 禁止 | 正确做法 |
|------|----------|
| 用整页截图当 PPT 背景 | 图片只做装饰/配图，主要信息层必须可编辑 |
| 把文字烘焙进图片 | 标题/正文/KPI/来源必须原生文字 |
| 随意用风格不统一的网图 | AI 生图或合规图库搜索 |

---

### 🛠 阶段三：PPTX 生成 + QA（产出：可编辑高保真 PPTX）

**目标：逐页生成、逐页QA、逐页确认，最终合并交付**

#### 步骤 3.1 — 选工具 + 环境准备

| 场景 | 工具 |
|------|------|
| 高视觉保真、复杂布局 | `pptxgenjs`（Node.js） |
| 快速出稿、模板编辑 | `python-pptx` |
| 渲染QA | `LibreOffice` → PDF → PNG（优先）或 zipfile 结构检查（兜底） |

**环境坑（已验证解决）：**
```bash
# pptxgenjs 全局安装后需要设置 NODE_PATH
export NODE_PATH=/root/.hermes/node/lib/node_modules
# 或用本地安装：
npm install pptxgenjs --save
```

**核心策略：** 复杂视觉（照片/Logo/插画/纹理）可保留为图片，但主要文字、标题、数字、标签、来源必须原生可编辑。

#### 步骤 3.2 — QA 流程

**QA 优先级：**
1. **LibreOffice 渲染** → PDF → PNG（像素级验证）
2. **stdlib-only 结构检查**（LibreOffice 不可用时兜底）

**结构检查（零依赖，永远可用）：**
```python
import zipfile, re
z = zipfile.ZipFile('deck.pptx')
assert z.testzip() is None, 'ZIP corrupted'
slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
                key=lambda x: int(re.search(r'(\d+)', x).group(1)))
for n in slides:
    xml = z.read(n).decode('utf-8', 'ignore')
    texts = [t for t in re.findall(r'<a:t>([^<]*)</a:t>', xml) if t.strip()]
    print(n.split('/')[-1], '|', len(texts), '|', (texts[0] if texts else '(empty)')[:46])

# 字体检查（中文防乱码）—— 必须区分 latin / ea 两个槽位
# 坑：只查 typeface 出现过是不够的。中文字体若写在 <a:latin> 槽位，
#     中文根本不生效（静默失效）；必须确认 <a:ea> 槽位。
CJK_FONTS = {'微软雅黑', 'Microsoft YaHei', 'Noto Sans CJK SC', 'Source Han Sans SC',
             '思源黑体', 'Hiragino Sans GB', 'PingFang SC', '宋体', 'SimSun'}
ea_fonts, problems = set(), []
for n in slides:
    xml = z.read(n).decode('utf-8', 'ignore')
    ea = set(re.findall(r'<a:ea typeface="([^"]+)"', xml))
    latin = set(re.findall(r'<a:latin typeface="([^"]+)"', xml))
    ea_fonts |= ea
    has_cjk = bool(re.search(r'<a:t>[^<]*[\u4e00-\u9fff]', xml))
    if has_cjk and not ea:
        problems.append(f'{n}: CJK_NO_EA 有中文但未设 <a:ea>')
    if (latin & CJK_FONTS) and not ea:
        problems.append(f'{n}: CJK_FACE_UNREACHED 中文字体写在 latin 槽位，不生效')
assert not problems, '中文字体问题: ' + '; '.join(problems)
assert ea_fonts & CJK_FONTS, f'CJK_NO_EA: 未绑定中文字体 ea 槽位 (当前: {ea_fonts})'
print(f'中文字体 OK: {ea_fonts}')
print(f'⚠️ 交付时告知用户：本 deck 依赖 {", ".join(sorted(ea_fonts))}，收件人需安装')
# 注意：不要用 WenQuanYi / 其他 Linux 发行版字体作投递字体 ——
#       开发机有但 Windows/macOS 收件人没有，等于未绑定。

# 占位符扫描
blob = b''.join(z.read(n) for n in slides)
for bad in ['Lorem',' ipsum','单击此处','xxxx','TODO']:
    assert bad.encode() not in blob, f'placeholder found: {bad}'

# chart 文件检查
charts = [n for n in z.namelist() if 'charts/chart' in n and n.endswith('.xml')]
for c in charts:
    cx = z.read(c).decode('utf-8')
    dir_pos = cx.find('barDir')
    if dir_pos > -1:
        print(f'{c}: has barDir ("col" expected for column charts)')
```

**⚠️ Chart Type 大坑（pptxgenjs）：**
- `slide.addChart('column', data, opts)` **不报错但产出空白页**
- **修复：** 竖柱状图用 `'bar'` + `barDir:'col'`：
  ```js
  // ❌ 空白页：
  slide.addChart('column', data, { x, y, w, h });
  // ✅ 可工作：
  slide.addChart('bar', data, { x, y, w, h, barDir: 'col' });
  ```

#### 步骤 3.3 — 逐页生成流程

每页执行顺序：
1. 选布局模板 → 换算坐标（px → inch）
2. 写 slide_manifest.json（记录该页文字、图片、组件、QA期望）
3. **生成演讲者备注**（v2.0 新增）— 根据标题 + 证据 + SO WHAT 自动生成每页备注
4. 生成单页 PPTX
5. LibreOffice 渲染导出 PNG 或结构检查
6. 视觉 QA 检查
7. 用户确认 → 再进下一页

**演讲者备注生成规则：**
- 备注 = 标题展开 + 关键数据强调 + SO WHAT 口语化表达
- 控制在 60-100 字以内，口语化，适合现场讲
- 非逐字稿，而是要点提示
- 示例：标题"市场增长在修复，但价值正向结构性优势赛道转移" → 备注"2025年行业增长12%，主要集中在中高端赛道。建议关注赛道A和B，放弃低毛利赛道C。具体数据见XX报告。"

#### 步骤 3.4 — QA 检查清单（v2.0：**机械项 / 视觉项 分离**）

> **原则：机械项绝不靠"看图"判断** —— 用渲染图去确认一个 lint 能秒判的问题，
> 是纯浪费。先跑机械检查，只剩视觉项才渲图。

**A. 机械项（zipfile / 脚本，秒级，必跑）**

```
□ 所有页面都存在（slide 数量 == 预期）
□ 无占位文案残留（Lorem ipsum / xxxx / 单击此处添加 / TODO）
□ 柱状图 barDir 正确（"col" 非 "bar"，否则空白页）—— 见 chart-type-anatomy.md
□ 图表有数据点（<c:pt> 非空）
□ 中文字体：<a:ea> 槽位已绑定（**不是**只查 typeface 出现过）—— 见 merge-and-qa.md
□ 无语言元数据残留（lang="en-US" 于中文 run 上）
□ 字体层级符合 C0/T1-T14（字号值在白名单内）
□ 主要文字可编辑（不存在整页 base64 大图）
□ **页面数字全部可溯源**（跑 `trace-claims.py`，见下）
□ **图片来源与授权完整**（跑 `collect-credits.py`，见下）
```

**A1. 数字溯源校验（v2.0 新增，把"不编造数据"变成可计算）**

```bash
# 先把证据表存成机器可读 JSON，再对 deck 溯源
python3 scripts/trace-claims.py --deck output.pptx --evidence evidence.json
```
输出 `UNTRACED: slide7 "42%"` = 该数字在证据表里查不到。
**处理要求（二选一，不可忽略）**：补进证据表（附来源）或从页面删除。
退出码 1 表示存在未溯源数字，可作交付门禁。

**A2. 图片来源与授权校验（v2.0 新增）**

```bash
# 扫描 manifest，列出缺失授权字段的图片，或直接生成「图片来源」页
python3 scripts/collect-credits.py --manifest slide_manifest.json
python3 scripts/collect-credits.py --manifest slide_manifest.json --format markdown
```
图库图（Pexels/Unsplash/Pixabay）需 `source_url`，多数需 `credit_text`（署名）；
AI 生图需 `generated_by`。**客户/商业交付前必须补齐**。

**B. 视觉项（必须渲染成图看，或交给盲读子 agent）**

```
□ 文字没溢出容器 / 没被裁切  ← 最高频缺陷，优先查
□ 标题匹配已确认故事线（读起来是不是一个结论句）
□ 标签没压住图标/节点/曲线
□ 视觉风格一致（没漂移）
□ 每页有 SO WHAT / 含义块（且区域明显）
□ 留白均衡（不空不挤）
□ 图片质量与风格统一
```

**C. 内容项（人工/模型核对）**

```
□ 数字匹配证据表（有证据表中不存在的数字 = 违规）
□ 标题是结论句而非主题词
□ 演讲者备注已生成且 ≤100 字
```

**QA 深度（按成本选，默认 standard）**

| 档位 | 做什么 | 成本 |
|------|--------|------|
| `fast` | 仅机械项 + 抽 3 页渲染 | 低 |
| `standard`（默认）| 机械项 + 全页渲染 + 逐页看视觉项 | 中 |
| `thorough` | standard + 逐页用户确认门 | 高 |
| `none` | 跳过 QA | — |

> ⚠️ `none` **只能由主人明确要求**，不可自行推断、不可因"赶时间"自动降级。
> 无论砍哪一档，**砍的是成本，不是范围** —— 机械项永远要跑。

#### 步骤 3.5 — 最终合并

**单脚本优先原则（含 chart 时强制）：**
- 含 chart 的 PPT → **必须用单个 pptxgenjs 实例**
- 纯文字 >15 页 → 可以 batch 生成后 zipfile 合并（详见 `references/merge-and-qa.md`）

---

## 🚫 红线

| 绝对禁止 | 原因 |
|----------|------|
| 编造数据/市场规模/调研结果 | 违反咨询基本诚信 |
| **页面上出现证据表中查不到的数字** | 等价于编造；用 `trace-claims.py` 机械校验 |
| **图片来源/授权信息缺失就交付** | 客户场景有合规风险；用 `collect-credits.py` 校验 |
| 用整页截图当PPT背景 | 不可编辑 |
| 把文字烘焙进图片 | 不可编辑 |
| 为可编辑把复杂图表简化成默认图形 | 视觉降级 |
| 一次性生成≥3页终版 | 质量失控 |
| 跳过SO WHAT只放图表 | 咨询PPT必须有含义 |
| 跳过用户确认门 | 流程失控 |
| 把主人的私人/业务 PPT 内容上传到公开项目仓库 | 私人信息绝不外泄 |

反哺项目只沉淀**去内容化的方法论**，绝不携带业务数据/演讲稿/客户信息。

---

## ⚙️ 关键技术参数

```python
P0容差 = 3px（最大6px）    # 标题/主图/SO WHAT/页脚/关键数字
P1容差 = 4px（最大8px）    # 卡片/图标/标签/箭头/表格
P2容差 = 6px（最大12px）   # 装饰线/纹理/背景纹样
LARGE_IMAGE_RATIO = 0.40   # >40%页面面积=大图风险
FULL_SLIDE_IMAGE_RATIO = 0.90
GLOBAL_MIN_FONT_PT = 6.5
```

## 🎨 设计原则（完整版见 references/design-principles.md）

1. **PPTX 优先，可编辑是底线** — 所有文字/图表必须 PowerPoint 可修改
2. **结论先行，SO WHAT 必在** — 每页一个可挑战的判断句标题 + 行动建议
3. **证据驱动，不编造数据** — 每个论点有 Evidence ID，缺失标记"需验证"
4. **视觉服务于内容** — 颜色反映主题，全篇锁定同一视觉系统
5. **克制优于炫技** — 一页一个结论，一个图表一个信息
6. **结构优于装饰** — 靠字号/字体/留白组织信息，不靠阴影/3D/渐变
7. **图文比例按内容定** — 叙事型图多，数据型图精
8. **复杂图表原生重建** — 柱状图用 `'bar'` + `barDir:'col'`
9. **单脚本优先** — 含 chart 时强制单 pptxgenjs 实例
10. **私人材料不反哺** — 只沉淀方法论，不携带业务数据

## 📚 项目文件索引（含**何时读**）

> ⚠️ 不要一次读完所有文件。按"何时读"列，在对应阶段才加载，避免上下文浪费。

### 必读（按阶段）

| 路径 | 说明 | **何时读** |
|------|------|-----------|
| `SKILL.md` | 本技能文件（流程主干） | 全程 |
| `references/palettes.md` | **16+1 种配色代码** | **Phase 2 步骤 2.2 选风格时必读** |
| `references/typography-scale.md` | C0/T1-T14 字体层级 | Phase 2 步骤 2.3 |
| `references/layouts/layout-library.md` | 12 种布局模板库 | Phase 2 步骤 2.4 选布局时 |
| `references/chart-type-anatomy.md` | **pptxgenjs chart 坑 + barDir** | **Phase 3 生成任何含图表的页之前必读** |
| `references/merge-and-qa.md` | **多 batch 合并 + 中文字体双槽位 QA** | **含中文的 deck 交付前必读**；页数 >15 需合并时 |

### 按需读

| 路径 | 说明 | **何时读** |
|------|------|-----------|
| `references/design-principles.md` | 10 条设计原则 | Phase 2 结束前复核一遍 |
| `references/prompt-templates.md` | 各阶段 system prompt 模板 | 需要固定流程话术时 |
| `references/multi-model-guide.md` | 多模型选择指南 | 想按阶段换模型省钱时 |
| `competitive-analysis.md` | 竞品深度对比 | 了解差异化定位时（非执行必需） |

### 脚本

| 路径 | 用途 | 何时用 |
|------|------|--------|
| `scripts/research-topic.py` | Deep Research 多引擎搜索 | Phase 0（材料不全时） |
| `scripts/learn-from-pptx.py` | 从参考 PPTX 提取风格 | Phase 2 步骤 2.0（有参考文件时） |
| `scripts/generate-image.js` | AI 生图（Agnes API） | Phase 3 需要 AI 配图时 |
| `scripts/search-image.py` | 图库搜索（Pexels/Unsplash/Pixabay） | Phase 3 需要照片素材时 |
| `scripts/extract-palette.py` | 从图片/Logo 提取配色 | Phase 2（有品牌色参考时） |
| **`scripts/trace-claims.py`** | **🆕 数字溯源校验（防编造）** | **Phase 3 QA 机械项必跑** |
| **`scripts/collect-credits.py`** | **🆕 图片来源与授权登记** | **交付前必跑（客户/商业场景）** |
| `scripts/generate-sample.js` | 示例 PPT 生成脚本 | 环境验证 / 学习代码结构 |

### 资源

| 路径 | 说明 |
|------|------|
| `assets/palette-samples/` | 16 种风格样张（PNG） |
| `examples/duduppt-sample.pptx` | 示例输出（可直接打开看效果） |
