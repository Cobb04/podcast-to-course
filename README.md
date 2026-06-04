# Podcast-to-Course

> Turn any podcast transcript into reusable AI judgment assets — framework cards, decision checklists, interview talking points, and an interactive HTML course.

This is a Claude Code / Codex skill. It does NOT summarize podcasts. It extracts mental models, counter-intuitive insights, and decision frameworks that help builders, PMs, and founders make better AI product decisions.

## What it produces

| Tier | Output | Use case |
|---|---|---|
| **Tier 1** | 10-min learning card (markdown) | Daily post-listen review |
| **Tier 2** (default) | Study notes + framework cards + decision checklists + interview answer bank | Deposit into Notion/Obsidian |
| **Tier 3** | Interactive self-contained HTML course | Landmark episodes (Karpathy, OpenAI, product-lead interviews) |

Every output includes: credibility tagging (🟢 data / 🟡 experience / 🔴 speculation), anti-summary rules enforcement, personal AI growth log, and cross-episode knowledge base connections.

## Example output

The `ai-judgment-kb/` directory contains 2 processed episodes:

1. **[Agent Harness 深度拆解](ai-judgment-kb/episodes/2026-06-04-agent-harness-explained/)** — Harness 三层架构 + 双自洽标准
2. **[AI 创业真实复盘](ai-judgment-kb/episodes/2026-06-04-ai-startup-reality/)** — 垂直 Agent 死亡螺旋 + Gym vs Whale 模型

Each episode folder includes: learning card, framework card, decision checklist, interview answer bank, terms glossary, growth log, knowledge entry, and Tier 3 HTML course.

## Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/xuannan-chen/podcast-to-course.git ~/.agents/skills/podcast-to-course

# Or symlink
ln -s $(pwd)/podcast-to-course ~/.agents/skills/podcast-to-course
```

## Supported input formats

- 通义听悟 transcript export (.txt / .md / .docx)
- 飞书妙记 transcript export
- YouTube transcript
- 小宇宙 / Apple Podcasts manual transcription
- Any STT-transcribed audio
- Your own listening notes

## Three operating modes

- `/podcast-preview` — Send title + guest, get listen-worthiness score + pre-listen questions
- `/podcast-course` — Send transcript, get Tier 1/2/3 output
- `/podcast-review` — Send your own notes, get bias check + gap fill + framework refinement

## Credits

Based on the [codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) skill by zarazhangrui. Shares the same CSS design system and HTML course architecture.
