# 竞品分析 v3 —— GitHub PPT 项目全景对比与升级路线

> 调研日期：2026-10-12
> 调研方式：GitHub API 实测（星数/推送/许可）+ 逐仓库细读 README/结构
> 结论：**有升级空间，方向是补结构性短板（原生深度、可编辑闭环、分发生态），
> 同时放大独有护城河（QA 证据链审计）。**

---

## 一、市场格局（2026-10 实测）

| 梯队 | 项目 | ★ | 形态 | 核心路线 |
|---|---|---|---|---|
| 🥇 统治级 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | **60.4k** | Skill | SVG 中间层 → 原生 PPTX |
| 🥈 头部 | [presenton/presenton](https://github.com/presenton/presenton) | 11.0k | App+API+MCP | Gamma 开源替代 |
| 🥈 头部 | [1weiho/open-slide](https://github.com/1weiho/open-slide) | 9.2k | Skill | 每页 = React 组件 |
| 🥉 强势 | [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent) | 5.1k | Framework+MCP | 学术派"反思式生成"（ACL 2026） |
| 🥉 强势 | dashi-ppt-skill | 4.3k | Skill | "产物即编辑器" |
| 中部 | [johnson7788/MultiAgentPPT](https://github.com/johnson7788/MultiAgentPPT) | 1.6k | 多Agent系统 | A2A+MCP（已停维护） |
| 中部 | [CRui5in/paper-ppt-agent](https://github.com/CRui5in/paper-ppt-agent) | 1.1k | 工作台 | 论文→PPT，Critic 循环 |
| **长尾** | **Shine8592/duduppt（本项目）** | **0** | Skill | 咨询风三阶段 |

其他扫描到的同类（规模较小或停更）：sunbigfly/ppt-agent-skills、
linhut/ppt-studio（PPTD DSL）、xuboboo/apple-keynote-ppt、
zhouzengxian/zhouz-ppt-skill（HTML 演示）、iwbaga724-Hinda/ai-editable-ppt-skill、
LRriver/AIPPT（21★）、bruc3van/bruce-pptx-generator、xiongwenhao112/ppt-template-fill 等。

聚合清单：[ningzimu/awesome-ai-ppt](https://github.com/ningzimu/awesome-ai-ppt)（可作为分发渠道）。

---

## 二、头名 ppt-master 的取胜逻辑（60.4k★ / 10 个月）

duduppt 最直接的对手（同为 Skill 形态、本地生成路线）。细读其 README，赢在四点：

### ① "原生深度"叙事

> "Editable is already table stakes — what sets PPT Master apart is native depth."

交付的不是"能打开的 PPTX"，而是 PowerPoint 对象模型本身：
- 幻灯片母版/版式（`p:sldMaster` / `p:sldLayout` 继承）
- **数据驱动原生图表**（带"编辑数据"的真 Chart 对象）
- OMML 原生公式（PowerPoint 2010+ 可编辑）
- 原生形状 + 调整手柄、转场、动画、旁白
- 公开《PowerPoint↔SVG 映射指南》逐特性记录覆盖度

### ② 四条流水线（不止"从零生成"）

```
新文档→PPT ｜ 从参考稿蒸馏模板 ｜ 填充已有 PPTX（字节级保留设计） ｜ 给成品加动画旁白
```

第三条直接命中"改一个字 = 重做一遍"这个全行业痛点。

### ③ 工程成熟度

- `npx skills add hugohe3/ppt-master` 一键装进任意 Agent
- Claude Code 插件市场收录（`.claude-plugin/marketplace.json`）
- Windows 专版安装文档、FAQ 持续更新
- 图片双通道：AI 生成 + 版权合规网络搜索（自动署名）

### ④ 明确的模型策略与诚实声明

推荐 Kimi K3/Claude + 大上下文；公开声明"工具只拥有工作流，模型决定上限"。

---

## 三、对比矩阵

| 维度 | duduppt | ppt-master | PPTAgent | dashi | presenton |
|---|---|---|---|---|---|
| 咨询方法论（SCR/SO WHAT） | ✅✅ 独有叙事 | ✅ | ✅ 反思式 | ❌ | ❌ |
| **QA 严谨度** | ✅✅ 盲读+断言溯源+qa-compare | ⚠️ 预览页 | ✅ Critic | ❌ | ❌ |
| **CJK 字体处理** | ✅✅ fix-cjk-font | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| 原生图表（可编辑数据） | ❌ 形状拼图 | ✅✅ | ✅ | ❌ | ⚠️ |
| 母版/版式 | ❌ | ✅✅ | ✅ | ❌ | ⚠️ |
| 编辑既有 PPTX | ❌ | ✅✅ | ⚠️ | ❌ | ❌ |
| 公式（OMML） | ❌ | ✅ | ❌ | ❌ | ❌ |
| 转场/动画/旁白 | ❌ | ✅ | ❌ | ⚠️ | ⚠️ |
| 产物即编辑器 | ❌ | ❌ | ❌ | ✅✅ | ✅ App |
| 模板生态 | 8 配色+版式库 | 蒸馏+品牌模板 | 模板路线 | 千套模板 | ✅ |
| 多画幅（小红书等） | ❌ | ✅ 10+ | ❌ | ❌ | ⚠️ |
| MCP 形态 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 学术背书 | ❌ | ❌ | ✅ ACL+HF模型 | ❌ | ❌ |
| 分发（marketplace/收录） | ❌ | ✅✅ | ✅ | ✅ | ✅ |

---

## 四、duduppt 的护城河（升级时绝不丢弃）

"咨询风"本身不是护城河（ppt-master 作者即 CPA/咨询工程师）。真正的差异是：

1. **盲读验收**（`references/blind-read-prompt.md`）—— 不看原稿只看成品检验信息传达，
   传播学级 QA，无竞品做到
2. **断言溯源**（`scripts/trace-claims.py`）—— 每页 SO WHAT 追溯证据源，防 AI 编数
3. **qa-compare 双版本对比** —— 迭代不回退的保障

**品牌定位建议**：*"唯一带证据链审计的咨询级 PPT 生成器"*。
在 AI 幻觉焦虑的环境下，"每个数字都能溯源"是能立住的口号。

---

## 五、升级路线（按性价比排序）

### 🔴 P0 —— 不做就出局

| # | 升级项 | 学谁 | 工作量 | 说明 |
|---|---|---|---|---|
| 1 | **一键分发**（`npx skills add` 兼容） | ppt-master | 小 | 0★ 的核心原因是分发不是质量 |
| 2 | **原生图表+母版版式** | ppt-master | 大 | pptxgenjs 天花板所在，需评估 SVG→OOXML / python-pptx 路线 |
| 3 | **编辑既有 PPTX** | ppt-master | 大 | 全行业最大痛点 |

### 🟡 P1 —— 拉开差异

| # | 升级项 | 说明 |
|---|---|---|
| 4 | QA 审计报告外化 | 盲读/溯源/对比结果生成《质量审计报告》随交付 —— 让差异"被看见" |
| 5 | 静态 Critic 检测 | 学 paper-ppt-agent（装饰遮挡、低对比度），保留人工验收门 |
| 6 | 版本快照 | 每次迭代自动归档，支持回溯 |
| 7 | 多画幅 | 小红书 3:4、公众号 9:16 —— 中文场景刚需 |

### 🟢 P2 —— 锦上添花

| # | 升级项 | 说明 |
|---|---|---|
| 8 | OMML 公式 | 学术场景 |
| 9 | 转场/动画/旁白 | ppt-master 深耕区，跟随成本高 |
| 10 | MCP server 形态 | 复用 duduExcel 架构经验，把 QA 三件套做成可复用工具 |

---

## 六、执行节奏

```
第一步（1-2 周）：分发先行
  ├─ 兼容 npx skills add（目录结构 + 元数据）
  ├─ 提交 datawhalechina/ai-skills-for-everyone 收录
  └─ 提交 ningzimu/awesome-ai-ppt 清单

第二步（2-4 周）：放大护城河
  ├─ QA 审计报告外化
  ├─ 静态 Critic 检测
  └─ 版本快照

第三步（长期）：啃硬骨头
  ├─ 原生图表/母版（SVG→OOXML 管线评估）
  └─ 编辑既有 PPTX（字节级保留设计）
```

**战略**：不对标 ppt-master 的 60k★（全职+赞助投入）。差异化定位：
它卷"原生深度"，duduppt 卷"可信度"。

---

## 附：数据快照

```
hugohe3/ppt-master        ★60368  MIT      Python   2025-12 创建，持续推送
presenton/presenton       ★11045  Apache   TS       持续推送
1weiho/open-slide         ★9178   MIT      TS       持续推送
icip-cas/PPTAgent         ★5099   MIT      Python   持续推送
johnson7788/MultiAgentPPT ★1641   MIT      Python   2026-07 后停推
CRui5in/paper-ppt-agent   ★1064   AGPL     Python   2026-08 后停推
Shine8592/duduppt         ★0      MIT      Python   本项目
```

（数据采集于 2026-10-12，GitHub API）
