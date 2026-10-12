# duduppt

> **Consulting-grade PPTX generation with an auditable evidence chain.**
> A skill for AI agents — not just page layout, but verifiable claims.

[中文 README](README.md) · [Quick Start (中文)](skills/duduppt/docs/QUICKSTART.md) · [Competitive Analysis](competitive-analysis-v3.md)

---

## What it is

duduppt turns documents, data, or ideas into high-density consulting-style
`.pptx` decks. What sets it apart from other AI PPT tools is not layout —
it is **auditability**:

- **Blind-read review** — verify a slide communicates without seeing the source
- **Claim tracing** — every number in the deck traces back to an evidence file
- **Quality audit report** — a deliverable alongside the PPTX (JSON + Markdown)
- **Version snapshots** — archive each iteration, restore any previous version

Where most AI PPT tools optimise for "looks good", duduppt optimises for
"**can be defended**".

## Who it's for

- People who need numbers in their deck to hold up under questioning
- Consultants, analysts, finance and strategy roles
- Chinese-language users (built-in CJK font slot handling)
- Anyone tired of "change one word" meaning "regenerate the whole deck"

## Install

```bash
# Any agent CLI (Claude Code, Codex, Cursor, OpenCode, ...)
npx skills add Shine8592/duduppt

# Or via the Claude Code plugin marketplace
/plugin marketplace add Shine8592/duduppt
/plugin install duduppt@duduppt
```

Then install dependencies:

```bash
pip install python-pptx Pillow     # QA, editing, and master-layout scripts
npm install pptxgenjs              # generation engine
```

**Requirements**: Python 3.10+, Node.js 18+, and any agent that can read/write
files and run commands.

## Usage

Just tell your agent:

> "Turn this report into a 10-page consulting deck. Every figure must be
> traceable to the source, and include a quality audit report."

The agent follows the four-phase workflow in `skills/duduppt/SKILL.md`:

| Phase | What happens |
|---|---|
| 0 · Deep Research | Fill evidence gaps via multi-engine search |
| 1 · Evidence Analysis | Extract claims, data points, confidence levels |
| 2 · Visual Blueprint | Choose layout + style per page |
| 3 · Generate + QA | Build PPTX, then run the QA pipeline |

## The QA pipeline (the difference)

```bash
# Mechanical checks — 11 lint rules, zero dependencies, seconds
python skills/duduppt/scripts/qa-check.py --deck output.pptx

# Full audit report — blind-read + claim tracing + mechanical + version diff
python skills/duduppt/scripts/qa-report.py --deck output.pptx \
    --evidence evidence.json
```

**11 lint rules**: structure · placeholder text · charts · CJK font slot ·
font whitelist · language metadata · full-page images · font size ·
text overflow · element overlap · contrast.

## Scripts

| Script | Purpose |
|---|---|
| `qa-check.py` | Mechanical checks (11 rules, zero deps) |
| `qa-report.py` | Quality audit report (JSON + Markdown) |
| `trace-claims.py` | Trace numbers back to evidence (anti-fabrication) |
| `qa-compare.py` | Blind-read vs. manifest consistency |
| `fix-cjk-font.py` | Fix CJK East-Asian `<a:ea>` font slots |
| `snapshot.py` | Version archive / list / restore / diff |
| `edit-deck.py` | Edit existing PPTX (text, chart data, add/remove slides) |
| `native-charts.py` | Native OOXML charts with "Edit Data" |
| `build-master.py` | Compile a style into real `sldLayout` template |
| `retemplate.py` | Restyle a whole deck in one pass |
| `canvas-formats.py` | 9 canvas formats (16:9, Xiaohongshu 3:4, WeChat 9:16, A4, ...) |
| `omml-formula.py` | Native OMML math formulas |
| `mcp_server.py` | MCP server exposing 8 QA/utility tools |

Full list and usage: `skills/duduppt/SKILL.md`.

## Honest limitations

- **Star count is 0** — this is a new project (created 2026-07); the value is
  in the methodology, not popularity.
- Requires Python + Node.js and an agent tool — **not** a web app.
- Output quality depends on your model (the workflow sets the floor, the model
  sets the ceiling).
- Complex animations, transitions, and SmartArt are **not** supported.
- **"Change the master, whole deck follows" is not fully true**: real PowerPoint
  master inheritance depends on `theme1.xml`'s `fontScheme`, which `python-pptx`
  supports only weakly. Use `retemplate.py` for whole-deck restyling instead.

## Risks

- Do not send confidential or personal material to external models.
- Respect copyright when using reports, images, or web content
  (`collect-credits.py` helps track image attribution).
- **Always review the numbers yourself** — the tool flags whether a figure is
  traceable, but it cannot judge whether the conclusion is right.
- For commercial use, keep the MIT copyright and licence notice.

## Project layout

```
skills/duduppt/          ← the Skill (installable unit)
├── SKILL.md             workflow and rules
├── references/          9 reference docs (layouts, palettes, blind-read, ...)
├── scripts/             20+ scripts
├── docs/                QUICKSTART, SUBMISSION
├── examples/            sample deck + master template
└── assets/              palette samples
tests/                   self-checks (structure, MCP e2e, master)
competitive-analysis-v3.md
```

## Licence

MIT.
