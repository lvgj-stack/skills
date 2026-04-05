# Frontmatter Schemas

All wiki and output files use YAML frontmatter. This enables Obsidian Dataview
queries and the lint script to reason about the knowledge base programmatically.

---

## Wiki Article

A compiled synthesis article in `wiki/`.

```yaml
---
type: wiki
title: "Human-readable title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - ../raw/articles/filename.md
  - ../raw/articles/another.md
tags:
  - concept
  - tool
  - person
---
```

**Field notes:**
- `type: wiki` — always this value for wiki pages
- `sources` — list every `raw/` file this article drew from; the lint script checks these paths exist
- `tags` — use consistent vocabulary: `concept`, `tool`, `person`, `company`, `event`, `method`, `dataset`
- `updated` — must be refreshed every time the article is modified

---

## Source Document

A raw source file in `raw/articles/`. Add frontmatter when ingesting.

```yaml
---
type: source
source_kind: article          # article | note | data | paper | book-chapter
title: "Original title"
url: "https://..."            # omit if no URL (e.g. personal notes)
author: "Author Name"         # omit if unknown
date: YYYY-MM-DD              # publication date, not ingest date
ingested: YYYY-MM-DD          # date you added it to raw/
tags:
  - topic-tag
---
```

**`source_kind` values:**
- `article` — web article, blog post
- `note` — personal notes or journal entries
- `data` — structured data files (CSV, JSON, etc.)
- `paper` — academic paper
- `book-chapter` — excerpt from a book

---

## Query Output

A filed Q&A answer in `outputs/queries/`.

```yaml
---
type: output
stage: query
question: "The exact question asked"
date: YYYY-MM-DD
sources_consulted:
  - wiki/topic-name.md
  - wiki/another-topic.md
promoted: false               # set to true if promoted to a wiki article
promoted_to: ""               # path of the wiki article, if promoted
---
```

**`promoted`** — when you promote a query answer to a wiki article, set this to
`true` and fill in `promoted_to` so there's a trace.

---

## Lint Report

A structured lint output in `outputs/reports/`.

```yaml
---
type: output
stage: lint-report
date: YYYY-MM-DD
dead_links: 0
orphan_pages: 0
missing_sources: 0
---
```
