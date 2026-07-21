const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");

test("homepage represents every published course directory", () => {
  const courseDirectories = fs.readdirSync(path.join(root, "courses"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
  const homepageSlugs = [...html.matchAll(/slug:\s*"([^"]+)"/g)]
    .map((match) => match[1])
    .sort();

  assert.deepEqual(homepageSlugs, courseDirectories);
});

test("hero uses a real editorial image and one primary library action", () => {
  assert.match(html, /<img[^>]+class="hero-image"[^>]+src="assets\/judgment-library-hero\.webp"/);
  assert.equal((html.match(/class="hero-cta"/g) || []).length, 1);
  assert.ok(fs.existsSync(path.join(root, "assets", "judgment-library-hero.webp")));
});

test("course archive includes a searchable library interface", () => {
  assert.match(html, /<section[^>]+id="library"/);
  assert.match(html, /<input[^>]+id="courseSearch"[^>]+type="search"/);
  assert.match(html, /addEventListener\("input"/);
  assert.match(html, /class="course-list"/);
});
