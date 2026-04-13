# LLM Wiki Import Guide

## Overview

The **import** operation enables you to fetch documents directly from Feishu and automatically ingest them into your wiki, complete with recursive node discovery. This eliminates manual document collection and ensures complete documentation by fetching all linked nodes.

## Quick Start

```bash
# Ingest a Feishu docx document with all linked nodes
/llm-wiki import https://bytedance.larkoffice.com/docx/I3gedS2q9ossEqxdAL1ctuCMnDc

# Ingest a Feishu wiki with all child nodes
/llm-wiki import https://bytedance.larkoffice.com/wiki/UxTYwrUjhiQJ9OkkAICcJ4yGnTe
```

## Supported URL Formats

### Feishu Document (Docx)
```
https://bytedance.larkoffice.com/docx/[doc_id]

Example:
https://bytedance.larkoffice.com/docx/I3gedS2q9ossEqxdAL1ctuCMnDc
```

### Feishu Wiki
```
https://bytedance.larkoffice.com/wiki/[wiki_id]

Example:
https://bytedance.larkoffice.com/wiki/UxTYwrUjhiQJ9OkkAICcJ4yGnTe
```

## What Happens When You Import

1. **URL Validation**
   - Parses the Feishu URL and extracts the document ID
   - Returns an error if the URL format is invalid

2. **Directory Setup**
   - Creates `raw/works/ai/YYYY-MM-DD/` directory for today's imports
   - All fetched documents are saved here, with YYYY-MM-DD being today's date

3. **Root Document Fetch**
   - Fetches the document using `lark-cli` API
   - Extracts Markdown content from the response
   - Saves with proper YAML frontmatter

4. **Recursive Node Discovery**
   - Scans the fetched Markdown for Feishu links:
     - Documents: `https://bytedance.larkoffice.com/docx/[id]`
     - Wikis: `https://bytedance.larkoffice.com/wiki/[id]`
   - For each unique linked URL not yet fetched:
     - Fetches the document
     - Saves to the target directory
     - Adds to the discovery queue
   - Continues until no new documents are found or max depth (10 documents) is reached

5. **Document Manifest**
   - Creates `_MANIFEST.md` listing:
     - Root document URL and ID
     - All discovered documents with their URLs and IDs
     - Fetch timestamp
     - Total document count

6. **Auto-Ingest**
   - Automatically runs the **ingest** operation on all fetched files
   - Creates wiki concept pages (source-*.md)
   - Updates related topic pages
   - Updates INDEX.md
   - Appends comprehensive entry to LOG.md

7. **Final Report**
   - Shows total documents fetched
   - Lists all newly created wiki pages
   - Lists all updated wiki pages
   - Provides clickable links to new wiki pages

## Example: Complete Import Workflow

### Input
```
/llm-wiki import https://bytedance.larkoffice.com/docx/I3gedS2q9ossEqxdAL1ctuCMnDc
```

### Process
1. Parse URL → Extract doc_id: `I3gedS2q9ossEqxdAL1ctuCMnDc`, type: `docx`
2. Create directory: `raw/works/ai/YYYY-MM-DD/`
3. Fetch root document → Save as `raw/works/ai/YYYY-MM-DD/arkclaw-tech-planning.md`
4. Scan for links → Find reference to competitive analysis docx
5. Fetch linked document → Save as `raw/works/ai/YYYY-MM-DD/arkclaw-competitive-analysis.md`
6. Create `_MANIFEST.md` with both documents listed
7. Run ingest on both files:
   - Create `wiki/concepts/source-arkclaw-tech-planning.md`
   - Create `wiki/concepts/source-arkclaw-competitive-analysis.md`
   - Update `wiki/concepts/ark-claw.md` with new source references
   - Update `wiki/INDEX.md` with new entries
   - Append entry to `wiki/LOG.md`

### Output Report
```
✓ Import Complete

Documents Fetched: 2
├─ https://bytedance.larkoffice.com/docx/I3gedS2q9ossEqxdAL1ctuCMnDc (root)
└─ https://bytedance.larkoffice.com/docx/GQ2vdyuQ7ohfgxxdc7Lc4MF8n3b (discovered)

Wiki Pages Created: 2
├─ [[source-arkclaw-tech-planning]]
└─ [[source-arkclaw-competitive-analysis]]

Wiki Pages Updated: 2
├─ [[ark-claw]]
└─ [[INDEX.md]]

Saved to: raw/works/ai/YYYY-MM-DD/
Manifest: raw/works/ai/YYYY-MM-DD/_MANIFEST.md
```

## Use Cases

### 1. Bulk Documentation Import
When you have a complex project with multiple linked documentation:
```
/llm-wiki import https://bytedance.larkoffice.com/wiki/[root-wiki-id]
```
Automatically fetches the entire wiki subtree and ingests everything.

### 2. Technical Planning Import
Import comprehensive technical planning documents:
```
/llm-wiki import https://bytedance.larkoffice.com/docx/[planning-doc-id]
```
Fetches main planning doc plus all linked analysis/competitive documents.

### 3. Research Paper Collections
Import a document with extensive references:
```
/llm-wiki import https://bytedance.larkoffice.com/docx/[research-doc-id]
```
Automatically fetches all cited research papers stored as Feishu links.

## Advanced: Avoiding Missed Documents

The import operation is designed to be comprehensive:

- **Recursive Discovery**: Automatically finds all linked documents to depth 10
- **Deduplication**: Avoids refetching the same document by tracking URLs
- **Manifest**: Lists every fetched document for manual verification
- **Traceable Links**: Every wiki page cites the source document with URL and ID

If you suspect documents were missed:
1. Check `raw/works/ai/YYYY-MM-DD/_MANIFEST.md` for the complete list
2. Read the linked documents in Feishu to identify missing references
3. Run import again on the missing document URL
4. The ingest operation will update existing pages with new information

## Troubleshooting

### "Invalid Feishu URL"
- Ensure the URL is in one of these formats:
  - `https://bytedance.larkoffice.com/docx/[doc_id]`
  - `https://bytedance.larkoffice.com/wiki/[wiki_id]`
- Double-check the URL was copied correctly from the address bar

### Some Documents Not Fetched
- Check the manifest at `raw/works/ai/YYYY-MM-DD/_MANIFEST.md`
- Some links may be internal anchors or external URLs, which are skipped
- For missed Feishu documents, run import on their URL directly

### Import Stalled or Very Slow
- Large wiki subtrees (50+ documents) take longer to discover and fetch
- Be patient — the operation will continue to completion
- Check the manifest after completion to see what was fetched

## How It Differs from Manual Ingest

| Aspect | Manual Ingest | Auto Import |
|--------|---------------|------------|
| **Input** | `raw/` file path | Feishu URL |
| **Fetching** | Manual (save file first) | Automatic |
| **Linked Docs** | Must download manually | Automatically discovered |
| **Time** | Multiple steps | Single command |
| **Errors** | Can miss linked docs | Comprehensive discovery |

## Implementation Details

### Helper Script: `import-feishu.py`

Located at `./.claude/skills/llm-wiki/scripts/import-feishu.py`

Functions:
- `extract_doc_id(url)` — Parse URL to get doc ID and type
- `fetch_feishu_doc(doc_id, doc_type)` — Prepare document fetch metadata (actual fetch via lark-cli)
- `extract_feishu_links(markdown)` — Find all Feishu links in content
- `discover_nodes(root_url, max_depth=10)` — Recursive discovery
- `slugify(text)` — Create hyphenated file names

### API Integration

Uses `lark-cli` commands for Feishu access:
```bash
# Wiki node fetch
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'

# Document content fetch
lark-cli api GET "/open-apis/docx/v1/documents/{doc_token}/raw_content" --as user
```

### Directory Structure

```
raw/works/ai/YYYY-MM-DD/
├── _MANIFEST.md                          # Import manifest
├── arkclaw-tech-planning.md              # Root document
├── arkclaw-competitive-analysis.md       # Discovered document
└── [other-discovered-docs].md
```

## Next Steps After Import

1. **Verify the manifest** — Check `_MANIFEST.md` to see what was fetched
2. **Review wiki updates** — Check `[[ark-claw]]` and related pages for new links
3. **Read the LOG entry** — Last entry in `wiki/LOG.md` shows what was ingested
4. **Query the wiki** — Ask questions about the newly imported content

Example:
```
/llm-wiki query ArkClaw 的技术规划是什么？
```
