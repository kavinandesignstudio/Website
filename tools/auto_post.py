#!/usr/bin/env python3
"""
Kavinan Design Studio — automatic Journal & FAQ writer
======================================================
Turns short studio updates into finished journal articles and new FAQs,
using Claude (Anthropic API). Runs by itself every day on GitHub Actions
(see .github/workflows/publish.yml), or by hand:

    pip install anthropic
    set ANTHROPIC_API_KEY=sk-ant-...          (Windows)   |  export ANTHROPIC_API_KEY=...  (Mac/Linux)
    python tools/auto_post.py                 # process new files in content/updates/
    python tools/auto_post.py --topic         # also write one evergreen guide from content/topics.txt
    python tools/auto_post.py --dry-run       # show what would happen, call nothing

How to feed it:
  1. Drop a short note in content/updates/, e.g. content/updates/2026-11-05-strata-foundation.md

        ---
        date: 2026-11-05
        project: strata-yercaud
        ---
        Foundation and retaining walls for Strata are complete. Stilt-floor columns going up.
        Client approved the Moss Nest interior palette: oak, lime plaster, moss green textiles.

  2. The next run writes a full article in content/journal/ and adds 1–3 related FAQs to
     content/faqs.json, then build.py publishes them.

Environment:
  ANTHROPIC_API_KEY   required for writing (without it the script exits quietly)
  AUTO_PUBLISH        "true" (default) publishes immediately; "false" saves posts as drafts
                      (draft: true) so you can review them before they go live.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
UPDATES = CONTENT / "updates"
JOURNAL = CONTENT / "journal"
STATE = UPDATES / ".processed.json"
TOPICS = CONTENT / "topics.txt"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TODAY = dt.datetime.now(IST).date()
MODEL = "claude-opus-5-5"

POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Article headline, 45-75 characters, natural and specific."},
        "slug": {"type": "string", "description": "lowercase-hyphenated URL slug, 3-8 words"},
        "description": {"type": "string", "description": "Meta description, 130-160 characters, includes a location or service keyword."},
        "tags": {"type": "array", "items": {"type": "string"}, "description": "2-4 short topic tags, Title Case"},
        "cover": {"type": "string", "description": "One image key copied exactly from the AVAILABLE IMAGES list"},
        "project": {"type": "string", "description": "Related project slug from the list, or empty string"},
        "body_markdown": {"type": "string", "description": "Article body in Markdown (## headings, lists, one > pull quote). 450-800 words. No H1. End with a one-line call to action linking to /contact.html."},
        "faqs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "cat": {"type": "string", "enum": ["start", "fees", "process", "build", "interiors", "landscape", "approvals", "remote", "platform"]},
                    "q": {"type": "string"},
                    "a": {"type": "string", "description": "2-4 sentence answer, practical and honest"},
                },
                "required": ["cat", "q", "a"],
                "additionalProperties": False,
            },
            "description": "1-3 new FAQs a homeowner would genuinely ask after reading this. Must not duplicate EXISTING FAQ QUESTIONS.",
        },
    },
    "required": ["title", "slug", "description", "tags", "cover", "project", "body_markdown", "faqs"],
    "additionalProperties": False,
}

SYSTEM = """You write the Journal for Kavinan Design Studio, an architecture, interior design, landscape,
project management and design + build practice in Chennai and Kumbakonam, Tamil Nadu, India, led by
founder and principal architect Ar. SRK (Sivaramakrishnan S K). Tagline: "Rooted with design."

Voice: warm, calm, precise, quietly confident — an experienced architect explaining things clearly to a
homeowner or client. British/Indian English spelling (colour, centre, programme). Short paragraphs.
Practical over poetic. Never invent facts: no made-up prices, client quotes, awards, dates, areas or
regulations. Use only facts from the studio update and project data you are given; when general advice
is needed, keep it general and correct for Tamil Nadu. Write for search: use the natural phrases people
search for (e.g. "architect in Chennai", "house renovation", "interior designer Kumbakonam") where they
fit, never stuffed. Link to relevant pages with relative links such as /projects/<slug>.html,
/services/<slug>.html or /contact.html."""


def front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return {}, text.strip()
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2).strip()


def context():
    projects = json.loads((CONTENT / "projects.json").read_text(encoding="utf-8"))
    faqs = json.loads((CONTENT / "faqs.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "assets" / "img" / "manifest.json").read_text(encoding="utf-8"))
    posts = [front_matter(p.read_text(encoding="utf-8"))[0].get("title", "") for p in JOURNAL.glob("*.md")]
    images = [k for k in manifest if not k.startswith("team/")]
    proj_lines = "\n".join(f"- {p['slug']}: {p['title']} ({p['location']}) — {p['summary']}" for p in projects)
    return projects, faqs, posts, images, proj_lines


def ask_claude(prompt):
    import anthropic  # imported here so --dry-run works without the package

    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": POST_SCHEMA}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("The model declined this request; edit the update text and try again.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response was cut off (max_tokens); try a shorter update.")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def write_post(data, images, projects, faqs, source):
    slugs = {p["slug"] for p in projects}
    cover = data["cover"] if data["cover"] in images else images[0]
    project = data["project"] if data["project"] in slugs else ""
    slug = re.sub(r"[^a-z0-9-]+", "-", data["slug"].lower()).strip("-") or "studio-update"
    path = JOURNAL / f"{TODAY.isoformat()}-{slug}.md"
    n = 2
    while path.exists():
        path = JOURNAL / f"{TODAY.isoformat()}-{slug}-{n}.md"
        n += 1
    draft = os.environ.get("AUTO_PUBLISH", "true").lower() != "true"
    fm = [
        "---",
        f"title: {data['title'].strip()}",
        f"date: {TODAY.isoformat()}",
        f"description: {data['description'].strip()}",
        f"tags: {', '.join(t.strip() for t in data['tags'][:4])}",
        f"cover: {cover}",
    ]
    if project:
        fm.append(f"project: {project}")
    fm += [f"source: {source}", "generated: claude", f"draft: {'true' if draft else 'false'}", "---", ""]
    path.write_text("\n".join(fm) + data["body_markdown"].strip() + "\n", encoding="utf-8")

    existing = {f["q"].strip().lower() for f in faqs["items"]}
    added = 0
    for f in data["faqs"][:3]:
        if f["q"].strip().lower() in existing:
            continue
        faqs["items"].append({"cat": f["cat"], "added": TODAY.isoformat(), "q": f["q"].strip(), "a": f["a"].strip(), "generated": True})
        added += 1
    (CONTENT / "faqs.json").write_text(json.dumps(faqs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}{' (draft)' if draft else ''} + {added} FAQ(s)")


def main():
    dry = "--dry-run" in sys.argv
    UPDATES.mkdir(exist_ok=True)
    done = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else []
    pending = [p for p in sorted(UPDATES.glob("*.md")) if p.name not in done and not p.name.startswith(("_", "README"))]
    topic = None
    if "--topic" in sys.argv and TOPICS.exists():
        lines = [ln.strip() for ln in TOPICS.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
        topic = lines[0] if lines else None

    print(f"{len(pending)} new update(s){', topic: ' + topic if topic else ''}")
    if not pending and not topic:
        return
    if dry:
        for p in pending:
            print("  would process", p.name)
        return
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set — skipping automatic writing (scheduled posts still publish on build).")
        return

    projects, faqs, posts, images, proj_lines = context()
    common = (f"PROJECTS:\n{proj_lines}\n\nEXISTING ARTICLE TITLES (do not repeat):\n" + "\n".join(f"- {t}" for t in posts) +
              "\n\nEXISTING FAQ QUESTIONS (do not repeat):\n" + "\n".join(f"- {f['q']}" for f in faqs["items"]) +
              "\n\nAVAILABLE IMAGES (choose the cover from these keys):\n" + ", ".join(images))

    for p in pending:
        meta, body = front_matter(p.read_text(encoding="utf-8"))
        prompt = (f"Write a journal article based on this studio update dated {meta.get('date', TODAY)}"
                  f"{' about project ' + meta['project'] if meta.get('project') else ''}:\n\n<update>\n{body}\n</update>\n\n"
                  f"Turn it into a useful article for prospective clients — what happened, why it matters, and the design or "
                  f"construction lesson behind it. Prefer a cover image from the related project.\n\n{common}")
        try:
            data = ask_claude(prompt)
            write_post(data, images, projects, faqs, source=f"updates/{p.name}")
            done.append(p.name)
        except Exception as e:  # keep going; the update is retried on the next run
            print(f"  ! {p.name}: {e}")

    if topic:
        prompt = (f"Write an evergreen practical guide for homeowners and clients on this topic:\n\n<topic>\n{topic}\n</topic>\n\n"
                  f"Relate it to the studio's real projects where it genuinely fits.\n\n{common}")
        try:
            data = ask_claude(prompt)
            write_post(data, images, projects, faqs, source="topics.txt")
            remaining = [ln for ln in TOPICS.read_text(encoding="utf-8").splitlines() if ln.strip() != topic]
            TOPICS.write_text("\n".join(remaining) + "\n", encoding="utf-8")
        except Exception as e:
            print(f"  ! topic: {e}")

    STATE.write_text(json.dumps(done, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
