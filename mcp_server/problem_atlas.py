"""
Search the mix problem atlas (knowledge/problem_atlas/*.md) by the words a
user uses to describe what they hear.

Entries are parsed from markdown:

    ### 057 Nasal vocal
    - **severity:** minor
    - **says:** "sounds nasal", "through the nose"
    - **cause:** ...

Scoring is deliberately simple and explainable: a quoted "says" phrase found
in the complaint counts most, then shared words with the phrases and title,
then shared words with the cause.
"""
from __future__ import annotations

import os
import re

_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "knowledge", "problem_atlas")
_ENTRY = re.compile(r"^###\s+(\d{3})\s+(.+)$")
_FIELD = re.compile(r"^-\s+\*\*(\w+):\*\*\s*(.*)$")
_STOP = set("""a an the and or but is are was were be been it its this that my
me i you your of to in on for with at by from as so too very not no just like
sounds sound feel feels kind sort bit little really some how do does can get
make more less than there""".split())
_cache: list[dict] | None = None


_SYN = {"centre": "center", "colour": "color", "upfront": "front", "forward": "front",
        "far": "distant", "away": "distant", "pops": "pop", "popping": "pop",
        "plosives": "pop", "plosive": "pop", "esses": "s", "sibilant": "sibilance"}


def _stem(w: str) -> str:
    w = _SYN.get(w, w)
    for suf in ("iness", "ness", "ing", "ed", "ly", "es", "s", "y"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _words(text: str) -> set[str]:
    return {_stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP}


def load(directory: str | None = None) -> list[dict]:
    """Parse every atlas file into a list of entries (cached)."""
    global _cache
    if _cache is not None and directory is None:
        return _cache
    d = directory or _DIR
    entries: list[dict] = []
    if not os.path.isdir(d):
        return entries
    for fname in sorted(os.listdir(d)):
        if not re.match(r"^\d\d-.*\.md$", fname):
            continue
        domain = fname[3:-3]
        cur = None
        with open(os.path.join(d, fname), encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip()
                m = _ENTRY.match(line)
                if m:
                    cur = {"id": m.group(1), "title": m.group(2).strip(), "domain": domain}
                    entries.append(cur)
                    continue
                f = _FIELD.match(line)
                if f and cur is not None:
                    key, val = f.group(1).lower(), f.group(2).strip()
                    if key == "says":
                        cur["says"] = [s.strip().strip('"').strip()
                                       for s in re.findall(r'"[^"]+"', val)] or [val]
                    elif key == "evidence":
                        cur["evidence"] = [e.strip() for e in val.split(",") if e.strip()]
                    else:
                        cur[key] = val
    if directory is None:
        _cache = entries
    return entries


def lookup(complaint: str, limit: int = 5, domain: str = "",
           entries: list[dict] | None = None) -> list[dict]:
    """Return the best-matching entries for a complaint, each with a score and
    the phrases that matched."""
    entries = entries if entries is not None else load()
    text = " " + re.sub(r"\s+", " ", complaint.lower()) + " "
    cw = _words(complaint)
    out = []
    for e in entries:
        if domain and domain.lower() not in e["domain"]:
            continue
        score, hits = 0.0, []
        for phrase in e.get("says", []):
            p = phrase.lower()
            if p and f" {p} " in text or (len(p) > 6 and p in text):
                score += 6
                hits.append(phrase)
            else:
                shared = _words(phrase) & cw
                if shared:
                    score += 2.0 * len(shared) / max(1, len(_words(phrase)))
                    hits.append(phrase)
        score += 1.5 * len(_words(e["title"]) & cw)
        score += 0.3 * len(_words(e.get("cause", "")) & cw)
        if score > 0:
            out.append((score, e, hits))
    out.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [{**e, "score": round(s, 2), "matched": h[:4]} for s, e, h in out[: max(1, limit)]]
