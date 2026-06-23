# Gotchas — Common Failure Points

> **When to read this:** During Phase 3 (writing module HTML) and Phase 4 (review). Check every one before considering a course complete.

---

## Podcast-Specific Gotchas (Tier 3 HTML)

### CRITICAL: Never use absolute positioning for .screen-annotation
**Never** use `position: absolute`, `right` negative offsets, `top`, `::after` pseudo-elements, or any out-of-flow positioning on `.screen-annotation`. This pattern is fragile: it breaks when the viewport is too narrow for the offset, when the annotation is taller than the screen content, and when `transform` or `:has()` create new stacking contexts.

**Always** keep `.screen-annotation` in normal document flow as an inline card. It renders with a left accent border, warm background, and monospace label — stable on all screen widths with zero overflow risk.

❌ **Forbidden pattern:**
```css
.screen-annotation {
  position: absolute;
  right: -180px;  /* NEVER do this */
}
```

✅ **Required pattern:**
```css
.screen-annotation {
  margin: 0.75rem 0;
  padding: 0.6rem 0.85rem;
  /* ... inline card styling only, no position/right/top */
}
```

### CRITICAL: data-correct on quiz-feedback breaks HTML
**Never** put feedback text in a `data-correct` attribute on `.quiz-feedback`. Chinese quotes `""` and English quotes inside the text will break the HTML attribute boundary.

**❌ Wrong:**
```html
<div class="quiz-feedback" data-correct="新路说这是"信仰"问题——不要默认"新协议更好"。">
```

**✅ Correct:**
```html
<div class="quiz-feedback">
  <span class="quiz-feedback-text" hidden>新路说这是"信仰"问题——不要默认"新协议更好"。</span>
</div>
```
The JS engine reads from `.quiz-feedback-text` textContent — no escaping needed.

### Framework viz button class must be fw-btn
The JS engine looks for `button.fw-btn` inside `.framework-visualization`. Don't use `fw-next` or other class names.

### Framework layers need 3 div.fw-layer elements
The JS engine hides all but the first `.fw-layer` on init. Every framework visualization must have exactly the number of layers it wants to reveal step by step (typically 3).

### quiz-options data-correct must be a number
`<div class="quiz-options" data-correct="2">` — the value is compared to `quiz-option[data-value]`. Both must be plain integers.

### Never put inline styles on fw-layer
The CSS handles `.fw-layer` styling including the hidden/revealed/active states. Inline `style="opacity:0.5"` or `style="background:..."` on `.fw-layer` will fight with the CSS.

### Screen annotations need the :has() guard
When a screen has a `<aside class="screen-annotation">`, the `.quote-translation` and `.framework-visualization` on that screen must NOT break out wide — the `:has()` rule in podcast-styles.css handles this. Don't override it.

---

## General Gotchas (all tiers)

### Tooltip Clipping
Translation blocks use `overflow: hidden` for code wrapping. If tooltips use `position: absolute` inside the term element, they get clipped. **Fix:** Tooltips must use `position: fixed` and be appended to `document.body`.

### Walls of Text
Every screen must be at least 50% visual. Convert any list of 3+ items into cards, any sequence into step cards or flow diagrams, any quote into a quote↔insight translation block.

### Recycled Metaphors
Every module needs its own metaphor. Never "building a house" or "cooking a meal." If you catch yourself reaching for the same metaphor twice, stop.

### Knowledge-check quizzes instead of application quizzes
The #1 content failure. "What did X say?" is never acceptable. Every quiz must place the learner in a realistic scenario.

### Missing credibility badges
Every claim in output needs a 🟢🟡🔴 badge. If evidence basis is unknown, default to 🔴.

### Inventing CSS class names instead of reading the CSS contract
**The #1 Tier 3 HTML failure mode.** The agent writes module HTML with class names it imagines (`.feature-cards`, `.quote-panel`, `.chat-flow`, `.duality-cards`, `.comparison-table`…) — none of which exist in any loaded stylesheet. The browser renders bare, unstyled HTML with only default typography. **Fix:** Read `podcast-styles.css` BEFORE writing any module HTML. Every class must exist in `podcast-styles.css`, `styles.css`, or `supplement.css`. If you need a new visual component, add its CSS to `supplement.css` first, then use it in HTML. See the DOM contract table in SKILL.md Step 2.5.

### Skipping Phase 5 (growth log + knowledge entry)
Phase 5 is mandatory for all tiers. Without it, this is a summarizer, not a learning system.
