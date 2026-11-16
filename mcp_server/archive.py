"""
Session archive: an append-only log of everything mix-buddy sees, so the
assistant can learn from past sessions.

Layout (under ~/.mix-buddy/archive, or $MIXBUDDY_HOME/archive):

    <project-slug>/events.jsonl   one JSON object per line, oldest first
    <project-slug>/state.json     last-seen mixer and plugin settings (for diffs)
    lessons.jsonl                 lessons from every project, for cross-project
                                  learning

Event kinds:
    read      a tool read the mixer or a plugin
    change    a setting differs from the last time mix-buddy saw it (detected
              automatically on every read, so changes the user makes by hand
              are logged the next time anything is read)
    analysis  an audio analysis result (summary and headline numbers)
    snapshot  a full read of the session, with a label ("start", "bounce")
    complaint / decision / outcome / lesson / note
              written by the assistant through archive_note

Nothing here may break a tool: callers wrap these functions in `safe()`.
"""
from __future__ import annotations

import json
import os
import re
import time

_MAX_DATA_CHARS = 6000
NOTE_KINDS = ("complaint", "decision", "outcome", "lesson", "note")


def root() -> str:
    base = os.environ.get("MIXBUDDY_HOME") or os.path.join(os.path.expanduser("~"), ".mix-buddy")
    path = os.path.join(base, "archive")
    os.makedirs(path, exist_ok=True)
    return path


def slug(project: str | None) -> str:
    name = re.sub(r"\.flp$", "", (project or "").strip(), flags=re.I)
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "unknown-project"


def _dir(project: str | None) -> str:
    path = os.path.join(root(), slug(project))
    os.makedirs(path, exist_ok=True)
    return path


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _append(path: str, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # a half-written line never breaks reading
    return out


def _trim(data):
    if data is None:
        return None
    text = json.dumps(data, ensure_ascii=False, default=str)
    if len(text) <= _MAX_DATA_CHARS:
        return data
    return {"truncated": True, "json": text[:_MAX_DATA_CHARS]}


def record(project: str | None, kind: str, summary: str, data=None, **fields) -> dict:
    """Append one event to the project's log and return it."""
    ev = {"ts": _now(), "session": time.strftime("%Y-%m-%d"), "project": project,
          "kind": kind, "summary": summary, **fields}
    if data is not None:
        ev["data"] = _trim(data)
    _append(os.path.join(_dir(project), "events.jsonl"), ev)
    return ev


# ---------------------------------------------------------------------------
# State and automatic change detection
# ---------------------------------------------------------------------------
def _load_state(project) -> dict:
    path = os.path.join(_dir(project), "state.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            s = json.load(fh)
        return s if isinstance(s, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(project, state: dict) -> None:
    path = os.path.join(_dir(project), "state.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False)
    os.replace(tmp, path)


def _track_view(t: dict) -> dict:
    return {
        "name": t.get("name"),
        "volume_db": t.get("volume_db"),
        "pan": t.get("pan"),
        "muted": bool(t.get("muted")),
        "solo": bool(t.get("solo")),
        "plugins": [p.get("plugin") for p in sorted(t.get("plugins", []),
                                                     key=lambda p: p.get("slot", 0))],
        "routes": sorted(int(r["to"]) for r in t.get("routes_to", []) if "to" in r),
    }


def _fmt(v):
    if isinstance(v, float):
        return f"{v:+.2f}" if v else "0"
    return str(v)


def observe_mixer(project, tracks: list[dict]) -> list[dict]:
    """Compare a mixer read with the last one; log and return the changes."""
    state = _load_state(project)
    old = state.get("mixer", {})
    new = {str(t["index"]): _track_view(t) for t in tracks}
    changes = []
    for idx, nv in new.items():
        ov = old.get(idx)
        label = f"track {idx} '{nv['name']}'"
        if ov is None:
            continue  # first sighting is not a change
        if ov["name"] != nv["name"]:
            changes.append(f"{label}: renamed from '{ov['name']}'")
        for key, eps in (("volume_db", 0.05), ("pan", 0.01)):
            a, b = ov.get(key), nv.get(key)
            if a is not None and b is not None and abs(a - b) > eps:
                unit = " dB" if key == "volume_db" else ""
                changes.append(f"{label}: {key} {_fmt(a)}{unit} -> {_fmt(b)}{unit}")
        for key in ("muted", "solo"):
            if ov.get(key) != nv.get(key):
                changes.append(f"{label}: {key} {ov.get(key)} -> {nv.get(key)}")
        if ov.get("plugins") != nv.get("plugins"):
            added = [p for p in nv["plugins"] if p not in ov.get("plugins", [])]
            removed = [p for p in ov.get("plugins", []) if p not in nv["plugins"]]
            if added or removed:
                bits = ([f"added {', '.join(added)}"] if added else []) + \
                       ([f"removed {', '.join(removed)}"] if removed else [])
                changes.append(f"{label}: " + "; ".join(bits))
            else:
                changes.append(f"{label}: chain reordered to {' -> '.join(nv['plugins'])}")
        if ov.get("routes") != nv.get("routes"):
            changes.append(f"{label}: routing {ov.get('routes')} -> {nv.get('routes')}")
    # Tracks missing from this read are kept, not reported: a read without
    # "empty" tracks legitimately leaves out tracks that were emptied.
    state["mixer"] = {**old, **new}
    _save_state(project, state)
    return [record(project, "change", c, source="mixer") for c in changes]


def observe_params(project, track: int, slot: int, plugin: str, track_name: str,
                   params: list[dict]) -> list[dict]:
    """Compare a plugin read with the last read of the same slot; log changes.
    Only parameters present in both reads are compared, so filtered reads work.
    If a different plugin now sits in the slot, the old record is replaced."""
    state = _load_state(project)
    allp = state.setdefault("params", {})
    key = f"{int(track)}:{int(slot)}"
    cur = {p["name"]: str(p.get("display") or "").strip() for p in params if p.get("name")}
    prev = allp.get(key)
    changes = []
    if prev and prev.get("plugin") == plugin:
        for name, disp in cur.items():
            if name in prev["values"] and prev["values"][name] != disp:
                changes.append(f"track {track} '{track_name}' {plugin}: {name} "
                               f"{prev['values'][name]} -> {disp}")
        merged = {**prev["values"], **cur}
    else:
        merged = cur
    allp[key] = {"plugin": plugin, "track_name": track_name, "values": merged,
                 "seen": _now()}
    _save_state(project, state)
    return [record(project, "change", c, source="params", track=int(track),
                   slot=int(slot), plugin=plugin) for c in changes]


# ---------------------------------------------------------------------------
# Notes, lessons, history
# ---------------------------------------------------------------------------
def note(project, kind: str, text: str, tags: list[str] | None = None) -> dict:
    kind = (kind or "note").strip().lower()
    if kind not in NOTE_KINDS:
        raise ValueError(f"kind must be one of {NOTE_KINDS}")
    tags = [t.strip().lower() for t in (tags or []) if t and t.strip()]
    ev = record(project, kind, text, tags=tags)
    if kind == "lesson":
        _append(os.path.join(root(), "lessons.jsonl"),
                {"ts": ev["ts"], "project": project, "text": text, "tags": tags})
    return ev


def history(project, kinds: list[str] | None = None, limit: int = 40,
            session: str | None = None) -> list[dict]:
    evs = _read_jsonl(os.path.join(_dir(project), "events.jsonl"))
    if kinds:
        evs = [e for e in evs if e.get("kind") in kinds]
    if session:
        evs = [e for e in evs if e.get("session") == session]
    return evs[-max(1, int(limit)):]


def sessions(project) -> list[dict]:
    """One line per session date: event counts by kind."""
    out: dict[str, dict] = {}
    for e in _read_jsonl(os.path.join(_dir(project), "events.jsonl")):
        s = out.setdefault(e.get("session", "?"), {})
        s[e.get("kind", "?")] = s.get(e.get("kind", "?"), 0) + 1
    return [{"session": k, "counts": v} for k, v in sorted(out.items())]


def lessons(tags: list[str] | None = None, limit: int = 30) -> list[dict]:
    out = _read_jsonl(os.path.join(root(), "lessons.jsonl"))
    if tags:
        want = {t.lower() for t in tags}
        out = [l for l in out if want & set(l.get("tags", []))]
    return out[-max(1, int(limit)):]


def projects() -> list[str]:
    r = root()
    return sorted(d for d in os.listdir(r) if os.path.isdir(os.path.join(r, d)))


def last_project() -> str | None:
    """The project whose log was written most recently (for when FL is closed)."""
    best, best_t = None, -1.0
    for d in projects():
        p = os.path.join(root(), d, "events.jsonl")
        if os.path.exists(p) and os.path.getmtime(p) > best_t:
            evs = _read_jsonl(p)
            if evs:
                best, best_t = evs[-1].get("project") or d, os.path.getmtime(p)
    return best
