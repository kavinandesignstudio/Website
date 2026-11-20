# Studio updates → automatic journal articles + FAQs

Drop a short note here whenever something happens: a site milestone, a handover, a new
project, a design approval, a competition entry. Two or three sentences is enough.

The daily automation (`tools/auto_post.py`, run by GitHub Actions) turns each new note into a
finished, SEO-friendly journal article plus 1–3 new FAQs, and publishes them.

## File name

`YYYY-MM-DD-short-name.md` — for example `2026-11-05-strata-foundation.md`

## Format

```
---
date: 2026-11-05
project: strata-yercaud
---
Foundation and retaining walls for Strata are complete; stilt-floor columns are going up.
The client approved the Moss Nest interior palette: oak, lime plaster and moss-green textiles.
```

- `project` is optional — use the project's slug (the end of its web address, e.g. `s-gan-villa`).
- Write only true facts. The writer is instructed never to invent prices, dates or quotes,
  so the more real detail you give, the better the article.
- Files starting with `_` are ignored (see `_example.md`).
- Processed notes are remembered in `.processed.json`, so each note is used once.

Want to check articles before they go live? Set the GitHub variable `AUTO_PUBLISH` to `false`.
New articles are then saved with `draft: true`; change it to `draft: false` to publish.
