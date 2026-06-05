# Podcast to Course

A Claude Code skill that turns any podcast transcript into reusable AI judgment assets — so the insights stick, compound, and actually change how you make product decisions.

Send it a transcript. Get back structured framework cards, decision checklists, interview talking points, a personal growth log — and for landmark episodes, a beautiful interactive HTML course.

## Who is this for?

**Builders, PMs, and founders** who consume a high volume of AI/Agent/AI-product podcasts but struggle to retain and apply what they learn.

You listen during commutes, workouts, or chores. The insights feel profound in the moment — but evaporate within days. You have no system to capture, organize, and operationalize what you hear.

**Your goals are practical, not academic:**
- Extract reusable mental models from conversations and apply them to your own product decisions
- Build product intuition — know which AI patterns to adopt and which to ignore
- Make faster, better calls by internalizing how experienced builders think about tradeoffs
- Speak with confidence in meetings, interviews, and presentations
- Connect insights across episodes — see how Episode 7 builds on Episodes 2 and 5

You're not trying to become a researcher. You want the podcast's wisdom translated into tools you can use tomorrow morning.

## What the output looks like

The skill produces **three tiers** of output, from lightweight to deep:

### Tier 1: 10-Minute Learning Card
A single markdown file scannable in 10 minutes: core question, 3 judgments, 3 counter-intuitive insights, 1 framework, 5 actions.

### Tier 2: Study Notes + Framework Cards (Default)
A portable knowledge base directory — drag into Notion, Obsidian, or any markdown editor:
- `summary.md` — structured overview with logic map
- `framework-card.md` — named framework with decision rules and boundary conditions
- `decision-checklist.md` — when-to-do-what derived from the episode
- `interview-answer-bank.md` — 30s/60s responses with key terms to drop
- `growth-log.md` — before/after snapshot of your AI worldview
- `knowledge-entry.md` — cross-episode connections and credibility summary

### Tier 3: Interactive HTML Course (for landmark episodes)
A self-contained, zero-dependency HTML file that opens in any browser:

- **Original Words ↔ Actionable Insight translations** — speaker's verbatim quote on the left, actionable takeaway on the right
- **Framework visualizations** — click to reveal each layer of a decision framework step by step
- **Scenario-based quizzes** — not "what did the guest say?" but "you encounter X situation, using this episode's framework, what's your call?"
- **Conversation flow animations** — iMessage-style exchanges dramatizing key debates from the episode
- **Credibility badges** — every claim tagged 🟢 data / 🟡 experience / 🔴 speculation
- **Side annotations** — pull-out insights on key screens without breaking document flow
- **Knowledge base persistence** — each processed episode updates your master index and cross-references previous episodes

## How to use

### As a Claude Code skill

```bash
git clone https://github.com/Cobb04/podcast-to-course.git ~/.agents/skills/podcast-to-course
```

Then open any project in Claude Code and say: *"Turn this podcast transcript into a course"*

### Three modes

| Mode | What you send | What you get |
|---|---|---|
| `/podcast-preview` | Title + guest name | Listen-worthiness score, 3 pre-listen questions, what to skip |
| `/podcast-course` | Full transcript | Tier 1/2/3 output |
| `/podcast-review` | Your own listening notes | Bias check, gap fill, framework refinement |

### Supported input formats

通义听悟 · 飞书妙记 · YouTube transcript · 小宇宙 / Apple Podcasts manual transcription · Any STT-transcribed audio · Your own notes

## Design philosophy

### Judgment extraction, not summarization

A summary tells you what was said. Judgment extraction tells you **when to use it, when not to use it, and how strongly to believe it**. Every claim carries a credibility badge. Every framework has boundary conditions. Empty praise like "这期很有启发" is banned — if the output works for any episode on the same topic, it's a summary, not an extraction.

### Application over memorization

Every quiz places you in a realistic scenario. "Your CTO proposes a multi-agent architecture. Using the framework from this episode, what's your first question?" — not "What did the guest say about multi-agent?"

### Your knowledge compounds

Each episode updates your personal AI judgment library. The `knowledge-entry.md` connects new insights to previous episodes — marking whether they reinforce, contradict, or extend existing frameworks. After 20 episodes, you have ~15 sharp framework cards, not 60 duplicate ones.

### Honest calibration

The most dangerous thing in AI podcasts is confident-sounding claims backed by nothing. Every insight gets an evidence tag. When a speaker hedges, the output preserves that uncertainty. When an episode has no strong framework, the output says so — rather than inventing one that sounds plausible.

### Portable by design

Markdown goes everywhere. HTML is self-contained. No platform lock-in. Your judgment library lives where your thinking already lives.

## Skill structure

```
podcast-to-course/
├── SKILL.md                          # Main skill instructions
├── README.md
└── references/
    ├── build-self-contained.sh       # Universal build pipeline
    ├── podcast-engine.js             # Interactive JS (quiz, framework viz, nav)
    ├── podcast-styles.css            # Podcast-specific CSS
    ├── gotchas.md                    # Failure points checklist
    └── interactive-elements.md       # Quiz, framework, annotation patterns
```

---

Built with Claude Code. Based on the [codebase-to-course](https://github.com/zarazhangrui/codebase-to-course) skill by [Zara](https://x.com/zarazhangrui).
