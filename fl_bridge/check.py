"""
Live check of the MixBuddy FL Studio bridge. Run with FL Studio open:

    python C:\\Users\\brahi\\mix-buddy\\fl_bridge\\check.py

Needs only the Python standard library.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "mcp_server"))
import fl_client  # noqa: E402


def step(title, fn):
    print("\n== " + title)
    t0 = time.perf_counter()
    try:
        out = fn()
        print("   ok in %.0f ms" % ((time.perf_counter() - t0) * 1000))
        return out
    except Exception as e:
        print("   FAILED: %s" % e)
        return None


def main():
    c = fl_client.FLClient(timeout=30)
    d = step("find controller script folder", fl_client.find_script_dir)
    if d:
        print("   " + d)
    door = step("open MIDI port", lambda: fl_client.WinMidiDoorbell(
        os.environ.get("MIXBUDDY_MIDI_PORT", fl_client.DEFAULT_PORT)))
    if not (d and door):
        return
    print("   port: " + door.port)
    c._doorbell = door

    r = step("ping", lambda: c.call("ping"))
    if not r:
        print("\nFL did not answer. Check: FL open, loopMIDI running, MIDI input "
              "'MixBuddy' enabled with Controller type 'MixBuddy'.")
        return
    print("   " + json.dumps(r["result"]))
    print("   round trip %s ms (FL work %s ms)" % (r["round_trip_ms"], r["fl_ms"]))

    pings = []
    for _ in range(10):
        pings.append(c.call("ping")["round_trip_ms"])
    print("   10 pings: min %.1f / avg %.1f / max %.1f ms"
          % (min(pings), sum(pings) / len(pings), max(pings)))

    m = step("mixer snapshot", lambda: c.call("mixer"))
    lead = None
    if m:
        res = m["result"]
        print("   round trip %s ms, FL timing %s" % (m["round_trip_ms"], res.get("timing")))
        for t in res["tracks"]:
            plugs = ", ".join(p["plugin"] for p in t["plugins"]) or "-"
            print("   %2d %-14s %6s dB  %s" % (t["index"], t["name"], t["volume_db"], plugs))
            if lead is None and t["plugins"] and t["index"] != 0:
                lead = t

    if lead:
        s = lead["plugins"][0]["slot"]
        p = step("plugin params: track %d slot %d" % (lead["index"], s),
                 lambda: c.call("params", {"track": lead["index"], "slot": s}))
        if p:
            res = p["result"]
            kept = fl_client.compact_params(res["params"])
            print("   %s: %d params read in %s ms, %d after compaction"
                  % (res["plugin"], len(res["params"]), res["read_ms"], len(kept)))
            for q in kept[:8]:
                print("     %s = %s" % (q["name"], q["display"]))
    door.close()
    print("\nAll done.")


if __name__ == "__main__":
    main()
