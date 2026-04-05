#!/usr/bin/env python3
"""
lint-wiki.py — Structural linter for the llm-wiki knowledge base.

Checks:
  1. Dead wikilinks  — [[Target]] where no matching .md file exists anywhere in wiki/
  2. Orphan pages   — wiki/concepts/*.md with zero incoming wikilinks from other pages
  3. Missing sources — frontmatter sources: entries pointing at nonexistent raw/ files
  4. INDEX.md drift  — concept pages not listed in INDEX.md

Usage:
  python lint-wiki.py <wiki_dir> [--raw-dir <raw_dir>]

  wiki_dir defaults to ./wiki
  raw_dir  defaults to ./raw

Exit codes:
  0 — clean
  1 — issues found
  2 — usage error
"""

import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and inline code to avoid false wikilink matches."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def extract_wikilinks(text: str) -> list[str]:
    """Return list of wikilink targets from [[target]] syntax."""
    clean = strip_code_blocks(text)
    return re.findall(r"\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]", clean)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter block. Returns empty dict if none."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def build_filename_index(wiki_dir: Path) -> dict[str, Path]:
    """Map stem (lowercase) -> full path for every .md anywhere in wiki_dir."""
    index = {}
    for path in wiki_dir.rglob("*.md"):
        index[path.stem.lower()] = path
    return index


def all_content_files(wiki_dir: Path) -> list[Path]:
    """All .md files in wiki_dir, including subdirectories."""
    return list(wiki_dir.rglob("*.md"))


def concept_files(wiki_dir: Path) -> list[Path]:
    """Content article files only (concepts/), excluding INDEX.md and LOG.md."""
    skip = {"INDEX.md", "LOG.md"}
    return [p for p in wiki_dir.rglob("*.md") if p.name not in skip]


def check_dead_links(
    wiki_dir: Path, filename_index: dict[str, Path]
) -> dict[str, list[str]]:
    """Return {relative_path: [dead_target, ...]} for dead wikilinks."""
    issues = {}
    for path in all_content_files(wiki_dir):
        text = path.read_text(encoding="utf-8")
        dead = [
            t for t in extract_wikilinks(text)
            if t.lower() not in filename_index
        ]
        if dead:
            issues[str(path.relative_to(wiki_dir))] = sorted(set(dead))
    return issues


def check_orphan_pages(wiki_dir: Path) -> list[str]:
    """Return concept pages that have zero incoming wikilinks from any other page."""
    incoming: dict[str, int] = defaultdict(int)
    all_files = all_content_files(wiki_dir)

    for path in all_files:
        text = path.read_text(encoding="utf-8")
        for target in extract_wikilinks(text):
            incoming[target.lower()] += 1

    orphans = []
    for path in concept_files(wiki_dir):
        if incoming.get(path.stem.lower(), 0) == 0:
            orphans.append(str(path.relative_to(wiki_dir)))
    return sorted(orphans)


def check_missing_sources(wiki_dir: Path, raw_dir: Path) -> dict[str, list[str]]:
    """Return {relative_path: [missing_src, ...]} for sources: entries that don't exist.

    Resolves each source path relative to the file that declares it.
    """
    issues = {}
    for path in concept_files(wiki_dir):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        sources = fm.get("sources", []) or []
        missing = []
        for src in sources:
            if not isinstance(src, str) or src.startswith("http"):
                continue
            # Resolve relative to the file's own directory
            resolved = (path.parent / src).resolve()
            if not resolved.exists():
                missing.append(src)
        if missing:
            issues[str(path.relative_to(wiki_dir))] = missing
    return issues


def check_index_drift(wiki_dir: Path) -> list[str]:
    """Return concept pages not mentioned in INDEX.md."""
    index_path = wiki_dir / "INDEX.md"
    if not index_path.exists():
        return []
    index_text = index_path.read_text(encoding="utf-8")
    indexed = {t.lower() for t in extract_wikilinks(index_text)}

    return sorted(
        str(p.relative_to(wiki_dir))
        for p in concept_files(wiki_dir)
        if p.stem.lower() not in indexed
    )


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: lint-wiki.py <wiki_dir> [--raw-dir <raw_dir>]", file=sys.stderr)
        sys.exit(2)

    wiki_dir = Path(args[0])
    raw_dir = Path("raw")

    if "--raw-dir" in args:
        idx = args.index("--raw-dir")
        raw_dir = Path(args[idx + 1])

    if not wiki_dir.is_dir():
        print(f"Error: {wiki_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    filename_index = build_filename_index(wiki_dir)
    found_issues = False

    dead = check_dead_links(wiki_dir, filename_index)
    if dead:
        found_issues = True
        print("\n=== Dead Wikilinks ===")
        for fpath, targets in sorted(dead.items()):
            for t in targets:
                print(f"  {fpath}: [[{t}]]")

    orphans = check_orphan_pages(wiki_dir)
    if orphans:
        found_issues = True
        print("\n=== Orphan Pages (zero incoming links) ===")
        for name in orphans:
            print(f"  {name}")

    missing_src = check_missing_sources(wiki_dir, raw_dir)
    if missing_src:
        found_issues = True
        print("\n=== Missing Source Files ===")
        for fpath, paths in sorted(missing_src.items()):
            for p in paths:
                print(f"  {fpath}: {p}")

    drift = check_index_drift(wiki_dir)
    if drift:
        found_issues = True
        print("\n=== Pages Missing from INDEX.md ===")
        for name in drift:
            print(f"  {name}")

    if not found_issues:
        print("✓ Wiki is clean — no structural issues found.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
