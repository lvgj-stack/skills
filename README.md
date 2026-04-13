# skills

A collection of Claude Code skills.

## Skills

### llm-wiki

Maintain and query a personal LLM-powered wiki knowledge base.

Automatically triggers when working inside a directory with `raw/`, `wiki/`, and `outputs/` subdirectories. Supports four operations:

- **Ingest** — process source documents from `raw/articles/` into interlinked wiki pages
- **Query** — answer questions from the accumulated wiki with citations
- **Import** — fetch documents from Feishu (docx/wiki URLs) or local paths, auto-discover linked nodes, and auto-ingest into the wiki
- **Lint** — run structural health checks (dead links, orphan pages, INDEX.md drift)

See [`llm-wiki/SKILL.md`](llm-wiki/SKILL.md) for full documentation.