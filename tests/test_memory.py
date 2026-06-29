"""
Unit tests for the project-memory module.

Uses a temporary HOME so it never touches the user's real ~/.mixing-assistant.
Standalone script (run with: python tests/test_memory.py).
"""
import importlib
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Redirect HOME so memory writes into a throwaway dir, then import the module.
_TMP_HOME = tempfile.mkdtemp(prefix="mixmem_")
os.environ["USERPROFILE"] = _TMP_HOME  # Windows
os.environ["HOME"] = _TMP_HOME         # POSIX

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))
import memory  # noqa: E402

importlib.reload(memory)  # ensure module picks up the patched home

PASS, FAIL = 0, 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        print(f"  PASS  {name}")
        PASS += 1
    else:
        print(f"  FAIL  {name}")
        FAIL += 1


print("=== TEST: read empty project returns template ===")
r = memory.read_memory("song1")
check("exists is False for new project", r["exists"] is False)
check("returns template fields", "reference_artists" in r["memory"])
check("project name echoed", r["project"] == "song1")

print("\n=== TEST: write then read round-trips ===")
content = {
    "reference_artists": ["Brent Faiyaz"],
    "target_lufs": -14,
    "recurring_problems": ["muddy low-mids"],
    "notes": "airy vocal goal",
}
w = memory.write_memory(content, "song1")
check("write reports saved", w["saved"] is True)
check("write stamps _updated_at", "_updated_at" in w["memory"])

r = memory.read_memory("song1")
check("exists is True after write", r["exists"] is True)
check("reference_artists persisted", r["memory"]["reference_artists"] == ["Brent Faiyaz"])
check("target_lufs persisted", r["memory"]["target_lufs"] == -14)

print("\n=== TEST: write replaces (does not merge) ===")
memory.write_memory({"notes": "only notes now"}, "song1")
r = memory.read_memory("song1")
check("old field gone after replace", "reference_artists" not in r["memory"])
check("new field present", r["memory"]["notes"] == "only notes now")

print("\n=== TEST: multiple projects isolated ===")
memory.write_memory({"notes": "project two"}, "song2")
r1 = memory.read_memory("song1")
r2 = memory.read_memory("song2")
check("song1 unaffected by song2", r1["memory"]["notes"] == "only notes now")
check("song2 stored separately", r2["memory"]["notes"] == "project two")
check("list_projects sees both", set(memory.list_projects()) >= {"song1", "song2"})

print("\n=== TEST: default project + bad input ===")
memory.write_memory({"notes": "default proj"})  # no project arg
check("default project works", memory.read_memory()["memory"]["notes"] == "default proj")
try:
    memory.write_memory("not a dict", "song3")
    check("non-dict raises TypeError", False)
except TypeError:
    check("non-dict raises TypeError", True)

print("\n=== TEST: corrupt store does not crash ===")
with open(memory._store_path(), "w", encoding="utf-8") as fh:
    fh.write("{ this is not valid json")
r = memory.read_memory("song1")
check("corrupt file -> empty/template, no crash", r["exists"] is False)

print(f"\n{'='*40}\nMEMORY: {PASS} passed, {FAIL} failed\n{'='*40}")
sys.exit(1 if FAIL else 0)
