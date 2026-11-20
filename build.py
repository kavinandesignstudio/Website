#!/usr/bin/env python3
"""
Kavinan Design Studio — static site builder
===========================================
Turns the files in content/ into a complete, SEO-ready website in public/.

    python build.py            # build the site into public/
    python build.py --serve    # build, then preview at http://localhost:8000
    python build.py --docs     # also render README + docs/*.md to docs/html/ for easy reading
    python build.py --offline  # also make offline/ — opens by double-clicking offline/index.html

Pure Python standard library — no installs needed (Python 3.8+).

Content you edit:
    content/site.json       studio details, phones, offices, social links, analytics IDs
    content/projects.json   every project (text, facts, images)
    content/services.json   the five service pages
    content/team.json       team members
    content/faqs.json       FAQs (add "publish": "YYYY-MM-DD" to schedule one)
    content/quotes.json     architectural quotes
    content/journal/*.md    journal posts — a post dated in the future is held back
                            and goes live automatically on the first build on/after that date
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

from illustrations import PROCESS_SKETCH, SERVICE_SKETCH, sketch

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
OUT = ROOT / "public"

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TODAY = dt.datetime.now(IST).date()


def load(name):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


SITE = load("site.json")
PROJECTS = sorted(load("projects.json"), key=lambda p: p.get("order", 99))
SERVICES = load("services.json")
TEAM = load("team.json")
FAQS = load("faqs.json")
QUOTES = load("quotes.json")
MANIFEST = json.loads((ASSETS / "img" / "manifest.json").read_text(encoding="utf-8"))
P_BY_SLUG = {p["slug"]: p for p in PROJECTS}
S_BY_SLUG = {s["slug"]: s for s in SERVICES}
URL = SITE["url"].rstrip("/")
CSS_VER = JS_VER = TODAY.strftime("%Y%m%d")

SECTORS = [
    ("residential", "Residential"),
    ("hospitality-commercial", "Hospitality & Commercial"),
    ("healthcare-institutional", "Healthcare & Institutional"),
    ("public-landscape", "Public Realm & Landscape"),
    ("interior", "Interior Design"),
    ("technical", "Technical Documentation"),
]
SECTOR_LABEL = dict(SECTORS)

esc = html.escape


# --------------------------------------------------------------------------- helpers
def url_for(path):
    """Output path -> public URL path ('services/index.html' -> '/services/')."""
    if path.endswith("index.html"):
        return "/" + path[: -len("index.html")]
    return "/" + path


def img(key, alt="", sizes="100vw", cls="", eager=False, attrs=""):
    m = MANIFEST.get(key)
    if not m:
        raise SystemExit(f"Image not in manifest: {key} — run tools/optimize_images.py")
    widths = m["widths"]
    src_w = 1280 if 1280 in widths else widths[-1]
    w, h = src_w, round(m["h"] * src_w / m["w"])
    srcset = ", ".join(f"/assets/img/{key}-{x}.webp {x}w" for x in widths)
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img src="/assets/img/{key}-{src_w}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" {load_attr} decoding="async"{c}{attrs}>')


def img_full(key):
    return f"/assets/img/{key}-{MANIFEST[key]['widths'][-1]}.webp"


def img_abs(key):
    m = MANIFEST[key]
    w = 1280 if 1280 in m["widths"] else m["widths"][-1]
    return f"{URL}/assets/img/{key}-{w}.webp"


def fmt_date(d):
    return d.strftime("%d %b %Y").lstrip("0")


def tel(n):
    return "+" + re.sub(r"\D", "", n)


ICONS = {
    "arrow": '<svg class="arrow" viewBox="0 0 18 10" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M0 5h17M13 1l4 4-4 4"/></svg>',
    "arrow-ur": '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3 13L13 3M5 3h8v8"/></svg>',
    "sun": '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>',
    "moon": '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8h18M3 16h18"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
    "up": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.8.9-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2 3.1 4.9 4.3.7.3 1.2.5 1.7.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4C2.7 15.6 2.2 13.8 2.2 12 2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9 1.8 1.8 2.9 4.3 2.9 6.9 0 5.4-4.4 9.8-9.8 9.8zm8.4-18.2C18.2 1.3 15.2 0 12 0 5.4 0 0 5.4 0 12c0 2.1.6 4.2 1.6 6L0 24l6.2-1.6c1.8 1 3.8 1.5 5.8 1.5 6.6 0 12-5.4 12-12 0-3.2-1.3-6.2-3.6-8.3z"/></svg>',
    "home": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M6 22L24 8l18 14M10 19v21h28V19M20 40V28h8v12"/></svg>',
    "sun-path": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="24" cy="20" r="7"/><path d="M4 40h40M8 34c4-12 28-12 32 0M24 4v4M38 20h4M6 20h4M34 10l3-3M11 7l3 3"/></svg>',
    "pencil": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M8 40l4-12L32 8l8 8-20 20-12 4zM28 12l8 8M8 40h32"/></svg>',
    "hand": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M6 26l10-8 8 4 10-6 8 6M6 26l10 12h10l14-12M18 32l4 4M24 28l6 6"/></svg>',
    "leaf": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M10 38C10 18 22 8 40 8c0 18-10 30-30 30zM10 38l16-16"/></svg>',
    "grid": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="8" y="8" width="32" height="32"/><path d="M8 20h32M8 30h32M20 8v32M30 8v32"/></svg>',
}

SOCIAL_LABEL = {"instagram": "Instagram", "facebook": "Facebook", "linkedin": "LinkedIn", "youtube": "YouTube", "pinterest": "Pinterest", "houzz": "Houzz"}


# --------------------------------------------------------------------------- markdown
def inline_md(t):
    t = esc(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def markdown(src):
    """Small Markdown converter: headings, paragraphs, lists, blockquotes, tables, links, bold/italic."""
    lines = src.strip().splitlines()
    out, i, toc = [], 0, []
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + esc("\n".join(buf), quote=False) + "</code></pre>")
            continue
        if re.match(r"^-{3,}\s*$", ln):
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", ln)
        if m:
            lvl, text = len(m.group(1)), m.group(2).strip()
            hid = slugify(text)
            if lvl == 2:
                toc.append((hid, text))
            out.append(f'<h{lvl} id="{hid}">{inline_md(text)}</h{lvl}>')
            i += 1
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append(f"<blockquote><p>{inline_md(' '.join(buf))}</p></blockquote>")
            continue
        if ln.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not re.match(r"^:?-{2,}", r[0] or "--")]
            th = "".join(f"<th>{inline_md(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ol>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|>|\||```|\s*[-*]\s|\s*\d+\.\s)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline_md(' '.join(buf))}</p>")
    return "\n".join(out), toc


def read_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"Missing front matter in {path.name}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["date"] = dt.date.fromisoformat(meta["date"])
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["slug"] = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    meta["draft"] = meta.get("draft", "false").lower() == "true"
    meta["body_html"], meta["toc"] = markdown(m.group(2))
    words = len(re.sub(r"<[^>]+>", " ", meta["body_html"]).split())
    meta["read"] = max(2, round(words / 220))
    meta["updated"] = dt.date.fromisoformat(meta["updated"]) if meta.get("updated") else meta["date"]
    return meta


ALL_POSTS = sorted((read_post(p) for p in (CONTENT / "journal").glob("*.md")), key=lambda p: p["date"], reverse=True)
POSTS = [p for p in ALL_POSTS if p["date"] <= TODAY and not p["draft"]]
SCHEDULED = [p for p in ALL_POSTS if p["date"] > TODAY and not p["draft"]]
FAQ_ITEMS = [f for f in FAQS["items"] if dt.date.fromisoformat(f.get("publish", f.get("added", "2000-01-01"))) <= TODAY]


# --------------------------------------------------------------------------- structured data
def org_schema():
    chennai, kum = SITE["offices"][0], SITE["offices"][1]

    def address(o):
        return {"@type": "PostalAddress", "streetAddress": o["street"], "addressLocality": o["city"],
                "addressRegion": o["region"], "postalCode": o["postal"], "addressCountry": o["country"]}
    same_as = [u for u in SITE["social"].values() if u]
    data = {
        "@type": ["ProfessionalService", "GeneralContractor"],
        "@id": URL + "/#organization",
        "name": SITE["name"],
        "alternateName": "KDS",
        "slogan": SITE["tagline"],
        "description": SITE["description"],
        "url": URL + "/",
        "logo": URL + "/assets/img/brand/icon-512.png",
        "image": URL + "/assets/img/og/default.jpg",
        "telephone": tel(SITE["phones"][0]),
        "email": SITE["emails"][0],
        "address": address(chennai),
        "areaServed": [{"@type": "Place", "name": a} for a in SITE["areas_served"]],
        "founder": {"@type": "Person", "name": "Sivaramakrishnan S K", "alternateName": "Ar. SRK", "jobTitle": "Founder & Principal Architect"},
        "knowsAbout": ["Architecture", "Interior design", "Landscape architecture", "Construction project management",
                       "Design and build", "Residential architecture", "Hospitality design", "Healthcare architecture", "Vastu-aware planning"],
        "department": [{"@type": "ProfessionalService", "name": SITE["name"] + " — Kumbakonam", "address": address(kum),
                        "telephone": tel(SITE["phones"][-1])}],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services",
                            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["title"], "url": f"{URL}/services/{s['slug']}.html"}} for s in SERVICES]},
    }
    if same_as:
        data["sameAs"] = same_as
    if SITE.get("founded"):
        data["foundingDate"] = SITE["founded"]
    return data


def website_schema():
    return {"@type": "WebSite", "@id": URL + "/#website", "url": URL + "/", "name": SITE["name"],
            "publisher": {"@id": URL + "/#organization"}, "inLanguage": "en-IN"}


def breadcrumb_schema(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": URL + href} for i, (name, href) in enumerate(trail)]}


def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in items]}


# --------------------------------------------------------------------------- layout
NAV = [("Studio", "/about.html"), ("Services", "/services/"), ("Projects", "/projects/"), ("AI Platform", "/platform.html"),
       ("Team", "/team.html"), ("Journal", "/journal/"), ("FAQ", "/faq.html"), ("Contact", "/contact.html")]


def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=page" if active == n else ""}>{n}</a>' for n, h in NAV)
    mlinks = "".join(f'<a href="{h}">{n}<span>0{i + 1}</span></a>' for i, (n, h) in enumerate([("Home", "/")] + NAV))
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="container">
    <a class="brand" href="/" aria-label="{esc(SITE['name'])} — home">
      <img class="logo-light" src="/assets/img/brand/logo.webp" alt="{esc(SITE['name'])}" width="640" height="200">
      <img class="logo-dark" src="/assets/img/brand/logo-white.webp" alt="{esc(SITE['name'])}" width="640" height="200">
    </a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="header-tools">
      <button class="icon-btn theme-toggle" type="button" aria-label="Toggle dark mode">{ICONS['moon']}{ICONS['sun']}</button>
      <a class="btn header-cta" href="/contact.html" style="--b: currentColor; color: inherit">Start a project</a>
      <button class="icon-btn menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu">{ICONS['menu']}</button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <button class="icon-btn close" type="button" aria-label="Close menu">{ICONS['close']}</button>
  <nav aria-label="Mobile">{mlinks}</nav>
  <div class="mm-foot">
    <a href="tel:{tel(SITE['phones'][0])}">{SITE['phones'][0]}</a>
    <a href="mailto:{SITE['emails'][0]}">{SITE['emails'][0]}</a>
    <button class="btn theme-toggle mt-1" type="button" style="justify-self:start">{ICONS['moon']}{ICONS['sun']} Light / Dark</button>
  </div>
</div>"""


def footer():
    o1, o2 = SITE["offices"]
    socials = "".join(f'<a class="icon-btn" href="{u}" rel="noopener" target="_blank" aria-label="{SOCIAL_LABEL[k]}" title="{SOCIAL_LABEL[k]}"><span style="font-size:.62rem;font-weight:700">{SOCIAL_LABEL[k][:2].upper()}</span></a>'
                      for k, u in SITE["social"].items() if u)
    svc = "".join(f'<li><a href="/services/{s["slug"]}.html">{s["title"]}</a></li>' for s in SERVICES)
    return f"""
<footer class="site-footer">
  <div class="container">
    <p class="footer-big">Have a site in mind? <a href="/contact.html">Let's talk.</a></p>
    <div class="footer-cols">
      <div>
        <a class="footer-logo" href="/" aria-label="Home"><img class="logo-light" src="/assets/img/brand/logo.webp" alt="{esc(SITE['name'])}" width="640" height="200" loading="lazy"><img class="logo-dark" src="/assets/img/brand/logo-white.webp" alt="" width="640" height="200" loading="lazy"></a>
        <p class="muted" style="max-width:34ch">Architecture · Interior Design · Landscape · Project Management · Design + Build — from first sketch to final handover.</p>
        <div class="socials">{socials}</div>
      </div>
      <div><h4>Services</h4><ul>{svc}</ul></div>
      <div><h4>Studio</h4><ul>
        <li><a href="/about.html">About the studio</a></li><li><a href="/projects/">Projects</a></li>
        <li><a href="/platform.html">AI Platform <span class="pill pill--sm">Soon</span></a></li>
        <li><a href="/team.html">Team</a></li><li><a href="/journal/">Journal</a></li>
        <li><a href="/faq.html">FAQ</a></li><li><a href="/contact.html">Contact</a></li></ul></div>
      <div><h4>Visit</h4>
        <address><strong>{o1['label']}</strong><br>{o1['street']},<br>{o1['locality']}, {o1['city']} – {o1['postal']}</address>
        <address class="mt-1"><strong>{o2['label']}</strong><br>{o2['street']},<br>{o2['city']} – {o2['postal']}</address>
        <p class="mt-1"><a href="tel:{tel(SITE['phones'][0])}">{SITE['phones'][0]}</a><br><a href="mailto:{SITE['emails'][0]}">{SITE['emails'][0]}</a></p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>{TODAY.year}</span> {esc(SITE['legal_name'])}. All rights reserved.</span>
      <span><a href="/privacy.html">Privacy</a> · <a href="/sitemap.xml">Sitemap</a> · <a href="/feed.xml">RSS</a></span>
    </div>
  </div>
</footer>
<a class="fab" href="https://wa.me/{SITE['whatsapp']}?text={html.escape('Hello Kavinan Design Studio, I would like to discuss a project.')}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{ICONS['whatsapp']}</a>
<button class="to-top" type="button" aria-label="Back to top">{ICONS['up']}</button>"""


def page(path, title, description, body, active=None, og_image=None, schema=None, has_hero=False,
         og_type="website", noindex=False, extra_head=""):
    canonical = URL + url_for(path)
    full_title = title if SITE["name"] in title else f"{title} | {SITE['name']}"
    og = og_image or URL + "/assets/img/og/default.jpg"
    graph = [org_schema(), website_schema()] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    an = SITE["analytics"]
    verify = ""
    if an.get("google_site_verification"):
        verify += f'<meta name="google-site-verification" content="{an["google_site_verification"]}">'
    if an.get("bing_site_verification"):
        verify += f'<meta name="msvalidate.01" content="{an["bing_site_verification"]}">'
    ga = ""
    if an.get("ga4_id"):
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={an["ga4_id"]}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{an['ga4_id']}');</script>")
    doc = f"""<!doctype html>
<html lang="en-IN" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large'}">
<meta name="author" content="{esc(SITE['name'])}">
<meta name="geo.region" content="IN-TN">
<meta name="geo.placename" content="Chennai, Kumbakonam">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(SITE['name'])}">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(full_title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{og}">
<meta name="theme-color" content="#f7f5f0">
{verify}
<script>(function(){{try{{var t=localStorage.getItem('kds-theme');if(t){{document.documentElement.setAttribute('data-theme',t);}}}}catch(e){{}}}})();</script>
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['name'])} Journal" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap">
<link rel="stylesheet" href="/assets/css/site.css?v={CSS_VER}">
{extra_head}
<script type="application/ld+json">{ld}</script>
{ga}
</head>
<body class="{'has-hero' if has_hero else ''}">
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={JS_VER}" defer></script>
</body>
</html>
"""
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc, encoding="utf-8")
    SITEMAP.append((url_for(path), noindex))


SITEMAP = []


# --------------------------------------------------------------------------- shared blocks
def crumbs(trail):
    items = "".join(f'<li><a href="{h}">{esc(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{esc(n)}</li>'
                    for i, (n, h) in enumerate(trail))
    return f'<ol class="breadcrumb">{items}</ol>'


def project_card(p, variant="", sizes="(max-width: 640px) 100vw, (max-width: 1000px) 50vw, 33vw", i=0):
    return f"""<a class="pcard {variant} reveal" style="--d:{(i % 3) * .08}s" href="/projects/{p['slug']}.html" data-sector="{p['sector']}">
  <div class="media">{img(p['cover'], alt=f"{p['title']}, {p['location']} — {SITE['name']}", sizes=sizes)}</div>
  <div class="pcard-meta"><div><h3>{esc(p['title'])}</h3><p class="loc">{esc(p['location'])}</p></div><span class="tag">{SECTOR_LABEL[p['sector']]}</span></div>
</a>"""


def journal_card(post, lead=False, i=0):
    cls = "jcard jcard--lead" if lead else "jcard"
    sizes = "(max-width: 640px) 100vw, 60vw" if lead else "(max-width: 640px) 100vw, (max-width: 1000px) 50vw, 33vw"
    tags = "|".join(post["tags"])
    return f"""<a class="{cls} reveal" style="--d:{(i % 3) * .08}s" href="/journal/{post['slug']}.html" data-tags="{esc(tags)}">
  <div class="media">{img(post['cover'], alt=post['title'], sizes=sizes)}</div>
  <div><div class="meta"><span class="t">{esc(post['tags'][0] if post['tags'] else 'Journal')}</span><time datetime="{post['date']}">{fmt_date(post['date'])}</time><span>{post['read']} min read</span></div>
  <h3>{esc(post['title'])}</h3><p>{esc(post['description'])}</p></div>
</a>"""


def faq_list(items):
    out = []
    for f in items:
        added = dt.date.fromisoformat(f.get("publish", f.get("added", "2000-01-01")))
        new = '<span class="new">New</span>' if (TODAY - added).days <= 21 else ""
        out.append(f'<details><summary><span>{esc(f["q"])}{new}</span><span class="pm" aria-hidden="true"></span></summary><div class="ans"><p>{esc(f["a"])}</p></div></details>')
    return f'<div class="faq">{"".join(out)}</div>'


PROCESS = [
    ("01", "Brief & Site Study", "We listen — to you, the site and the climate — and survey what exists, setting scope, budget and timeline."),
    ("02", "Concept Design", "Options for planning and massing, explored in sketches and models until the idea feels right."),
    ("03", "Design Development & 3D", "Photo-real 3D views, materials, structure and services resolved together."),
    ("04", "Working Drawings", "Approval drawings and complete good-for-construction sets, details and schedules."),
    ("05", "Execution & Handover", "Site supervision, project management or full design + build — through to the keys."),
]


def process_block():
    items = "".join(f'<li class="reveal" style="--d:{i * .08}s"><div class="pk-sketch">{sketch(PROCESS_SKETCH[i])}</div><span class="k">{n}</span><h4>{t}</h4><p>{d}</p></li>' for i, (n, t, d) in enumerate(PROCESS))
    return f'<ol class="process">{items}</ol>'


def cta(image="strata-yercaud/str2_3", title="Let's build something <em>rooted</em>.", text="Tell us about your site, your family or your organisation, and what you dream of building. We'll take it from the first conversation to the final handover."):
    return f"""<section class="cta">
  <div class="bg">{img(image, alt="", sizes="100vw")}</div>
  <div class="container">
    <p class="eyebrow" style="color:rgba(255,255,255,.75)">Start a project</p>
    <h2 class="reveal">{title}</h2>
    <p class="reveal">{text}</p>
    <div class="btns reveal">
      <a class="btn btn--solid" href="/contact.html">Book a consultation {ICONS['arrow']}</a>
      <a class="btn btn--light" href="https://wa.me/{SITE['whatsapp']}" target="_blank" rel="noopener">WhatsApp us</a>
    </div>
  </div>
</section>"""


def quotes_block(dark=True):
    figs = "".join(f'<figure class="{"is-active" if i == 0 else ""}"><blockquote>{esc(q["text"])}</blockquote><cite>— {esc(q["by"])}</cite></figure>' for i, q in enumerate(QUOTES))
    return f'<section class="section {"section--ink" if dark else ""}"><div class="container"><div class="quote quote-rotator" aria-live="polite">{figs}</div></div></section>'


def compare(render_key, alt, cls=""):
    """Drag (or keyboard) slider: pencil sketch on the left, finished render on the right."""
    return f"""<div class="compare reveal {cls}" style="--pos:50%">
  <div class="compare__img">{img(render_key, alt=alt, sizes='(max-width:900px) 100vw, 60vw')}</div>
  <div class="compare__top is-sketch-img" aria-hidden="true">{img(render_key + '-sketch', alt='', sizes='(max-width:900px) 100vw, 60vw')}</div>
  <span class="compare__line" aria-hidden="true"><i>{ICONS['arrow']}</i></span>
  <span class="compare__lbl compare__lbl--l">Sketch</span><span class="compare__lbl compare__lbl--r">Render</span>
  <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Slide to compare the pencil sketch with the render">
</div>"""


def scrub_story(render_key, title, steps, eyebrow):
    """Pinned scroll story: the pencil sketch wipes away to reveal the render as you scroll."""
    st = "".join(f'<li data-at="{a}"><b>0{i + 1}</b><span>{t}</span></li>' for i, (a, t) in enumerate(steps))
    return f"""<section class="scrub" data-scrub aria-label="From sketch to render">
  <div class="scrub__sticky">
    <div class="scrub__stage">
      <div class="scrub__img">{img(render_key, alt=title, sizes='100vw')}</div>
      <div class="scrub__sketch is-sketch-img" aria-hidden="true">{img(render_key + '-sketch', alt='', sizes='100vw')}</div>
      <span class="scrub__bar" aria-hidden="true"></span>
    </div>
    <div class="scrub__panel">
      <p class="eyebrow">{eyebrow}</p>
      <h2>From a pencil line to a <em>place</em>.</h2>
      <ol class="scrub__steps">{st}</ol>
      <p class="small muted mb-0">Scroll to draw the building into being.</p>
    </div>
  </div>
</section>"""


def filmstrip():
    cards = "".join(f"""<a class="film__card" href="/projects/{p['slug']}.html">
      <div class="media">{img(p['cover'], alt=p['title'], sizes='(max-width:700px) 70vw, 30vw')}</div>
      <span class="film__n">{i + 1:02d}</span><strong>{esc(p['title'])}</strong><span class="muted small">{esc(p['location'])}</span></a>""" for i, p in enumerate(PROJECTS))
    return f"""<section class="section film" data-film>
  <div class="container section-head">
    <div><p class="eyebrow">Portfolio in motion</p><h2>{len(PROJECTS)} projects, <em>one</em> way of working.</h2></div>
    <a class="link-arrow" href="/projects/">Browse all projects {ICONS['arrow']}</a>
  </div>
  <div class="film__viewport"><div class="film__track">{cards}</div></div>
</section>"""


def doodle(name, cls):
    return f'<div class="doodle {cls}" data-parallax="0.12" aria-hidden="true">{sketch(name)}</div>'


# --------------------------------------------------------------------------- pages
def build_home():
    slides = [
        ("strata-yercaud/str2_5", "Strata — Yercaud", "Strata Luxury Stay · latest design"),
        ("prabu-residence-kumbakonam/pr_2", "Mr. Prabu Residence", "Courtyard home · Kumbakonam"),
        ("strata-yercaud/str2_1", "Strata — Yercaud", "Stacked suites & timber jaali"),
        ("prabu-residence-kumbakonam/pr_4", "Mr. Prabu Residence", "Living under a coffered timber ceiling"),
        ("strata-yercaud/str2_3", "Strata — Yercaud", "Terraces stepping up the slope"),
        ("prabu-residence-kumbakonam/pr_7", "Mr. Prabu Residence", "The courtyard & kolam niche"),
    ]
    slide_html = []
    for i, (k, t, l) in enumerate(slides):
        if i < 2:
            im = img(k, alt=f"{t} — {l}", sizes="100vw", eager=(i == 0))
        else:  # lazy-swapped by JS
            m = MANIFEST[k]
            srcset = ", ".join(f"/assets/img/{k}-{x}.webp {x}w" for x in m["widths"])
            im = f'<img data-src="/assets/img/{k}-1280.webp" data-srcset="{srcset}" sizes="100vw" alt="{esc(t)} — {esc(l)}" width="1280" height="{round(m["h"] * 1280 / m["w"])}">'
        slide_html.append(f'<div class="hero-slide{" is-active" if i == 0 else ""}" data-title="{esc(t)}" data-loc="{esc(l)}">{im}</div>')
    dots = "".join(f'<button type="button" aria-label="Show slide {i + 1}"><i></i></button>' for i in range(len(slides)))
    svc_rows = "".join(f"""<a class="svc-row reveal" href="/services/{s['slug']}.html">
      <span class="n">{s['num']}<span class="svc-sk">{sketch(SERVICE_SKETCH[s['slug']])}</span></span><h3>{s['title']}</h3><p>{esc(s['lede'])}</p><span class="go">{ICONS['arrow-ur']}</span>
      <span class="peek" aria-hidden="true">{img(s['image'], sizes='220px')}</span></a>""" for s in SERVICES)
    prabu = P_BY_SLUG["prabu-residence-kumbakonam"]
    strata, sgan = P_BY_SLUG["strata-yercaud"], P_BY_SLUG["s-gan-villa"]
    tri_labels = [("01", "Existing · Oct 2025"), ("02", "Strip-out · Dec 2025"), ("03", "Completed · Mar 2026")]
    tri = "".join(f'<figure class="reveal" style="--d:{i * .1}s"><div class="media">{img(k, alt=f"S-Gan Villa — {lab}", sizes="(max-width:700px) 50vw, 33vw")}</div><div class="step"><b>{n}</b><span>{lab}</span></div></figure>'
                  for i, (k, (n, lab)) in enumerate(zip(sgan["transformation"], tri_labels)))
    selected = ["alpha-multispeciality-hospital", "elidi-stadia", "architectural-institute", "archdais-interior-competition",
                "pond-park-sivakasi", "isro-campus-visualisation", "mixed-use-development"]
    variants = ["pcard--wide", "pcard--tall", "", "", "", "pcard--tall", "pcard--wide"]
    cards = "".join(project_card(P_BY_SLUG[s], v, i=i, sizes="(max-width: 640px) 100vw, 66vw" if v else "(max-width: 640px) 100vw, 33vw") for i, (s, v) in enumerate(zip(selected, variants)))
    stats = "".join(f'<div class="stat reveal" style="--d:{i * .08}s"><div class="val"><span data-count="{s["value"]}">{s["value"]}</span>{"<sup>" + s["suffix"] + "</sup>" if s["suffix"] else ""}</div><div class="lbl">{s["label"]}</div></div>' for i, s in enumerate(SITE["stats"]))
    sectors = "".join(f"<span>{lab}</span>" for _, lab in SECTORS) + "<span>Design + Build</span>"
    jcards = "".join(journal_card(p, i=i) for i, p in enumerate(POSTS[:3]))
    faq_prev = faq_list([f for f in FAQ_ITEMS if f["cat"] in ("start", "build", "fees")][:5])

    body = f"""
<section class="hero" aria-label="Featured projects">
  {''.join(slide_html)}
  <div class="hero-meta" aria-hidden="true"><span></span><strong></strong></div>
  <div class="hero-content"><div class="container">
    <p class="eyebrow">Architecture · Interiors · Landscape · Project Management · Build</p>
    <h1 data-split>Rooted in place. <em>Built with care.</em></h1>
    <div class="hero-bottom">
      <p>An architecture, interior, landscape and design + build studio in Chennai &amp; Kumbakonam — carrying every project from the first conversation to the final handover.</p>
      <div class="flex">
        <a class="btn btn--light" href="/projects/">Explore projects {ICONS['arrow']}</a>
        <div class="hero-progress">{dots}</div>
      </div>
    </div>
  </div></div>
  <div class="scroll-cue" aria-hidden="true"></div>
</section>

<section class="section has-doodle">
  {doodle('courtyard', 'doodle--r')}
  <div class="container">
    <div class="grid-2">
      <div class="span-7">
        <p class="eyebrow"><span class="num">01</span> The Studio</p>
        <p class="statement" data-split>We design homes, hotels, hospitals and public places that are <em>rooted</em> in their site, climate and craft — and we stay until they are built well.</p>
      </div>
      <div class="span-4" style="grid-column:9 / span 4">
        <p class="reveal">Kavinan Design Studio brings architecture, interiors, landscape, project management and construction together under one roof. Our work begins with listening: to the client, to the site and to the climate.</p>
        <p class="reveal muted">From compact family homes and renovations to hill hotels, hospitals, campuses and international technical packages, every project receives the same care for planning, proportion and detail.</p>
        <div class="signature reveal">{img('team/tm_srk', alt='Ar. SRK, Founder & Principal Architect', sizes='64px')}<div><strong>Ar. SRK (Sivaramakrishnan S K)</strong><span>Founder &amp; Principal Architect</span></div></div>
        <a class="link-arrow mt-2" href="/about.html">About the studio {ICONS['arrow']}</a>
      </div>
    </div>
    <div class="stats mt-4">{stats}</div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee__track"><span>{sectors}</span><span>{sectors}</span></div></div>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow"><span class="num">02</span> What we do</p><h2>One studio, from idea to <em>keys</em>.</h2></div>
      <p>Five disciplines, one accountable team. Appoint us for design alone, or let us carry your project all the way to handover.</p>
    </div>
    <div class="svc-list">{svc_rows}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <div class="feature">
      <div class="feature__media stack-media">
        <div class="media ratio-4x5 reveal-img" style="aspect-ratio:5/4">{img(strata['cover'], alt='Strata boutique hill hotel, Yercaud — stacked volumes on the slope', sizes='(max-width:900px) 100vw, 58vw')}</div>
        <div class="media media--float ratio-4x5 reveal-img">{img('strata-yercaud/str2_2', alt='Strata upper suites with timber jaali screens', sizes='25vw')}</div>
      </div>
      <div class="feature__body">
        <p class="eyebrow"><span class="num">03</span> Featured · Hospitality</p>
        <h2 class="reveal">Strata — <em>Yercaud</em></h2>
        <p class="reveal">{esc(strata['summary'])}</p>
        <dl class="facts-mini reveal">
          <div><dt>Site area</dt><dd>4,287 sq.ft</dd></div><div><dt>Built-up</dt><dd>6,677 sq.ft</dd></div>
          <div><dt>Suites</dt><dd>8 named suites</dd></div><div><dt>Levels</dt><dd>Stilt + 3 · 12 m</dd></div>
        </dl>
        <a class="btn reveal" href="/projects/strata-yercaud.html">View Strata {ICONS['arrow']}</a>
      </div>
    </div>
  </div>
</section>

{scrub_story('strata-yercaud/str2_5', 'Strata Luxury Stay, Yercaud', [(0.0, 'Concept sketch'), (0.4, 'Design development'), (0.75, 'Photo-real render')], 'Sketch → Render · Strata')}

<section class="section has-doodle">
  {doodle('interior', 'doodle--l')}
  <div class="container">
    <div class="feature feature--rev">
      <div class="feature__media">{compare('prabu-residence-kumbakonam/pr_2', 'Mr. Prabu Residence — open-to-sky courtyard with timber pillars')}</div>
      <div class="feature__body">
        <p class="eyebrow"><span class="num">04</span> New · Kumbakonam</p>
        <h2 data-split>Mr. Prabu <em>Residence</em></h2>
        <div class="feature-sketch">{sketch('courtyard')}</div>
        <p class="reveal">{esc(prabu['summary'])} An open-to-sky courtyard, turned timber pillars, kolam motifs and a coffered timber ceiling — heritage character for everyday modern living.</p>
        <p class="small muted reveal">Drag the handle to compare our pencil sketch with the final render.</p>
        <a class="btn reveal" href="/projects/prabu-residence-kumbakonam.html">View the project {ICONS['arrow']}</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow"><span class="num">05</span> Design + Build · Completed 2026</p><h2>S-Gan Villa — survey to keys in <em>under six months</em>.</h2></div>
      <div><p>{esc(sgan['summary'])} Measured survey, 3D design, working drawings, procurement, site execution and handover — one team.</p>
      <a class="link-arrow mt-2" href="/projects/s-gan-villa.html">See the transformation {ICONS['arrow']}</a></div>
    </div>
    <div class="triptych">{tri}</div>
  </div>
</section>

{filmstrip()}

<section class="section section--alt">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow"><span class="num">06</span> Selected works</p><h2>Across <em>six</em> sectors.</h2></div>
      <a class="link-arrow" href="/projects/">All {len(PROJECTS)} projects {ICONS['arrow']}</a>
    </div>
    <div class="projects-grid">{cards}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow"><span class="num">07</span> How we work</p><h2>A clear path from <em>brief</em> to handover.</h2></div>
      <p>Five stages, each ending with your review and approval — so you always know where your project stands.</p>
    </div>
    {process_block()}
  </div>
</section>

<section class="section section--ink platform-band">
  <div class="container grid-2">
    <div class="span-6"><p class="eyebrow"><span class="pill">Coming soon</span> AI Platform</p>
      <h2 class="reveal">An AI-based project &amp; design management tool for <em>every</em> client.</h2>
      <p class="reveal">We're building a shared workspace where clients, consultants and contractors see the same latest drawings, approvals, schedule, site progress and payments — for design-only, design + supervision and design + build projects alike. Precise, transparent, no miscommunication.</p>
      <div class="flex mt-2 reveal"><a class="btn btn--solid" href="/platform.html">Discover the platform {ICONS['arrow']}</a><a class="btn btn--light" href="/platform.html#early-access">Get early access</a></div>
    </div>
    <div class="span-6 reveal" style="grid-column:7 / span 6">{platform_mock()}</div>
  </div>
</section>

{quotes_block(dark=False)}

<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow"><span class="num">08</span> Journal</p><h2>Notes from the <em>studio</em>.</h2></div>
      <a class="link-arrow" href="/journal/">All articles {ICONS['arrow']}</a>
    </div>
    <div class="jgrid">{jcards}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="container grid-2">
    <div class="span-4"><p class="eyebrow"><span class="num">09</span> Questions</p><h2>Good to <em>know</em>.</h2>
      <p class="muted">Straight answers to what clients ask us most — fees, timelines, design + build and more.</p>
      <a class="link-arrow mt-2" href="/faq.html">All FAQs {ICONS['arrow']}</a></div>
    <div class="span-7" style="grid-column:6 / span 7">{faq_prev}</div>
  </div>
</section>

{cta()}
"""
    page("index.html",
         f"{SITE['name']} | Architects, Interior Designers & Design + Build in Chennai & Kumbakonam",
         "Award-worthy architecture, interior design, landscape, project management and turnkey design + build in Chennai & Kumbakonam, Tamil Nadu. Homes, villas, hotels, hospitals and public spaces — rooted with design.",
         body, has_hero=True, schema=[{"@type": "WebPage", "@id": URL + "/#webpage", "url": URL + "/", "name": SITE["name"], "isPartOf": {"@id": URL + "/#website"}, "about": {"@id": URL + "/#organization"}}])


def build_about():
    values = [
        ("leaf", "Rooted in place", "Every design begins with the site, its light, climate, materials and crafts — and the way people live around it."),
        ("home", "Contemporary & traditional", "Clean, modern planning with the warmth of tradition: courtyards, jaali, clay tiles, timber and deep shade."),
        ("sun-path", "Climate first", "Orientation, shade, cross-ventilation and passive cooling come before machines — comfort that costs less to run."),
        ("pencil", "Designed to be built", "Drawings detailed for site, budgets tested early, and 3D before construction — so what you see is what you get."),
        ("hand", "One accountable team", "Architecture, interiors, landscape, MEP, project management and construction — under one roof."),
        ("grid", "Care in every detail", "From a 65-sheet stone set-out to a kitchen shutter, the same care for proportion and precision."),
    ]
    vhtml = "".join(f'<div class="value reveal" style="--d:{(i % 3) * .08}s"><div class="ic">{ICONS[ic]}</div><h3>{t}</h3><p>{d}</p></div>' for i, (ic, t, d) in enumerate(values))
    offices = "".join(f"""<div class="office-card reveal"><p class="eyebrow">{esc(o['label'])}</p><h3>{esc(o['city'])}</h3>
      <address style="font-style:normal" class="muted">{esc(o['street'])},<br>{esc(o['locality'])}, {esc(o['city'])} – {o['postal']}<br>{esc(o['region'])}, India</address>
      <a class="link-arrow mt-1" href="{o['map']}" target="_blank" rel="noopener">Get directions {ICONS['arrow']}</a></div>""" for o in SITE["offices"])
    sectors = "".join(f'<li><a href="/projects/#{k}">{lab}</a></li>' for k, lab in SECTORS)
    stats = "".join(f'<div class="stat"><div class="val">{s["value"]}{"<sup>" + s["suffix"] + "</sup>" if s["suffix"] else ""}</div><div class="lbl">{s["label"]}</div></div>' for s in SITE["stats"])
    body = f"""
<section class="page-hero page-hero--image">
  <div class="ph-img">{img('strata-yercaud/st_7', alt='Curved balconies and suite terraces at Strata, Yercaud', sizes='100vw', eager=True)}</div>
  <div class="container">
    {crumbs([('Home', '/'), ('Studio', '/about.html')])}
    <p class="eyebrow">The Studio</p>
    <h1>Rooted <em>with</em> design.</h1>
    <p class="lede">An architecture and design practice working from Chennai and Kumbakonam — from the first conversation to the final handover.</p>
  </div>
</section>

<section class="section">
  <div class="container grid-2">
    <div class="span-5"><p class="eyebrow"><span class="num">01</span> Our story</p>
      <h2 class="reveal">Design only matters when it is <em>built well</em>.</h2></div>
    <div class="span-6 prose" style="grid-column:7 / span 6">
      <p class="lede reveal">Kavinan Design Studio is an architecture and interior design practice working from Chennai and Kumbakonam. We design homes, hospitality, healthcare, institutional and public projects — and carry them from the first conversation to the final handover.</p>
      <p class="reveal">Our work begins with listening: to the client, to the site and to the climate. We believe good buildings are rooted in their place — in the light, materials, crafts and ways of living around them — and that design only matters when it is built well. That is why our studio brings architecture, interiors, landscape, project management and construction together under one roof.</p>
      <p class="reveal">From compact family homes and renovations to hill hotels, hospitals, campuses and international technical packages for clients in New Zealand, every project receives the same care for planning, proportion and detail.</p>
      <div class="signature reveal">{img('team/tm_srk', alt='Ar. SRK', sizes='64px')}<div><strong>Ar. SRK (Sivaramakrishnan S K)</strong><span>Founder &amp; Principal Architect</span></div></div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow"><span class="num">02</span> What we believe</p><h2>Six principles behind <em>every</em> project.</h2></div></div>
    <div class="values">{vhtml}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="stats">{stats}</div>
    <div class="grid-2 mt-4">
      <div class="span-5"><p class="eyebrow"><span class="num">03</span> Sectors</p><h2>Breadth, with <em>depth</em>.</h2>
        <p class="muted">We work across scales and typologies — and every one informs the others. Hospital planning sharpens our homes; hill hotels teach us about climate.</p></div>
      <div class="span-6" style="grid-column:7 / span 6"><ul class="features">{sectors}</ul></div>
    </div>
  </div>
</section>

{quotes_block()}

<section class="section">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow"><span class="num">04</span> Two studios</p><h2>Chennai &amp; <em>Kumbakonam</em>.</h2></div>
      <p>Visits by appointment. We work on site across Tamil Nadu and online with clients anywhere.</p></div>
    <div class="offices">{offices}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="container feature feature--rev">
    <div class="feature__media"><div class="media ratio-3x2 reveal-img">{img('strata-yercaud/st_3', alt='Terraces and bridge at Strata, Yercaud', sizes='(max-width:900px) 100vw, 58vw')}</div></div>
    <div class="feature__body"><p class="eyebrow">The people</p><h2 class="reveal">Nine specialists, <em>one</em> table.</h2>
      <p class="reveal">Architects, engineers, landscape and MEP designers and project managers working side by side — so nothing is lost between disciplines.</p>
      <a class="btn reveal" href="/team.html">Meet the team {ICONS['arrow']}</a></div>
  </div>
</section>
{cta()}
"""
    page("about.html", "About the Studio — Architects in Chennai & Kumbakonam",
         "Kavinan Design Studio is an architecture, interior, landscape, project management and design + build practice in Chennai and Kumbakonam, founded by Ar. SRK. Our story, principles and studios.",
         body, active="Studio", has_hero=True,
         schema=[{"@type": "AboutPage", "url": URL + "/about.html", "name": "About Kavinan Design Studio", "about": {"@id": URL + "/#organization"}},
                 breadcrumb_schema([("Home", "/"), ("Studio", "/about.html")])])


SERVICE_FAQ = {"architecture": ["process", "approvals"], "interior-design": ["interiors"], "landscape": ["landscape"],
               "project-management": ["build", "fees"], "design-build": ["build"]}


def build_services():
    rows = "".join(f"""<a class="svc-row reveal" href="/services/{s['slug']}.html">
      <span class="n">{s['num']}</span><h3>{s['title']}</h3><p>{esc(s['intro'][:170].rsplit(' ', 1)[0])}…</p><span class="go">{ICONS['arrow-ur']}</span>
      <span class="peek" aria-hidden="true">{img(s['image'], sizes='220px')}</span></a>""" for s in SERVICES)
    comp = """<div class="table-wrap prose"><table><thead><tr><th></th><th>Design only</th><th>Design + supervision</th><th>Design + Build (turnkey)</th></tr></thead><tbody>
<tr><td><strong>Concept, 3D & working drawings</strong></td><td>✓</td><td>✓</td><td>✓</td></tr>
<tr><td><strong>Approval drawings & guidance</strong></td><td>✓</td><td>✓</td><td>✓</td></tr>
<tr><td><strong>BOQ, tendering & contractor selection</strong></td><td>Optional</td><td>✓</td><td>Included</td></tr>
<tr><td><strong>Periodic site visits & quality checks</strong></td><td>—</td><td>✓</td><td>✓ continuous</td></tr>
<tr><td><strong>Construction, procurement & interiors</strong></td><td>Your contractor</td><td>Your contractor</td><td>✓ by our team</td></tr>
<tr><td><strong>Single point of accountability</strong></td><td>—</td><td>Partial</td><td>✓</td></tr>
<tr><td><strong>AI project platform</strong> <a class="text-link" href="/platform.html">(coming soon)</a></td><td>Drawings &amp; approvals</td><td>+ site reports &amp; RFIs</td><td>+ schedule, budget &amp; payments</td></tr>
</tbody></table></div>"""
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('Services', '/services/')])}
  <p class="eyebrow">Services</p>
  <h1>One studio, from idea to <em>keys</em>.</h1>
  <p class="lede">Architecture, interiors, landscape, project management and construction — take one service, or let one accountable team deliver it all.</p>
</div></section>
<section class="section--tight"><div class="container"><div class="svc-list">{rows}</div></div></section>
<section class="section section--alt" id="process"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Process</p><h2>How a project <em>moves</em>.</h2></div><p>Each stage ends with your approval. You'll always know what's next, what it costs and when it happens.</p></div>
  {process_block()}
</div></section>
<section class="section"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Ways to work with us</p><h2>Choose your <em>level</em> of involvement.</h2></div><p>Whichever route you choose, the same team designs your project.</p></div>
  {comp}
</div></section>
{quotes_block()}
{cta()}"""
    page("services/index.html", "Services — Architecture, Interiors, Landscape, Project Management & Design + Build",
         "Architecture, interior design, landscape design, construction project management and turnkey design + build services across Chennai, Kumbakonam and Tamil Nadu.",
         body, active="Services",
         schema=[breadcrumb_schema([("Home", "/"), ("Services", "/services/")])])

    for s in SERVICES:
        inc = "".join(f'<li>{esc(x)}</li>' for x in s["includes"])
        dl = "".join(f'<li>{esc(x)}</li>' for x in s["deliverables"])
        projs = [P_BY_SLUG[x] for x in s["projects"] if x in P_BY_SLUG][:6]
        cards = "".join(project_card(p, i=i) for i, p in enumerate(projs))
        faqs = [f for f in FAQ_ITEMS if f["cat"] in SERVICE_FAQ[s["slug"]]][:6]
        others = "".join(f'<li><a href="/services/{o["slug"]}.html">{o["title"]}</a></li>' for o in SERVICES if o["slug"] != s["slug"])
        body = f"""
<section class="page-hero page-hero--image">
  <div class="ph-img">{img(s['image'], alt=f"{s['title']} by {SITE['name']}", sizes='100vw', eager=True)}</div>
  <div class="container">
    {crumbs([('Home', '/'), ('Services', '/services/'), (s['title'], f"/services/{s['slug']}.html")])}
    <p class="eyebrow">Service {s['num']}</p><h1>{s['title']}</h1><p class="lede">{esc(s['lede'])}</p>
  </div>
</section>
<section class="section"><div class="container grid-2">
  <div class="span-5"><p class="eyebrow">Overview</p><p class="statement reveal" style="font-size:clamp(1.6rem,2.6vw,2.4rem)">{esc(s['intro'])}</p>
    <a class="btn btn--solid mt-2" href="/contact.html">Discuss your project {ICONS['arrow']}</a>
    <div class="svc-illus">{sketch(SERVICE_SKETCH[s['slug']], label=s['title'] + ' illustration')}</div></div>
  <div class="span-6" style="grid-column:7 / span 6"><h2 style="font-size:2rem">What's included</h2><ul class="include-list">{inc}</ul>
    <h2 class="mt-3" style="font-size:2rem">What you receive</h2><ul class="features">{dl}</ul></div>
</div></section>
<section class="section section--alt"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Selected work</p><h2>{s['title']} in <em>practice</em>.</h2></div><a class="link-arrow" href="/projects/">All projects {ICONS['arrow']}</a></div>
  <div class="projects-grid">{cards}</div>
</div></section>
<section class="section"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Process</p><h2>From brief to <em>handover</em>.</h2></div></div>
  {process_block()}
</div></section>
<section class="section section--alt"><div class="container grid-2">
  <div class="span-4"><p class="eyebrow">FAQ</p><h2>Questions about <em>{s['title'].lower()}</em></h2><a class="link-arrow mt-2" href="/faq.html">All FAQs {ICONS['arrow']}</a>
    <h4 class="mt-3" style="font-family:var(--font-body);font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)">Other services</h4><ul class="features">{others}</ul></div>
  <div class="span-7" style="grid-column:6 / span 7">{faq_list(faqs)}</div>
</div></section>
{cta()}"""
        trail = [("Home", "/"), ("Services", "/services/"), (s["title"], f"/services/{s['slug']}.html")]
        page(f"services/{s['slug']}.html", s["seo_title"], s["seo_description"], body, active="Services", has_hero=True,
             og_image=URL + f"/assets/img/og/{s['projects'][0]}.jpg",
             schema=[{"@type": "Service", "name": s["title"], "serviceType": s["title"], "description": s["seo_description"],
                      "provider": {"@id": URL + "/#organization"}, "areaServed": SITE["areas_served"][:12],
                      "url": URL + f"/services/{s['slug']}.html", "image": img_abs(s["image"])},
                     breadcrumb_schema(trail), faq_schema(faqs)])


def build_projects():
    chips = [f'<button class="chip" type="button" data-filter="all" aria-pressed="true">All<span class="count">{len(PROJECTS)}</span></button>']
    for k, lab in SECTORS:
        n = sum(1 for p in PROJECTS if p["sector"] == k)
        chips.append(f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{lab}<span class="count">{n}</span></button>')
    # 12-column rows: wide(8)+tall(4) | 4+4+4 | 6+6 | tall(4)+wide(8) | 4+4+4 — paired cards share one height
    pattern = ["pcard--wide", "pcard--tall", "", "", "", "pcard--half", "pcard--half", "pcard--tall", "pcard--wide", "", "", ""]
    cards = "".join(project_card(p, pattern[i % len(pattern)], i=i) for i, p in enumerate(PROJECTS))
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('Projects', '/projects/')])}
  <p class="eyebrow">Selected works · {len(PROJECTS)} projects</p>
  <h1>Work rooted in <em>place</em>.</h1>
  <p class="lede">Homes, hotels, hospitals, campuses, parks and interiors across Tamil Nadu, India and New Zealand.</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="container">
  <div class="filters" data-filter-group="projects" role="toolbar" aria-label="Filter projects by sector">{''.join(chips)}</div>
  <div class="projects-grid">{cards}</div>
</div></section>
{cta()}"""
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{URL}/projects/{p['slug']}.html", "name": p["title"]} for i, p in enumerate(PROJECTS)]
    page("projects/index.html", "Projects — Architecture & Interior Design Portfolio",
         "Explore the portfolio of Kavinan Design Studio: S-Gan Villa, Strata Yercaud, Alpha Multispeciality Hospital, Elidi Stadia and more — residential, hospitality, healthcare, landscape and interiors.",
         body, active="Projects",
         schema=[{"@type": "CollectionPage", "name": "Projects", "url": URL + "/projects/", "mainEntity": {"@type": "ItemList", "itemListElement": items}},
                 breadcrumb_schema([("Home", "/"), ("Projects", "/projects/")])])

    for i, p in enumerate(PROJECTS):
        prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
        facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in p["facts"].items())
        facts += f"<div><dt>Location</dt><dd>{esc(p['location'])}</dd></div><div><dt>Sector</dt><dd>{SECTOR_LABEL[p['sector']]}</dd></div>"
        body_txt = "".join(f"<p>{inline_md(t)}</p>" for t in p["body"])
        feats = "".join(f"<li>{esc(f)}</li>" for f in p["features"])
        # gallery groups (preserve order)
        groups = {}
        for im in p["images"]:
            groups.setdefault(im.get("group", "Gallery"), []).append(im)
        gal = []
        for g, ims in groups.items():
            figs = "".join(f'<figure class="reveal" data-lightbox="{p["slug"]}" data-full="{img_full(x["key"])}" data-caption="{esc(x["caption"])}">'
                           f'<div class="media">{img(x["key"], alt=p["title"] + " — " + x["caption"], sizes="(max-width:700px) 100vw, 50vw")}</div><figcaption class="caption">{esc(x["caption"])}</figcaption></figure>'
                           for x in ims)
            cols = "gallery--3" if len(ims) >= 6 else ""
            gal.append(f'<div class="gallery-group"><h3>{esc(g)}</h3><div class="gallery {cols}">{figs}</div></div>')
        transform = ""
        if p.get("transformation"):
            labels = ["Existing · Oct 2025", "Strip-out · Dec 2025", "Completed · Mar 2026"]
            tri = "".join(f'<figure class="reveal" style="--d:{j * .1}s"><div class="media">{img(k, alt=p["title"] + " — " + labels[j], sizes="33vw")}</div><div class="step"><b>0{j + 1}</b><span>{labels[j]}</span></div></figure>' for j, k in enumerate(p["transformation"]))
            transform = f'<section class="section section--alt"><div class="container"><div class="section-head"><div><p class="eyebrow">Transformation</p><h2>Existing → in progress → <em>completed</em>.</h2></div><p>Documented on site by our team, from first survey to handover.</p></div><div class="triptych">{tri}</div></div></section>'
        sk = next((x["key"] for x in p["images"] if x["key"] + "-sketch" in MANIFEST), None)
        compare_html = ""
        if sk:
            compare_html = f'''<section class="section"><div class="container grid-2" style="align-items:center">
  <div class="span-4"><p class="eyebrow">Sketch → Render</p><h2>Drawn by hand, <em>refined</em> in 3D.</h2>
  <p class="muted">Every project begins as a pencil sketch. Drag the handle to see how this one grew into the final design.</p></div>
  <div class="span-8" style="grid-column:5 / span 8">{compare(sk, p["title"] + " — render")}</div></div></section>'''
        schedule = ""
        if p.get("schedule"):
            fl = "".join(f'<div class="floor reveal"><h4><span>{esc(f["floor"])}</span><b>{f["total"]}</b></h4>' + "".join(f'<div class="row"><span>{esc(r[0])}</span><span>{r[1]}</span></div>' for r in f["rooms"]) + "</div>" for f in p["schedule"])
            schedule = f'<section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow">Area statement</p><h2>Room schedule <em>(sq.ft)</em></h2></div></div><div class="schedule">{fl}</div><div class="schedule-total"><span class="eyebrow mb-0">Total built-up area · Stilt + 3 floors · 12 m height · 8 guest suites</span><b>6,677 sq.ft</b></div></div></section>'
        svc_links = "".join(f'<li><a href="/services/{s}.html">{S_BY_SLUG[s]["title"]}</a></li>' for s in p["services"])
        related_posts = [x for x in POSTS if x.get("project") == p["slug"]]
        rp = ""
        if related_posts:
            rp = f'<p class="mt-2"><a class="link-arrow link-arrow--wrap" href="/journal/{related_posts[0]["slug"]}.html">Read the story: {esc(related_posts[0]["title"])} {ICONS["arrow"]}</a></p>'
        body = f"""
<section class="page-hero page-hero--image">
  <div class="ph-img">{img(p['cover'], alt=f"{p['title']}, {p['location']}", sizes='100vw', eager=True)}</div>
  <div class="container">
    {crumbs([('Home', '/'), ('Projects', '/projects/'), (p['title'], f"/projects/{p['slug']}.html")])}
    <p class="eyebrow">{SECTOR_LABEL[p['sector']]} · {esc(p['location'])}</p>
    <h1>{esc(p['title'])}</h1>
    <p class="lede">{esc(p['summary'])}</p>
  </div>
</section>
<section class="section"><div class="container">
  <dl class="facts">{facts}</dl>
  <div class="grid-2 mt-4">
    <div class="span-6 prose reveal">{body_txt}{rp}</div>
    <div class="span-5" style="grid-column:8 / span 5">
      <p class="eyebrow">Key features</p><ul class="features">{feats}</ul>
      <p class="eyebrow mt-3">Services</p><ul class="tag-list">{svc_links}</ul>
    </div>
  </div>
</div></section>
{transform}
{compare_html}
<section class="section{' section--alt' if not transform else ''}"><div class="container">{''.join(gal)}</div></section>
{schedule}
<nav class="container pnav" aria-label="More projects">
  <a href="/projects/{prev_p['slug']}.html"><span>← Previous</span><strong>{esc(prev_p['title'])}</strong></a>
  <a href="/projects/{next_p['slug']}.html"><span>Next →</span><strong>{esc(next_p['title'])}</strong></a>
</nav>
{cta(image='strata-yercaud/st_7' if p['slug'] == 'strata-yercaud' else 'strata-yercaud/st_3')}"""
        desc = f"{p['title']}, {p['location']} — {p['summary']} {p['facts'].get('Scope', '')} by {SITE['name']}."
        trail = [("Home", "/"), ("Projects", "/projects/"), (p["title"], f"/projects/{p['slug']}.html")]
        page(f"projects/{p['slug']}.html", f"{p['title']} — {p['location']}", desc[:300], body, active="Projects", has_hero=True,
             og_image=URL + f"/assets/img/og/{p['slug']}.jpg",
             schema=[{"@type": "CreativeWork", "name": p["title"], "description": " ".join(re.sub(r"\*\*", "", t) for t in p["body"])[:500],
                      "url": URL + f"/projects/{p['slug']}.html", "image": [img_abs(x["key"]) for x in p["images"][:6]],
                      "creator": {"@id": URL + "/#organization"}, "genre": SECTOR_LABEL[p["sector"]],
                      "locationCreated": {"@type": "Place", "name": p["location"]}, "keywords": ", ".join(p["features"])},
                     breadcrumb_schema(trail)])


def build_team():
    lead = TEAM[0]
    rest = TEAM[1:]
    grid = "".join(f"""<article class="member reveal" style="--d:{(i % 4) * .07}s"><div class="media">{img(m['photo'], alt=f"{m['name']}, {m['role']} at {SITE['name']}", sizes='(max-width:700px) 50vw, 25vw')}</div>
      <h3>{esc(m['name'])}</h3><p class="role">{esc(m['role'])}</p><p>{esc(m['bio'])}</p></article>""" for i, m in enumerate(rest))
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('Team', '/team.html')])}
  <p class="eyebrow">The Team</p>
  <h1>People behind the <em>work</em>.</h1>
  <p class="lede">A multidisciplinary team of architects, engineers and designers working across architecture, interiors, landscape, MEP and project delivery.</p>
</div></section>
<section class="section" style="padding-top:0"><div class="container team-lead">
  <div class="media reveal-img">{img(lead['photo'], alt=f"{lead['name']} ({lead['full_name']}), {lead['role']}", sizes='(max-width:900px) 100vw, 40vw', eager=True)}</div>
  <div class="body">
    <p class="eyebrow">{esc(lead['role'])}</p>
    <h2 class="reveal">{esc(lead['name'])} <span class="muted" style="font-size:.5em;display:block;margin-top:.4em">{esc(lead['full_name'])}</span></h2>
    <p class="statement reveal" style="font-size:clamp(1.4rem,2.2vw,2rem)">“Architecture should be rooted in its place and delivered with care.”</p>
    <p class="reveal">{esc(lead['bio'])}</p>
    <a class="link-arrow reveal" href="mailto:{lead['email']}">{lead['email']} {ICONS['arrow']}</a>
  </div>
</div></section>
<section class="section section--alt"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Studio</p><h2>Architecture, engineering &amp; <em>delivery</em>.</h2></div><p>Every project is shaped by the whole team — design, landscape, MEP and accounts working together from day one.</p></div>
  <div class="team-grid">{grid}</div>
</div></section>
<section class="section"><div class="container grid-2">
  <div class="span-6"><p class="eyebrow">Careers</p><h2>Grow <em>with</em> us.</h2></div>
  <div class="span-5" style="grid-column:8 / span 5"><p>We're always glad to hear from architects, interior designers, landscape designers, site engineers and interns who care about design and about building it well.</p>
    <p class="muted">Send your CV and portfolio (PDF, under 10 MB) to <a class="text-link" href="mailto:{SITE['emails'][1]}?subject=Career%20application">{SITE['emails'][1]}</a>.</p></div>
</div></section>
{cta()}"""
    people = [{"@type": "Person", "name": m.get("full_name", m["name"]) if m.get("lead") else m["name"], "jobTitle": m["role"],
               "worksFor": {"@id": URL + "/#organization"}, "image": img_abs(m["photo"])} for m in TEAM]
    page("team.html", "Our Team — Architects, Designers & Engineers",
         "Meet the team at Kavinan Design Studio — founder Ar. SRK and our architects, landscape designer, MEP head and project specialists in Chennai & Kumbakonam.",
         body, active="Team", schema=[{"@type": "AboutPage", "url": URL + "/team.html", "name": "Team", "mentions": people},
                                     breadcrumb_schema([("Home", "/"), ("Team", "/team.html")])])


def build_journal():
    tags = []
    for p in POSTS:
        for t in p["tags"]:
            if t not in tags:
                tags.append(t)
    chips = ['<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>'] + \
            [f'<button class="chip" type="button" data-filter="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in tags[:10]]
    cards = journal_card(POSTS[0], lead=True) + "".join(journal_card(p, i=i) for i, p in enumerate(POSTS[1:])) if POSTS else "<p>New articles coming soon.</p>"
    upcoming = ""
    if SCHEDULED:
        nxt = SCHEDULED[-1]
        upcoming = f'<p class="notice mt-3">Next article: <strong>{esc(nxt["title"])}</strong> — publishing {fmt_date(nxt["date"])}. <a class="text-link" href="/feed.xml">Subscribe via RSS</a>.</p>'
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('Journal', '/journal/')])}
  <p class="eyebrow">Journal</p>
  <h1>Notes from the <em>studio</em>.</h1>
  <p class="lede">Project stories, practical guides for homeowners and ideas on building well in Tamil Nadu's climate.</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="container">
  <div class="flex between" data-filter-group="journal">
    <div class="filters" style="margin:0" role="toolbar" aria-label="Filter articles">{''.join(chips)}</div>
    <label class="search" style="margin:0;min-width:260px">{ICONS['search']}<span class="sr-only">Search articles</span><input id="journal-search" type="search" placeholder="Search articles"></label>
  </div>
  <div class="jgrid mt-3">{cards}</div>
  {upcoming}
</div></section>
{cta()}"""
    page("journal/index.html", "Journal — Architecture, Interiors & Homeowner Guides",
         "Articles from Kavinan Design Studio: project stories, renovation and construction guides, interior and landscape ideas, and climate-responsive design for Tamil Nadu homes.",
         body, active="Journal",
         schema=[{"@type": "Blog", "name": f"{SITE['name']} Journal", "url": URL + "/journal/", "publisher": {"@id": URL + "/#organization"},
                  "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{URL}/journal/{p['slug']}.html", "datePublished": p["date"].isoformat()} for p in POSTS]},
                 breadcrumb_schema([("Home", "/"), ("Journal", "/journal/")])])

    for i, p in enumerate(POSTS):
        related = [x for x in POSTS if x is not p and set(x["tags"]) & set(p["tags"])][:3] or [x for x in POSTS if x is not p][:3]
        toc = "".join(f'<li><a href="#{h}">{esc(t)}</a></li>' for h, t in p["toc"])
        proj = P_BY_SLUG.get(p.get("project", ""))
        proj_html = f'<p class="eyebrow mt-3">Project</p><a class="link-arrow link-arrow--wrap" href="/projects/{proj["slug"]}.html">{esc(proj["title"])} {ICONS["arrow"]}</a>' if proj else ""
        tags_html = "".join(f"<li>{esc(t)}</li>" for t in p["tags"])
        body = f"""
<article>
  <header class="container article-head">
    {crumbs([('Home', '/'), ('Journal', '/journal/'), (p['title'], f"/journal/{p['slug']}.html")])}
    <h1>{esc(p['title'])}</h1>
    <p class="lede" style="max-width:52ch">{esc(p['description'])}</p>
    <div class="article-meta"><span>By {esc(p.get('author', 'Kavinan Design Studio'))}</span><time datetime="{p['date']}">{fmt_date(p['date'])}</time><span>{p['read']} min read</span></div>
  </header>
  <div class="container article-cover"><div class="media reveal-img">{img(p['cover'], alt=p['title'], sizes='100vw', eager=True)}</div></div>
  <div class="container article-layout">
    <div class="prose">{p['body_html']}</div>
    <aside class="article-aside">
      {'<p class="eyebrow">In this article</p><ul class="features" style="font-size:.85rem">' + toc + '</ul>' if toc else ''}
      <p class="eyebrow mt-3">Topics</p><ul class="tag-list">{tags_html}</ul>
      {proj_html}
      <p class="eyebrow mt-3">Share</p><div class="share"><button class="btn" type="button" data-share>Share article</button>
        <a class="btn" href="https://wa.me/?text={html.escape(p['title'] + ' ' + URL + '/journal/' + p['slug'] + '.html')}" target="_blank" rel="noopener">WhatsApp</a></div>
    </aside>
  </div>
</article>
<section class="section"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Keep reading</p><h2>More from the <em>journal</em>.</h2></div><a class="link-arrow" href="/journal/">All articles {ICONS['arrow']}</a></div>
  <div class="jgrid">{''.join(journal_card(r, i=j) for j, r in enumerate(related))}</div>
</div></section>
{cta()}"""
        trail = [("Home", "/"), ("Journal", "/journal/"), (p["title"], f"/journal/{p['slug']}.html")]
        page(f"journal/{p['slug']}.html", p["title"], p["description"], body, active="Journal", og_type="article",
             og_image=img_abs(p["cover"]),
             extra_head=f'<meta property="article:published_time" content="{p["date"]}"><meta property="article:modified_time" content="{p["updated"]}">' + "".join(f'<meta property="article:tag" content="{esc(t)}">' for t in p["tags"]),
             schema=[{"@type": "BlogPosting", "headline": p["title"], "description": p["description"], "image": img_abs(p["cover"]),
                      "datePublished": p["date"].isoformat(), "dateModified": p["updated"].isoformat(),
                      "author": {"@type": "Person", "name": "Ar. SRK (Sivaramakrishnan S K)", "url": URL + "/team.html"},
                      "publisher": {"@id": URL + "/#organization"}, "mainEntityOfPage": URL + f"/journal/{p['slug']}.html",
                      "keywords": ", ".join(p["tags"]), "inLanguage": "en-IN"},
                     breadcrumb_schema(trail)])


def build_faq():
    cats = [c for c in FAQS["categories"] if any(f["cat"] == c["id"] for f in FAQ_ITEMS)]
    nav = "".join(f'<a href="#{c["id"]}">{esc(c["title"])}<span>{sum(1 for f in FAQ_ITEMS if f["cat"] == c["id"])}</span></a>' for c in cats)
    sections = "".join(f'<section class="faq-cat" id="{c["id"]}"><h2>{esc(c["title"])}</h2>{faq_list([f for f in FAQ_ITEMS if f["cat"] == c["id"]])}</section>' for c in cats)
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('FAQ', '/faq.html')])}
  <p class="eyebrow">Frequently asked questions</p>
  <h1>Straight <em>answers</em>.</h1>
  <p class="lede">Practical answers on fees, timelines, approvals, design + build, interiors and working with us from anywhere.</p>
  <label class="search mt-2">{ICONS['search']}<span class="sr-only">Search questions</span><input id="faq-search" type="search" placeholder="Search {len(FAQ_ITEMS)} questions — e.g. cost, Vastu, renovation"></label>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="container faq-layout">
  <nav class="faq-nav" aria-label="FAQ categories">{nav}</nav>
  <div>{sections}<p id="faq-empty" class="notice" hidden>No matching questions. <a class="text-link" href="/contact.html">Ask us directly</a> — we reply within one working day.</p></div>
</div></section>
{cta(title="Still have a <em>question</em>?", text="Call, WhatsApp or write to us — a real architect will answer.")}"""
    page("faq.html", "FAQ — Architecture, Interiors, Construction Costs & Design + Build",
         "Answers to common questions about hiring an architect in Chennai and Tamil Nadu — fees, construction cost, timelines, approvals, Vastu, renovation, interiors and design + build.",
         body, active="FAQ", schema=[faq_schema(FAQ_ITEMS), breadcrumb_schema([("Home", "/"), ("FAQ", "/faq.html")])])


def form_open(name, subject, success, form_id=""):
    """Opening <form> tag + hidden fields for the configured provider (content/site.json → form).
    web3forms (default, works on GitHub Pages) · netlify (Netlify hosting) · any other endpoint (e.g. Formspree)."""
    f = SITE["form"]
    provider = f.get("provider", "web3forms")
    hidden = '<p hidden><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'
    if provider == "netlify":
        endpoint = "/"
        attrs = f'name="{name}" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="/thank-you.html"'
        hidden = f'<input type="hidden" name="form-name" value="{name}">' + hidden
    else:
        endpoint = f.get("endpoint") or "https://api.web3forms.com/submit"
        attrs = f'name="{name}" method="POST" action="{endpoint}"'
        if provider == "web3forms":
            hidden += (f'<input type="hidden" name="access_key" value="{esc(f.get("access_key", ""))}">'
                       f'<input type="hidden" name="subject" value="{esc(subject)} — kavinandesignstudio.com">'
                       f'<input type="hidden" name="from_name" value="{esc(SITE["name"])} website">'
                       f'<input type="hidden" name="form" value="{name}">')
    idattr = f' id="{form_id}"' if form_id else ""
    return (f'<form{idattr} class="form" {attrs} data-ajax data-endpoint="{endpoint}" data-mail="{SITE["emails"][1]}" '
            f'data-subject="{esc(subject)}" data-success="{esc(success)}" novalidate>{hidden}')


def build_contact():
    o1, o2 = SITE["offices"]
    svc_checks = "".join(f'<label><input type="checkbox" name="services" value="{s["title"]}"><span>{s["title"]}</span></label>' for s in SERVICES)
    maps = "".join(f"""<div class="reveal"><p class="eyebrow">{esc(o['label'])}</p>
      <iframe class="map" src="{o['embed']}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Map — {esc(o['label'])}"></iframe>
      <p class="mt-1 small">{esc(o['street'])}, {esc(o['locality'])}, {esc(o['city'])} – {o['postal']} · <a class="text-link" href="{o['map']}" target="_blank" rel="noopener">Open in Google Maps</a></p></div>""" for o in SITE["offices"])
    body = f"""
<section class="page-hero"><div class="container">
  {crumbs([('Home', '/'), ('Contact', '/contact.html')])}
  <p class="eyebrow">Contact</p>
  <h1>Let's build something <em>rooted</em>.</h1>
  <p class="lede">Tell us about your project. We reply to every enquiry within one working day.</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="container contact-grid">
  <dl class="contact-list">
    <div><dt>Call</dt><dd>{'<br>'.join(f'<a href="tel:{tel(p)}">{p}</a>' for p in SITE['phones'])}</dd></div>
    <div><dt>WhatsApp</dt><dd><a href="https://wa.me/{SITE['whatsapp']}" target="_blank" rel="noopener">Chat with the studio →</a></dd></div>
    <div><dt>Email</dt><dd>{'<br>'.join(f'<a href="mailto:{e}">{e}</a>' for e in SITE['emails'])}</dd></div>
    <div><dt>Hours</dt><dd>{esc(SITE['hours'])}<br><span class="muted small">Site visits & meetings by appointment</span></dd></div>
    <div><dt>{esc(o1['label'])}</dt><dd>{esc(o1['street'])},<br>{esc(o1['locality'])}, {esc(o1['city'])} – {o1['postal']}</dd></div>
    <div><dt>{esc(o2['label'])}</dt><dd>{esc(o2['street'])},<br>{esc(o2['city'])} – {o2['postal']}</dd></div>
  </dl>
  {form_open("enquiry", "Project enquiry", "Thank you — your enquiry has reached our studio. We'll call or email you within one working day.", "enquiry-form")}
    <div class="field"><label for="f-name">Your name *</label><input id="f-name" name="name" autocomplete="name" required><p class="err">Please enter your name.</p></div>
    <div class="field"><label for="f-phone">Phone / WhatsApp *</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required><p class="err">Please enter a valid phone number.</p></div>
    <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email"></div>
    <div class="field"><label for="f-loc">Project location *</label><input id="f-loc" name="location" placeholder="e.g. Tambaram, Chennai" required><p class="err">Where is the project?</p></div>
    <div class="field"><label for="f-type">Project type</label><select id="f-type" name="project_type">
      <option value="">Select…</option><option>New house / villa</option><option>Renovation / extension</option><option>Apartment interiors</option>
      <option>Farmhouse / landscape</option><option>Hotel / resort / hospitality</option><option>Hospital / clinic</option><option>Office / commercial</option>
      <option>Institution / campus</option><option>Drawings / documentation</option><option>Other</option></select></div>
    <div class="field"><label for="f-budget">Approximate budget</label><select id="f-budget" name="budget">
      <option value="">Prefer to discuss</option><option>Under ₹25 lakh</option><option>₹25 – 50 lakh</option><option>₹50 lakh – 1 crore</option><option>₹1 – 3 crore</option><option>Above ₹3 crore</option></select></div>
    <div class="field full"><label>Services you need</label><div class="checks">{svc_checks}</div></div>
    <div class="field full"><label for="f-msg">Tell us about your project *</label><textarea id="f-msg" name="message" required placeholder="Plot size, rooms you need, timeline, anything else…"></textarea><p class="err">A few words about your project, please.</p></div>
    <div class="full flex">
      <button class="btn btn--solid" type="submit">Send enquiry {ICONS['arrow']}</button>
      <button class="btn" type="button" data-wa-submit="{SITE['whatsapp']}">Send via WhatsApp</button>
    </div>
    <p class="form-note full">By sending this form you agree to be contacted about your enquiry. We never share your details. <a class="text-link" href="/privacy.html">Privacy</a></p>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div></section>
<section class="section section--alt"><div class="container">
  <div class="section-head"><div><p class="eyebrow">Find us</p><h2>Two studios in <em>Tamil Nadu</em>.</h2></div>
  <div class="flex"><img src="/assets/img/brand/location-qr.png" alt="QR code with the studio location" width="96" height="96" loading="lazy" style="background:#fff;padding:6px"><span class="small muted">Scan for<br>location</span></div></div>
  <div class="offices-maps">{maps}</div>
</div></section>"""
    page("contact.html", "Contact — Book a Consultation with Architects in Chennai & Kumbakonam",
         f"Contact Kavinan Design Studio: call {SITE['phones'][0]}, WhatsApp or email {SITE['emails'][0]}. Studios at New Perungalathur, Chennai and Kumbakonam, Tamil Nadu.",
         body, active="Contact",
         schema=[{"@type": "ContactPage", "url": URL + "/contact.html", "name": "Contact", "about": {"@id": URL + "/#organization"}},
                 breadcrumb_schema([("Home", "/"), ("Contact", "/contact.html")])])

    page("thank-you.html", "Thank you", "Thank you for contacting Kavinan Design Studio.", f"""
<section class="page-hero"><div class="container"><p class="eyebrow">Enquiry received</p><h1>Thank <em>you</em>.</h1>
<p class="lede">Your message has reached our studio. We'll call or email you within one working day.</p>
<div class="flex mt-2"><a class="btn btn--solid" href="/projects/">Browse projects {ICONS['arrow']}</a><a class="btn" href="https://wa.me/{SITE['whatsapp']}">WhatsApp us</a></div></div></section>""", noindex=True)


PLATFORM_ICONS = {
    "layers": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M24 6L4 16l20 10 20-10L24 6zM4 24l20 10 20-10M4 32l20 10 20-10"/></svg>',
    "check": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="8" y="6" width="32" height="38" rx="2"/><path d="M16 6v4h16V6M15 24l6 6 12-12"/></svg>',
    "spark": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M24 4l4 14 14 4-14 4-4 14-4-14-14-4 14-4 4-14zM38 34l1.5 4.5L44 40l-4.5 1.5L38 46l-1.5-4.5L32 40l4.5-1.5z"/></svg>',
    "camera": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M6 14h9l3-5h12l3 5h9v26H6z"/><circle cx="24" cy="26" r="8"/></svg>',
    "chart": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M6 6v36h36M14 32V22M22 32V14M30 32V24M38 32V10"/></svg>',
    "chat": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M6 8h36v24H20l-10 8v-8H6z"/><path d="M14 17h20M14 23h12"/></svg>',
    "calendar": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="6" y="10" width="36" height="32" rx="2"/><path d="M6 20h36M16 6v8M32 6v8M14 28h8v6h-8z"/></svg>',
    "lock": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="10" y="22" width="28" height="20" rx="2"/><path d="M16 22v-6a8 8 0 0 1 16 0v6M24 30v5"/></svg>',
}


def platform_mock():
    """A stylised, illustrative product preview built in HTML (no screenshot exists yet)."""
    rows = [("A-101", "Ground floor plan", "R4", "Approved", "ok"), ("A-201", "Front elevation", "R3", "Client review", "wait"),
            ("S-104", "Footing details", "R2", "Issued to site", "ok"), ("E-301", "Lighting layout", "R1", "Consultant comments", "wait")]
    rhtml = "".join(f'<li><b>{c}</b><span>{n}</span><em>{r}</em><i class="st st--{k}">{s}</i></li>' for c, n, r, s, k in rows)
    bars = [("Design development", 100, 0), ("Working drawings", 70, 22), ("Approvals", 45, 40), ("Foundation", 20, 58), ("Superstructure", 0, 70)]
    bhtml = "".join(f'<li><span>{n}</span><div class="bar"><i style="left:{o}%;width:{max(w * (100 - o) / 100, 8):.0f}%" class="{"done" if w == 100 else ""}"></i></div></li>' for n, w, o in bars)
    return f"""<div class="mock" aria-hidden="true">
  <div class="mock-top"><span></span><span></span><span></span><b>Project workspace · Residence, Chennai</b></div>
  <div class="mock-body">
    <aside><p class="on">Overview</p><p>Drawings</p><p>Approvals</p><p>Site</p><p>Budget</p><p>Team</p></aside>
    <div class="mock-main">
      <div class="mock-ai">{PLATFORM_ICONS['spark']}<p><strong>This week, in plain words:</strong> 2 drawings await your approval · foundation inspection on Thursday · no open payment issues.</p></div>
      <div class="mock-cols">
        <div><h5>Drawing register</h5><ul class="mock-dr">{rhtml}</ul></div>
        <div><h5>Schedule</h5><ul class="mock-gantt">{bhtml}</ul></div>
      </div>
    </div>
  </div>
</div>"""


def build_platform():
    pains = [
        ("Old drawings on site", "A superseded drawing gets built because nobody knew a new revision existed."),
        ("Decisions lost in chats", "Approvals buried in WhatsApp threads, calls and emails — then disputed later."),
        ("No single picture", "Clients, consultants and contractors each hold a different version of the truth."),
        ("Clients far from site", "Families abroad or in other cities can't see real progress or what's pending."),
    ]
    pain_html = "".join(f'<div class="value reveal" style="--d:{(i % 4) * .06}s"><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(pains))
    audiences = [
        ("Clients", "See your project's live status, approve designs and materials in one tap, track progress photos, schedule and payments — from anywhere."),
        ("Consultants", "Structural, MEP and landscape consultants share drawings, comments and RFIs against the same register — no duplicated sets."),
        ("Contractors & vendors", "Always build from the latest approved drawing. Raise RFIs, log progress and close snags with clear responsibilities."),
    ]
    aud_html = "".join(f'<div class="aud reveal" style="--d:{i * .08}s"><span class="n">0{i + 1}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(audiences))
    tiers = [
        ("Design only", "For clients who appoint us for design and build with their own contractor.",
         ["Drawing register with every revision", "Design approvals & digital sign-off", "Consultant comments in one place", "Design schedule & deliverables", "Design fee milestones"]),
        ("Design + Supervision", "For clients whose contractor builds while we supervise quality on site.",
         ["Everything in Design only", "Site visit reports with photos", "Stage-wise quality checklists", "RFIs tracked to closure", "Snag lists & contractor progress"]),
        ("Design + Build", "For clients who hand us the whole journey, from first sketch to keys.",
         ["Everything in Design + Supervision", "Live construction schedule", "Daily site photo timeline", "Budget, BOQ & stage-wise payments", "Material approvals & handover documents"]),
    ]
    tier_html = "".join(f"""<div class="tier reveal" style="--d:{i * .08}s"><p class="eyebrow mb-0">Engagement 0{i + 1}</p><h3>{t}</h3><p class="muted">{d}</p>
      <ul>{''.join(f'<li>{x}</li>' for x in items)}</ul></div>""" for i, (t, d, items) in enumerate(tiers))
    feats = [
        ("layers", "One drawing register", "Every sheet, every revision, clearly marked current or superseded — so site always builds from the latest approved drawing."),
        ("check", "Approvals & decisions log", "Designs, materials and changes approved digitally, with who decided what and when — no more 'who said this?'."),
        ("spark", "AI project summaries", "Weekly updates written in plain language: what moved, what's pending, what needs your decision."),
        ("chat", "AI minutes & action items", "Meeting notes turned into clear actions with owners and due dates, followed up automatically."),
        ("calendar", "Schedule & milestones", "A live programme for design and construction, with early warnings when something starts to slip."),
        ("camera", "Site photo timeline", "Dated progress photos and site reports, organised by stage and location."),
        ("chart", "Budget & payments", "BOQ, variations and stage-wise payments tracked transparently against work completed."),
        ("lock", "Right access for each role", "Clients, consultants, contractors and vendors see exactly what they need — nothing more."),
    ]
    feat_html = "".join(f'<div class="value reveal" style="--d:{(i % 4) * .06}s"><div class="ic">{PLATFORM_ICONS[ic]}</div><h3>{t}</h3><p>{d}</p></div>' for i, (ic, t, d) in enumerate(feats))
    steps = [("Now", "In development", "Designing the workflows around how our projects actually run."),
             ("Next", "Pilot on live projects", "Trialled with our ongoing projects, clients, consultants and contractors."),
             ("Then", "Early access", "Opened to registered clients and their project teams."),
             ("Later", "Wider release", "Available to every Kavinan project from day one.")]
    step_html = "".join(f'<li class="reveal" style="--d:{i * .08}s"><span class="k">{a}</span><h4>{b}</h4><p>{c}</p></li>' for i, (a, b, c) in enumerate(steps))
    faqs = [f for f in FAQ_ITEMS if f["cat"] == "platform"]
    body = f"""
<section class="page-hero platform-hero"><div class="container">
  {crumbs([('Home', '/'), ('AI Platform', '/platform.html')])}
  <p class="eyebrow"><span class="pill">Coming soon</span> AI Project &amp; Design Management</p>
  <h1>One shared source of <em>truth</em> for every project.</h1>
  <p class="lede">We're building an AI-powered project and design management platform so clients, consultants and contractors always see the same drawings, decisions, schedule and progress — precise, transparent and free of miscommunication.</p>
  <div class="flex mt-2"><a class="btn btn--solid" href="#early-access">Register for early access {ICONS['arrow']}</a><a class="link-arrow" href="#how">How it works {ICONS['arrow']}</a></div>
  <div class="mt-4 reveal">{platform_mock()}</div>
  <p class="small muted mt-1">Illustrative preview — the platform is in development and features may change.</p>
</div></section>

<section class="section section--alt"><div class="container">
  <div class="section-head"><div><p class="eyebrow"><span class="num">01</span> Why we're building it</p><h2>Most site problems start with a <em>lost message</em>.</h2></div>
  <p>After years of carrying projects from sketch to handover, we've seen the same issues again and again. They're rarely about design — they're about information.</p></div>
  <div class="values values--4">{pain_html}</div>
</div></section>

<section class="section" id="how"><div class="container">
  <div class="section-head"><div><p class="eyebrow"><span class="num">02</span> Everyone on one page</p><h2>Built for the whole <em>project team</em>.</h2></div></div>
  <div class="auds">{aud_html}</div>
</div></section>

<section class="section section--alt"><div class="container">
  <div class="section-head"><div><p class="eyebrow"><span class="num">03</span> Fits how you work with us</p><h2>Useful for <em>every</em> type of client.</h2></div>
  <p>Whether you hire us only for design, for design with supervision, or for full design + build — the platform shows exactly what matters for your engagement.</p></div>
  <div class="tiers">{tier_html}</div>
</div></section>

<section class="section"><div class="container">
  <div class="section-head"><div><p class="eyebrow"><span class="num">04</span> What we're building</p><h2>Planned <em>features</em>.</h2></div>
  <p>AI does the paperwork — summarising, reminding and flagging. Our architects stay in charge of every design and site decision.</p></div>
  <div class="values values--4">{feat_html}</div>
</div></section>

<section class="section section--ink"><div class="container">
  <div class="section-head"><div><p class="eyebrow"><span class="num">05</span> Roadmap</p><h2>From studio tool to <em>client platform</em>.</h2></div></div>
  <ol class="process process--4">{step_html}</ol>
</div></section>

<section class="section" id="early-access"><div class="container contact-grid">
  <div><p class="eyebrow"><span class="num">06</span> Early access</p><h2>Be the first to <em>use it</em>.</h2>
    <p>Register your interest — whether you're a client, a consultant or a contractor. We'll invite you to the pilot and keep you updated as features go live.</p>
    <div class="mt-3">{faq_list(faqs)}</div></div>
  {form_open("platform-early-access", "Platform early access", "Thank you — you're on the early-access list. We'll be in touch as the pilot opens.")}
    <div class="field"><label for="p-name">Your name *</label><input id="p-name" name="name" autocomplete="name" required><p class="err">Please enter your name.</p></div>
    <div class="field"><label for="p-phone">Phone / WhatsApp *</label><input id="p-phone" name="phone" type="tel" autocomplete="tel" required><p class="err">Please enter a valid phone number.</p></div>
    <div class="field"><label for="p-email">Email *</label><input id="p-email" name="email" type="email" autocomplete="email" required><p class="err">Please enter a valid email.</p></div>
    <div class="field"><label for="p-org">Company (optional)</label><input id="p-org" name="company" autocomplete="organization"></div>
    <div class="field full"><label>I am a</label><div class="checks">
      {''.join(f'<label><input type="radio" name="role" value="{r}"{" checked" if i == 0 else ""}><span>{r}</span></label>' for i, r in enumerate(["Client", "Consultant", "Contractor", "Vendor / supplier", "Other"]))}</div></div>
    <div class="field full"><label>Engagement type (for clients)</label><div class="checks">
      {''.join(f'<label><input type="radio" name="engagement" value="{r}"><span>{r}</span></label>' for r in ["Design only", "Design + Supervision", "Design + Build", "Not sure yet"])}</div></div>
    <div class="field full"><label for="p-msg">What would help you most?</label><textarea id="p-msg" name="message" placeholder="e.g. tracking approvals, seeing site progress from abroad, managing RFIs…"></textarea></div>
    <div class="full"><button class="btn btn--solid" type="submit">Join early access {ICONS['arrow']}</button></div>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div></section>
{cta(title="Start your project <em>today</em>.", text="Our platform is coming — our care for every project is already here. Talk to us about your site.")}"""
    page("platform.html", "AI Project & Design Management Platform — Coming Soon",
         "Kavinan Design Studio is building an AI-powered project and design management platform for clients, consultants and contractors — one shared source of truth for drawings, approvals, schedule, site progress and payments.",
         body, active="AI Platform",
         schema=[{"@type": "WebPage", "url": URL + "/platform.html", "name": "AI Project & Design Management Platform",
                  "about": {"@id": URL + "/#organization"}}, faq_schema(faqs),
                 breadcrumb_schema([("Home", "/"), ("AI Platform", "/platform.html")])])


def build_misc():
    page("privacy.html", "Privacy Policy", "How Kavinan Design Studio collects, uses and protects your information.", f"""
<section class="page-hero"><div class="container">{crumbs([('Home', '/'), ('Privacy', '/privacy.html')])}<p class="eyebrow">Legal</p><h1>Privacy <em>policy</em></h1></div></section>
<section class="section--tight" style="padding-top:0"><div class="container"><div class="prose" style="max-width:720px">
<p>Last updated {fmt_date(TODAY)}.</p>
<h2>What we collect</h2><p>When you send an enquiry we receive the details you enter — such as your name, phone number, email, project location and message. If analytics is enabled, we also collect anonymous usage statistics (pages visited, device type, approximate region) to improve this website.</p>
<h2>How we use it</h2><p>Only to respond to your enquiry, prepare proposals and deliver our services. We do not sell or share your personal information with third parties for marketing.</p>
<h2>Where it is stored</h2><p>Form submissions are delivered to our studio email through our website host's form service. Analytics data, if enabled, is processed by Google Analytics.</p>
<h2>Your choices</h2><p>You can ask us to update or delete your information at any time by emailing <a href="mailto:{SITE['emails'][1]}">{SITE['emails'][1]}</a>.</p>
<h2>Cookies</h2><p>This site stores your light/dark mode preference in your browser. Analytics, if enabled, may set cookies; you can block them in your browser settings.</p>
<h2>Contact</h2><p>{esc(SITE['legal_name'])}, {esc(SITE['offices'][0]['street'])}, {esc(SITE['offices'][0]['locality'])}, {esc(SITE['offices'][0]['city'])} – {SITE['offices'][0]['postal']}.</p>
</div></div></section>""")

    page("404.html", "Page not found", "The page you were looking for could not be found.", f"""
<section class="page-hero" style="min-height:80svh"><div class="container"><p class="eyebrow">Error 404</p><h1>This room hasn't been <em>built</em> yet.</h1>
<p class="lede">The page you're looking for may have moved. Try one of these instead:</p>
<div class="flex mt-2"><a class="btn btn--solid" href="/">Home {ICONS['arrow']}</a><a class="btn" href="/projects/">Projects</a><a class="btn" href="/contact.html">Contact</a></div></div></section>""", noindex=True)


# --------------------------------------------------------------------------- feeds & meta files
def build_feeds():
    lastmod = TODAY.isoformat()
    post_dates = {f"/journal/{p['slug']}.html": p["updated"].isoformat() for p in POSTS}
    urls = []
    for u, noindex in SITEMAP:
        if noindex:
            continue
        pri = "1.0" if u == "/" else "0.9" if u.count("/") == 2 and u.endswith("/") or u in ("/contact.html",) else "0.8" if u.startswith(("/projects/", "/services/")) else "0.7"
        urls.append(f"<url><loc>{URL}{u}</loc><lastmod>{post_dates.get(u, lastmod)}</lastmod><priority>{pri}</priority></url>")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /thank-you.html\n\nSitemap: {URL}/sitemap.xml\n", encoding="utf-8")

    items = "".join(f"""<item><title>{esc(p['title'])}</title><link>{URL}/journal/{p['slug']}.html</link><guid>{URL}/journal/{p['slug']}.html</guid>
<pubDate>{dt.datetime.combine(p['date'], dt.time(9, 0), IST).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><description>{esc(p['description'])}</description>{''.join(f'<category>{esc(t)}</category>' for t in p['tags'])}</item>""" for p in POSTS[:20])
    (OUT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>{esc(SITE['name'])} — Journal</title><link>{URL}/journal/</link><description>Project stories and practical guides from {esc(SITE['name'])}.</description>
<language>en-in</language><atom:link href="{URL}/feed.xml" rel="self" type="application/rss+xml"/>{items}
</channel></rss>""", encoding="utf-8")

    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": SITE["name"], "short_name": SITE["short_name"], "start_url": "/", "display": "standalone",
        "background_color": "#f7f5f0", "theme_color": "#126249",
        "icons": [{"src": "/assets/img/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/img/brand/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1), encoding="utf-8")

    # llms.txt — a plain summary for AI search assistants (ChatGPT, Perplexity, Gemini, Claude)
    proj_lines = "\n".join(f"- [{p['title']}]({URL}/projects/{p['slug']}.html): {p['location']} — {p['summary']}" for p in PROJECTS)
    svc_lines = "\n".join(f"- [{s['title']}]({URL}/services/{s['slug']}.html): {s['lede']}" for s in SERVICES)
    (OUT / "llms.txt").write_text(f"""# {SITE['name']}

> {SITE['description']}

Founder & Principal Architect: {SITE['founder']}. Phone: {', '.join(SITE['phones'])}. Email: {SITE['emails'][0]}.
Studios: {SITE['offices'][0]['street']}, {SITE['offices'][0]['locality']}, Chennai {SITE['offices'][0]['postal']}; {SITE['offices'][1]['street']}, Kumbakonam {SITE['offices'][1]['postal']}.

## Services
{svc_lines}

## Projects
{proj_lines}

## Coming soon
- [AI Project & Design Management Platform]({URL}/platform.html): a shared workspace for clients, consultants and contractors — drawings, approvals, schedule, site progress and payments, with AI summaries. In development.

## More
- [FAQ]({URL}/faq.html)
- [Journal]({URL}/journal/)
- [Contact]({URL}/contact.html)
""", encoding="utf-8")

    # Apache / cPanel hosting (Hostinger, GoDaddy, BigRock…): HTTPS + www, 404 page, caching. Ignored by Netlify.
    host = URL.split("//", 1)[1]
    (OUT / ".htaccess").write_text(f"""ErrorDocument 404 /404.html
Options -Indexes
DirectoryIndex index.html

<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{{HTTPS}} off [OR]
  RewriteCond %{{HTTP_HOST}} !^{re.escape(host)}$ [NC]
  RewriteRule ^(.*)$ https://{host}/$1 [L,R=301]
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
</IfModule>

AddType image/webp .webp
AddType application/manifest+json .webmanifest
""", encoding="utf-8")

    # GitHub Pages: custom domain + serve files as-is (no Jekyll processing)
    (OUT / "CNAME").write_text(host + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Netlify headers: long cache for images, short for HTML
    (OUT / "_headers").write_text("""/assets/img/*
  Cache-Control: public, max-age=31536000, immutable
/assets/css/*
  Cache-Control: public, max-age=31536000, immutable
/assets/js/*
  Cache-Control: public, max-age=31536000, immutable
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
""", encoding="utf-8")


# --------------------------------------------------------------------------- docs (local reading copies)
def build_docs():
    """Render README.md and docs/*.md to docs/html/*.html for reading in a browser (not published)."""
    dest = ROOT / "docs" / "html"
    dest.mkdir(parents=True, exist_ok=True)
    style = ("body{font:16px/1.7 'DM Sans',system-ui,sans-serif;max-width:860px;margin:0 auto;padding:40px 20px 80px;color:#12241e;background:#f7f5f0}"
             "h1,h2,h3{font-family:Outfit,system-ui,sans-serif;font-weight:300;line-height:1.15}h1{font-size:3rem}h2{font-size:2rem;margin-top:2.2em;border-top:1px solid #0002;padding-top:.8em}"
             "a{color:#b8460f}table{border-collapse:collapse;width:100%;font-size:.92rem;margin:1em 0}th,td{border-bottom:1px solid #0002;padding:8px 10px 8px 0;text-align:left;vertical-align:top}"
             "pre{background:#171613;color:#ece8df;padding:16px;overflow:auto;border-radius:4px}code{font-family:Consolas,monospace;font-size:.9em}"
             "blockquote{border-left:3px solid #f26122;margin:1.5em 0;padding-left:1em;font-style:italic}nav{margin-bottom:30px;font-size:.85rem}hr{border:0;border-top:1px solid #0002;margin:2em 0}"
             "@media (prefers-color-scheme:dark){body{background:#0c221b;color:#eef2ee}a{color:#f5884f}th,td,h2{border-color:#fff2}}")
    sources = [ROOT / "README.md"] + sorted((ROOT / "docs").glob("*.md"))
    nav = " · ".join(f'<a href="{p.stem}.html">{p.stem.replace("-", " ").title()}</a>' for p in sources)
    for src in sources:
        body, _ = markdown(src.read_text(encoding="utf-8"))
        body = body.replace("[ ]", "☐").replace("✅", "✓")
        (dest / f"{src.stem}.html").write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{src.stem} — {esc(SITE["name"])}</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500&family=DM+Sans:wght@400;600&display=swap">'
            f"<style>{style}</style></head><body><nav>{nav}</nav>{body}</body></html>", encoding="utf-8")
    print(f"Docs rendered to {dest}")


# --------------------------------------------------------------------------- offline copy
def build_offline():
    """Copy public/ to offline/ with relative links, so the site opens by double-clicking
    offline/index.html from a local drive or USB stick (no server needed)."""
    dest = ROOT / "offline"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(OUT, dest, ignore=shutil.ignore_patterns("CNAME", ".nojekyll", ".htaccess", "_headers"))

    def rel(url, prefix):
        if not url.startswith("/") or url.startswith("//"):
            return url
        m = re.match(r"([^?#]*)(.*)", url)
        path, rest = m.group(1), m.group(2)
        if path.endswith("/"):
            path += "index.html"
        return prefix + path.lstrip("/") + rest

    for f in dest.rglob("*.html"):
        depth = len(f.relative_to(dest).parts) - 1
        prefix = "../" * depth
        html = f.read_text(encoding="utf-8")
        html = re.sub(r'((?:href|src|data-full|data-src|action)=")(/[^"]*)"',
                      lambda m: m.group(1) + rel(m.group(2), prefix) + '"', html)
        html = re.sub(r'((?:srcset|data-srcset)=")([^"]*)"',
                      lambda m: m.group(1) + ", ".join(
                          " ".join([rel(p.strip().split(" ")[0], prefix)] + p.strip().split(" ")[1:])
                          for p in m.group(2).split(",")) + '"', html)
        f.write_text(html, encoding="utf-8")
    print(f"Offline copy: open {dest / 'index.html'} by double-clicking")


# --------------------------------------------------------------------------- sub-folder hosting
def apply_base(base):
    """Prefix site-root links with a sub-folder, e.g. "/Website" when GitHub Pages serves the site at
    username.github.io/Website/. The workflow sets SITE_BASE automatically from GitHub; with a custom
    domain it is empty and nothing changes."""
    base = "/" + base.strip("/")

    def fix(url):
        return base + url if url.startswith("/") and not url.startswith("//") and not url.startswith(base + "/") else url

    for f in OUT.rglob("*.html"):
        html = f.read_text(encoding="utf-8")
        html = re.sub(r'((?:href|src|data-full|data-src|action)=")(/[^"]*)"', lambda m: m.group(1) + fix(m.group(2)) + '"', html)
        html = re.sub(r'((?:srcset|data-srcset)=")([^"]*)"',
                      lambda m: m.group(1) + ", ".join(" ".join([fix(p.strip().split(" ")[0])] + p.strip().split(" ")[1:])
                                                       for p in m.group(2).split(",")) + '"', html)
        f.write_text(html, encoding="utf-8")
    mf = OUT / "manifest.webmanifest"
    data = json.loads(mf.read_text(encoding="utf-8"))
    data["start_url"] = base + "/"
    for icon in data["icons"]:
        icon["src"] = fix(icon["src"])
    mf.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"Links prefixed with {base}/ for sub-folder hosting")


# --------------------------------------------------------------------------- main
def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets", ignore=shutil.ignore_patterns("manifest.json"))
    build_home()
    build_about()
    build_services()
    build_projects()
    build_team()
    build_journal()
    build_faq()
    build_contact()
    build_platform()
    build_misc()
    build_feeds()
    base = os.environ.get("SITE_BASE", "").strip()
    if base.strip("/"):
        apply_base(base)
    print(f"Built {len(SITEMAP)} pages into {OUT}  (date {TODAY}, {len(POSTS)} posts live, {len(SCHEDULED)} scheduled, {len(FAQ_ITEMS)} FAQs)")
    for p in reversed(SCHEDULED):
        print(f"  scheduled: {p['date']}  {p['title']}")


if __name__ == "__main__":
    main()
    if "--docs" in sys.argv:
        build_docs()
    if "--offline" in sys.argv:
        build_offline()
    if "--serve" in sys.argv:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("Preview at http://localhost:8000  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()
