# Business Knowledge — Insights Hub

A personal library of business wisdom: beautiful, self-contained
**insights pages** distilled from the conversations that matter — the world's
best operators, writers, and thinkers.

Each page is built from the **real source content** (YouTube transcript or
article text), read in full, and distilled into key insights, real quotes,
and concrete actions you can take today.

**Live site (GitHub Pages):** https://niba-tech.github.io/Business-Knowledge/

## What's inside

| Path | What it is |
| --- | --- |
| `index.html` | The hub — a library grid. New pages are added here as cards. |
| `<slug>-insights.html` | Individual insights pages (e.g. `seth-godin-insights.html`). |
| `assets/img/` | Thumbnails referenced by the hub cards. |
| `.opencode/skills/media-to-insights/` | The reusable **media-to-insights** skill that automates the whole pipeline. |
| `.opencode/agents/` | *(optional)* support agents. |

---

## The process (how a page gets made)

The whole workflow is captured in the **`media-to-insights`** opencode skill.
This section documents it so you can also run it by hand.

### 1. Fetch the source content

**YouTube videos & Shorts** — download captions with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp):

```bash
# probe the video
yt-dlp --skip-download --print "%(title)s | %(uploader)s | %(duration_string)s | %(upload_date)s" "<URL>"

# list captions, prefer manual en over auto (en-orig)
yt-dlp --skip-download --list-subs "<URL>"

# download subtitles only (no video/audio)
yt-dlp --skip-download --write-subs --write-auto-subs \
       --sub-langs "en" --sub-format "srt" -o "video.%(ext)s" "<URL>"

# download the thumbnail
yt-dlp --skip-download --write-thumbnail -o "thumb.%(ext)s" "<URL>"
```

**Articles / blog posts** — fetch the page text (WebFetch/curl) and save it as a
plain-text file.

### 2. Convert the transcript to clean text

```bash
python3 scripts/srt_to_text.py video.en.srt
```

Produces `video.en.txt` (`[HH:MM:SS] text`, timestamped) and
`video.en_plain.txt` (plain). Included in the skill at `.opencode/skills/media-to-insights/scripts/srt_to_text.py`.

### 3. Read it — all of it

Read the **entire** transcript or article (chunk long ones into sections)
before writing anything. Never summarize from the title or intro.

### 4. Distill

Extract, in this order:
1. **One-paragraph takeaway** — the single perspective shift.
2. **Mental model / framework** — the structure the author uses to explain the world.
3. **Key insights** — distinct big ideas, each backed by a **real quote** from the source.
4. **Evidence / data** cited by the source (keep the actual numbers).
5. **Concrete applications** — "do this today" steps with time-boxes.
6. **Quotes worth keeping** — punchy, self-contained lines.

### 5. Build the HTML page

Copy the template `.opencode/skills/media-to-insights/templates/insights-template.html`
→ `<slug>-insights.html` and fill the `{{TOKEN}}` placeholders.

Non-negotiables:
- **Fully self-contained:** thumbnail embedded as a base64 data-URI
  (`python3 -c "import base64;print(base64.b64encode(open('thumb.jpg','rb').read()).decode())"`);
  no local file references; the only external dependency is an optional Google Fonts link.
- **Real quotes only.** If the auto-captions garbled a name/term, fix it or flag it.
- Always include **concrete applications**, not just abstract takeaways.
- Keep the dark editorial design (navy + gold, Fraunces/Inter) so the hub looks cohesive.

### 6. Register it in the hub

Edit `index.html`:
1. Copy the newest `<a class="card">` block (there's a marked `NEW CARDS` comment).
2. Set `href="<slug>-insights.html"`, and `assets/img/<slug>.jpg` (copy the thumbnail there).
3. Update the tag-badge, `.meta` (date/source), `<h3>` title, and `<p>` blurb.
4. Always use **relative links** — the site lives under a GitHub Pages sub-path.

### 7. Verify & publish

```bash
open index.html          # click through to the new page locally
git add -A
git commit -m "Add <Title> insights page"
git push                 # GitHub Pages auto-rebuilds
```

Live at `https://niba-tech.github.io/Business-Knowledge/<slug>-insights.html`.

---

## Using the skill with opencode

The skill is stored twice — both are identical:

- **Global install** `~/.config/opencode/skills/media-to-insights/` — available in every project.
- **In-repo copy** `.opencode/skills/media-to-insights/` — loaded automatically whenever opencode opens this repo.

**Restart opencode after installing/editing a skill** — skills load only at startup.

### How to invoke it

Just paste a URL into a session, e.g.:

> use media-to-insights on https://www.youtube.com/watch?v=abc123
> make insights for https://example.com/great-article

Or invoke it by name when it matters: mention "media-to-insights" or
"Insights page from this video."

The skill handles **YouTube videos**, **YouTube Shorts**, and **articles**.
Short/deep flow differences are built in (Shorts → compact page; articles →
no thumbnail block).

### Prerequisites (first-time setup on a new machine)

```bash
# 1. Python >= 3.10 (yt-dlp requires it)
brew install python@3.13

# 2. yt-dlp (installed via pipx for an isolated env)
brew install pipx && pipx ensurepath   # then open a new terminal
pipx install --editable <path/to/yt-dlp-src>   # or: pipx install yt-dlp

# 3. Git credentials for GitHub (macOS keeps the token in Keychain)
git config --global credential.helper osxkeychain
#   create a token at https://github.com/settings/tokens/new (scope: repo),
#   then the first `git push` prompts for username + token as password.

# 4. Clone the hub on a new machine
git clone https://github.com/niba-tech/Business-Knowledge.git
#   the repo's .opencode/skills/ comes with the skill already installed.
```

---

## Adding a page manually (no opencode)

1. Download captions + thumbnail (step 1 above).
2. `python3 .opencode/skills/media-to-insights/scripts/srt_to_text.py video.en.srt`
3. Read the transcript, distill insights.
4. Copy the template to `<slug>-insights.html` and fill it in.
5. Copy the thumbnail to `assets/img/<slug>.jpg`.
6. Add a card to `index.html`, verify locally, commit, and push.

## Repository layout for GitHub Pages

No CI files needed. Pages is configured in the repo Settings:
**Settings → Pages → Deploy from a branch → `main` → `/ (root)`**.
Pushing to `main` triggers an automatic rebuild.