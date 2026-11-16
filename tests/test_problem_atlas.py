"""Tests for the mix problem atlas: every entry parses, ids are complete, and
common complaints find the right entry. Run: python tests/test_problem_atlas.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "mcp_server"))
import problem_atlas  # noqa: E402

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name} {detail}")


E = problem_atlas.load()
ids = [e["id"] for e in E]
check("250 entries", len(E) == 250, len(E))
check("ids 001-250 in order, no gaps", ids == [f"{i:03d}" for i in range(1, 251)])
need = ("severity", "says", "cause", "check", "fix", "evidence")
bad = [e["id"] for e in E if not all(e.get(k) for k in need)]
check("every entry has severity/says/cause/check/fix/evidence", not bad, bad)
check("severity is minor or major",
      all(e["severity"] in ("minor", "major") for e in E))
check("10 domains of 25", sorted({e["domain"] for e in E}).__len__() == 10 and
      all(sum(1 for e in E if e["domain"] == d) == 25 for d in {e["domain"] for e in E}))

cases = {
    "my vocal sounds nasal": "057",
    "it's muddy": "078",
    "the S sounds hurt my ears": "051",
    "vocal sounds like karaoke on top of the beat": "177",
    "808 disappears on my phone": "084",
    "too much reverb, sounds far away": "176",
    "popping on my Ps": "026",
    "my vocal is boxy like a closet": "002",
    "auto tune sounds too robotic": "151",
}
for q, want in cases.items():
    top = [h["id"] for h in problem_atlas.lookup(q, 3)]
    check(f"'{q}' finds {want}", want in top, top)
check("center/centre spelling both work",
      "204" in [h["id"] for h in problem_atlas.lookup("the center sounds back", 3)])
check("domain filter", all(h["domain"] == "space" for h in
                           problem_atlas.lookup("muddy", 5, domain="space")))
check("nonsense finds nothing", problem_atlas.lookup("qwzx plorb", 3) == [])

print("=" * 40)
print(f"ATLAS: {passed} passed, {failed} failed")
print("=" * 40)
sys.exit(1 if failed else 0)
