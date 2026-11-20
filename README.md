# Kavinan Design Studio — Website Package

**www.kavinandesignstudio.com** · Architecture · Interior Design · Landscape · Project Management · Design + Build

A fast, SEO-ready, multi-page website with light and dark mode, built from your portfolio, project
images, logos and team photos — plus an automatic journal and FAQ publisher.

---

## 1. What's in the box

| Folder / file | What it is |
|---|---|
| `OPEN WEBSITE.html` | **Double-click to view the site on your computer.** |
| `Preview Website.bat` | Double-click for a full local preview at http://localhost:8000. |
| `offline/` | Copy of the site that opens from a local drive (made by `python build.py --offline`). |
| `public/` | **The finished website for the web server** (46 pages). Built automatically on GitHub. |
| `content/` | **Everything you edit** — text, projects, team, FAQs, journal posts. |
| `assets/` | Stylesheet, JavaScript, optimised images (WebP), logos, favicons. |
| `build.py` | Turns `content/` into `public/`. No installs needed — just Python. |
| `tools/optimize_images.py` | Converts new photos into fast responsive WebP images. |
| `tools/make_sketches.py` | Turns selected renders into pencil sketches for the sketch → render effects. |
| `illustrations.py` | The hand-drawn line illustrations used across the site. |
| `tools/auto_post.py` | Writes journal articles + FAQs automatically from your studio updates (Claude AI). |
| `.github/workflows/publish.yml` | Builds & publishes to GitHub Pages on every push and every morning at 06:00 IST (plus the AI writer). |
| `netlify.toml` | Optional: settings if you ever host on Netlify instead. |
| `docs/HOSTING-GITHUB-ZOHO.md` | **Step-by-step go-live guide** for GitHub Pages + your Zoho domain. |
| `docs/SEO-GUIDE.md` | **Your step-by-step SEO guide** — start here after launch. |
| `docs/DESIGN-STUDY.md` | The research and design rationale behind the site. |

### Pages

Home · Studio · Services (+5 service pages) · Projects (+22 project pages) · AI Platform (coming soon) · Team · Journal (+posts)
· FAQ · Contact · Privacy · Thank-you · 404 · plus `sitemap.xml`, `robots.txt`, `feed.xml` (RSS),
`llms.txt` (for AI search), `manifest.webmanifest`.

---

## 2. Preview on your computer

**Easiest: double-click `OPEN WEBSITE.html`** in this folder. It opens the offline copy
(`offline/index.html`), which works straight from your drive or a USB stick, no installs needed.
(Fonts and maps load when you're online; everything else works offline.)

**Full preview (exactly like the live site):** double-click **`Preview Website.bat`**.
It rebuilds the site and opens http://localhost:8000. Keep the black window open while browsing.
Or run it yourself:

```bash
python build.py --serve
```

**After editing content**, refresh the offline copy with:

```bash
python build.py --offline
```

> Why not `public/index.html`? That folder is the version for the web server: its links start
> with `/`, which on a local drive points to the root of `D:`. That's why pages looked broken when
> opened directly. Use `OPEN WEBSITE.html` or the `.bat` file instead.

---

## 3. Go live — GitHub Pages + Zoho Domains

Follow **[docs/HOSTING-GITHUB-ZOHO.md](docs/HOSTING-GITHUB-ZOHO.md)**, which covers it step by step:

1. Put this `website` folder on GitHub with **GitHub Desktop** (repository name `USERNAME.github.io`, public).
2. Settings → Pages → Source: **GitHub Actions**. The included workflow builds and publishes the site.
3. In **Zoho Domains → DNS Management** add 4 **A** records for `@` (185.199.108–111.153) and a **CNAME**
   `www → USERNAME.github.io`. Leave your Zoho Mail records (MX, SPF, DKIM) untouched.
4. Settings → Pages → custom domain `www.kavinandesignstudio.com` → **Enforce HTTPS**.
5. Get a free **Web3Forms** key and paste it into `content/site.json → form → access_key` so the forms email you.
6. Optional: add the `ANTHROPIC_API_KEY` secret so Claude writes articles from your updates.

From then on: edit files → commit & push in GitHub Desktop → live in about 2 minutes.
Every morning at 06:00 IST the site also rebuilds itself, releasing scheduled posts.

**Other hosts:** the site also runs on Netlify (`netlify.toml` included; set `form.provider` to
`"netlify"`) or any cPanel host (upload `public/` into `public_html`; `.htaccess` included).

---

## 4. Editing content

All text lives in `content/`. Edit with Notepad, VS Code or any text editor, then rebuild
(or just commit & push in GitHub Desktop — GitHub rebuilds and publishes by itself).

| To change… | Edit |
|---|---|
| Phone, email, addresses, hours, social links, Google Analytics | `content/site.json` |
| A project's text, facts or images | `content/projects.json` |
| Service pages | `content/services.json` |
| Team members and bios | `content/team.json` |
| FAQs | `content/faqs.json` |
| Quotes on the dark bands | `content/quotes.json` |
| Journal articles | `content/journal/*.md` |

`.json` files are strict: keep the quotes and commas exactly as they are. If the build shows an
error, it names the file and line.

### Add a journal post by hand

Create `content/journal/2026-11-20-my-post.md`:

```markdown
---
title: Your headline here
date: 2026-11-20
description: One or two sentences (130–160 characters) shown in Google results.
tags: Homeowners guide, Renovation
cover: s-gan-villa/sg_c2
project: s-gan-villa
---
Your article in Markdown. Use ## for headings, - for bullet lists, > for a pull quote,
**bold**, and [links](/contact.html).
```

- **Schedule it:** give it a future `date`. It stays hidden and goes live automatically on that morning.
- **Hide it:** add `draft: true`.
- `cover` is any image key from `assets/img/manifest.json` (folder/name without the size).

Six articles are already scheduled to publish every two weeks until January 2027.

### Let the studio write for you (automatic)

Drop a 2–3 line note into `content/updates/` whenever something happens on a project — see
`content/updates/README.md`. Every morning the automation turns new notes into a full article
plus 1–3 new FAQs. Every Monday it also writes one practical guide from `content/topics.txt`.
New FAQs show a green **New** badge for three weeks.

### Add a new project

1. Keep the project's final images in its own folder, e.g. `D:\KDS\Mr. XYZ Residence\Renders\`.
2. Open `tools/optimize_images.py` and add a line to `SOURCES`, pointing at the files:
   ```python
   "xyz-residence": [("xyz_1", "Mr. XYZ Residence/Renders/1.jpg"), ("xyz_2", "Mr. XYZ Residence/Renders/2.jpg")],
   ```
   Then run `pip install pillow numpy` (once) and `python tools/optimize_images.py`.
3. Copy an existing project block in `content/projects.json`, change the `slug`, text and image keys
   (`xyz-residence/xyz_1` …), and rebuild. The project page, sitemap, listings and film strip update themselves.
4. **Optional pencil sketch:** add the image key (e.g. `"xyz-residence/xyz_1"`) to `SKETCHES` in
   `tools/make_sketches.py` and run `python tools/make_sketches.py`. The project page then gets a
   drag-to-compare "Sketch → Render" slider automatically.
5. Add a note in `content/updates/` so the journal announces it.

### Illustrations and animations

- The hand-drawn line illustrations (architecture, interiors, landscape, PMC, design + build, courtyard
  and the five process stages) live in `illustrations.py`. They are plain SVG strokes, so they follow
  light/dark mode and draw themselves as visitors scroll.
- Motion respects visitors who switch on "reduce motion" on their phone or computer: everything still
  shows, just without animation.

---

## 5. Please check before launch

These are placeholders or details I could not verify from your files:

- [ ] `content/site.json` → `hours` (set to Mon–Sat 9:30–6:30 as a placeholder)
- [ ] `content/site.json` → `social` links (Instagram, LinkedIn, Facebook…) — empty ones are hidden
- [ ] `content/site.json` → `founded` year (optional; used in Google's business data)
- [ ] `content/team.json` → short bios for team members other than Ar. SRK were written from their
      roles — please confirm or replace with real ones
- [ ] `content/site.json` → `whatsapp` number (set to +91 90034 34422)
- [ ] `content/site.json` → `form` → `access_key` from web3forms.com (forms email you once this is set)
- [ ] Map pins on the Contact page — replace the `embed` links with the exact pin from Google Maps
      (*Share → Embed a map*) once your Google Business Profile is set up
- [ ] FAQ answers about timelines and fees — adjust wording to match how you actually work

---

## 6. Technical notes

- Pure static HTML/CSS/JS — no WordPress, no database, nothing to hack or update. Loads fast on 4G.
- Images are WebP in 640 / 1280 / 1920 px with `srcset`, lazy loading and fixed dimensions (no layout jump).
- Light/dark mode follows the visitor's phone/computer setting and remembers their choice.
- Accessible: skip link, keyboard-navigable menu, lightbox and FAQs, visible focus, reduced-motion support.
- Structured data (JSON-LD): ProfessionalService + GeneralContractor (both offices), WebSite, BreadcrumbList,
  Service, CreativeWork (projects), BlogPosting, FAQPage, Person.
- Fonts: Outfit (headings, geometric like the logo wordmark) + DM Sans (text) from Google Fonts.
- Colours come from the logo: orange `#F26122` and forest green `#126249`. Dark mode is deep forest green, not black.
