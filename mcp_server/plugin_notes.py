"""
Plugin notes lookup.

Reads skill/references/plugin_notes.md (one "## Title" section per plugin,
with a "match:" line of comma-separated name prefixes) and returns the
section for an FL plugin name. The markdown file is the single source, shared
by the skill and the server.
"""
from __future__ import annotations

import os

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "skill", "references", "plugin_notes.md")
_cache: dict | None = None


def _load(path: str = _PATH) -> list[tuple[list[str], str, str]]:
    sections = []
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return sections
    for chunk in text.split("\n## ")[1:]:
        lines = chunk.strip().splitlines()
        title = lines[0].strip()
        prefixes, body = [], []
        for line in lines[1:]:
            if line.lower().startswith("match:"):
                prefixes = [p.strip().lower() for p in line.split(":", 1)[1].split(",")
                            if p.strip()]
            else:
                body.append(line)
        if prefixes:
            sections.append((prefixes, title, "\n".join(body).strip()))
    return sections


def lookup(plugin_name: str | None) -> dict | None:
    """Return {"title", "notes"} for the plugin, or None if not covered."""
    global _cache
    if not plugin_name:
        return None
    if _cache is None:
        _cache = {"sections": _load()}
    name = plugin_name.strip().lower()
    best = None
    for prefixes, title, body in _cache["sections"]:
        for p in prefixes:
            if name.startswith(p) and (best is None or len(p) > best[0]):
                best = (len(p), title, body)
    if best is None:
        return None
    return {"title": best[1], "notes": best[2]}
