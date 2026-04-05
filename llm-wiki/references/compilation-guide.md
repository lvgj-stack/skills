# Compilation Guide

Standards for writing and updating wiki articles. The wiki is only valuable if
the articles are substantive. Follow these rules every time you compile or update.

---

## Article Quality Standards

### Length
- **Target: 800–2000 words** per article
- Below 300 words: the article is a stub — either expand it or merge it into a
  parent article
- Above 2000 words: consider splitting into two articles with a clear parent/child
  relationship

### Source Synthesis
- Every article must draw from **at least 2 sources** where possible
- Do not write an article that summarizes a single source — that's what the
  source summary page is for
- The value of a wiki article is precisely the synthesis across sources: recurring
  themes, contradictions, comparisons

### Wikilinks
- Every article needs **at least 5 `[[wikilinks]]`**, preferably 10+
- Every concept mentioned that has (or should have) its own page must be wikilinked
- Do not over-link: link a term once per article, on first mention
- After writing, scan for concepts mentioned 3+ times that lack a wiki page — note
  them as candidates for new articles

### Citations
- Every factual claim must trace back to a source in `raw/`
- Inline citations: use the format `([Source Title](../raw/articles/filename.md))`
- Avoid assertions that come from general LLM knowledge and aren't in the raw sources
  — if you can't cite it, don't claim it

### Lead Paragraph
- The first paragraph must be a standalone summary of the topic (2–4 sentences)
- It should be readable in isolation — the INDEX.md reader sees this first
- It should answer: what is this, why does it matter, what's the key insight

---

## Backlink Audit (mandatory after every compile)

After writing or updating an article, you must check that other articles link back
to it appropriately:

1. Search `wiki/` for every article that mentions the topic by name
2. For each mention that lacks a `[[wikilink]]`, add the link in that article
3. If a related article should mention the topic but doesn't, add a brief reference

This step is the most commonly skipped — don't skip it. Orphan articles are
the primary indicator of a degraded wiki.

---

## Updating Existing Articles

When a new source changes something already in the wiki, use this structure:

```
**Update (YYYY-MM-DD):**
- **Current:** what the article currently says
- **Proposed:** what it should say instead
- **Reason:** why the new source changes the picture
- **Source:** link to the raw/ file
```

Add this block at the top of the relevant section, then rewrite the section and
remove the block (or keep it as a changelog entry at the bottom if significant).

### Contradiction handling

When a new source contradicts existing content:

1. Do not silently overwrite — note the contradiction explicitly:
   ```
   > **Contradiction:** [Source A](../raw/articles/a.md) claims X.
   > [Source B](../raw/articles/b.md) (added YYYY-MM-DD) claims Y instead.
   > Current best interpretation: [your synthesis].
   ```
2. Update the `updated` frontmatter field
3. List both sources in the `sources` frontmatter array

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it's bad |
|---|---|
| Article summarizes a single source | That's what the source page is for; wiki articles must synthesize |
| Zero outgoing wikilinks | The article is isolated; navigation breaks |
| Zero incoming wikilinks | Orphan page; won't be discovered |
| Factual claims without citations | Unverifiable; may be hallucinated |
| Stub articles (< 300 words) | Waste of a page slot; merge or expand |
| Lead paragraph is not standalone | INDEX.md readers can't assess relevance |

---

## Source Summary Pages

When ingesting a new source, create a dedicated summary page at
`wiki/source-slug.md` in addition to updating topic pages. This page is *not*
a wiki article in the synthesis sense — it's a structured reading note:

```markdown
---
type: wiki
title: "Source: Article Title"
...
---

# Source: Article Title

One-paragraph overview of what this source is about.

## Key Takeaways

- Bullet point of main claim 1
- Bullet point of main claim 2

## Excerpts Worth Revisiting

> "Memorable quote or data point"

## Topics Touched

[[topic-a]], [[topic-b]], [[topic-c]]

## Notes

Any personal observations or caveats about this source.
```

Source pages are always lower priority for the INDEX.md — group them under a
"Sources" section separate from concept articles.
