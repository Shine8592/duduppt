# 盲读 QA Prompt（给子 agent 用）

> **用途**：把渲染好的 slide 图片交给一个**不带任何上下文**的子 agent，让它只凭图片回答固定问题。
> 然后用 `scripts/qa-compare.py` 把它的回答与 `slide_manifest.json` 做机器比对。
>
> **为什么必须"盲"**：一个已经看过设计意图的读者，会在图片里"看到"他想看到的东西，
> 即使图片根本没表达出来。只有盲读者才能暴露"结论没讲出来 / 页面重复 / 元素看不清"。

---

## 调用方式

1. 先渲染所有页面为图片（见 SKILL.md Phase 3 步骤 3.2）：
   ```bash
   soffice --headless --convert-to pdf deck.pptx
   pdftoppm -jpeg -r 150 deck.pdf slide
   ```
2. **开一个新会话 / 子 agent**（关键：不要带 deck 的设计上下文）
3. 把下面的 prompt 原样交给它，并**一次性附上所有 slide-*.jpg**
4. 收集它输出的 JSON，存为 `blind_read.json`
5. 跑比对：
   ```bash
   python3 scripts/qa-compare.py --blind blind_read.json --manifest slide_manifest.json
   ```

---

## 给子 agent 的 Prompt（整段复制）

```
你是一名第一次看到这份演示文稿的读者。你只会拿到一串幻灯片图片。

【硬规则】
1. 只看图片。不要打开任何其他文件（.json / .py / .md），不要列目录猜主题。
   违反此规则，本次结果作废，必须换一个全新的读者重做。
2. 不要猜测。读不出来的文字放进 unreadable，**不要猜**。
   猜出来的字符串比留空更糟——它会把一个缺陷报告成"已修复"。
3. 每页都要回答，即使看起来是空白页或过渡页。

【对每一页，回答以下 7 个问题】
- n            : 页码（从 1 开始）
- claim        : 这一页想让读者记住的**一句话**是什么？（用你自己的话，不是照抄标题）
- about        : 这一页"关于什么"（3-5 个字，如"市场规模""竞争格局"）
- largest      : 页面上视觉面积最大的元素是什么？（如"图表""大数字""一段文字""一张照片"）
- elements     : 页面上有哪些元素类型？从这些里选：
                 chart / table / big_number / bullets / photo / icon / diagram / quote
- legible_text : 你**能一眼读清**的文字（原文照抄，最多 5 条）
- unreadable   : 你**看不清或读不出**的文字/元素（有多少写多少；没有就空数组）
- problems     : 你注意到的排版问题（文字溢出/重叠/被裁切/空白异常/风格突兀等）

【最后额外回答】
- style_consistent : 整份 deck 看起来是同一个设计系统吗？（true / false）
- any_blank        : 有没有整页空白或明显缺内容的页？（列出页码）

【输出格式】只输出 JSON，不要解释：
{
  "slides": [
    {"n": 1, "claim": "...", "about": "...", "largest": "...",
     "elements": ["..."], "legible_text": ["..."],
     "unreadable": [], "problems": []}
  ],
  "style_consistent": true,
  "any_blank": []
}
```

---

## 为什么这样设计（供维护者参考）

| 设计 | 理由 |
|---|---|
| `claim` 用**自己的话**而非照抄 | 照抄标题无法判断"结论是否传达"；用自己的话才能暴露"标题和内容脱节" |
| `about` 只有 3-5 字 | 用来检测**跨页重复**——两页 about 相同说明它们讲的是同一件事 |
| `legible_text` 限定 5 条 | 强迫读者只报告"一眼能读清"的，避免把"努力辨认"也算通过 |
| `unreadable` 明确"不许猜" | 防止把缺陷粉饰成已修复 |
| `problems` 允许空 | 不制造假问题 |
| 只看图片 | 防止"知情读者"脑补出图片里没有的信息 |

---

## 比对会得到什么（见 qa-compare.py）

- **claim 覆盖率低** → 这些页的结论没传达给读者
- **about 跨页重复** → 页面冗余
- **unreadable 非空** → 有元素读者看不清
- **any_blank / style_consistent** → 结构性问题
- **problems 非空** → 需逐条响应（改稿 或 说明为何是误报）

> ⚠️ 比对给出的是**差异**，不是判决。每条差异都必须**书面响应**（改了什么 / 为何是误报），
> 不允许"看到了但忽略"。
