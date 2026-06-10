---
name: podcast-to-course
description: "Turn any podcast transcript into reusable AI judgment assets — structured frameworks, decision checklists, interview talking points, and an optional interactive HTML course. Use this skill whenever someone wants to extract actionable knowledge from a podcast episode, systematize an interview, build AI product intuition, or create a learning resource from spoken content. Also trigger when users mention 'learn from this podcast,' 'make this transcript actionable,' 'podcast study guide,' 'systematize this interview,' 'extract frameworks from this episode,' 'podcast learning cards,' or 'turn this conversation into reusable notes.' This skill produces a knowledge directory containing framework cards, decision checklists, a structured summary, an optional interactive HTML course, and a personal growth log entry."
---

# Podcast-to-AI-Judgment-System

Transform podcast transcripts into a **reusable AI judgment asset library**. The core output is structured, portable knowledge — framework cards, decision checklists, interview talking points, and a personal worldview growth log — that compounds across episodes. An interactive HTML course is available as the premium output tier for high-signal episodes.

This skill does NOT just summarize. It extracts the mental models, counter-intuitive insights, and decision frameworks that help a builder, product thinker, or founder make better AI product calls tomorrow morning.

## Three Output Tiers

Not every episode deserves a full course. Default to the tier that matches what the user asks for — and if they don't specify, default to **Standard** and mention the other options.

### Tier 1: 10-Minute Learning Cards (Lightweight)

For daily post-listen review. Output a single markdown file. No HTML, no build process.

**Deliverables:**
- `learning-card.md` containing:
  - **Core Question** — the one question this episode answers
  - **3 Core Judgments** — the speaker's main theses, each ≤2 sentences
  - **3 Counter-Intuitive Insights** — "You think X, but Y" format
  - **1 Reusable Framework** — named, diagrammed in ASCII, with decision rules
  - **5 Action Suggestions** — concrete "do this tomorrow" items
  - **1 Self-Test Question** — a scenario-based quiz with answer rationale

**When to use:** User says "quick review," "give me the key points," "10-minute recap," or the episode is a regular weekly listen rather than a landmark conversation.

### Tier 2: Study Notes + Framework Cards (Standard — DEFAULT)

For users who want to deposit knowledge into Notion, Obsidian, or a personal knowledge base. The output is a directory of markdown assets.

**Deliverables:**
```
EPISODE-HOME.md          ← Single user-facing entry point for this episode
episode-slug/
  summary.md              ← Structured summary (core arguments, logic map)
  framework-card.md       ← Named framework with diagram, rules, and when-to-use
  decision-checklist.md   ← When-to-do-what checklist derived from the episode
  interview-answer-bank.md ← Talking points for interviews/presentations
  terms.md                ← Glossary of domain-specific terms from this episode
  claim-ledger.md         ← Claim-level source anchors, evidence, and status
  debate-arena.md         ← AI-vs-guest challenges + web-search checks when needed
  wiki-change-report.md   ← What changed in the user's KB
  growth-log.md           ← Personal AI worldview update (see Phase 5)
  knowledge-entry.md      ← Cross-episode connection entry (see Phase 5)
```

**When to use:** This is the DEFAULT output tier. Use it unless the user explicitly asks for a lighter or heavier format.

### Tier 3: Interactive HTML Course (Heavy — for landmark episodes)

For Karpathy, LangChain, OpenAI, or product-lead interviews — episodes the user will reference for months.

**Deliverables:** All Tier 2 assets plus the full interactive HTML course (directory-based build, same output format as codebase-to-course).

The HTML course is the primary learning experience. Markdown lesson files are source assets, not a substitute for the course. Every Tier 3 course must include:
- `index.html` with progress/navigation
- `pretest.md` — diagnostic scenario before study
- `application-exercise.md` — apply the framework to a real AI feature
- `review-card.md` — 24-hour recall/review card

**When to use:** User says "make a course," "full interactive version," "I want to really study this one," or the episode features a field-defining guest.

**At the start of each session, clarify the tier if the user hasn't specified:**
> I can process this episode at three depths:
> - **10-min learning card** — quick recap
> - **Study notes + framework cards** (default) — structured assets for your knowledge base
> - **Full interactive course** — for landmark episodes you'll reference for months
>
> Which would you like? (Or just say "default" and I'll go with study notes.)

## Mandatory Output Contract

For every full transcript ingest, produce one strong entry point and one trust layer. Do not leave users with only a directory tree.

Required outputs:

```
EPISODE-HOME.md
raw/transcripts/<episode>.md
knowledge-kernels/<episode>.md
ai-judgment-kb/index.md
ai-judgment-kb/log.md
ai-judgment-kb/claim-status-policy.md
ai-judgment-kb/framework-governance.md
ai-judgment-kb/episodes/<episode>/summary.md
ai-judgment-kb/episodes/<episode>/framework-card.md
ai-judgment-kb/episodes/<episode>/decision-checklist.md
ai-judgment-kb/episodes/<episode>/interview-answer-bank.md
ai-judgment-kb/episodes/<episode>/terms.md
ai-judgment-kb/episodes/<episode>/claim-ledger.md
ai-judgment-kb/episodes/<episode>/debate-arena.md
ai-judgment-kb/episodes/<episode>/wiki-change-report.md
ai-judgment-kb/episodes/<episode>/growth-log.md
ai-judgment-kb/episodes/<episode>/knowledge-entry.md
```

If Tier 3 is requested, additionally produce:

```
course/<episode>/index.html
course/<episode>/pretest.md
course/<episode>/application-exercise.md
course/<episode>/review-card.md
course/<episode>/assets/*.md
```

### `EPISODE-HOME.md`

This is the user-facing map. It must answer:
- what to open first
- what to read if the user has 3 minutes
- where to study the course
- where to verify evidence
- where to challenge the thesis
- what changed in the wiki
- which files can be ignored at first

### Claim Status Policy

Podcast claims are not facts. Every high-impact claim must carry one status:
- `accepted` — strong enough to use as a working judgment
- `tentative` — plausible but not fully validated
- `challenged` — AI or external sources found a serious weakness
- `disputed` — credible sources conflict
- `outdated` — may no longer be current
- `rejected` — unsupported enough to keep out of active wiki knowledge

No claim can appear in a framework or course as an unqualified rule unless it has a claim ID, evidence level, status, and source anchor.

### Debate Arena

Every high-signal episode must include `debate-arena.md`. It is the wiki immune system: an AI-vs-guest debate that challenges claims before they become durable knowledge.

Each challenged item must include:
- challenged quote
- timestamp/source line
- guest claim
- AI challenge
- whether web search is required
- web-search sources and search date when used
- verdict
- wiki action

Use web search for product status, company metrics, market outcomes, research claims, model capability, legal/regulatory facts, and anything likely to change after the recording date. Do not use web search as a substitute for judgment on values, taste, or private causal interpretation.

### Framework Governance

Create a new framework only when it changes a decision rule. If a new episode merely restates, reinforces, or gives another example of an existing decision rule, update the existing framework instead of creating a new one.

Before creating a new framework, answer:
1. What decision can the user make differently because this framework exists?
2. Which existing framework is closest, and why is this not a duplicate?
3. When should the user not apply it?
4. Which claim anchors support it?
5. Where should future related episodes attach?

### What Good Output Looks Like (For the AI Agent)

These are quality benchmarks, not templates. When an agent writes Tier 1 or Tier 2 output, the following examples define the bar.

**Good Tier 1 learning card (excerpt):**

```markdown
# Learning Card: Why Multi-Agent Is Overkill for 95% of Use Cases
**Episode:** 张小珺对话李志飞 | 2025.03.15

## Core Question
When should you NOT use multi-agent architecture?

## 3 Core Judgments

1. **Coordination overhead grows quadratically with agent count.**
   🟡 Medium | 李志飞's engineering team benchmarked this across 3 production systems.
   → 5 agents = 10 communication channels. 10 agents = 45. Most demos ignore this cost.

2. **A single well-prompted model beats 3 poorly-coordinated agents.**
   🟢 High | Backed by GPT-4 vs multi-agent benchmarks from 3 independent papers.
   → The "intelligence gain" from parallelism is often < 15%, while latency increases 3×.

3. **The real moat is data + evals, not agent topology.**
   🟡 Medium | Observed across 20+ portfolio companies at 李志飞's fund.
   → Startups obsess over agent architecture and ignore eval infrastructure. That's backwards.
...
```

**Bad Tier 1 learning card:**
```markdown
# Episode Summary: AI Agents Podcast

The guest talked about AI agents and shared some interesting thoughts.
He said multi-agent systems are complex and sometimes overkill.
He also mentioned RAG and fine-tuning. Good episode for AI learners.
```
↑ No named claims, no credibility tags, no framework, no actionable takeaway. This is a summary, not a learning card.

**Good `framework-card.md` (Tier 2 excerpt):**
```markdown
# Framework: The Two-Question Agent Test
**Origin:** 李志飞, 张小珺播客 Episode 47 | 🟡 Medium (production experience)

## When to Use
You're considering whether to add an agent or agent-to-agent communication to your system.

## The Test
Ask two questions before adding any agent:

1. **"What decision does this agent make that couldn't be a function call?"**
   If the answer is "none," you don't need an agent — you need better tool definitions.

2. **"What information does this agent have that the calling agent doesn't already have?"**
   If the answer is "nothing," you're adding latency for zero information gain.

## Decision Rules
- Pass both → Probably needs to be an agent
- Pass only #1 → Consider a tool instead
- Pass only #2 → Consider a data pipeline instead
- Pass neither → Remove this agent from the design

## When NOT to Use
- Real-time systems where latency budget < 200ms
- Single-domain tasks with clear input/output boundaries
- When you haven't built the single-agent baseline yet

## Boundary Conditions
李志飞 noted this test breaks when:
- The agent accesses a unique tool or API that others can't (passes #2 even if #1 is weak)
- Regulatory requirements force human-in-the-loop separation (external constraint overrides)
```

**Good `growth-log.md` (Tier 2 excerpt):**
```markdown
## What I used to think
Multi-agent systems are always more capable because more agents = more intelligence.
Architecture decisions should start from "how many agents do we need?"

## What I now think
Multi-agent adds coordination overhead that grows faster than the intelligence gain.
Architecture decisions should start from "can this be a function call?" and only upgrade to agent when necessary.

## What changed
李志飞's quadratic overhead argument + the Two-Question Agent Test gave me a concrete
filter instead of a vague "keep it simple" heuristic.

## Next time I encounter an architecture discussion, I will ask:
1. What decision does this agent make that couldn't be a function call?
2. What information does it have that the caller doesn't?
3. Have we built the single-agent baseline first?
```

**Good vs bad `growth-log.md`:**
- Good: "I used to think X, now I think Y, here's the specific evidence that changed my mind."
- Bad: "This was a great episode! I learned a lot about agents. Will apply this at work."
- Bad: A restatement of the episode summary. The growth log is about *your* worldview shift, not the content.

---

## Knowledge Base Persistence

The user's judgment library lives as a directory of episode folders. There is no database — just a naming convention and a simple index file.

### Directory Convention

```
ai-judgment-kb/
  index.md                  ← Master index (auto-generated, see below)
  episodes/
    2025-03-15-multi-agent-overkill/
      learning-card.md       ← Always present (Tier 1 minimum)
      summary.md             ← Tier 2+
      framework-card.md      ← Tier 2+
      decision-checklist.md  ← Tier 2+
      interview-answer-bank.md ← Tier 2+
      terms.md               ← Tier 2+
      growth-log.md          ← Tier 2+
      knowledge-entry.md     ← Tier 2+
      index.html             ← Tier 3 only
   2025-03-22-rag-is-not-enough/
   2025-04-01-eval-manifesto/
```

### Naming Convention

Episode folders follow: `YYYY-MM-DD-<slug>` where slug is the episode's core topic in 3–5 hyphenated words. Date is the episode's release date (or recording date if unknown). This naming ensures chronological sorting and human-readable scanning.

### Index File (`index.md`)

Every time a new episode is processed, regenerate `index.md`. It's a simple table the user can pin in Notion or open in any editor:

```markdown
# AI Judgment Knowledge Base

| Date | Episode | Core Framework | Credibility | Growth Shift |
|---|---|---|---|---|
| 2025-04-01 | [Eval Manifesto](./episodes/2025-04-01-eval-manifesto/) | Eval-First Development | 🟢🟡🟡 | Evals aren't QA — they're the product spec |
| 2025-03-22 | [RAG Is Not Enough](./episodes/2025-03-22-rag-is-not-enough/) | The RAG+ Pipeline | 🟢🟡🔴 | RAG alone fails on anything needing reasoning |
| 2025-03-15 | [Multi-Agent Overkill](./episodes/2025-03-15-multi-agent-overkill/) | Two-Question Agent Test | 🟢🟡🟡 | Start from "can this be a function?" not "how many agents?" |
```

**When processing a new episode:** If the user has an existing knowledge base directory, add to it. If this is their first episode, create the directory structure and explain:
> I've created `ai-judgment-kb/` with this episode. Each time you process a new episode, I'll add to it and update the index. This is your AI judgment library — it compounds.

---

## Operating Modes

This skill supports three modes that cover the full learning loop:

### Mode 1: Preview (`/podcast-preview` or "should I listen to this?")

**Input:** Episode title, description, guest name, and any context the user has (e.g., show notes, tweet thread about the episode).

**Output:**
- **Listen-worthiness score** (1–10) with rationale
- **3 pre-listen questions** to hold in mind while listening — these prime the user to catch the most valuable signals
- **What to skip** — if the guest is known for certain tangents or the first 20 minutes are intro fluff
- **Related episodes** the user may have already processed (from their knowledge base)

**Processing flow for Preview mode (abbreviated):**

1. **Guest triage** — Who is this person? What are they uniquely qualified to speak on? What are their known biases or blind spots? (If the guest is unknown, ask the user or search.)
2. **Topic calibration** — Is this topic in the user's learning sweet spot? Too basic? Too advanced? Compare against the user's knowledge base to calibrate.
3. **Signal density estimate** — Based on the guest's track record and the topic, how many actionable insights per 30 minutes is this episode likely to deliver? Some guests are 5 insights/hour, others are 0.5.
4. **Generate pre-listen questions** — The 3 best questions to hold in mind while listening. Good pre-listen questions are specific, answerable from conversation (not requiring data lookup), and connected to the user's learning goal.
5. **Output the preview card** — A compact markdown block the user can screenshot or paste into their podcast app notes.

**Example Preview output:**
```markdown
# Preview: 张小珺对话李志飞 — AI Agent 创业的十个坑

## Worth listening? 8/10
李志飞 has built and shipped agent products at scale (出门问问). He's in the top 5%
of guests who can speak from production experience, not demos. This episode is
likely to deliver 4-6 actionable frameworks in 60 minutes.

## 3 Pre-Listen Questions
1. What's the #1 reason agents fail in production (not in demos)?
2. When does he think multi-agent is actually worth it?
3. What's his eval philosophy — how does he know an agent is "working"?

## What to Skip
- First ~15 min is typical founder backstory (unless you're interested in 出门问问 history)
- The "AGI timeline" tangent around 45 min mark is speculative — skip unless you enjoy that

## Connects To
- Your existing: [[Multi-Agent Overkill]] (2025-03-15) — this episode likely extends those ideas
- Your existing: [[Eval Manifesto]] (2025-04-01) — likely overlaps on eval philosophy
```

### Mode 2: Course Generation (`/podcast-course` or "turn this into a course")

**Input:** Full transcript (any format — see Supported Input Formats).

**Output:** Tier 1, 2, or 3 deliverables based on user choice.

This is the main mode and follows the full Phase 1–5 process below.

### Mode 3: Review (`/podcast-review` or "help me process what I heard")

**Input:** The user's own listening notes, takeaways, or a brain dump after listening.

**Output:**
- **Bias check** — what assumptions might the user have brought in? What did they miss?
- **Gap fill** — what the user's notes didn't capture that the episode likely covered
- **Framework refinement** — take the user's raw takeaways and structure them into a named framework
- **Growth log entry** — update the user's AI worldview based on their own synthesis

**Processing flow for Review mode:**

1. **Parse the brain dump** — The user's notes will be messy: half-formed thoughts, emotional reactions ("this part blew my mind"), verbatim quotes mixed with paraphrasing. Identify what's a claim, what's a quote, what's the user's own reaction, and what's missing.
2. **Bias check** — Compare the user's takeaways against common listener biases:
   - **Confirmation bias**: Did they only capture points they already agreed with?
   - **Recency bias**: Did they overweight the last 10 minutes?
   - **Guest charisma bias**: Did they assign high credibility to weak claims because the guest sounds authoritative?
   - **Missing the tension**: Did they capture moments where the host pushed back or the guest qualified their own claim? These are often the most important signals.
3. **Gap fill** — Based on the episode's likely structure (guest, topic, format), what did the user likely hear but not write down? Prompt the user: "You mentioned X — did the guest also talk about Y? That's a common companion topic."
4. **Framework refinement** — Take the user's raw takeaways and give them structure. If the user wrote "agents need better testing," upgrade that to a named, decision-rule-equipped framework: "The Agent Eval Triad: Unit tests for tool calls, Scenario tests for multi-turn reasoning, and Guardrail tests for safety boundaries."
5. **Growth log generation** — Compare the user's notes to their previous growth log entries. Is this episode reinforcing a shift that was already starting? Contradicting it? Fill in the `growth-log.md` template based on what the user's notes reveal about their evolving worldview.

**What NOT to do in Review mode:**
- Do NOT read the full transcript yourself (the user hasn't provided it). Work only from the user's notes.
- Do NOT fabricate episode content to fill gaps. Mark gaps honestly: "Based on the guest's expertise in X, the episode likely covered Y — but I can't confirm without the transcript."
- Do NOT override the user's interpretation. If they found insight in something you'd consider minor, honor that. Their learning, their lens.

---

## First-Run Welcome

When the skill is first triggered and the user hasn't provided a transcript yet, introduce yourself and explain what you do:

> **I turn podcasts into reusable AI judgment assets — so the insights stick, compound, and actually change how you make product decisions.**
>
> **Three ways to use me:**
> - **Preview an episode** — send me a title + guest, I'll tell you if it's worth your time and what to listen for.
> - **Process a full episode** — send me the transcript, I'll extract frameworks, counter-intuitive insights, decision checklists, and scenario quizzes.
> - **Review your own notes** — send me what you wrote down after listening, I'll help you catch blind spots and structure your thinking.
>
> **Supported input formats (best → good):**
> - 通义听悟 transcript export (.txt / .md / .docx)
> - 飞书妙记 transcript export
> - YouTube transcript (paste or .txt)
> - 小宇宙 / Apple Podcasts manual transcription
> - Audio transcribed via any STT tool
> - Your own listening notes or brain dump
>
> **Optional:** Tell me your learning focus and I'll personalize the output:
> - **A.** AI product judgment (for PMs, designers, product thinkers)
> - **B.** Engineering implementation understanding (for developers, tech leads)
> - **C.** Interview / job-talk preparation (for job seekers)
> - **D.** Startup / business judgment (for founders, investors)
> - **E.** General comprehensive (default)
>
> **Output depth:**
> - Quick: **10-min learning card** — for daily recaps
> - Default: **Study notes + framework cards** — structured assets for your knowledge base
> - Deep: **Full interactive HTML course** — for landmark episodes
>
> Just drop a transcript and say what you need.

---

## Who This Is For

The target learner is a **builder, product thinker, or founder** who consumes a high volume of AI/Agent/AI-product podcasts but struggles to retain and apply what they learn. They listen to episodes during commutes, workouts, or chores — but the insights evaporate within days because there's no system to capture, organize, and operationalize them.

**Their real pain points:**
- **They listen to everything but remember nothing.** Hours of consumption, zero structured takeaways.
- **They can't connect the dots.** Insight A from Episode 37 and Insight B from Episode 52 are related, but they have no way to see the relationship.
- **They can't apply what they hear.** Knowing "agents need guardrails" is different from knowing *when and how to add guardrails to my specific product*.
- **They drown in information, starved for frameworks.** Podcasts are optimized for engagement, not retention.
- **They can't express what they know.** When asked in an interview or meeting, they can't articulate the insight clearly because they never structured it.
- **They need judgment, not just knowledge.** They don't need to memorize facts — they need to know *what to do when*.

**Their goals are practical, not academic:**
- **Extract reusable mental models** and apply them to their own product/business decisions
- **Build product intuition** — develop the judgment to know which AI patterns to adopt and which to ignore
- **Make faster, better decisions** by internalizing how experienced builders think about tradeoffs
- **Speak with confidence** — have structured frameworks and talking points at their fingertips for meetings, interviews, and presentations
- **Compound their knowledge** — each new episode connects to and builds on previous ones, forming an ever-sharpening AI judgment system
- **Track their growth** — see how their AI worldview evolves over time

**They are NOT trying to become researchers or academics.** They're operators. They need the podcast's wisdom translated into tools they can use tomorrow morning.

## Why This Approach Works

This skill inverts passive content consumption. The old model: listen → feel enlightened → forget → listen to another. This model: **listen → extract frameworks → connect to existing knowledge → apply to real decisions → update worldview.**

**Beautiful courses are a delivery mechanism, not the goal.** The goal is reusable judgment that compounds. A framework card the user references 6 months later in a product meeting is worth more than the most stunning interactive visualization they opened once. Three design decisions make this possible:

1. **Tiered output matches real usage patterns.** Most episodes deserve 10 minutes of structured reflection, not a 6-module course. By making lightweight output the easiest path, the user actually uses the skill daily instead of saving episodes "for later" and never processing them.

2. **Every output is portable.** Markdown files go directly into Notion, Obsidian, Logseq, or a GitHub repo. No platform lock-in. The user's AI judgment library lives where their thinking already lives.

3. **The knowledge compounds.** `knowledge-entry.md` and `growth-log.md` create a trail of connections and worldview shifts. Episode 7 isn't just processed in isolation — it's linked to Episodes 2 and 5, and the user can see their product intuition sharpening over time.

That said, when a user chooses Tier 3, the visual design follows the same principles as codebase-to-course: warm, notebook-like, scroll-based, 50% visual weight, Bricolage Grotesque typography. The HTML course shares the same CSS/JS reference files as codebase-to-course — only the content generation logic differs.

Every module answers **"when would I actually use this?"** before "what does this mean?" The answer is always a concrete scenario: *because the next time you're deciding whether to build a multi-agent system, this framework tells you the two questions to ask first.*

---

## Quality Bar (Non-Negotiable)

Every output — regardless of tier — must pass these checks before delivery. If any check fails, revise until it passes.

### What "Good" Means

A good output must:
- **Convert podcast opinions into reusable judgment**, not ordinary summaries. The user should walk away with a decision tool, not just "what was said."
- **Tag every core claim with evidence source**: 🟢 data, 🟡 experience, or 🔴 speculation. Untagged claims are incomplete output.
- **Answer "when to use" AND "when NOT to use"** for every framework. A framework without boundary conditions is half-finished.
- **Make every action suggestion executable within 7 days.** "Think about evals more" fails. "Write down the 3 failure modes your current eval doesn't catch — do this Monday morning" passes.
- **Never use empty praise**: "这期很有启发," "值得思考," "very insightful episode," "a must-listen." These phrases signal that the agent summarized instead of extracted. Delete them all.

### Pre-Delivery Self-Check

Before handing output to the user, ask:

1. **"Would I bet my own product decision on this framework?"** If the framework is too vague to guide a real choice, it's not done.
2. **"Can the user act on this without re-listening to the episode?"** If they need the original audio to understand what you meant, the extraction failed.
3. **"Did I preserve the speaker's uncertainty where it existed?"** If the speaker hedged, waffled, or said "I'm not sure about this part," your output must reflect that. Over-polishing uncertainty into certainty is misinformation.
4. **"Is there at least one counter-intuitive or surprise element preserved?"** If every insight feels obvious and expected, you probably summarized instead of extracted.
5. **"Did I mark any claim as high-evidence that's actually just the speaker's opinion?"** 🟢 is earned, not defaulted. When in doubt, downgrade to 🟡 or 🔴.

---

## Anti-Summary Rules (Non-Negotiable)

The #1 failure mode of podcast-processing agents is producing a well-structured, beautifully formatted **summary that has zero learning value**. These rules exist to prevent that.

### Do NOT

- **Summarize topic by topic** without extracting judgment. "They discussed agent architecture, then RAG, then evals" — this is a table of contents, not a learning asset. The user already knows what topics were discussed; they need the *judgment framework behind each topic.*
- **Repeat speaker opinions without evaluating credibility.** "The guest believes multi-agent is overhyped" — stop. *Why* do they believe it? What evidence? How strongly? A claim without credibility calibration is noise.
- **Produce generic advice** that could apply to any episode. "Focus on user needs," "Start simple and iterate," "Testing is important." If the advice fits on a fortune cookie, it doesn't belong in the output. Every insight must be *specific to this episode's unique intellectual contribution.*
- **Turn every quote into an inspirational slogan.** Verbatim quotes are for preserving the speaker's exact reasoning — not for creating motivational posters. If a quote's actionable insight is "believe in yourself," you've stripped all the useful content out.
- **Over-polish the speaker's original uncertainty.** Real conversations are messy. Speakers say "I'm not sure but I think maybe..." and that uncertainty is valuable signal. "The speaker recommends X" is a lie if the speaker actually said "X seems promising but we haven't tested it at scale." Preserve the hedging.
- **Ignore disagreement, tension, or ambiguity.** The most valuable moments in a podcast are often when the host pushes back, the guest qualifies their own claim, or two guests disagree. These tensions reveal the boundary conditions of ideas. If your output reads like everyone agreed on everything, you've filtered out the most important content.

### The Smell Test

If you can swap the episode title with another episode on the same topic and the output still mostly works — you've written a generic summary. Good extraction is *specific to this conversation.* The user should be able to identify which episode this came from just by reading the frameworks and quotes.

---

## Framework Extraction Fallback

Not every episode contains a clean, extractable framework. Forcing one where none exists produces fake precision — a named "model" that the speaker never actually articulated, dressed up to look rigorous.

### When No Strong Framework Exists

Apply this escalation ladder. Start at Level 1 and only move down if the level above is genuinely unavailable:

| Level | What to extract | When to use |
|---|---|---|
| **1. Named framework** | Speaker articulated a repeatable decision process (2×2, decision tree, checklist, taxonomy). Name it, diagram it, give decision rules. | The speaker actually has a structured way of thinking. |
| **2. Judgment heuristic** | Speaker has a rule of thumb or a recurring phrase they use to make decisions. "I always ask myself two questions before..." Capture it as a heuristic, not a full framework. | The thinking pattern is consistent but not formally structured. |
| **3. Decision checklist** | Derive a checklist from the speaker's described behavior, even if they never stated it as a checklist. "Based on how the speaker described their decision process, here are the 4 questions they implicitly ask." | The speaker's logic is reconstructable but not explicitly packaged. |
| **4. Tension map** | The episode's value isn't a framework — it's the unresolved tension between competing ideas. Map the tension: "On one hand X, on the other hand Y. The speaker hasn't resolved this, and here's why that matters." | The conversation is exploratory, not conclusive. |
| **5. Low framework density (transparent)** | The episode is primarily narrative, case study, or opinion. Output: "This episode is low on extractable frameworks. Its primary value is [specific thing]. If you're looking for decision tools, this one may not be the best use of your study time." | The episode genuinely doesn't have reusable structure. Be honest about it. |

### Hard Rules

- **Never invent a framework** the speaker didn't articulate or strongly imply. "The Three Pillars of Agent Design" is only valid if the speaker actually described three pillars. Naming something that doesn't exist is fabrication.
- **Never force a 2×2 or pyramid** just because it looks good. A plain checklist is better than a fake matrix.
- **If you hit Level 5**, still deliver the rest of the output (arguments, counter-intuitive insights, quotes, growth log). Low framework density doesn't mean low value — it means the value is elsewhere.
- **The user would rather hear "this episode didn't have a strong framework"** than receive a plausible-sounding framework the speaker never said. Trust is built on honest calibration.

---

## The Process

### Mode Routing

The skill has three modes. The process flow differs for each:

| Mode | Trigger | Process |
|---|---|---|
| **Preview** | User provides title + guest only (no transcript) | Guest triage → topic calibration → signal density estimate → pre-listen questions → preview card. Skip all other phases. |
| **Course** | User provides full transcript | Full Phase 0 → Phase 5 process below. This is the main mode. |
| **Review** | User provides their own listening notes/brain dump | Bias check → gap fill → framework refinement → growth log. Skip Phases 1, 2, 2.5, 3. |

### Phase 0: Determine Tier and Learning Goal (Course Mode only)

Before any analysis, resolve three things:

1. **Which tier?** Lightweight / Standard / Heavy — based on what the user asked for. Default to Standard (Tier 2). If the user hasn't specified, ask the one-liner from the Three Output Tiers section.
2. **Which learning goal?** If the user specified A/B/C/D/E from the welcome menu, apply the personalization lens throughout all phases. If they didn't specify, use E (General comprehensive) but mention they can switch.
3. **Is there an existing knowledge base?** Check for an `ai-judgment-kb/` directory or `index.md`. If it exists, read it to understand what the user has already processed — this enables cross-episode connections in Phase 5.

**Personalization by learning goal:**

| Goal | Phase 1 emphasis | Phase 2 module arc bias | Quiz type priority | Output bias |
|---|---|---|---|---|
| A. AI Product Judgment | Product tradeoffs, UX implications, when-to-build vs when-to-buy | Decision frameworks, edge cases | Product judgment, rebuttal | 多输出"如何向 mentor/团队解释这个判断"；每个框架附"产品场景触发条件" |
| B. Engineering Implementation | Architecture patterns, technical tradeoffs, scalability | Mental model, framework | Technical understanding, architecture | 多输出"技术决策 checklist"；每个框架附"实现时的坑和边界条件" |
| C. Interview / Job-Talk | Narrative arcs, compelling examples, articulation patterns | Golden quotes, framework | Presentation, rebuttal | 多输出"60秒电梯演讲版本"；金句附"面试中什么时候用"；每个观点附常见追问 |
| D. Startup / Business | Market timing, commercialization, competitive moat | Counter-intuitive, action | Product judgment, tradeoff | 多输出"机会判断与商业风险"；框架附"这个判断在什么市场阶段成立/不成立" |
| E. General | Balanced extraction across all dimensions | Follow the episode's natural arc | Mix of all types | 均衡输出，所有维度等权重 |

**Learner mode is not just a filter — it changes what counts as valuable.** The same episode on multi-agent systems yields:

- **AI PM Intern**: "How do I explain to my mentor why we shouldn't use multi-agent for our chatbot? Here's the 3-sentence case."
- **Builder**: "Here's the coordination overhead formula, the latency budget worksheet, and when a single well-prompted model beats 3 agents."
- **Founder**: "Multi-agent is a competitive moat only when X — here's how to know if your use case qualifies. Otherwise it's premature complexity that burns runway."
- **Research**: "This maps to the agent coordination literature (Bernstein et al. 2024, Li et al. 2025). The speaker's contribution is the empirical failure mode taxonomy."

Apply the learner mode lens at every phase — not just as a final output filter, but as a decision driver during extraction, framework naming, quiz design, and action suggestion generation.

### Phase 1: Transcript Analysis & Knowledge Extraction

Deeply understand the podcast conversation. Read the entire transcript, identify the intellectual architecture of the discussion, and extract structured knowledge from unstructured dialogue.

**What to extract:**

1. **Core Arguments (3–5)** — The main theses the speaker(s) are advancing. These are not topics ("they talked about AI agents") but *claims* ("multi-agent systems are overkill for 95% of use cases because coordination overhead outweighs parallelism benefits"). Each core argument should be a single, debatable sentence.

2. **Judgment Criteria (判断依据) with Credibility Tags** — When speakers make claims, what evidence or reasoning do they cite? Categorize EVERY claim with a visible credibility badge:
   - **🟢 Evidence: High** — backed by published data, benchmarks, or systematically collected user research
   - **🟡 Evidence: Medium** — backed by the speaker's direct product/company-building experience
   - **🔴 Evidence: Low** — speaker's speculation, hypothesis, or secondhand anecdote. Valuable for inspiration but NOT ready to bet on.

   These badges must appear in the output, not just in analysis. AI podcast listeners especially need this — the space is full of confident-sounding claims that are actually one person's阶段性经验.

3. **Counter-Intuitive Insights (反直觉洞见)** — Moments where the speaker contradicts conventional wisdom or the learner's likely assumption. These are the highest-value nuggets because they change behavior. Flag them explicitly: "You probably think X — but here's why Y is actually true."

4. **Reusable Frameworks & Models** — Any structured way of thinking: 2×2 matrices, decision trees, maturity models, evaluation criteria, taxonomies. If the speaker has a repeatable approach to a recurring problem, extract it into a named framework. Even if the speaker didn't name it, **name it for them** (e.g., "The Two-Question Agent Test").

5. **Golden Quotes (金句 — keep verbatim)** — The best 8–15 sentences from the transcript, preserved word-for-word. These are the lines that make you stop and think. They'll be used in the "original words → actionable insight" translation blocks. Mark timestamps for traceability but strip them from the final output.

6. **Logical Relationships Between Arguments** — Map how the ideas connect. Does Argument A depend on B? Does Insight C contradict D? Is there a through-line connecting the entire conversation? This becomes the narrative arc.

7. **Actionable Takeaways** — Specific "do this on Monday" items, organized by the user's learning goal. These should be concrete enough that the user can act without re-listening.

**Pre-processing steps:**

- **Strip timestamps** — `[00:03:15]`, `[03:15]`, and any other timecode format. Remove all.
- **Normalize speaker labels** — "张老师（某公司CEO）" → "张老师". One consistent label per speaker.
- **Remove filler words and repetition** — "um," "you know," "就是说," "然后呢," false starts, mid-sentence corrections, and restatements of the same point. Collapse into the clearest single articulation. **Never alter meaning** — only remove verbal padding.
- **Flag and correct transcription errors** — "RAG" → "rag," "vector" → "victor." Use context. Mark uncertain corrections.
- **Identify conversational structure** — Topic shifts, host interjections, "let's pivot to..." moments become module boundaries.
- **Skip meta-content** — Sponsor reads, "subscribe and rate us," episode housekeeping.

**Figure out what the episode is about yourself.** Don't ask the user to summarize — they came to you precisely because they can't.

### Phase 2: Curriculum / Asset Design

The design differs by output tier:

#### Tier 1 Design (Learning Card)

Structure the single `learning-card.md` in this order:
1. Core Question (1 line)
2. 3 Core Judgments (each with credibility badge)
3. 3 Counter-Intuitive Insights
4. Framework deep-dive (name, ASCII diagram, decision rules, when-to-use)
5. 5 Action Suggestions
6. Self-Test Question (scenario + answer + rationale)

Keep total output under 800 words. This is scannable in 10 minutes.

#### Tier 2 Design (Study Notes + Framework Cards)

Each asset file has a specific purpose and structure:

- **`summary.md`** — The structured overview: core question, arguments with credibility badges, logic map (ASCII), counter-intuitive insights, speaker mental model description.
- **`framework-card.md`** — One named framework per file (if multiple frameworks, create multiple files). Contains: name, one-line description, visual diagram (ASCII), decision rules, when-to-use triggers, when-NOT-to-use (boundary conditions), origin (who said it, based on what evidence).
- **`decision-checklist.md`** — A checklist the user can copy into Notion/Obsidian. "When you encounter X situation, ask: 1. ... 2. ... 3. ..." Derived from the episode's frameworks.
- **`interview-answer-bank.md`** — 3–5 interview/presentation-ready talking points. Each has: the question it answers, the 30-second response, the 60-second response (with example), and the key terms to drop for credibility.
- **`terms.md`** — Glossary of domain terms from this episode. Term + one-sentence definition + "you'll hear this when..." context.

#### Tier 3 Design (Interactive HTML Course)

Structure the course as **4–6 modules**. Same arc as codebase-to-course but reframed for knowledge internalization:

| Module Position | Purpose | Why it matters |
|---|---|---|
| 1 | "Here's the core question this episode answers — and why it matters right now" | Frame as a solution to a problem the learner actually has |
| 2 | The speaker's mental model | Understand *how* they think, not just their conclusions — the meta-skill |
| 3 | The counter-intuitive turns | Challenge assumptions → behavior change |
| 4 | The reusable framework(s) | Extract structured tools. Name them, diagram them, give decision rules |
| 5 | The edge cases & failure modes | When does the framework break? Builds judgment, not just knowledge |
| 6 | From insight to action | Concrete "Monday morning" moves + Personal AI Growth Log |

This is a **menu, not a checklist**. Pick 4–6 modules that serve the conversation.

Course is not just readable lessons. It must create a learning loop:
- **Diagnostic pre-test** before the modules
- **Scenario quizzes** inside the course
- **Application exercise** after the course
- **24-hour review card** for recall
- **Debate Arena link** so the learner sees which claims are accepted, tentative, or challenged

**Each Tier 3 module should contain:**
- 3–6 screens (sub-sections that flow within the module)
- At least one **Original Words → Actionable Insight** translation block (see below)
- At least one interactive element (quiz or visualization)
- One or two "aha!" callout boxes
- A metaphor — NEVER reuse across modules. NEVER "building a house" or "cooking a meal."

**Original Words → Actionable Insight Translation Blocks:**

These replace code↔English blocks from codebase-to-course. Format:
- **Left side**: The speaker's verbatim quote — preserve their voice, tone, emphatic phrasing. Warm background, quotation marks, speaker attribution.
- **Right side**: The refined, actionable insight. Strip conversational framing. State the principle directly. Add a one-line "When to use this:" trigger.

**Tier 3 mandatory interactive elements:**
- **Conversation Flow Animation** — at least one. iMessage/WeChat-style exchanges dramatizing a key debate or tension: "Host pushes back → Guest refines → Aha moment emerges."
- **Framework Visualization** — at least one. Animated walkthrough of the central framework (decision tree, 2×2, maturity model, evaluation rubric). Each step reveals on tap.
- **Original Words → Actionable Insight Translation Blocks** — at least one per module.
- **Quizzes** — at least one per module, always scenario-based (see Quiz Philosophy below).
- **Glossary Tooltips** — on every domain term, first use per module.
- **Credibility Badges** — 🟢🟡🔴 displayed next to every core claim throughout the course.

**Do NOT present the curriculum for approval — just build it.**

**Build path decision:**
- Simple episode (single speaker, focused, ≤5 modules) → Phase 3 Sequential.
- Complex episode (multi-guest, wide-ranging, 6+ modules) → Phase 2.5 first, then Phase 3 Parallel.

### Phase 2.5: Module Briefs (complex episodes, Tier 3 only)

For complex episodes at Tier 3, write a brief for each module before writing HTML.

Read `references/module-brief-template.md` for the template. Read `references/content-philosophy.md` for content rules.

**For each module, write `course-name/briefs/0N-slug.md` containing:**
- Teaching arc (metaphor, hook, key insight, "when would I use this?")
- Pre-extracted quotes and insights (copy-pasted from transcript with attribution)
- Credibility badges for every claim in the module
- Interactive elements checklist with build details
- Which reference file sections the writing agent needs
- Previous/next module context for transitions

### Phase 3: Build the Assets

#### Tier 1 Build

Write a single `learning-card.md` file. No build process, no HTML, no reference files needed. Just clear, structured markdown.

#### Tier 2 Build

Write each markdown asset file to `episode-slug/`. No build process needed — these are directly usable in any markdown-compatible knowledge base.

#### Tier 3 Build

Same directory-based HTML build as codebase-to-course:

```
course-name/
  styles.css       ← copied verbatim from references/styles.css
  main.js          ← copied verbatim from references/main.js
  _base.html       ← customized shell (title, accent color, nav dots)
  _footer.html     ← copied verbatim from references/_footer.html
  build.sh         ← copied verbatim from references/build.sh
  pretest.md       ← diagnostic scenario before study
  application-exercise.md ← apply the framework to user's work
  review-card.md   ← 24-hour recall card
  briefs/          ← module briefs (complex episodes only)
  assets/          ← Tier 2 markdown assets (summary, framework cards, etc.)
  modules/
    01-intro.html
    02-mental-model.html
    ...
  index.html       ← assembled by build.sh
```

**Step 1: Setup** — Create the course directory. Copy four files verbatim from references: `styles.css`, `main.js`, `_footer.html`, `build.sh`.

**Step 2: Customize `_base.html`** — Read `references/_base.html`, substitute `COURSE_TITLE`, `ACCENT_*` placeholders, and `NAV_DOTS`.

**Step 3: Write modules** — Sequential or parallel path (same as codebase-to-course).

**Step 4: Assemble** — `cd course-name && bash build.sh` → produces `index.html`.

**Step 5: Copy Tier 2 assets** — Include all Tier 2 markdown files in an `assets/` subdirectory so the course directory is self-contained.

**Step 6: Add learning loop assets** — Write `pretest.md`, `application-exercise.md`, and `review-card.md`. Link them from the final course module and `EPISODE-HOME.md`.

**Critical rules (Tier 3 only):**
- **Never regenerate** `styles.css` or `main.js` — always copy from references
- Module files contain only `<section>` content — no boilerplate
- Use CSS `scroll-snap-type: y proximity` (NOT `mandatory`)
- Use `min-height: 100dvh` with `100vh` fallback on `.module`
- Interactive element JS is in `main.js`; wire up via `data-*` attributes
- Chat containers need `id` attributes; flow animations need `data-steps='[...]'`

### Phase 4: Review

For all tiers: review the output for accuracy against the transcript, consistency of speaker attribution, and credibility badge calibration. For Tier 3, also open `index.html` in the browser and walk the user through what was built.

### Phase 5: Knowledge Base Update & Growth Log

This phase runs for **all tiers** — it's what makes this a learning system, not just a course generator.

Phase 5 has six mandatory outputs:

1. `claim-ledger.md` — claim-level source anchors, evidence level, and status
2. `debate-arena.md` — AI-vs-guest challenge layer with web-search checks when needed
3. `wiki-change-report.md` — created/updated/reinforced/contradicted/open questions
4. `knowledge-entry.md` — cross-episode connection entry
5. `growth-log.md` — personal judgment shift
6. `framework-governance.md` — update or create if missing, then enforce it

#### 5a. Knowledge Entry (`knowledge-entry.md`)

A structured entry designed to connect this episode to the user's growing knowledge base.

**Before writing this entry, check the existing knowledge base for duplicates and relationships:**

1. **Detect genuine novelty.** Is this insight actually new, or is it the same mental model in different words? "Agent evals need scenario coverage" and "You should test agents across diverse tasks" are the same idea. Don't create two separate entries for one concept.
2. **Merge repeated ideas.** If this episode reinforces a framework already in the knowledge base, update the existing `framework-card.md` — add a "Reinforced by: [Episode X]" line. Don't create a duplicate framework card.
3. **Tag the relationship precisely:**
   - **Reinforces** — same conclusion, different evidence or context. Strength increases.
   - **Contradicts** — opposite conclusion from a credible source. This is the most valuable relationship. Flag it prominently.
   - **Extends** — same direction, adds nuance or boundary conditions. The original framework gets sharper.
   - **Unrelated** — genuinely different topic. Let it stand alone.
4. **Avoid knowledge base bloat.** After 20 episodes, the user should have ~10–15 framework cards, not 60. Each new episode should merge into existing frameworks more often than it creates new ones. The knowledge base is a *judgment model being refined*, not a *library being filled.*

**Framework admission rule:** Only create a new framework if it changes a decision rule. Otherwise, reinforce, extend, contradict, or merge into an existing framework/concept.

```markdown
# Episode Knowledge Entry: [Episode Title]

## Core Thesis
[One paragraph]

## Reusable Frameworks
- **Framework Name**: [one-line description + decision rule]
- **Relationship to existing KB**: [Reinforces / Contradicts / Extends] [existing framework name]
  - If NEW: "New framework — no existing equivalent in KB"
  - If REINFORCES: "Same conclusion as [[existing-framework]], adds evidence from [domain]"
  - If CONTRADICTS: "⚠️ Opposite conclusion from [[existing-framework]]. [Speaker X] says Y, while [Speaker Z] says not-Y. Resolution unclear — flag for your own judgment."
  - If EXTENDS: "Builds on [[existing-framework]] by adding boundary condition: [specific condition]"

## Key Concepts Introduced
- concept-1, concept-2, concept-3
- **Already in KB**: [concepts that overlap with existing entries — note which entries]

## Connects To Previous Knowledge
- **Similar to**: [concepts from other episodes that align]
- **Contradicts**: [concepts from other episodes that conflict — this is gold]
- **Extends**: [concepts this episode builds upon]

## Credibility Summary
- 🟢 High-evidence claims: [count + summary]
- 🟡 Medium-evidence claims: [count + summary]
- 🔴 Low-evidence claims: [count + summary]

## KB Maintenance Actions
- [ ] Update [[existing-framework-card]] with reinforcement/extension from this episode
- [ ] Merge [concept] into existing [[entry]] — no new card needed
- [ ] Create new framework card for [genuinely new concept]
- [ ] Flag [[contradiction]] for user attention — two credible sources disagree
```

#### 5b. Claim Ledger (`claim-ledger.md`)

Every core claim must be traceable:

```markdown
# Claim Ledger: [Episode Title]

| ID | Extracted Claim | Evidence | Status | Timestamp | Source Line | Exact Anchor | What Would Upgrade Confidence |
|---|---|---|---|---|---:|---|---|
| C1 | [claim] | Medium | tentative | 12:34 | 88 | "[short exact anchor]" | [data/source needed] |
```

Evidence is not enough. Status controls wiki behavior:
- `accepted`: can be used as working judgment
- `tentative`: must carry caveat
- `challenged`: must link to Debate Arena before reuse
- `disputed`: show both sides
- `outdated`: web-check before reuse
- `rejected`: do not use in active wiki knowledge

#### 5c. Debate Arena (`debate-arena.md`)

Challenge high-impact claims before they enter the wiki.

For each challenged claim:

```markdown
## Debate N: [Claim]

### Challenged Quote
[verbatim quote]

Transcript anchor: [line/timestamp]

### Guest Claim
[what the speaker is really asserting]

### AI Challenge
[logic gap, sample bias, causal overreach, missing counterfactual, or conflict with existing KB]

### Web Search Check
[only when the claim may be time-sensitive or externally verifiable]

### Verdict
Status: [accepted/tentative/challenged/disputed/outdated/rejected]

Wiki action: [keep / keep with caveat / mark disputed / reject / needs update]
```

AI can challenge stable reasoning issues without web search. Use web search for product status, company metrics, market outcomes, model capability, research claims, and legal/regulatory facts.

#### 5d. Wiki Change Report (`wiki-change-report.md`)

Make compounding visible:

```markdown
# Wiki Change Report: [Episode Title]

## Created
[new framework/concept/evidence pages]

## Updated
[index, logs, existing framework pages]

## Reinforced
[existing ideas strengthened]

## Contradictions
[credible conflicts]

## Open Questions
[what still needs validation]

## Next Merge Targets
[where future episodes should attach]
```

#### 5e. Personal AI Growth Log (`growth-log.md`)

This is the most important artifact for long-term learning. It tracks not what the user *learned*, but how their *judgment model changed*:

```markdown
# Personal AI Growth Log: [Episode Title]

## What I used to think
[Before this episode, my working assumption was...]

## What I now think
[After this episode, my updated understanding is...]

## What changed
[The specific insight or framework that caused the shift]

## Next time I encounter [X situation], I will ask:
1. [Question 1]
2. [Question 2]
3. [Question 3]

## I want to test this by
[A concrete experiment or application in the next 2 weeks]
```

The growth log should feel personal and honest. It's not a summary — it's a before/after snapshot of the user's AI judgment. Over 10+ episodes, these entries form a visible trajectory of deepening product intuition.

---

## Feedback Handling

Real users give feedback. The skill should absorb it, not defend against it.

### When User Gives Feedback

1. **Classify the feedback type:**
   - **Content**: "This framework is wrong," "You missed the part where she said X," "This insight is too generic."
   - **Structure**: "This module order doesn't make sense," "Too many screens," "The quiz doesn't match the content."
   - **Tone**: "This feels too academic," "Too casual for my use case," "The language is too marketing-y."
   - **Tier**: "This should have been a learning card, not a full course," "I wanted more depth on this one."
   - **Learner mode**: "I said product judgment but this feels like engineering notes," "I need interview prep, not architecture."

2. **Revise the current output immediately.** Do not explain why the original was right. Do not say "but the speaker actually said..." The user is telling you the output didn't work for them — believe them.

3. **If the feedback is durable** (structural preference, learner mode correction, tier preference), update how you generate for this user going forward. Note it: "Got it — I'll bias toward [X] and away from [Y] for future episodes. This preference will persist across sessions."

4. **If the feedback reveals a knowledge gap** (user knows something about the episode that the transcript didn't capture, or has domain context the agent missed), incorporate it and thank the user. Their context is real — the transcript is a partial record.

### What NOT to Do with Feedback

- **Do not defend** the previous output. "I structured it this way because..." is never the right response. The user is the judge of utility.
- **Do not over-correct.** If the user said "this one framework is too vague," fix that framework. Don't strip all frameworks from all future outputs.
- **Do not ask the user to do the agent's job.** "What specifically would you like me to change?" is lazy when the feedback type is clear. Diagnose and fix. Only ask clarifying questions when the feedback is genuinely ambiguous.
- **Do not silently ignore** feedback that would require restructuring. If the user says "I actually care about commercialization, not engineering," and you're already at Phase 4 — say "That's a significant shift — let me re-generate with the right lens" rather than grafting a few business bullet points onto engineering-focused output.

---

## Use Case Outputs (Scenario-Specific Generation)

Beyond the three modes (Preview / Course / Review), users often have a specific real-world use case in mind. When the user states or implies one of these, bias the output structure accordingly.

### Scenario Outputs

| Use Case | Trigger phrases | Output adaptation |
|---|---|---|
| **Mentor Brief** | "Brief my mentor," "汇报用," "explain to my team lead" | Condense to: core insight in 3 sentences, why it matters to our project specifically, one framework the team can adopt this week. Max 500 words. |
| **Interview Prep** | "Interview prep," "面试," "I have an interview" | Output: 3 likely interview questions this episode helps answer, 60-second response framework for each, key terms to drop for credibility, common follow-up questions and how to handle them. |
| **Project Application** | "Apply to my project," "用到我的项目," "how does this relate to what I'm building" | Ask 2 clarifying questions about the user's project, then map every framework and insight to their specific context. "Your project has X characteristic — here's how this framework applies differently." |
| **Reading List** | "What should I read next," "延伸阅读," "go deeper" | Extract: concepts mentioned that deserve deeper study, papers referenced (with explicit titles), related frameworks from other thinkers, what to search for. Format as a prioritized list with "read this first" and "read this if you want to go deeper." |
| **Debate Prep** | "Debate prep," "反驳," "someone told me X," "push back on" | Output: the popular-but-wrong claim this episode dismantles, the 3-sentence rebuttal using the episode's framework, the most likely counter-argument and how to handle it, what evidence to cite. |

### How to Detect the Use Case

The user won't always say "I need interview prep." They'll say "I have a PM interview next week and I'm bingeing AI podcasts." That's interview prep. They'll say "My CTO keeps pushing multi-agent and something feels off." That's debate prep.

**When in doubt, ask:** "It sounds like you're planning to use this for [detected use case]. Want me to bias the output that way, or keep it general?"

---

## Environment Adaptability & Fallback Strategy

The build process assumes a file-writing environment with reference files available. When that's not the case, degrade gracefully:

| Environment | Detection | Behavior |
|---|---|---|
| **Full environment** (Claude Code, Codex with FS access) | Reference files exist, can run shell | Tier 3: full directory build + `build.sh` |
| **File writing, no references** | Can Write files but `references/` is missing | Tier 2: write markdown assets directly. Tier 3: inline all CSS/JS into a single `index.html` (no build step). |
| **No file writing** (ChatGPT, web chat) | Write tool errors or unavailable | Output everything inline in the conversation. Tier 1: full learning card in chat. Tier 2: each asset as a separate chat message with copy-paste-friendly formatting. Tier 3: suggest the user switch to a file-writing environment. |
| **Minimal context** (mobile, voice) | Short context window detected | Auto-downgrade to Tier 1. Output only the learning card. Offer to email or save the rest. |

**Rule of thumb:** Never fail because the environment is too limited. Always deliver the highest tier the environment supports, and tell the user what they'd get in a richer environment.

---

## Design Identity (Tier 3)

The visual design should feel like a **beautiful developer notebook** — warm, inviting, and distinctive. Read `references/design-system.md` for the full token system.

- **Warm palette**: Off-white backgrounds (like aged paper), warm grays, NO cold whites or blues
- **Bold accent**: One confident accent color (vermillion, coral, teal — NOT purple gradients)
- **Distinctive typography**: Display font with personality for headings (Bricolage Grotesque, or similar bold geometric face — NEVER Inter, Roboto, Arial, or Space Grotesk). Clean sans-serif for body (DM Sans or similar). JetBrains Mono for code.
- **Generous whitespace**: Modules breathe. Max 3–4 short paragraphs per screen.
- **50% visual weight**: Every screen balances text with visual elements — diagrams, quote blocks, animations, callout boxes. Never a wall of text.
- **Alternating backgrounds**: Even/odd modules alternate between two warm background tones for visual rhythm
- **Dark quote blocks**: IDE-style with Catppuccin-inspired syntax highlighting on deep indigo-charcoal (#1E1E2E) for verbatim quotes
- **Depth without harshness**: Subtle warm shadows, never black drop shadows

---

## Quiz Philosophy

Every quiz tests **application, not memory**. "What did the guest say?" is never acceptable.

### Quiz Types

**1. Scenario Judgment** — "Here's a situation. What do you do?"
> *Your team wants to replace a rule-based pipeline with an Agent. The boss asks if it's worth it. Using this episode's framework, what's the first question you should ask?*

**2. Framework Application** — "Apply the named framework to this case."
> *Apply the Two-Question Agent Test to this scenario: [details]. Which answer is correct?*

**3. Tradeoff Dilemma** — "Both options are valid. Which would the speaker recommend?"
> *Option A: Fine-tune a small model. Option B: Use few-shot prompting with a large model. Using the speaker's evaluation criteria, which would they choose for a production customer-facing feature?*

**4. Spot-the-Bad-Call** — "Which assumption does this decision violate?"
> *A founder says: 'We'll launch with 5 specialized agents so the system is more capable from day one.' Which principle from this episode does this violate?*

**5. Product Judgment** (AI-product-specific) — "Should you build this?"
> *Your engineer proposes RAG + fine-tuning + multi-agent for a customer support bot. Using this episode's framework, how do you determine if this is over-engineered?*

**6. Technical Understanding** (AI-product-specific) — "Do you understand the tradeoff?"
> *The speaker says multi-agent coordination overhead grows quadratically. If you have 5 agents, how many agent-to-agent communication channels exist? Why does this matter for latency?*

**7. Presentation / Interview Response** (AI-product-specific) — "Can you articulate it?"
> *You have 60 seconds to explain this episode's core insight to your mentor/team. Which structure would you use?* (multiple choice of narrative structures, then ask user to actually articulate it)

**8. Rebuttal** (AI-product-specific) — "Defend against bad reasoning."
> *Someone tells you: 'The more agents you add, the smarter the system gets.' Using this episode's framework, construct a 3-sentence rebuttal.*

Quiz types 1–4 apply to all learning goals. Types 5–6 are priority for Product and Engineering goals. Types 7–8 are priority for Interview and general professional development.

---

## Gotchas (Common Failure Points)

Read `references/gotchas.md` for the full checklist.

### Transcript-Specific Gotchas

- **Colloquial language left raw**: Transcripts contain filler words, false starts, mid-sentence corrections. Clean aggressively while preserving meaning and voice.
- **Timestamps not stripped**: `[00:03:15]` or `[03:15]` markers must be removed from all outputs.
- **Speaker repetition not collapsed**: Guests restate the same point 2–3 times with different wording. Collapse into the single clearest articulation.
- **Transcription errors in technical terms**: "RAG" → "rag," "vector database" → "victor database," "fine-tuning" → "fine tuning." Correct based on context. Flag uncertain corrections.
- **Speaker label inconsistency**: Same speaker appearing as "张老师," "张某," "张总." Normalize to one label.
- **Cross-talk and interruptions**: When speakers overlap, extract the dominant thread. If both are meaningful, present sequentially with a note.
- **Inside jokes and references**: References to previous episodes or "as we discussed offline." Provide context in a tooltip or cut if it doesn't add value.
- **Chinese-English code-switching**: Preserve natural mixing ("我们做了一个 agent-based 的 architecture"). Don't force pure Chinese or pure English.
- **Podcast intro/outro segments**: Skip sponsor reads, subscribe CTAs, and housekeeping.
- **Conversational tangents**: If a tangent doesn't serve the core thesis, summarize in one sentence or cut.

### Content Gotchas

- **Knowledge-check quizzes** — The #1 failure mode. Every quiz must be scenario-based. "What did X say?" is never acceptable.
- **Quote blocks without actionable translations** — Every verbatim quote must pair with a "When to use this:" trigger. A quote alone is inspiration; a quote with a trigger is a tool.
- **Missing credibility badges** — Every claim in the output needs a 🟢🟡🔴 badge. If you don't know the evidence basis, default to 🔴 and note it.
- **Metaphor overload** — One per module. Never reuse. Never "building a house" or "cooking."
- **Passive module titles** — Module titles should promise transformation. Not "Agent Architecture" but "Why Your Multi-Agent System Is Probably Over-Engineered."
- **Missing "when would I use this?"** — Every module must answer this in the first two screens.
- **Over-indexing on one speaker** — In multi-guest episodes, represent all substantive perspectives.
- **Skipping the growth log** — Phase 5 is mandatory for all tiers. Without it, this is a summarizer, not a learning system.
- **Defaulting to Tier 3** — The HTML course is for landmark episodes only. Default to Tier 2 unless the user asks for more.
- **Ignoring the learning goal** — If the user said "I want product judgment," don't give them an engineering-deep output.

---

## Reference Files

The `references/` directory contains detailed specs. **Read them only when you reach the relevant phase** — not upfront.

### Shared with codebase-to-course (copy verbatim)

These four files are identical to the codebase-to-course skill. If both skills are installed, they can share a single copy via symlink:

- **`references/styles.css`** — All CSS. Copy verbatim. Never regenerate.
- **`references/main.js`** — All interactive element JS. Copy verbatim. Never regenerate.
- **`references/_footer.html`** — Footer template. Copy verbatim.
- **`references/build.sh`** — Assembly script. Copy verbatim.

### Podcast-specific (requires adaptation from codebase-to-course)

- **`references/content-philosophy.md`** — **Adapted.** Visual density rules, metaphor guidelines, quiz design, tooltip rules. Replace code↔English guidance with quote↔insight translation guidance. Read during Phase 2.5 (briefs) and Phase 3 (writing).
- **`references/gotchas.md`** — **Adapted.** Add all podcast-specific gotchas from this SKILL.md (transcript cleaning, timestamps, repetition collapsing, etc.) alongside the general gotchas. Read during Phase 3 and Phase 4 (review).
- **`references/module-brief-template.md`** — **Adapted.** Replace code-snippet extraction fields with quote extraction fields. Read only for complex episodes at Tier 3.
- **`references/design-system.md`** — **Mostly identical.** Same CSS tokens. Add `.quote-block`, `.credibility-badge`, `.insight-card`, `.growth-log` visual treatments. Tier 3 only.
- **`references/interactive-elements.md`** — **Adapted.** Replace code↔English block patterns with Original Words ↔ Actionable Insight block patterns. Replace architecture diagrams with framework visualizations. Replace group chat animations with conversation flow animations. Add scenario quiz examples specific to AI product contexts. Tier 3 only.

### New files (podcast-to-course only)

- **`references/_base.html`** — Same structure as codebase-to-course. Substitutes `COURSE_TITLE`, `ACCENT_*`, `NAV_DOTS`.
- **`references/tier1-example.md`** — A complete, annotated Tier 1 learning card showing the quality bar (the example from this SKILL.md, expanded).
- **`references/tier2-example.md`** — Complete, annotated Tier 2 assets showing the quality bar.
- **`references/episode-home-template.md`** — Template for the single user-facing episode entry point. Read during Phase 3 or final assembly.
- **`references/claim-ledger-template.md`** — Template for claim IDs, evidence, status, source anchors, and confidence upgrade criteria. Read during Phase 5.
- **`references/debate-arena-template.md`** — Template for AI-vs-guest challenges and web-search checks. Read during Phase 5 before final wiki insertion.
- **`references/wiki-change-report-template.md`** — Template for created/updated/reinforced/contradicted/open-question reporting. Read during Phase 5.
- **`references/framework-governance-template.md`** — Template for preventing framework bloat. Read when creating or updating `ai-judgment-kb/framework-governance.md`.
- **`references/claim-status-policy-template.md`** — Template for accepted/tentative/challenged/disputed/outdated/rejected claim statuses. Read when creating or updating `ai-judgment-kb/claim-status-policy.md`.
