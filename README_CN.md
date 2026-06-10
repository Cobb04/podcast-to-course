# Podcast to Course

[English](README_CN.md) | [中文](README.md)

A Claude Code skill that turns any podcast transcript into **reusable AI judgment assets** — so the insights stick, compound, and actually change how you make product decisions.

Send it a transcript. Get back structured framework cards, decision checklists, interview talking points, a personal growth log — and for landmark episodes, a beautiful interactive HTML course.

## Who is this for?

**Builders, PMs, and founders** who consume a high volume of AI/Agent/AI-product podcasts but struggle to retain and apply what they learn.

You listen during commutes, workouts, or chores. The insights feel profound in the moment — but evaporate within days. You have no system to capture, organize, and operationalize what you hear.

**Your goals are practical, not academic:**
- Extract reusable mental models from conversations and apply them to your own product/business decisions
- Build product intuition — know which AI patterns to adopt and which to ignore
- Make faster, better calls by internalizing how experienced builders think about tradeoffs
- Speak with confidence in meetings, interviews, and presentations — with structured frameworks at your fingertips
- Connect insights across episodes — see how Episode 7 builds on Episodes 2 and 5

You're not trying to become a researcher. You want the podcast's wisdom translated into tools you can use tomorrow morning.

## Three output tiers

### Tier 1: 10-Minute Learning Card (Lightweight)

A single markdown file scannable in 10 minutes: core question + 3 core judgments + 3 counter-intuitive insights + 1 reusable framework + 5 action suggestions + 1 self-test question.

For daily post-listen review.

### Tier 2: Study Notes + Framework Cards (Standard, Default)

A set of markdown assets you can drop into Notion or Obsidian:
- `EPISODE-HOME.md` — the single episode entry point: learn, verify, apply, challenge
- `summary.md` — structured overview with logic map
- `framework-card.md` — named framework with decision rules and boundary conditions
- `decision-checklist.md` — when-to-do-what derived from the episode
- `interview-answer-bank.md` — 30s/60s responses for interviews and presentations
- `claim-ledger.md` — claim-level timestamps, source anchors, evidence, and status
- `debate-arena.md` — AI-vs-guest debate arena; challenges high-impact claims and uses web search when needed
- `wiki-change-report.md` — what this episode created, updated, contradicted, and left open
- `growth-log.md` — before/after snapshot of your AI worldview
- `knowledge-entry.md` — cross-episode connections and credibility summary

For learners who want to deposit knowledge into a personal knowledge base.

### Tier 3: Interactive HTML Course (Deep)

A self-contained, zero-dependency HTML file — double-click to open. For landmark episodes you'll reference for months: Karpathy, OpenAI, product-lead interviews.

- **Original Words ↔ Actionable Insight translations** — verbatim quote on the left, actionable takeaway on the right
- **Framework step-reveal** — click to reveal each layer of a decision framework
- **Scenario-based quizzes** — not "what did the guest say?" but "you encounter X, using this episode's framework, what's your call?"
- **Conversation flow animations** — iMessage-style exchanges dramatizing key debates
- **Credibility badges** — every claim tagged 🟢 data / 🟡 experience / 🔴 speculation
- **Learning loop** — pre-test, application exercise, and 24-hour review card
- **Knowledge base persistence** — each processed episode updates your master index, linking to previous episodes

## Three operating modes

| Mode | What you send | What you get |
|---|---|---|
| `/podcast-preview` | Title + guest name | Listen-worthiness score (1–10) + 3 pre-listen questions + what to skip |
| `/podcast-course` | Full transcript | Tier 1 / 2 / 3 output |
| `/podcast-review` | Your own listening notes | Bias check + gap fill + framework refinement |

## Supported input formats

通义听悟 · 飞书妙记 · YouTube transcript · 小宇宙 / Apple Podcasts manual transcription · Any STT-transcribed audio · Your own notes

## Design philosophy

### Judgment extraction, not summarization

A summary tells you what was said. Judgment extraction tells you **when to use it, when not to use it, and how strongly to believe it**. Every claim carries a credibility badge. Every framework has boundary conditions. Empty praise like "这期很有启发" is banned — if the output works for any episode on the same topic, it's a summary, not an extraction.

### Application over memorization

Every quiz places you in a realistic scenario. "Your CTO proposes a multi-agent architecture. Using the framework from this episode, what's your first question?" — not "What did the guest say about multi-agent?"

### Knowledge that compounds

Each episode updates your personal AI judgment library. `knowledge-entry.md` connects new insights to previous episodes — marking whether they reinforce, contradict, or extend existing frameworks. After 20 episodes, you have ~15 sharp framework cards, not 60 duplicate ones.

### Wiki contamination defense

Podcast speech is not a fact source. It is a claim source. High-impact claims go through `claim-ledger.md` and `debate-arena.md`: quote the guest, challenge the logic, inspect sample bias, check causal overreach, compare against the existing wiki, and use web search for time-sensitive facts like product status, market data, model capability, research claims, and regulations.

Each core claim carries a status:

```text
accepted / tentative / challenged / disputed / outdated / rejected
```

Only anchored, status-tagged, and challenged judgments enter the long-term wiki.

### Honest calibration

The most dangerous thing in AI podcasts is confident-sounding claims backed by nothing. Every insight gets an evidence tag. When a speaker hedges, the output preserves that uncertainty. When an episode has no strong framework, the output says so — rather than inventing one that sounds plausible.

### Portable by design

Markdown goes everywhere. HTML is self-contained. No platform lock-in. Your judgment library lives where your thinking already lives.

## Install

```bash
git clone https://github.com/Cobb04/podcast-to-course.git ~/.agents/skills/podcast-to-course
```

Then say in Claude Code: *"Turn this podcast transcript into a course"*

## Skill structure

```
podcast-to-course/
├── SKILL.md                          # Main skill instructions
├── README.md
├── README_CN.md                      # Chinese version
└── references/
    ├── build-self-contained.sh       # Universal build pipeline
    ├── podcast-engine.js             # Interactive engine (quiz, framework viz, nav)
    ├── podcast-styles.css            # Podcast-specific CSS
    ├── debate-arena-template.md      # AI-vs-guest debate template
    ├── claim-ledger-template.md       # Claim evidence ledger template
    ├── episode-home-template.md       # Strong episode entry template
    ├── gotchas.md                    # Failure points checklist
    └── interactive-elements.md       # Quiz, framework, annotation patterns
```

---

Built with Claude Code. Based on the [codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) skill by [Zara](https://x.com/zarazhangrui).
