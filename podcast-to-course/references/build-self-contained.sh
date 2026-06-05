#!/bin/bash
# ============================================================
# PODCAST-TO-COURSE — UNIVERSAL BUILD SCRIPT
# Produces a self-contained index.html with all CSS/JS inlined.
#
# Usage:  bash build-self-contained.sh <episode-dir>
#
# Episode dir must contain:  _base.html, _footer.html, modules/*.html
# Reference files (from skill's references/): styles.css, podcast-styles.css, podcast-engine.js
# ============================================================
set -euo pipefail

EPISODE_DIR="${1:-}"
if [ -z "$EPISODE_DIR" ] || [ ! -d "$EPISODE_DIR" ]; then
  echo "Usage: bash build-self-contained.sh <episode-dir>"
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REFS="$SKILL_DIR/references"
OUTPUT="$EPISODE_DIR/index.html"
TMP="$EPISODE_DIR/.index-tmp.html"
rm -f "$TMP"

# ---- extract placeholders ----
BASE=$(cat "$EPISODE_DIR/_base.html")
TITLE=$(echo "$BASE" | grep -o '<title>[^<]*</title>' | sed 's|<[/]*title>||g')
ACCENT_COLOR=$(echo "$BASE" | sed -n 's/.*--color-accent:\s*\([^;]*\).*/\1/p' | head -1 | xargs)
ACCENT_COLOR=${ACCENT_COLOR:-#D94F30}
ACCENT_HOVER=$(echo "$BASE" | sed -n 's/.*--color-accent-hover:\s*\([^;]*\).*/\1/p' | head -1 | xargs)
ACCENT_HOVER=${ACCENT_HOVER:-#C4432A}
ACCENT_LIGHT=$(echo "$BASE" | sed -n 's/.*--color-accent-light:\s*\([^;]*\).*/\1/p' | head -1 | xargs)
ACCENT_LIGHT=${ACCENT_LIGHT:-#FDEEE9}
ACCENT_MUTED=$(echo "$BASE" | sed -n 's/.*--color-accent-muted:\s*\([^;]*\).*/\1/p' | head -1 | xargs)
ACCENT_MUTED=${ACCENT_MUTED:-#E8836C}

export EPISODE_DIR
NAV_DOTS=$(python3 << 'PYNAV'
import re, os
ep_dir = os.environ.get('EPISODE_DIR', '')
base = open(os.path.join(ep_dir, '_base.html')).read()
m = re.search(r'<div class="nav-dots".*?</div>', base, re.DOTALL)
if m:
    text = m.group()
    buttons = []
    i = 0
    while i < len(text):
        idx = text.find('<button', i)
        if idx == -1: break
        j = idx + 7
        in_quote = False
        q = ''
        while j < len(text):
            c = text[j]
            if in_quote:
                if c == q:
                    in_quote = False
            elif c == '"' or c == "'":
                in_quote = True
                q = c
            elif c == '>':
                j += 1
                break
            j += 1
        end_idx = text.find('</button>', j)
        if end_idx == -1: break
        buttons.append(text[idx:end_idx + 9])
        i = end_idx + 9
    print(' '.join(buttons))
PYNAV
)

echo "📦 Building self-contained index.html..."
echo "   Title: $TITLE"
echo "   Accent: $ACCENT_COLOR"

# === STEP 1: HTML head + base CSS ===
cat > "$TMP" << 'ENDOFFILE'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
ENDOFFILE
echo "<title>$TITLE</title>" >> "$TMP"
cat >> "$TMP" << 'ENDOFFILE'
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ===== BASE DESIGN SYSTEM (styles.css) ===== */
ENDOFFILE
cat "$REFS/styles.css" >> "$TMP"

cat >> "$TMP" << 'ENDOFFILE'

/* ===== PODCAST ADDITIONS (podcast-styles.css) ===== */
ENDOFFILE
cat "$REFS/podcast-styles.css" >> "$TMP"

cat >> "$TMP" << ENDOFFILE

/* ===== ACCENT OVERRIDE ===== */
:root {
  --color-accent:       $ACCENT_COLOR;
  --color-accent-hover: $ACCENT_HOVER;
  --color-accent-light: $ACCENT_LIGHT;
  --color-accent-muted: $ACCENT_MUTED;
}
</style>
</head>
<body>

<nav class="nav" id="nav">
  <div class="progress-bar" id="progress-bar"></div>
  <div class="nav-inner">
    <span class="nav-title">$TITLE</span>
    <div class="nav-dots" id="nav-dots">
      $NAV_DOTS
    </div>
  </div>
</nav>

<main id="main">
ENDOFFILE

# === STEP 2: process and append each module ===
for f in "$EPISODE_DIR"/modules/[0-9]*.html; do
  [ -f "$f" ] || continue
  python3 -c "
import re, sys
html = open('$f').read()

# Strip inline styles from fw-layer and fw-btn
html = re.sub(r'<div class=\"fw-layer\"[^>]*>', '<div class=\"fw-layer\">', html)
html = re.sub(r'<button class=\"fw-btn\"[^>]*>', '<button class=\"fw-btn\">', html)

# Fix quiz-feedback with data-correct -> hidden span (single-line, no embedded quotes)
html = re.sub(
    r'<div class=\"quiz-feedback\" data-correct=\"([^\"]+)\">',
    r'<div class=\"quiz-feedback\"><span class=\"quiz-feedback-text\" hidden>\1</span>',
    html
)

# Fix quiz-feedback with embedded Chinese/English quotes in data-correct
def fix_broken(html):
    result, i = [], 0
    marker = '<div class=\"quiz-feedback\" data-correct=\"'
    while i < len(html):
        idx = html.find(marker, i)
        if idx == -1:
            result.append(html[i:])
            break
        result.append(html[i:idx])
        text_start = idx + len(marker)
        end_idx = html.find('\">', text_start)
        if end_idx == -1:
            result.append(html[idx:])
            break
        text = html[text_start:end_idx]
        i = end_idx + 2
        result.append('<div class=\"quiz-feedback\"><span class=\"quiz-feedback-text\" hidden>' + text + '</span>')
    return ''.join(result)

html = fix_broken(html)
sys.stdout.write(html)
" >> "$TMP"
done

# === STEP 3: footer + JS ===
FOOTER=$(cat "$EPISODE_DIR/_footer.html" 2>/dev/null || echo '')
cat >> "$TMP" << ENDOFFILE

</main>

<footer class="course-footer">
  <div class="footer-title">$TITLE</div>
  $FOOTER
  <p style="margin-top:0.5rem;">Generated with podcast-to-course skill</p>
</footer>

<script>
/* ===== INTERACTIVE ENGINE (podcast-engine.js) ===== */
ENDOFFILE
cat "$REFS/podcast-engine.js" >> "$TMP"
cat >> "$TMP" << 'ENDOFFILE'
</script>
</body>
</html>
ENDOFFILE

# === STEP 4: finalize ===
mv "$TMP" "$OUTPUT"
SIZE=$(wc -c < "$OUTPUT" | awk '{printf "%.0f", $1/1024}')
echo "✅ Built: $OUTPUT (${SIZE} KB, self-contained)"
