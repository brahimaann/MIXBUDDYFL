"""
Project memory for the mixing assistant.

Persists per-project context (reference artists, target loudness, recurring
problems, notes) so the assistant gives consistent advice across sessions.

Design follows Producer Pal's "context" semantics:
  * Reads return the whole stored object for a project.
  * Writes REPLACE the whole object for that project (read first, then write).

Storage is a single JSON file under the user's home directory, keyed by project
name. Writes are atomic (temp file + os.replace) to avoid corruption.
"""
from __future__ import annotations

import json
import os
import tempfile
import time

# All projects live in one JSON file: {project_name: {content..., _updated_at}}.
_STORE_DIR = os.path.join(os.path.expanduser("~"), ".mixing-assistant")
_STORE_PATH = os.path.join(_STORE_DIR, "memory.json")

# A gentle template so a brand-new project advertises the fields that matter.
_TEMPLATE = {
    "reference_artists": [],
    "target_lufs": None,
    "recurring_problems": [],
    "notes": "",
}


def _store_path() -> str:
    """Return the store path, ensuring its directory exists."""
    os.makedirs(_STORE_DIR, exist_ok=True)
    return _STORE_PATH


def _load_store() -> dict:
    """Load the whole multi-project store, or {} if missing/corrupt."""
    path = _store_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Never crash the server because of a bad memory file.
        return {}


def _save_store(store: dict) -> None:
    """Atomically write the whole store to disk."""
    path = _store_path()
    fd, tmp = tempfile.mkstemp(dir=_STORE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)  # atomic on Windows and POSIX
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def read_memory(project: str = "default") -> dict:
    """
    Return the stored memory for a project.

    For a project that has never been written, returns a copy of the template
    plus exists=False so callers know it is empty.
    """
    project = (project or "default").strip() or "default"
    store = _load_store()
    if project not in store:
        return {"project": project, "exists": False, "memory": dict(_TEMPLATE)}
    return {"project": project, "exists": True, "memory": store[project]}


def write_memory(content: dict, project: str = "default") -> dict:
    """
    REPLACE the entire memory for a project. Read first; unread fields are lost.

    Raises TypeError if content is not a dict.
    """
    if not isinstance(content, dict):
        raise TypeError("memory content must be a JSON object (dict)")

    project = (project or "default").strip() or "default"
    stored = dict(content)
    stored["_updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    store = _load_store()
    store[project] = stored
    _save_store(store)
    return {"project": project, "saved": True, "memory": stored}


def list_projects() -> list[str]:
    """Return all known project names."""
    return sorted(_load_store().keys())
