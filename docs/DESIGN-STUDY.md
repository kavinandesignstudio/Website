# Design Study — Kavinan Design Studio Website

*The research, decisions and system behind the site.*

---

## 1. Brief, distilled

> A high-quality, professional website for an architecture, interior, landscape, project-management
> and design + build firm. Modern, contemporary, traditional and minimal. Multi-page. Light and dark
> mode. Practical FAQs, a journal that keeps itself fresh, strong SEO. Use Strata and S-Gan Villa as the
> hero imagery.

### What the source material told us

| Source | Key findings |
|---|---|
| Portfolio 2026 (53 pages) | Positioning *"Rooted with design"*; 21 projects across 6 sectors; 2 countries; 9-person team; 5-stage process; both office addresses; founder statement. |
| Logo files | Symbol in **terracotta orange `#F26122`** and **forest green `#126249`**; script tagline; versions for light and dark backgrounds. |
| S-Gan Villa photos | The only fully **built** project with a documented **before → during → after** story, delivered design + build in under six months — the strongest trust asset. Photos are mostly portrait (phone), so they suit triptychs and galleries better than wide banners. |
| Strata renders | Landscape, cinematic, forested — ideal for **full-bleed hero banners**. Rich data (area statement, 8 named suites) for an "expertise" page. |
| Other projects | Breadth: healthcare, institutional, stadia, heritage master plans, parks, interiors and NZ technical packages — proof the studio works at every scale. |

---

## 2. Audiences & what they need

| Audience | Primary question | What the site gives them |
|---|---|---|
| **Homeowners in Chennai / Tamil Nadu** (largest group) | "Can they design *and* build my house within budget, and can I trust them?" | S-Gan transformation, Design + Build page, practical FAQs on fees/time/approvals/Vastu, WhatsApp button, journal guides |
| **NRIs & clients in other cities** | "Can I manage this from abroad?" | FAQ section "Clients abroad", progress-update promise, online consultation |
| **Hospitality & commercial developers** | "Have they done hotels/mixed-use? Do they understand feasibility?" | Strata page with area schedule, Mixed-Use, TATA, hostel |
| **Institutions & healthcare** | "Do they understand clinical flow / campus planning?" | Alpha Hospital, Architectural Institute, ISRO, arts centre; healthcare journal article |
| **International firms** | "Can they deliver precise documentation?" | Cubro & Pitau technical packages |
| **Future team members** | "Is this a good studio to join?" | Team page, careers block |

---

## 3. Benchmarks & design principles

Award-recognised architecture-practice sites (the kind featured on Awwwards, CSS Design Awards and
in the portfolios of practices such as Studio Mumbai, Snøhetta, Herzog & de Meuron, Zaha Hadid
Architects, Bjarke Ingels Group) share a consistent grammar:

1. **Imagery leads; the interface recedes.** Full-bleed photography, generous white space, few colours.
2. **Editorial typography.** A refined serif for headlines, a quiet sans for reading, small letter-spaced labels.
3. **A grid you can feel.** Asymmetric 12-column layouts, aligned captions, consistent rhythm.
4. **Slow, deliberate motion.** Fades, image reveals and gentle zooms — never bouncing widgets.
5. **Projects as stories.** Facts, narrative, then galleries — not just thumbnails.

Our principles for Kavinan, derived from the brand line *Rooted with design*:

- **Rooted** → warm paper tones, earthy terracotta and forest green from the logo, references to local craft
  (jaali, clay tile, courtyard) in content.
- **Contemporary + traditional** → a geometric display face (Outfit) that echoes the logo's bold
  wordmark, paired with a calm, highly readable text face (DM Sans); tradition comes through in the
  imagery, materials and content rather than in ornament.
- **Minimal** → one accent colour at a time, hairline rules instead of boxes, no stock photos, no clutter.
- **Built well** → every page leads to proof (projects) and to action (WhatsApp / consultation).

---

## 4. Information architecture

```
Home
├── Studio (About)
├── Services
│   ├── Architecture
│   ├── Interior Design
│   ├── Landscape Design
│   ├── Project Management
│   └── Design + Build
├── Projects  (filter by 6 sectors)
│   └── 21 project pages
├── AI Platform  (coming soon · early-access form)
├── Team
├── Journal  (filter + search, scheduled & auto-written posts)
│   └── Articles
├── FAQ  (8 categories, search)
├── Contact  (form, WhatsApp, 2 offices, maps)
└── Privacy · 404 · Thank-you
```

Primary navigation is seven items — the maximum that stays scannable. "Start a project" is always visible.
A floating WhatsApp button reflects how clients in Tamil Nadu actually make first contact.

### Home page narrative (scroll story)

1. **Hero** — Strata slideshow (five views): *"Rooted in place. Built with care."*
2. **The Studio** — positioning statement, founder signature, key numbers
3. **Sector marquee** — breadth at a glance
4. **What we do** — five services, hover previews
5. **Featured: Strata** — hospitality expertise with hard data
6. **Featured: S-Gan Villa** — before / during / after: proof of delivery
7. **Selected works** — curated cross-sector grid
8. **How we work** — 5 stages
9. **AI Platform (coming soon)** — the shared project workspace for every client type
10. **Architectural quote** — pause and breathe
11. **Journal** — latest thinking
12. **FAQ preview** — remove doubts
13. **Call to action** — consultation or WhatsApp

---

## 5. Visual system

### Colour tokens (matched to the logo)

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#F7F5F0` warm white | `#0C221B` deep forest green | Page |
| `--bg-2` | `#E6EEE9` sage tint of logo green | `#112C23` | Alternate sections, footer |
| `--ink` | `#12241E` green-black | `#EEF2EE` | Text |
| `--ink-2` | `#3E4D47` | `#C3D0CA` | Body copy |
| `--muted` | `#5C6863` | `#93A69E` | Labels |
| `--accent` | `#F26122` logo orange | same | Markers, rules, highlights |
| `--accent-strong` | `#C44A14` | same | Buttons with white text (4.8:1) |
| `--accent-ink` | `#B8460F` | `#F5884F` | Orange **text**, contrast-checked |
| `--band` | `#0F4A39` logo green, deepened | same | Feature bands (AI Platform, roadmap) |

Dark mode is deliberately **not black**: it uses a deep forest green drawn from the logo, so the
site feels like the brand in both modes. Every text colour passes WCAG AA (4.5:1 or better).

### Typography

- **Display:** Outfit 200–500 — a clean geometric sans echoing the bold "KAVINAN" wordmark;
  large headlines in light weights, accent words in orange at medium weight.
- **Text:** DM Sans 400–700 — 15.5–17px fluid body, 1.7 line-height.
- **Labels:** DM Sans 600, 0.72rem, 0.24em letter-spacing, uppercase — echoing the portfolio's spaced titles.

### Layout & components

12-column grid, fluid gutters (16–56px), max width 1440px. Components: hero slideshow with Ken Burns,
numbered section heads, statement paragraphs, stats with count-up, service rows with image peek,
project cards (wide/tall pairs share heights), facts tables, transformation triptych, masonry galleries
with lightbox, area-schedule table, process timeline, rotating quotes, FAQ accordions, editorial journal
layout with sticky table of contents, CTA band, large-type footer.

### Motion

Content fades up 28px; images unmask with a slow clip-path reveal; hero slides cross-fade over 1.6s.
All motion is disabled for visitors who prefer reduced motion.

---

## 6. Content strategy

- **Voice:** warm, calm, precise — an architect explaining clearly. British/Indian spelling.
- **Proof first:** every service page lists real projects; every project page links its services.
- **Practical FAQs (31)** grouped by the client's journey: getting started → fees → process →
  construction → interiors → landscape → approvals → working remotely.
- **Journal:** 12 articles written (6 live, 6 scheduled fortnightly to Jan 2027), mixing project
  stories and homeowner guides that match real search questions.
- **Automation:** studio updates → Claude writes an article + FAQs daily; a topic queue supplies a
  weekly evergreen guide. All posts are rooted in real facts supplied by the studio.
- **Architectural quotes:** Le Corbusier, Louis Kahn, Mies van der Rohe, Frank Lloyd Wright,
  Charles Eames, Churchill — rotating on dark bands.

---

## 7. Performance, accessibility, security

| Area | Decision |
|---|---|
| Stack | Static HTML/CSS/JS generated by a dependency-free Python script — nothing to patch, nothing to hack, near-zero hosting cost |
| Images | 1.2 GB of source files → ~31 MB of WebP in three widths; `srcset` + `sizes`, lazy loading, explicit dimensions |
| JS | One small file, no frameworks, deferred |
| Fonts | Two families, `display=swap`, preconnected |
| Accessibility | Semantic landmarks, skip link, focus styles, keyboard lightbox/menu, `aria` on toggles, alt text on every image, colour contrast checked on text tokens, reduced-motion support |
| Security headers | `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy` via Netlify `_headers` |
| Privacy | No tracking unless a GA4 ID is added; privacy page included; form honeypot against spam |

---

## 8. Future roadmap (optional)

1. **Before/after slider** for future renovations — shoot "before" and "after" from the same spot.
2. **Project video walkthroughs** (YouTube embeds) for Strata and Elidi Stadia.
3. **Tamil-language version** of key pages for local homeowners (`/ta/`).
4. **Client testimonials** section once Google reviews are collected (with permission).
5. **Cost estimator** — a simple calculator for indicative budgets by area and specification.
6. **Instagram feed** on the home page once the account is active.
