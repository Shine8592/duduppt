# duduppt 竞品深度对比分析

> 分析时间：2026-07-24
> 对标项目：Presenton (9.1k⭐) / PPTAgent-DeepPresenter (4.8k⭐) / ALLWEONE (3.2k⭐)

---

## 一、项目概览

| 维度 | duduppt | Presenton | PPTAgent/DeepPresenter |
|------|---------|-----------|----------------------|
| **Stars** | <10 | **9,100** ⭐ | **4,800** ⭐ |
| **定位** | AI Agent PPT技能（Hermes） | 开源 AI PPT 生成器 + API | Agentic 反射式 PPT 生成框架 |
| **技术栈** | Markdown skill + pptxgenjs | TypeScript 56% + Python 37% | Python 71% + JS 20% |
| **部署方式** | Hermes Agent 内运行 | Docker / Electron 桌面 App | Docker Compose / CLI |
| **许可** | MIT | Apache 2.0 | MIT |
| **核心优势** | 方法论深度、质量门禁 | 模板系统、BYOK、API | Deep Research、Sandbox、论文级 |
| **论文发表** | 无 | 无 | EMNLP 2025 + ACL 2026 |

---

## 二、深度对比矩阵

### 2.1 方法论与内容质量

| 能力 | duduppt | Presenton | PPTAgent | 胜负 |
|------|---------|-----------|----------|------|
| **叙事框架** | SCR（Situation→Complication→Resolution）✅ | 模板驱动，无固定叙事 | 反射式生成，无固定框架 | **duduppt胜** |
| **证据管理** | 证据表（ID/来源/置信度/Caveat）✅ | 无显式证据管理 | Deep Research 自动搜集 | **平**（方向不同） |
| **结论先行** | 强制每页强标题 + SO WHAT ✅ | 无强制 | 无强制 | **duduppt胜** |
| **故事线脑暴** | 2-3 条可选方向 + 用户确认 ✅ | 无 | Agent 自动决策 | **duduppt胜** |
| **内容研究深度** | 手动/依赖搜索技能 | 浅层 web 搜索 | **Deep Research 引擎**（多源自动搜集+合成）| PPTAgent 胜 |
| **多源输入** | 文字/文档输入 | **PDF/DOCX/PPTX/CSV** 多格式 | **DOC/PDF/URL/参考PPT** | Presenton/PPTAgent 胜 |
| **数据可视化** | 图表类型坑已排查（barDir 修复）✅ | 模板内置图表 | Free-Form 布局 | **平** |

**duduppt 的方法论在叙事逻辑上碾压竞品。** Presenton 和 PPTAgent 都缺少 SCR 论证框架、证据表、SO WHAT 强制要求。但 PPTAgent 的 Deep Research 引擎是我们要学习的方向。

### 2.2 视觉设计能力

| 能力 | duduppt | Presenton | PPTAgent | 胜负 |
|------|---------|-----------|----------|------|
| **风格数量** | 8+1 种预设（含清新高客风）✅ | 基于模板，数量不限 | Free-Form（无模板约束）| 方向不同 |
| **从参考PPT学习** | ❌ 无 | **✅ 上传 PPTX/PDF → AI 学习模板** | ✅ 参考 Presentation 输入 | **Presenton 大胜** |
| **字体体系** | C0-T14 十五级字体层级 ✅ | 基于模板 | 无固定体系 | **duduppt胜** |
| **图片生成** | Agnes API（单源） | **多源：Pexels/Pixabay/DALL-E/Gemini** | 内置 T2I 模型 | Presenton 胜 |
| **配色提取** | 从参考图/Logo 提取 ✅ | 从模板自动继承 | Free-Form | 平 |
| **布局模板库** | 蓝图描述（文字）| **layouts.json 可复用模板** | Agent 自由创作 | Presenton/PPTAgent 胜 |
| **视觉检查** | 子代理视觉 QA ✅ | 无自动检查 | 环境反射循环 | duduppt 胜 |

**Presenton 的"从已有 PPTX 学习模板"能力是 duduppt 最大的功能缺口。** 我们现在只有 8+1 种手动选择的风格，如果能"喂一个参考 PPTX → 自动提取配色/字体/布局模式"，体验会飞跃。

**PPTAgent 的 Free-Form 设计**：不受模板约束的灵活布局，适合创意型 PPT。但缺点是缺乏一致性（每页可能风格漂移）。

### 2.3 工程化与质量保障

| 能力 | duduppt | Presenton | PPTAgent | 胜负 |
|------|---------|-----------|----------|------|
| **QA 检查清单** | 15 项全覆盖 ✅ | 无（依赖用户检查）| 反射式自评估 | **duduppt 大胜** |
| **渲染 QA** | LibreOffice/zipfile 双兜底 ✅ | 内置渲染引擎 | 自动反射修正 | duduppt 胜 |
| **图表兼容性** | barDir 坑已排查 ✅ | 未知（封闭格式）| 未知 | duduppt 胜 |
| **中文字体** | WenQuanYi 绑定 + 检查 ✅ | 未知 | 未知（中文案例有）| **duduppt 独有优势** |
| **合并脚本** | zipfile 无损合并 + 校验 ✅ | 不适用（单文件输出）| 不适用 | duduppt 胜 |
| **错误处理** | 零依赖兜底 QA ✅ | Docker 依赖 | Docker 依赖 | **duduppt 胜** |
| **私人材料保护** | 硬编码红线，不上传公开仓库 ✅ | 自部署可控 | 自部署可控 | 平 |

**质量保障是 duduppt 最强的护城河。** 15 项 QA 清单、零依赖结构检查、中文字体绑定检查——这些竞品都没有。这是我们的差异化核心。

### 2.4 技术架构与集成

| 能力 | duduppt | Presenton | PPTAgent | 胜负 |
|------|---------|-----------|----------|------|
| **模型支持** | Hermes 当前模型（单模型）| **BYOK：Ollama/OpenAI/Gemini/Claude 等全部主流** | 需部署 DeepPresenter-9B 微调模型 | **Presenton 大胜** |
| **API 接口** | ❌ 无 | **✅ REST API（生成/编辑/导出）** | CLI + MCP Server | Presenton 胜 |
| **MCP 协议** | ❌ 无 | ❌ 无（但有 Docker） | **✅ MCP Server** | PPTAgent 胜 |
| **Agent Sandbox** | ❌ 无 | ❌ 无 | **✅ 隔离执行沙箱（30+ 工具）** | PPTAgent 胜 |
| **CI/CD** | 无 | ✅ | ✅ (pre-commit) | 平（Hermes 场景不需要） |
| **自部署** | ❌（Hermes 内运行）| **✅ Docker / 桌面 App** | **✅ Docker Compose** | 竞品胜 |
| **离线运行** | ✅（Hermes 本地）| ✅（Ollama + 离线模式）| ✅（设置 offline_mode）| 平 |

**duduppt 作为 Hermes 技能，天生是 agent-native 的**，这是跟 Presenton（Web App）和 PPTAgent（CLI/Docker）的根本区别。我们的优势是"一句话就让 AI 帮你做 PPT"，无需部署、无需开网页。

但 Presenton 的 **BYOK（Bring Your Own Key）多模型支持** 是值得借鉴的——不同阶段可以用不同模型。

### 2.5 用户体验

| 能力 | duduppt | Presenton | PPTAgent | 胜负 |
|------|---------|-----------|----------|------|
| **交互方式** | 自然语言对话 ✅ | Web UI + API | CLI + Web UI | 各有优势 |
| **实时预览** | ❌ 无 | **✅ Web 实时预览** | ✅ WebUI (Gradio) | 竞品胜 |
| **逐页确认** | 三阶段确认门 ✅ | ❌ 无确认机制 | Agent 自主决策 | **duduppt 大胜** |
| **学习成本** | 极低（会说话就行）✅ | 需了解 Web UI | 需了解 CLI | **duduppt 胜** |
| **迭代修改** | 对话式修改 ✅ | Web 编辑器修改 | 重新生成 | duduppt 胜 |
| **进度透明** | 三阶段进度汇报 ✅ | 黑盒生成 | 终端日志 | duduppt 胜 |

---

## 三、竞品最大优势提炼

### 🏆 Presenton 的 3 个核心优势

1. **模板学习引擎** — 上传 PPTX/PDF → AI 提取设计系统（配色/字体/布局）→ 新内容自动套用。这是 duduppt 最缺的能力
2. **BYOK 多模型支持** — 用户自由选择 Ollama/OpenAI/Gemini/Claude，无供应商锁定。duduppt 绑死 Hermes 当前模型
3. **REST API** — 可嵌入其他系统/工作流。duduppt 只能通过 Hermes 对话调用

### 🏆 PPTAgent/DeepPresenter 的 3 个核心优势

1. **Deep Research 引擎** — 多源自动搜索 → 内容合成 → 引用标注。duduppt 的证据表要主人手动提供或我手动搜
2. **Agent Sandbox（30+ 工具）** — 在隔离沙箱中执行代码、生成图片、处理数据。duduppt 没有沙箱
3. **Fine-tuned 模型（DeepPresenter-9B）** — 专门为 PPT 生成微调。duduppt 依赖通用模型

### 🏆 ALLWEONE 的亮点

1. **Web 端实时生成体验** — 用户边看边调，所见即所得。duduppt 缺预览

---

## 四、duduppt 的差异化优势（不可替代）

| 优势 | 说明 | 竞品能否复制 |
|------|------|------------|
| **SCR 叙事框架** | 从 Situation → Complication → Resolution 构建说服链 | 可以，但需大量 prompt 工程 |
| **15 项 QA 清单 + 零依赖检查** | zipfile 级别 QA，不需要任何第三方工具 | 可以，但没人做 |
| **中文字体原生支持** | QA 阶段自动检查中文字体绑定 | Presenton 不关注中文场景 |
| **结论先行 + SO WHAT 强制** | 每页必须有可挑战的强标题 | Presenton 没有这个设计哲学 |
| **三阶段确认门** | 主人可在每个阶段介入调整方向 | Agent 原则上是自主的 |
| **逐页交付** | 一页做完→确认→下一页，不批量 | 所有竞品都是批量生成 |
| **Hermes Agent 原生** | 对话中一句话触发，无需开网页/部署 | Presenton 是 Web App，不是 agent |
| **私人材料红线** | 自动识别业务内容，阻止上传公开仓库 | 不是 feature，是 policy |

---

## 五、升级建议（按优先级排序）

### P0 — 必须升级

| # | 升级项 | 灵感来源 | 具体做法 | 难度 |
|---|--------|---------|---------|------|
| 1 | **从参考 PPTX 学习模板**（Template Learning） | Presenton | 新增脚本 `scripts/learn-template.py`：读取参考 PPTX → 用 zipfile 分析配色/字体/布局比例 → 输出 style config | 中 |
| 2 | **Deep Research 阶段 0** | PPTAgent | 在 Phase 1 之前加 Research Phase：自动搜索补充证据表的数据缺口，搜索策略参考 china-briefing 的多引擎搜索 | 低-中 |
| 3 | **多模型配置指南** | Presenton BYOK | 在 SKILL.md 中新增"模型选择建议"章节：便宜模型做证据提取，高质量模型做视觉蓝图，当前模型做 PPTX 生成 | 低 |

### P1 — 重要升级

| # | 升级项 | 灵感来源 | 具体做法 | 难度 |
|---|--------|---------|---------|------|
| 4 | **布局模板库**（Layout Library） | Presenton layouts.json | 创建 `references/layouts/` 目录，收录 10+ 可复用布局（封面、目录、对比页、时间线、数据页、流程页等），每布局含蓝图描述 + pdf/jpg 样张 | 中 |
| 5 | **多来源图片** | Presenton 多图片源 | 扩展图片生成：除 Agnes 外增加 Pexels/Pixabay 免费图库搜索（用 curl + API），按内容主题自动选图 | 低 |
| 6 | **参考 PPT 风格提取** | Presenton + 配色提取 | 新增 `scripts/analyze-pptx-style.py`：读取参考 PPTX → 输出风格报告（色板、字体、布局类型、页数、图片比例） | 中 |

### P2 — 锦上添花

| # | 升级项 | 灵感来源 | 具体做法 | 难度 |
|---|--------|---------|---------|------|
| 7 | **PPT 生成 API 入口** | Presenton REST API | 在 Hermes 中注册为 tool，允许 cron 任务/其他技能调用 | 中 |
| 8 | **HTML 预览** | ALLWEONE | 生成 PPTX 的同时生成 HTML 预览版本（方便主人快速过内容） | 中 |
| 9 | **MCP Server 适配** | PPTAgent MCP | 将 duduppt 暴露为 MCP 服务，其他 agent 可调用 | 高 |
| 10 | **LLM 提示词模板库** | PPTAgent fine-tune | 为不同任务（证据提取、故事线生成、蓝图描述、代码生成）创建专用 system prompt 模板 | 低 |

---

## 六、总结

### duduppt 的核心竞争力不在功能多，而在深度

- **叙事深度**（SCR + SO WHAT + 证据表）— 竞品没有
- **质量深度**（15 项 QA + 零依赖检查 + 中文字体）— 竞品没有
- **交互深度**（三阶段确认 + 逐页交付）— 竞品没有

### 最值得优先做的 3 件事

1. **从参考 PPTX 学习模板** — 最大功能缺口，主人说"按这个风格做"时能直接理解
2. **Deep Research 阶段 0** — 让证据表不再依赖主人提供完整材料
3. **布局模板库** — 让蓝图阶段从"文字描述"升级为"选模板 + 微调"

> duduppt = 咨询方法论（SCR + 证据表 + 质量门禁）× Hermes Agent 原生交互
> 
> 竞品 = 功能堆砌 × Web/API 界面
>
> 我们要的不是堆功能，而是让方法论更深、质量更高、交互更顺。
