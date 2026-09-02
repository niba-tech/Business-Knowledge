---
name: media-to-insights
description: Turn any YouTube video, YouTube Short, or article URL into a beautiful, self-contained HTML "insights page" and register it in a knowledge hub. Use when the user gives a content URL (YouTube/video/short/Shorts/article/blog/long-read) and wants key insights, takeaways, notes, a summary page, or a reusable note added to their Business-Knowledge/personal notes site.
---

# media-to-insights

Produce polished, self-contained HTML notes pages from a single content URL,
and add them to the user's knowledge-hub library. The workflow mirrors the
pipeline used to build the existing "Seth Godin — The Art of Quitting" page:
fetch the real source content, read it in full, distill faithful insights,
render a beautiful standalone HTML page, register it in the hub, then commit
and push.

Knowledge-hub default repo: `/Users/nicubagiu/Porjects/YT-Business-knowledge/Business-Knowledge`
(hosted on GitHub Pages at `https://niba-tech.github.io/Business-Knowledge/`).

### Checkpoint/resume

On startup the skill checks for an existing `.checkpoint.json` in the working
directory. If found, it loads the saved state and resumes from the next step,
skipping already-completed work. The checkpoint contains:

- `step` — which step was last completed (1=fetched, 2=read, 3=distilled, 4=built, 5=registered)
- `transcript_text` — partial transcript text if step < 3
- `insights` — distilled insights if step < 4
- `url` and `title` — the source URL and title, so the skill can identify
  what to resume

If no checkpoint exists, the skill proceeds from Step 1 as normal.

## Rules of quality (non-negotiable)

1. **Never fabricate content.** Insights, quotes, and claims must come from
   what was actually read/heard — not from general knowledge about the author.
   If the transcript is ambiguous, say so rather than inventing a quote.
2. **Read the whole source before writing anything.** For video, read the
   entire timestamped transcript (chunk it in sections if long — thousands of
   lines is normal and expected). For articles, read the whole text.
3. **Be faithful and undistorted** — summarize, don't paraphrase away meaning,
   and flag obvious transcript errors (auto-captions garble names/terms).
4. **Exclude** podcast intros, subscribe asks, and ad reads from the insights.
5. **Every key insight gets a real quote** where the source has one.
6. **Every page must include concrete applications** ("do it today" steps),
   not just abstract takeaways.

## Step 1 — Identify the source and output location

Ask for (or derive) the URL, then classify it.

### Checkpoint/resume support

A checkpoint file `.checkpoint.json` in the working directory stores progress
so the skill can resume later if AI tokens are exhausted or the process is
interrupted. On startup the skill checks for an existing checkpoint and
automatically resumes from the last saved step.

Checkpoint steps:
1. **fetched** — content (captions/markdown) has been downloaded
2. **read** — full transcript/article text has been read/extracted
3. **distilled** — insights have been generated
4. **built** — HTML page has been constructed
5. **registered** — page has been added to the hub

If a checkpoint exists with step < 5, the skill will skip completed steps
and resume from the next one. The checkpoint also stores the partial
transcript text and any insights distilled so far, so no work is lost.

| Source | Fetch method |
| --- | --- |
| YouTube video / Short | yt-dlp captions (below) |
| Article / blog / long-read | `WebFetch` (format `markdown`). If the article is paywalled or the fetch returns junk, try `curl -sL` and strip HTML, or report back to the user. |

Working directory: put intermediate files in a new per-source working folder
(e.g. the hubs repo folder by default, or a scratch dir like
`/var/folders/rz/trfwjzhs1675w4lchtmvnlrc0000gn/T/opencode` when the user just
wants a preview without publishing).

Publishing target: the knowledge-hub repo
(`/Users/nicubagiu/Porjects/YT-Business-knowledge/Business-Knowledge`) by default. If it isn't a git
repo or doesn't exist, clone it first:
`git clone https://github.com/niba-tech/Business-Knowledge.git`. Ask the user
if there's any doubt about where the file should live.

## Step 2 — Fetch the content

### YouTube videos and Shorts (yt-dlp)

yt-dlp is installed via pipx: `~/.local/bin/yt-dlp`. Use it in this order:

1. Probe: `~/.local/bin/yt-dlp --skip-download --print "%(title)s | %(uploader)s | %(duration_string)s | %(upload_date)s" "<URL>"`. Repair the URL to a clean watch URL (`https://www.youtube.com/watch?v=<id>`) if needed. Shorts work identically.
2. Check caption availability: `~/.local/bin/yt-dlp --skip-download --list-subs "<URL>"`.
   - Prefer a **manual** track (e.g. `en` English) over auto (`en-orig`), and English over other languages. If no English, use the best available or ask the user.
3. Download subs only:
   `~/.local/bin/yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "<lang>" --sub-format "srt" -o "<workdir>/video.%(ext)s" "<URL>"`
4. Convert to clean timestamped text with the bundled helper:
   `python3 <skill_base>/scripts/srt_to_text.py <workdir>/video.en.srt`
   This writes `video.en.txt` (`[HH:MM:SS] text`) and `video.en_plain.txt`.
5. Download a thumbnail for the page:
   `~/.local/bin/yt-dlp --skip-download --write-thumbnail -o "<workdir>/thumb.%(ext)s" "<URL>"`, then convert to a web-safe JPEG with `sips -s format jpeg -s formatOptions 85 thumb.webp --out thumb.jpg`.
6. Gather page metadata (title, uploader, view/like/comment counts, URL) via `--print` for the HTML hero chips.

### Articles (WebFetch)

Fetch to markdown, save the extracted body to `<workdir>/source.md`, and read
it fully. If there are multiple pages or long-form material, chunk the reading.
Grab the article title, author, publication, publication date, and page URL
for the hero chips.

---

## Step 2 — Save checkpoint after content fetch

After successfully downloading captions (YouTube) or fetching article markdown
(Article), save a checkpoint file `.checkpoint.json` in the working directory
so the process can be resumed later if AI tokens are exhausted.

## Step 3 — Read the entire source

Read the full content before writing. For long videos (multi-hour), read the
transcript in sequential chunks — do not stop early. For very large content,
note word-count and make sure you have seen the ending, not just the opening.

For **Shorts** (< ~3 min): content is thin by nature. Produce a compact page —
takeaway, the 3–6 real ideas, applications, a couple quotes. Do not pad.
If a Short genuinely has no substance, say so in the page instead of inflating.

---

## Step 3 — Save checkpoint after reading

After reading the full transcript (YouTube) or article (Article), save a
checkpoint so progress is preserved if the process is interrupted or AI tokens
are burned. The checkpoint stores the transcript text read so far and marks
the step as "read".

## Step 4 — Distill

Structure your thinking before building the page:

- **The one-paragraph takeaway** — the single shift in perspective the source
  creates.
- **The mental model / framework** — the recurring structure the author uses
  to explain the world, made explicit.
- **Key insights** — the distinct, non-overlapping big ideas (typically 5–14
  for a long podcast, 3–6 for an article). Each with a real quote.
- **Evidence / data** the source cites (keep the actual numbers).
- **Concrete applications** — "do this today" actions with rough time-boxes.
- **Quotes worth keeping** — punchy, self-contained lines.

---

## Step 4 — Save checkpoint after distillation

After distilling insights, save a checkpoint with the generated insights and
mark the step as "distilled". This allows resuming later even if AI tokens
are exhausted — the skill will load the saved insights and continue from
Step 5 (building the HTML page).

## Step 5 — Build the HTML page

Copy the bundled template
`<skill_base>/templates/insights-template.html` to
`<hub>/<slug>-insights.html` and replace every `{{TOKEN}}`.

Slug rules: honest, `kebab-case`, descriptive (e.g. `seth-godin-insights`).

Filling the tokens:

- `{{KICKER}}` — e.g. `Processed with yt-dlp · Full transcript read · Distilled notes`
- `{{HERO_TITLE_1}}` / `{{HERO_TITLE_EM}}` — a two-line headline; line 2 italic (`<em>`).
- `{{HERO_SUB}}` — 1–2 sentences on what the source is and what the page gives you.
- `{{HERO_CHIPS}}` — `<span class="chip">` items: source platform, view/like
  counts, published date, runtime.
- `{{THUMB_SRC}}` — base64 data-URI (inject with the python one-liner in the
  template comment) so the file is fully self-contained. For articles without
  a suitable image, drop the `.hero-art` block entirely.
- `{{GLASS_TITLE}}` / `{{GLASS_AUTH}}` — title + channel/publication overlaid on the thumbnail.
- Body tokens (`{{TLDR_*}}`, `{{INSIGHT_*}}`, `{{STEP_*}}`, `{{QUOTE_*}}`,
  `{{STAT*_*}}`, `{{SOURCE_*}}`, `{{DISCLAIMER}}`) — fill from your distillation.
  **Copy the component blocks** (`.card`, `.step`, `.quote`, `.stat`) to the
  number needed, then delete the placeholder example blocks. Remove sections
  that don't apply (e.g. `.stats` if the source cites no data) and the telltale
  `section:nth-child(even)` banding still reads naturally.

Page flow to follow where it fits the source (see the template's comment
block for the full recipe and the shallow-source variant).

Self-containment checklist:

- [ ] Thumbnail embedded as base64 data-URI (or `.hero-art` removed)
- [ ] No local file references that break when the HTML is copied
- [ ] Only external dependency is the optional Google Fonts `<link>` (degrades gracefully)

## Step 6 — Register it in the hub

Edit `<hub>/index.html`:

1. Copy the whole `<a class="card">` block of the latest entry (there is a
   clearly marked template comment in the file: `NEW CARDS — copy the whole
   <a class="card"> block`).
2. Change: `href` → the new slug, image reference (`assets/img/<slug>.jpg` —
   **copy the thumbnail into `<hub>/assets/img/`** with
   `cp <workdir>/thumb.jpg <hub>/assets/img/<slug>.jpg`), the tag-badge,
   the `.meta` date/source line, the card `<h3>` title, the 1–2 sentence
   `<p>` blurb, and the `go` label.
3. Keep the `NEW CARDS:` comment marker in place so future entries can be
   added the same way. The "coming soon" placeholder can remain below the
   newest real card.
4. The hub uses **relative links** (`seth-godin-insights.html`,
   `assets/img/...`) so it works under the GitHub Pages sub-path — never use
   absolute GitHub URLs.

## Step 7 — Verify

- Open `<hub>/index.html` locally (`open` on macOS) and click through to the
  new page; confirm the thumbnails render and the new card links resolve.
- Confirm the page HTML parses: tag balance check optional but quick
  (`python3 -c "import re;html=open('<page>').read();[print(t,len(re.findall(r'<%s[\s>]'%t,html)),len(re.findall(r'</%s>'%t,html))) for t in ['section','div','blockquote','footer','nav','header']]"`).

## Step 8 — Commit & push

Working tree is a git repo (the hub). Only commit after verification, and
only if the user asked to publish (default: yes for the hub workflow; confirm
first if the intent is ambiguous):

```
cd <hub>
git add -A
git commit -m "Add <Title> insights page"
git push
```

Push uses the user's stored keychain credential (osxkeychain + GitHub PAT);
if a push errors with `could not read Username`, remind the user:
`git config --global credential.helper osxkeychain`, then `git push` and enter
`nicubagiu` with their token as the password. GitHub Pages auto-rebuilds on
push — the new page is live at
`https://niba-tech.github.io/Business-Knowledge/<slug>-insights.html`.

## Troubleshooting

- **No JavaScript runtime warning from yt-dlp** — harmless; captions still download.
- **No captions available** for a video: tell the user; optionally fall back to
  `WebFetch` of a transcript if one exists, or skip with a clear message.
- **`pip` refuses the install** (externally-managed Homebrew Python) — never
  use `--break-system-packages`. Use pipx/venv as the original install did.
- **GitHub Pages stale** — pushing `main` triggers a rebuild; there is no CI
  file in this repo, Pages deploys from the `main` branch `/ (root)`.