# SEO Guide for Kavinan Design Studio

*A plain-English, step-by-step plan to get found on Google by people looking for an architect,
interior designer or design-and-build firm in Chennai, Kumbakonam and across Tamil Nadu.*

---

## Part 1 — What SEO actually is (2-minute version)

When someone searches **"architect in Chennai"** or **"house renovation Kumbakonam"**, Google
decides which websites to show based on three things:

1. **Relevance** — does your site clearly talk about that service and that place?
2. **Trust** — do other places on the internet (Google Maps reviews, directories, articles) mention you?
3. **Experience** — is the site fast, mobile-friendly, secure and useful?

For a local studio, the single biggest lever is your **Google Business Profile** (the box with
the map, photos and reviews). The website supports it; the profile wins the clicks.

---

## Part 2 — Already done for you in this website ✅

You do not need to touch any of this — it's built in and updates itself.

| Done | What it means |
|---|---|
| ✅ Unique title + description on every page | What Google shows in results — written around your services and cities |
| ✅ One clear H1 heading per page, logical H2/H3 | Helps Google understand each page's topic |
| ✅ Dedicated page for each service | e.g. `/services/interior-design.html` targets "interior designers in Chennai" |
| ✅ Dedicated page for each of 21 projects | Real proof of work, rich with images and locations |
| ✅ Structured data (Schema.org JSON-LD) | Tells Google your business type, both addresses, phone, founder, services, projects, articles, FAQs and breadcrumbs |
| ✅ `sitemap.xml` (auto-updated) | A list of every page for Google to crawl |
| ✅ `robots.txt` | Points Google to the sitemap |
| ✅ Canonical URLs | Prevents duplicate-page confusion |
| ✅ Open Graph & Twitter cards | Nice previews when links are shared on WhatsApp, Facebook, LinkedIn |
| ✅ Fast WebP images, lazy loading, no layout shift | Good Core Web Vitals scores |
| ✅ Mobile-first, HTTPS-ready, accessible | Required for good rankings |
| ✅ Descriptive image alt text | Helps Google Images and screen readers |
| ✅ Breadcrumbs & internal links | Projects ↔ services ↔ journal all link to each other |
| ✅ Journal with RSS feed + scheduled posts | Fresh content every two weeks, automatically |
| ✅ FAQ page with FAQ schema | Answers the questions people type into Google |
| ✅ `llms.txt` | A summary for AI assistants (ChatGPT, Gemini, Perplexity, Claude) that increasingly answer "who is a good architect in Chennai?" |

---

## Part 3 — Launch week checklist (do these once)

### Step 1. Google Search Console — *30 minutes*
This is Google's free dashboard showing how your site appears in search.

1. Go to **search.google.com/search-console** → sign in with the studio Gmail.
2. *Add property* → choose **URL prefix** → enter `https://www.kavinandesignstudio.com`.
3. Choose **HTML tag** verification. Copy only the code inside `content="…"`.
4. Paste it into `content/site.json` → `"google_site_verification": "PASTE-HERE"`, rebuild/push.
5. Click **Verify**.
6. Left menu → **Sitemaps** → enter `sitemap.xml` → **Submit**.
7. Use **URL inspection** on the home page → **Request indexing**. Repeat for the Services and Projects pages.

### Step 2. Google Business Profile — *1 hour, most important*
1. Go to **business.google.com** → *Add business*.
2. Name: **Kavinan Design Studio** (exactly the same everywhere — never add keywords to the name).
3. Primary category: **Architect**. Additional categories: **Interior designer**,
   **Landscape architect**, **General contractor**, **Construction company**.
4. Address: the Chennai studio. Create a **second profile** for the Kumbakonam office.
5. Phone `+91 90034 34422`, website `https://www.kavinandesignstudio.com`.
6. Service areas: Chennai, Kumbakonam, Thanjavur, Trichy, Madurai, etc.
7. Hours, a 750-character description (use the About text), and **at least 20 photos**:
   S-Gan Villa before/after, Strata renders, team photo, office, logo.
8. Verify by video or postcard as Google asks.
9. Once live, copy the profile's map embed (*Share → Embed a map*) into `content/site.json` → `embed`.

### Step 3. Bing Webmaster Tools — *10 minutes*
**bing.com/webmasters** → *Import from Google Search Console*. Done. (Bing also powers ChatGPT search
and many voice assistants.)

### Step 4. Google Analytics 4 — *15 minutes*
1. **analytics.google.com** → *Admin → Create property* → "Kavinan Design Studio", India, INR.
2. *Data streams → Web* → enter the site URL → copy the **Measurement ID** (`G-XXXXXXX`).
3. Paste it into `content/site.json` → `"ga4_id"`. Rebuild/push.
4. Form submissions are already sent to Analytics as a `generate_lead` event — mark it as a
   **Key event** in *Admin → Events*.

### Step 5. Social profiles & links — *1 hour*
Create (or update) these with the **same name, phone, address and website**, then paste the links
into `content/site.json → social`:

- Instagram (most important for architecture in India) · Facebook · LinkedIn company page
- Pinterest (great for interiors) · YouTube (walkthroughs of 3D renders and completed projects)
- Houzz · Behance (portfolio) · Architizer

---

## Part 4 — Local listings ("citations")

Every listing that shows your **N**ame, **A**ddress and **P**hone (NAP) identically builds trust.
Copy your details exactly as they appear on the website:

```
Kavinan Design Studio
#3, SUS Palace, Vivekanandhar Street, Srinivasa Nagar, New Perungalathur, Chennai – 600063
+91 90034 34422 · www.kavinandesignstudio.com
```

Free listings worth doing (one per week is fine):
Justdial · Sulekha · IndiaMART · Apple Business Connect (Apple Maps) · Bing Places ·
Houzz · Architizer · ArchDaily/ArchiExpo (project submissions) · Council of Architecture member
listing (if available to you) · local Chamber of Commerce / builders' association directories ·
alumni pages of your architecture college.

---

## Part 5 — Reviews (the fastest way up the map)

- Ask **every** happy client for a Google review at handover. Send the direct review link on WhatsApp
  (Business Profile → *Ask for reviews* gives you the link).
- Ask them to mention the service and place naturally: *"…renovated our house in Madhanandapuram…"*.
- **Reply to every review** within a few days — thank them, mention the project.
- Never buy or swap reviews. Google removes them and can suspend the profile.
- Target: 10 reviews in the first 3 months, then 2–3 per month.

---

## Part 6 — Keywords: which page targets what

| Page | Main search phrases it is built for |
|---|---|
| Home | architects in Chennai, architecture firm Chennai, design and build company Chennai, architects in Kumbakonam |
| Services → Architecture | residential architect Chennai, house design Chennai, architect for villa, hospital architect Tamil Nadu |
| Services → Interior Design | interior designers in Chennai, modular kitchen designer, home interiors Kumbakonam |
| Services → Landscape | landscape architect Tamil Nadu, garden designer Chennai, farmhouse landscape |
| Services → Project Management | construction project management Chennai, site supervision architect |
| Services → Design + Build | turnkey house construction Chennai, design and build contractor, house renovation Chennai |
| S-Gan Villa | old house renovation Chennai, house extension first floor, renovation before and after |
| Strata — Yercaud | boutique hotel architect, hill resort design Yercaud, hotel design Tamil Nadu |
| Journal posts | long questions: "renovate or rebuild old house", "modular kitchen materials", "Vastu and design" |
| FAQ | "how much does an architect charge in Chennai", "how long to build a house" |

**Tip:** look at Search Console → *Performance → Queries* after 6–8 weeks. Phrases with many
impressions but few clicks are your next journal topics — add them to `content/topics.txt`.

---

## Part 7 — Your monthly SEO routine (2 hours / month)

| When | Do this |
|---|---|
| Every week | Post 2–3 photos on Google Business Profile + Instagram (site progress is perfect). Add a note in `content/updates/` for anything new. |
| Every 2 weeks | A journal article goes live automatically. Share it on WhatsApp status, LinkedIn and Instagram. |
| Monthly | Search Console: check *Pages* for errors; check *Performance* for top queries. Ask 2–3 clients for reviews. Add one new citation. |
| Each completed project | Add it as a project page with before/after photos (see README). This is your strongest content. |
| Quarterly | Refresh the top 3 journal posts (add `updated: YYYY-MM-DD` to their front matter). Review FAQs. |

---

## Part 8 — Getting other websites to link to you (backlinks)

Links from respected sites are Google's strongest trust signal. Good, safe ways for an architecture studio:

- Submit finished projects to **ArchDaily, Architizer, Houzz, Behance, Archello** and Indian design
  magazines/blogs (Architecture + Design, Surfaces Reporter, IGEN Architecture).
- Enter competitions (you already have the Archdais entry) — winners and shortlists get linked.
- Guest talks or juries at architecture colleges (e.g. Crescent School of Architecture) — ask for a link.
- Suppliers and brands you specify often feature projects — ask them to link back.
- Local news: handovers of public projects like the Pond Park make good stories.

**Never** buy links or use "SEO packages" that promise hundreds of backlinks — they cause penalties.

---

## Part 9 — About the AI-written journal

The automation writes from **your real updates** and is instructed never to invent prices, dates,
quotes or awards. To keep quality high (Google rewards genuine expertise):

- Give real detail in your update notes — materials, decisions, problems solved.
- Skim each new post on the site. If something's off, edit the `.md` file and push.
- Prefer `AUTO_PUBLISH=false` for the first month if you want to approve each post.
- Add your own photos from site visits to `assets/img/` over time — original photos beat renders.

---

## Part 10 — What to expect

| Time | Typical result |
|---|---|
| Week 1–2 | Site indexed. Brand searches ("Kavinan Design Studio") show your site and profile. |
| Month 1–3 | Google Business Profile appears for nearby "architect" searches as reviews grow. |
| Month 3–6 | Journal and service pages start ranking for longer phrases; enquiries via the form. |
| Month 6–12 | Competitive phrases like "architects in Chennai" become realistic with steady reviews, content and links. |

SEO compounds: consistency beats intensity.

---

## Part 11 — Quick troubleshooting

| Problem | Fix |
|---|---|
| A page isn't on Google | Search Console → URL inspection → Request indexing. Make sure it's linked from another page. |
| Wrong photo when a link is shared on WhatsApp | Each page has its own 1200×630 image in `assets/img/og/`. WhatsApp caches — try the link with `?v=2` at the end. |
| Want to check rich results | search.google.com/test/rich-results → paste a page URL. |
| Check speed | pagespeed.web.dev → aim for 90+ on mobile. |
| Form emails not arriving | Check the Web3Forms access key in `content/site.json` and your spam folder; see docs/HOSTING-GITHUB-ZOHO.md, Step 4. |
