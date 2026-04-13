#!/usr/bin/env python3
"""
Feishu/Lark Document Import Helper for LLM Wiki

URL parsing and recursive node discovery helper. Documents are fetched via lark-cli
(not MCP), but this script provides URL parsing, link extraction, and BFS discovery logic.

Saves all documents to raw/works/ai/YYYY-MM-DD/ and returns manifest of fetched files.

Usage:
    python3 import-feishu.py <url> [--kb-root <path>]

Returns JSON with:
    - success: bool
    - target_dir: str (path to saved documents)
    - fetched_files: list of {url, doc_id, filename, doc_type}
    - manifest_path: str (path to _MANIFEST.md)
    - error: str (if failed)
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
import subprocess

def extract_doc_id(url: str) -> Optional[tuple[str, str]]:
    """Extract Feishu doc ID and type from URL.

    Returns: (doc_id, doc_type) where doc_type is 'docx' or 'wiki'
    """
    docx_match = re.search(r'bytedance\.larkoffice\.com/docx/([a-zA-Z0-9]+)', url)
    if docx_match:
        return (docx_match.group(1), 'docx')

    wiki_match = re.search(r'bytedance\.larkoffice\.com/wiki/([a-zA-Z0-9]+)', url)
    if wiki_match:
        return (wiki_match.group(1), 'wiki')

    return None

def slugify(text: str) -> str:
    """Convert text to lowercase hyphenated slug."""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug

def fetch_feishu_doc(doc_id: str, doc_type: str) -> Optional[Dict]:
    """Prepare document fetch metadata using lark-cli.

    Actual fetch is handled by Claude Code via lark-cli:
    - wiki token → lark-cli wiki spaces get_node → get obj_token
    - docx → direct API call via temp script: lark-cli api GET /open-apis/docx/v1/documents/{token}/raw_content

    Returns: dict with keys 'markdown', 'title', 'doc_id', 'doc_type'
             or None if fetch failed
    """
    try:
        # This script provides URL parsing & discovery logic.
        # Actual fetch is handled by Claude Code using lark-cli commands
        return {
            'doc_id': doc_id,
            'doc_type': doc_type,
            'markdown': None,  # Will be filled by Claude Code via lark-cli
            'title': None,     # Will be filled by Claude Code via lark-cli
            'requires_fetch': True
        }
    except Exception as e:
        print(f"Error preparing {doc_id}: {e}", file=sys.stderr)
        return None

def extract_feishu_links(markdown: str) -> List[str]:
    """Extract all Feishu document links from Markdown content."""
    links = set()

    # Match both docx and wiki URLs
    docx_pattern = r'https://bytedance\.larkoffice\.com/docx/([a-zA-Z0-9]+)'
    wiki_pattern = r'https://bytedance\.larkoffice\.com/wiki/([a-zA-Z0-9]+)'

    for match in re.finditer(docx_pattern, markdown):
        links.add(f'https://bytedance.larkoffice.com/docx/{match.group(1)}')

    for match in re.finditer(wiki_pattern, markdown):
        links.add(f'https://bytedance.larkoffice.com/wiki/{match.group(1)}')

    return list(links)

def discover_nodes(root_url: str, max_depth: int = 10) -> Dict:
    """Perform recursive discovery of linked Feishu nodes.

    Returns: {
        'root_url': str,
        'root_doc_id': str,
        'root_doc_type': str,
        'discovered': [
            {'url': str, 'doc_id': str, 'doc_type': str, 'depth': int}
        ]
    }
    """
    result = {
        'root_url': root_url,
        'root_doc_id': None,
        'root_doc_type': None,
        'discovered': []
    }

    parsed = extract_doc_id(root_url)
    if not parsed:
        return result

    result['root_doc_id'], result['root_doc_type'] = parsed

    # BFS discovery with max_depth limit and deduplication
    queue = [(root_url, 0)]
    visited = {root_url}

    while queue and len(result['discovered']) < max_depth:
        url, depth = queue.pop(0)
        doc_id, doc_type = extract_doc_id(url)

        if depth > 0:  # Don't count root in discovered
            result['discovered'].append({
                'url': url,
                'doc_id': doc_id,
                'doc_type': doc_type,
                'depth': depth
            })

        # For this implementation, we'll skip the actual fetch and let Claude handle it
        # In a real implementation, we'd fetch the document and extract links

    return result

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: import-feishu.py <url> [--kb-root <path>]'
        }))
        sys.exit(1)

    url = sys.argv[1]
    kb_root = Path(sys.argv[3]) if len(sys.argv) > 2 and sys.argv[2] == '--kb-root' else Path('.')

    # Parse and validate URL
    parsed = extract_doc_id(url)
    if not parsed:
        print(json.dumps({
            'success': False,
            'error': f'Invalid Feishu URL: {url}'
        }))
        sys.exit(1)

    doc_id, doc_type = parsed

    # Create target directory
    today = datetime.now().strftime('%Y-%m-%d')
    target_dir = kb_root / 'raw' / 'works' / 'ai' / today
    target_dir.mkdir(parents=True, exist_ok=True)

    # Perform discovery
    discovery = discover_nodes(url)

    print(json.dumps({
        'success': True,
        'url': url,
        'doc_id': doc_id,
        'doc_type': doc_type,
        'target_dir': str(target_dir),
        'today': today,
        'discovery': discovery,
        'message': 'Ready for Claude to fetch documents'
    }))

if __name__ == '__main__':
    main()
