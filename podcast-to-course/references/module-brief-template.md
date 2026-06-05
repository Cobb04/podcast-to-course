# Module Brief Template

> **When to read this:** During Phase 2.5 (planning checkpoint) for complex codebases. Fill in one brief per module, save to `course-name/briefs/0N-slug.md`. Each brief gives a parallel agent everything it needs to write one module without reading the codebase or SKILL.md.

---

## Module N: [Title]

### Teaching Arc
- **Metaphor:** [A fresh, specific metaphor — never "restaurant." See `references/content-philosophy.md` > Metaphors First]
- **Opening hook:** [1 sentence that connects to something the learner already knows from using the app]
- **Key insight:** [The one thing the learner should walk away understanding]
- **"Why should I care?":** [How this helps them steer AI / debug / make decisions]

### Code Snippets (pre-extracted)

Include the actual code the module will use in code↔English translation blocks. Copy-paste from the codebase with file path and line numbers. The writing agent will use these verbatim — it will NOT re-read the codebase.

File: src/example/file.ts (lines 12-24)
[paste actual code here]

File: src/another/file.ts (lines 45-52)
[paste actual code here]

### Interactive Elements

Check which elements this module needs. Include enough detail for the writing agent to build them.

- [ ] **Code↔English translation** — which snippet(s) from above
- [ ] **Quiz** — [number] questions, style: [scenario / debugging / architecture / tracing]. Brief description of each question's angle.
- [ ] **Group chat animation** — actors: [list]. Message flow summary: [who says what to whom, in what order]
- [ ] **Data flow animation** — actors: [list]. Steps: [sequence of highlights and packet movements]
- [ ] **Drag-and-drop** — items: [list], targets: [list]
- [ ] **Other** — [architecture diagram, layer toggle, pattern cards, etc.]

### Reference Files to Read

List only the sections the writing agent needs — not the whole file.

- `references/interactive-elements.md` → [section names, e.g., "Multiple-Choice Quizzes", "Group Chat Animation"]
- `references/design-system.md` → [only if needed for specific tokens not in the brief]
- `references/content-philosophy.md` → [always include — agent needs content rules]
- `references/gotchas.md` → [always include — agent needs the checklist]

### Connections

- **Previous module:** [Title — what it covered, so this module can build on it]
- **Next module:** [Title — what it will cover, so this module can set it up]
- **Tone/style notes:** [Any course-wide consistency notes: accent color name, actor naming convention, etc.]
