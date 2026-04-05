---
name: llm-wiki
description: >
  Maintain and query a personal LLM-powered wiki knowledge base. This skill applies
  whenever you are working inside a directory that contains raw/, wiki/, and outputs/
  subdirectories — the LLM Wiki structure. Use it whenever the user:
  asks you to "ingest", "process", "add", or "file" a document or article;
  asks a question that should be answered from their accumulated knowledge;
  asks to "update the wiki", "lint the wiki", "health check", or "check the knowledge base";
  mentions a file in raw/ that should be processed;
  wants to find something they remember reading;
  asks "what do I know about X", "summarize what I've learned about Y", or similar.
  Do NOT wait for the user to say "use the wiki skill" — if the task touches their
  knowledge base, use it automatically.
---

## Overview

This knowledge base follows the LLM Wiki pattern: you (the LLM) own the wiki
entirely. Raw source documents are immutable; you read them and maintain a
persistent, interlinked wiki that accumulates knowledge over time.

The wiki is only valuable if it compounds. Every ingest adds to existing articles,
every query either draws on the wiki or feeds back into it, and every lint pass
keeps the structure healthy.

## Locating the KB Root

All paths in this skill are **relative to the knowledge base root** — the directory
that contains CLAUDE.md and the `raw/`, `wiki/`, `outputs/` subdirectories.

If you're unsure where you are, run `pwd` and look for these markers. If your
working directory is not the KB root, `cd` there before doing any wiki operations.

## Directory Layout

```
<kb-root>/
├── CLAUDE.md                   # Schema document (don't modify)
├── raw/
│   └── articles/               # Immutable source material — NEVER modify
├── wiki/
│   ├── INDEX.md                # Catalog of all pages (always keep current)
│   ├── LOG.md                  # Append-only operation log
│   └── concepts/               # One .md per concept, entity, or source
│       └── [topic].md
└── outputs/
    ├── queries/                # Filed Q&A answers
    └── reports/                # Lint reports
```

## Reference Files

Read these when needed — don't load them on every operation:

- `references/frontmatter-schemas.md` — YAML frontmatter for all file types
- `references/compilation-guide.md` — article quality standards and update workflow
- `assets/wiki-article-template.md` — template for new wiki articles
- `assets/index-template.md` — template for INDEX.md (use when INDEX.md doesn't exist)

---

## Operation 1: Ingest

**Trigger:** User adds a file to `raw/` or asks to process a source.

**Mode:** Automatic — complete all steps, then show a summary of what changed.

### Steps

1. **Read the source** in full. Add YAML frontmatter if missing
   (see `references/frontmatter-schemas.md` → Source Document schema).

2. **Read INDEX.md** to understand what topics already exist in the wiki.

3. **Write a source summary page** at `wiki/concepts/source-[slug].md`:
   - Use the source summary format from `references/compilation-guide.md`
   - Summarize key takeaways, notable quotes, and which topics it touches
   - Wikilink every topic mentioned

4. **Update or create topic pages** for every concept/entity the source covers:
   - **Existing page:** add new information, cite the source, follow the update
     workflow in `references/compilation-guide.md` if changing existing claims
   - **New page:** use `assets/wiki-article-template.md`; ensure it meets the
     quality standards in `references/compilation-guide.md`

5. **Backlink audit** — after writing/updating articles, check that other
   relevant articles link back to newly created or updated pages. Add missing
   wikilinks. This step is mandatory — orphan pages are the primary sign of wiki
   degradation.

6. **Update INDEX.md** — add new pages under the correct category, refresh
   summaries of updated pages.

7. **Append to LOG.md:**
   ```
   ## [YYYY-MM-DD] ingest | Source Title
   Pages created: X | Pages updated: Y
   Key topics: topic-a, topic-b, topic-c
   ```

8. **Report back:** list every file created or modified.

---

## Operation 2: Query

**Trigger:** User asks a question about their knowledge base.

### Steps

1. **Read INDEX.md** — identify relevant pages.

2. **Read relevant wiki pages** — start with summaries, drill into full content
   as needed. Answer only from what's in the wiki; do not supplement from
   general LLM knowledge unless explicitly asked.

3. **Synthesize the answer** with inline citations linking to wiki pages and
   original sources where relevant.

4. **Decide whether to file the answer.** File to `outputs/queries/YYYY-MM-DD-[slug].md`
   when the answer involves:
   - Non-obvious synthesis across multiple wiki pages
   - A conclusion not stated in any single article
   - A comparison or analysis the user might want to revisit

   Use the Query Output frontmatter schema from `references/frontmatter-schemas.md`.

5. **Decide whether to promote.** If a filed answer is substantial and durable
   enough to be useful beyond this conversation, promote it to a proper wiki
   article in `wiki/` and update INDEX.md. Set `promoted: true` and `promoted_to:`
   in the query output file.

---

## Operation 3: Lint

**Trigger:** User asks for a health check, "lint the wiki", or "check the wiki".

### Steps

1. **Run the automated linter** from the KB root:
   ```bash
   # Find the lint script relative to this skill file's location, then run from KB root
   python3 "$(find . -path '*llm-wiki/scripts/lint-wiki.py' | head -1)" wiki/ --raw-dir raw/
   ```
   This checks: dead wikilinks, orphan pages, missing source files, INDEX.md drift.

2. **LLM-driven checks** (scan wiki/ pages):
   - Articles citing sources that seem stale (source date much older than topic)
   - Concepts mentioned 3+ times across articles but lacking their own page
   - Articles shorter than 300 words (stubs that should be expanded or merged)
   - Contradictions between articles not yet marked as such
   - Filed query answers (`outputs/queries/`) whose insights should be absorbed
     into wiki articles

3. **Save a lint report** to `outputs/reports/YYYY-MM-DD-lint.md` with findings
   and recommendations. Use the Lint Report frontmatter schema.

4. **Fix obvious issues** automatically (dead links, INDEX.md drift, missing
   frontmatter). For structural changes (merging articles, resolving
   contradictions), list them and ask the user which to proceed with.

5. **Append to LOG.md:**
   ```
   ## [YYYY-MM-DD] lint | Health check
   Issues found: X | Auto-fixed: Y | Needs review: Z
   ```

---

## Core Conventions

- **Never modify `raw/`** — it is the immutable source of truth
- **`[[links]]` use the file stem without `.md`** — e.g. `[[machine-learning]]`
- **Every wiki page must have YAML frontmatter** — see `references/frontmatter-schemas.md`
- **Every factual claim must cite a source in `raw/`** — no uncited assertions
- **Dates** — ISO format always: `YYYY-MM-DD`
- **File names** — lowercase hyphenated slugs: `some-topic.md`
- **LOG.md is append-only** — never edit past entries
