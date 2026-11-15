"""
Tests for the FL Studio bridge without FL Studio.

A fake FL API (mixer/plugins/general/ui modules) is installed in sys.modules,
the real controller script (fl_bridge/device_MixBuddy.py) is loaded against it,
and the client's MIDI doorbell is replaced by a function that calls the
script's OnMidiMsg a moment later, the way FL would.

Run: python tests/test_fl_bridge.py
"""
import importlib.util
import os
import sys
import tempfile
import threading
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "mcp_server"))

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name} {detail}")


# ---------------------------------------------------------------- fake FL

PLUGS = {
    (1, 0): ("Pro-Q 4", [
        ("Band 1 Used", 1.0, "Used "), ("Band 1 Frequency", 0.3, "98.25 Hz "),
        ("Band 1 Gain", 0.5, "0.00 dB "), ("Band 1 Dynamic Range", 0.5, "0.00 dB "),
        ("Band 1 Attack", 0.5, "50.0% "), ("Band 1 Speakers", 0.0, "All "),
        ("Band 2 Used", 0.0, "Not Used "), ("Band 2 Frequency", 0.5, "1000 Hz "),
        ("Output Level", 0.5, "0.00 dB "),
        ("MIDI Channel 1 Aftertouch", 1.0, ""),
    ]),
    (1, 1): ("Fresh Air", [("Mid Air", 0.18, "18 % "), ("Trim", 1.0, "0.0 dB ")]),
}


def _fake_fl():
    mixer = types.ModuleType("mixer")
    mixer.trackCount = lambda: 4
    mixer.getTrackName = lambda i: {0: "Master", 1: "lead", 2: "verb"}.get(i, f"Insert {i}")
    mixer.getTrackVolume = lambda i, mode=0: -3.0 if mode == 1 else 0.7
    mixer.getTrackPan = lambda i: 0.0
    mixer.getTrackStereoSep = lambda i: 0.0
    mixer.isTrackMuted = lambda i: False
    mixer.isTrackSolo = lambda i: False
    mixer.isTrackSlotsEnabled = lambda i: True
    mixer.getTrackPeaks = lambda i, m: 0.5
    mixer.getRouteSendActive = lambda s, d: (d == 0 and s != 0) or (s == 1 and d == 2)
    mixer.getRouteToLevel = lambda s, d: 0.8

    plugins = types.ModuleType("plugins")
    plugins.isValid = lambda i, s=-1, g=False: (i, s) in PLUGS
    plugins.getPluginName = lambda i, s=-1, u=0, g=False: PLUGS[(i, s)][0]
    plugins.getParamCount = lambda i, s=-1, g=False: len(PLUGS[(i, s)][1])
    plugins.getParamName = lambda p, i, s=-1, g=False: PLUGS[(i, s)][1][p][0]
    plugins.getParamValue = lambda p, i, s=-1, g=False: PLUGS[(i, s)][1][p][1]
    plugins.getParamValueString = lambda p, i, s=-1, g=False: PLUGS[(i, s)][1][p][2]

    general = types.ModuleType("general")
    general.getVersion = lambda: 38
    ui = types.ModuleType("ui")
    ui.getVersion = lambda mode=0: "Producer Edition v25.1.6 [build 4997]"
    sys.modules.update(mixer=mixer, plugins=plugins, general=general, ui=ui)


def main():
    _fake_fl()
    folder = tempfile.mkdtemp()
    src = os.path.join(ROOT, "fl_bridge", "device_MixBuddy.py")
    dst = os.path.join(folder, "device_MixBuddy.py")
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as g:
        g.write(f.read())
    spec = importlib.util.spec_from_file_location("device_MixBuddy", dst)
    fl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fl)
    fl.OnInit()

    class Ev:
        handled = False

    def doorbell():
        threading.Timer(0.02, lambda: fl.OnMidiMsg(Ev())).start()

    os.environ["MIXBUDDY_FL_DIR"] = folder
    import fl_client
    import server
    server._fl = fl_client.FLClient(doorbell=doorbell, timeout=3)

    print("FL bridge tests")
    r = server.fl_status()
    check("fl_status connects", r.get("connected") is True, r)
    check("fl_status reports FL version", "25.1.6" in str(r.get("fl_version")))

    m = server.fl_get_mixer()
    names = [t["name"] for t in m.get("tracks", [])]
    check("mixer hides empty inserts", names == ["Master", "lead", "verb"], names)
    lead = m["tracks"][1]
    check("mixer lists plugins in slot order",
          [p["plugin"] for p in lead["plugins"]] == ["Pro-Q 4", "Fresh Air"])
    check("mixer resolves routing names",
          {x["to_name"] for x in lead["routes_to"]} == {"Master", "verb"}, lead["routes_to"])

    c = server.fl_get_track_chain(1)
    check("track chain summary", "Pro-Q 4 -> Fresh Air" in c.get("summary", ""), c)

    p = server.fl_get_plugin_params(1, 0)
    pn = [x["name"] for x in p.get("params", [])]
    check("params skip FL's MIDI channel entries", not any(n.startswith("MIDI") for n in pn))
    check("params hide unused EQ bands", not any(n.startswith("Band 2") for n in pn), pn)
    check("params hide inactive dynamic-EQ settings", "Band 1 Attack" not in pn, pn)
    check("params hide surround routing", "Band 1 Speakers" not in pn, pn)
    check("params keep real units", {"name": "Band 1 Frequency", "display": "98.25 Hz",
                                     "i": 1} in p["params"], p["params"])

    q = server.fl_get_plugin_params(1, 1, include="raw")
    check("display text is cleaned", q["params"][0]["display"] == "18 %", q["params"])
    check("raw include adds normalized value", q["params"][0].get("value") == 0.18)

    f = server.fl_get_plugin_params(1, 0, filter="frequency", include="all_bands")
    check("filter + all_bands", [x["name"] for x in f["params"]]
          == ["Band 1 Frequency", "Band 2 Frequency"], f["params"])

    e = server.fl_get_plugin_params(1, 9)
    check("missing plugin returns an error, not a crash", "error" in e, e)

    server._fl = fl_client.FLClient(doorbell=lambda: None, timeout=1.2)
    t = server.fl_status()
    check("no answer from FL gives a helpful error",
          t.get("connected") is False and "loopMIDI" in t.get("error", ""), t)

    print("=" * 40)
    print(f"FL bridge: {passed} passed, {failed} failed")
    print("=" * 40)
    return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
