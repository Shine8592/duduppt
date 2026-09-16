# 📢 duduppt 提交文案（Skill 生态目录）

> 面向 Agent Skill 目录与相关渠道的现成文案。
>
> ⚠️ 注意：duduppt 是 **Skill** 不是 **MCP server**。很多 MCP 目录（glama/mcp.so）
> 只收 MCP server，不接受纯 Skill。请提交到下面这些**接受 Skill** 的渠道。

---

## 项目现成信息

| 字段 | 值 |
|---|---|
| Name | `duduppt` |
| Type | Agent Skill (SKILL.md + scripts) |
| Repository | `https://github.com/Shine8592/duduppt` |
| License | MIT |
| Version | 2.0.0 |
| Language | Markdown (SKILL.md) + Python + JavaScript |
| 依赖 | 无必需依赖；pptxgenjs / LibreOffice / python-pptx 按需 |

**Short description（≤120 字符）**
```
Consulting-grade PPTX skill for AI agents: SCR narrative, evidence-table driven, 16+1 styles, native editable PPTX.
```
*(114 字符)*

**One-line pitch**
```
Most PPT tools give you HTML slides or screenshots. duduppt gives you native .pptx where
every character, number and chart stays editable in PowerPoint — with an auditable evidence trail.
```

---

## 长描述（可直接复制）

```
duduppt — Consulting-grade PPTX generator Skill for AI agents

duduppt turns documents, data and rough ideas into high-density consulting-style decks,
and outputs NATIVE EDITABLE .pptx — not HTML slides, not screenshots. Every text run,
number and chart stays editable in PowerPoint.

FOUR-PHASE PIPELINE

  Phase 0  Deep Research    Auto-fill evidence gaps when material is incomplete
  Phase 1  Analysis         Evidence table + story line + per-page outline   [gate]
  Phase 2  Visual Blueprint Style + layout + image plan                      [gate]
  Phase 3  PPTX + QA        Per-page generation, QA, then merge

Each phase ends with a confirmation gate — you never burn 30 slides on a wrong direction.

CORE CAPABILITIES

- SCR narrative (Situation -> Complication -> Resolution), consulting-grade argumentation
- Evidence table: every claim carries ID / value / unit / period / source / confidence / caveat
  — missing data is marked "needs verification", never fabricated
- 16+1 visual styles, from classic deep-red consulting to fresh high-end; brand-color extraction
- 15-level typography scale (C0 + T1-T14), aligned with MBB consulting standards
- 12 layout templates: cover / TOC / comparison / timeline / data / matrix ...
- Design interview: 5 questions before picking a style — no blind recommendations
- Image pipeline: AI generation + free stock (Pexels/Unsplash/Pixabay) + palette extraction
- Speaker notes auto-generated: 60-100 chars, spoken-style hints (not a script)
- Per-page confirmation: generate, QA and confirm one page at a time

MECHANICAL QA (zero-dependency, milliseconds)

- qa-check.py     : structure, placeholders, chart barDir, CJK font slots, font sizes
- fix-cjk-font.py : fixes the <a:ea> East-Asian font slot that pptxgenjs cannot set
- trace-claims.py : extracts every number from the deck and flags any NOT found in the
                   evidence table ("UNTRACED: slide7 42%") — makes "never fabricate" computable
- collect-credits.py : audits image sources and licenses; generates an Image Credits page
- qa-compare.py   : compares a blind-reader sub-agent's report against the manifest, to catch
                   "the conclusion never made it onto the slide"

WHY IT'S DIFFERENT

- Native PPTX is the bottom line: HTML-slide tools can't be edited in PowerPoint
- Mechanical vs visual QA are separated — don't spend a render round on what a lint can decide
- CJK-aware: validates the East-Asian font slot (<a:ea>), the slot where most tools silently fail
- Privacy red line: private/business material never flows back into the public repo

HONEST LIMITATIONS

- Visual QA needs LibreOffice to render slides to images (mechanical checks are zero-dependency)
- Font embedding: PowerPoint can embed fonts, but pptxgenjs/python-pptx cannot —
  recipients need the CJK font installed
- Decks containing charts must be generated with a single pptxgenjs instance

LINKS
  GitHub: https://github.com/Shine8592/duduppt
  License: MIT
```

---

## 🎯 提交渠道（接受 Skill 的）

| 渠道 | 入口 | 说明 |
|---|---|---|
| **gradually.ai Skills** | https://www.gradually.ai/en/claude-code-skills | 746+ skills 目录，接受提交 |
| **Claude Directory** | https://claudedirectory.org | Skills 专区，有 pptx 分类 |
| **claude-office-skills**（社区）| https://github.com/claude-office-skills/skills | 可提 PR 加入 office 类技能 |
| **Awesome Claude Skills** | 搜 "awesome-claude-skills" | 社区列表，提 PR |
| **skillhub / skills.sh** | 视其提交入口 | Skill 聚合站 |
| **LobeHub Skills**（若开放）| https://lobehub.com | 原为 MCP，逐步支持 skills |

> **不要提交到**：glama.ai / mcp.so / PulseMCP —— 这些是 **MCP server** 目录，
> duduppt 是 Skill，类型不符会被拒。

---

## PR 提交文案（用于 awesome 类列表 / claude-office-skills）

**PR 标题**
```
Add duduppt - Consulting-grade PPTX generator skill (native editable PPTX + evidence auditing)
```

**PR 条目（markdown）**
```markdown
- [duduppt](https://github.com/Shine8592/duduppt) - Consulting-grade PPTX generator skill:
  four-phase pipeline (research -> analysis -> visual blueprint -> PPTX + QA), SCR narrative,
  evidence-table driven (never fabricates data), 16+1 visual styles, 15-level typography,
  and NATIVE EDITABLE .pptx output. Includes mechanical QA scripts for chart pitfalls,
  CJK font slots, number-tracing against the evidence table, and image-license auditing.
  `markdown` `python` `javascript` `mit`
```

**PR 描述**
```markdown
## What is duduppt?

An Agent Skill that turns documents, data and ideas into consulting-style decks with an
auditable evidence trail, outputting **native editable .pptx** (not HTML slides, not screenshots).

## Why it belongs in this list

Most PPT skills either produce HTML sliders or rely on the model writing generation code
ad-hoc. duduppt is different in three ways:

1. **Native PPTX is the bottom line** — every character, number and chart stays editable.
2. **Evidence discipline is mechanical, not aspirational** — `trace-claims.py` extracts every
   number from the deck and flags any absent from the evidence table.
3. **CJK-aware** — validates the `<a:ea>` East-Asian font slot, where most tools silently fail
   (a font name written into the Latin slot never applies to Chinese text).

## Quality signals

- ✅ CI green: Ubuntu + Windows x Python 3.10/3.11/3.12
- ✅ `tests/test_structure.py`: 20 checks incl. reference-integrity and CJK slot unit tests
- ✅ MIT licensed, has CHANGELOG and a 5-page sample deck
- ✅ Zero mandatory dependencies

## Honest limitations

- Visual QA needs LibreOffice (mechanical checks are zero-dependency)
- No font embedding (a pptxgenjs/python-pptx limitation)
- Chart-containing decks need a single generation instance
```

---

## 标签建议

- **Category**: Productivity · Presentations · Office Automation
- **Tags**: `pptx` `powerpoint` `claude-skill` `agent-skill` `presentation` `consulting`
  `deck-generator` `pptxgenjs` `chinese` `slide-deck`

---

## 最该做的一件事（比铺渠道更有效）

**把 `examples/duduppt-sample.pptx` 的截图放进 README。**

Skill 类项目**全靠图文说服** —— 现在 README 是纯文字。做法：

```bash
# 1. 渲染示例为图片（需 LibreOffice）
soffice --headless --convert-to pdf examples/duduppt-sample.pptx
pdftoppm -jpeg -r 150 duduppt-sample.pdf slide

# 2. 挑 2-3 张有代表性的（如：结论先行页、数据图表页）
# 3. 放进 README 的「核心能力」上方
```

> 一张好截图的效果 > 提交 5 个目录。
