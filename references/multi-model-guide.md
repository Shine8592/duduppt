# duduppt 多模型配置指南

> 不同 PPT 制作阶段对模型能力要求不同。合理选择模型 = 更快 + 更省 + 更好。
> BYOK 理念：Bring Your Own Key，按需切换。

---

## 模型选择原则

| 阶段 | 需要的能力 | 推荐模型类型 | 理由 |
|------|-----------|-------------|------|
| **Phase 0: Research** | 信息检索 + 摘要 | 便宜/快速（如 DeepSeek V3 Flash, Gemini 2.0 Flash） | 大量搜索+处理，token 消耗大，不需要深度推理 |
| **Phase 1: 分析** | 结构化提取 + 逻辑推理 | 中等（如 Claude Sonnet, GPT-4o-mini） | 建证据表需结构化输出，需要一定推理 |
| **Phase 2: 蓝图** | 创意设计 + 审美判断 | **高质量**（如 Claude Sonnet 4, GPT-4o, Gemini 3.1 Pro） | 视觉设计是创意工作，审美判断需最强模型 |
| **Phase 3: 生成** | 代码生成 + 调试 | 中等偏强（如 Claude Sonnet, DeepSeek V4） | 写 pptxgenjs 代码需准确性，但不需要最强创意 |

---

## 在 Hermes 中切换模型

### 方法 1：对话中临时切换

```
/use openrouter/anthropic/claude-sonnet-4      # 切换到最强模型做视觉设计
# ... 做完 Phase 2 ...
/use openrouter/deepseek/deepseek-v4-flash      # 切回快速模型做生成
```

### 方法 2：Phase 前置提示（推荐）

在进入每个阶段时，在 prompt 开头指定模型偏好：

```
[模型建议: 当前进入 Phase 2 视觉蓝图阶段，建议使用高质量模型]
请设计 8 种视觉风格中的一种，并描述逐页布局...
```

### 方法 3：子代理隔离（Hermes 高级用法）

```python
# Phase 1 用快速模型做分析
delegate_task(goal="分析材料建证据表", model="fast")
# Phase 2 用强模型做设计
delegate_task(goal="设计视觉蓝图", model="best")
```

---

## 推荐模型组合（省钱方案）

| 预算 | Research | 分析 | 蓝图 | 生成 |
|------|----------|------|------|------|
| 💰 **省钱** | DeepSeek V3 Flash | DeepSeek V3 Flash | Claude Sonnet 4 | Gemini 2.0 Flash |
| 💰💰 **均衡** | Gemini 2.0 Flash | Claude Sonnet | Claude Sonnet 4 | Claude Sonnet |
| 💰💰💰 **顶配** | GPT-4o-mini | Claude Sonnet 4 | Claude Sonnet 4 + vision | GPT-4o |

---

## 注意事项

1. **模型切换不丢上下文** — Hermes 保持对话历史，换模型只是换推理引擎
2. **代码生成阶段**避免用纯推理模型（如 DeepSeek R1）— 它们擅长推理但代码输出格式不稳定
3. **视觉判断**永远用带 vision 的模型 — Phase 2/3 需要"看图说话"能力
4. **不改技能内容** — 模型选择是运行时决策，不写死在 SKILL.md 中
