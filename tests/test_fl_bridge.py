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
    (1, 2): ("CLA-76 Stereo", [("Input", 0.375, "-30.0 dB "), ("Attack", 0.4, "3.47 ")]),
    (2, 0): ("Timeless 3", [
        ("Delay Time", 0.3, "350.0 ms "), ("Feedback", 0.35, "35.0% "),
        ("Delay Tap 1 Used", 0.0, "Unused "), ("Delay Tap 1 Level", 0.5, "0.00 dB "),
        ("Filter 1 Used", 1.0, "Used "), ("Filter 1 Freq", 0.3, "200.00 Hz "),
        ("Lo-Fi Enabled", 0.0, "Off "), ("Lo-Fi", 0.5, "50% "),
        ("Drive Enabled", 1.0, "On "), ("Drive", 0.0, "0.00% "),
        ("Num Active XLFOs", 0.17, "1 "), ("XLFO 1 Frequency", 0.5, "0.69 Hz "),
        ("XLFO 1 Step 1 Value", 0.5, "0.5 "), ("XLFO 2 Frequency", 0.5, "0.53 Hz "),
        ("Num Active XLFO 2 Steps", 0.1, "2 "),
    ]),
    (2, 1): ("MixBuddy Tap", [("Tap ID", 1.0, "Unassigned")]),
    (3, 0): ("Mystery Plug", [("Amount", 0.5, "5.0 ")]),
}


def _fake_fl():
    mixer = types.ModuleType("mixer")
    mixer.trackCount = lambda: 4
    mixer.getTrackName = lambda i: {0: "Master", 1: "lead", 2: "verb", 3: "dbl bus"}.get(
        i, f"Insert {i}")
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
    plugins.writes = []

    def set_param(value, p, i, s=-1, pickup=0, g=False):
        # Behaves like MixBuddy Tap's Tap ID: 0..999, 999 shown as "Unassigned".
        plugins.writes.append((i, s, p, value))
        name, _v, _d = PLUGS[(i, s)][1][p]
        n = round(value * 999)
        PLUGS[(i, s)][1][p] = (name, value, "Unassigned" if n == 999 else str(n))
    plugins.setParamValue = set_param

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
    check("mixer hides empty inserts", names == ["Master", "lead", "verb", "dbl bus"], names)
    lead = m["tracks"][1]
    check("mixer lists plugins in slot order",
          [p["plugin"] for p in lead["plugins"]] == ["Pro-Q 4", "Fresh Air", "CLA-76 Stereo"])
    check("mixer resolves routing names",
          {x["to_name"] for x in lead["routes_to"]} == {"Master", "verb"}, lead["routes_to"])

    c = server.fl_get_track_chain(1)
    check("track chain summary", "Pro-Q 4 -> Fresh Air -> CLA-76" in c.get("summary", ""), c)

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

    n = server.fl_get_plugin_params(1, 2)
    check("plugin notes attached (CLA-76 knob direction)",
          "7 is fastest" in n.get("plugin_notes", ""), n.get("plugin_notes"))
    u = server.fl_get_plugin_params(3, 0)
    check("unknown plugin says don't guess", "don't guess" in u.get("plugin_notes", ""))

    t = server.fl_get_plugin_params(2, 0)
    tn = [x["name"] for x in t["params"]]
    check("unused delay taps hidden", "Delay Tap 1 Level" not in tn, tn)
    check("used filters kept", "Filter 1 Freq" in tn, tn)
    check("switched-off modules hidden", "Lo-Fi" not in tn and "Lo-Fi Enabled" in tn, tn)
    check("switched-on modules kept", "Drive" in tn, tn)
    check("inactive LFOs and step data hidden",
          "XLFO 2 Frequency" not in tn and "XLFO 1 Step 1 Value" not in tn
          and "Num Active XLFO 2 Steps" not in tn and "XLFO 1 Frequency" in tn, tn)

    # --- stems ---------------------------------------------------------------
    import numpy as np
    import soundfile as sf
    sdir = tempfile.mkdtemp()
    sr = 44100
    tt = np.arange(sr * 2) / sr
    tone = 0.2 * np.sin(2 * np.pi * 220 * tt)
    for fname in ("BEND DAT_lead.wav", "BEND DAT_dbl bus.wav", "BEND DAT_verb.wav",
                  "notes.txt", "random.wav"):
        path = os.path.join(sdir, fname)
        if fname.endswith(".wav"):
            sf.write(path, np.stack([tone, tone], axis=1), sr)
        else:
            with open(path, "w") as fh:
                fh.write("x")
    ms = server.fl_match_stems(sdir)
    pairs = {os.path.basename(m["file"]): m["track_name"] for m in ms.get("matched", [])}
    check("stems matched by track name",
          pairs == {"BEND DAT_lead.wav": "lead", "BEND DAT_dbl bus.wav": "dbl bus",
                    "BEND DAT_verb.wav": "verb"}, ms)
    check("unmatched audio reported", ms.get("unmatched") == ["random.wav"], ms)

    st = server.fl_analyze_track_stem(1, stems_folder=sdir, analyses="loudness,spectrum")
    check("track stem analyzed with chain",
          st.get("file", "").endswith("BEND DAT_lead.wav")
          and "Pro-Q 4" in (st.get("track") or {}).get("chain", "")
          and "integrated_loudness_lufs" in st.get("results", {}).get("loudness", {}), st)
    bad = server.fl_analyze_track_stem(1, file_path=os.path.join(sdir, "x.wav"),
                                       analyses="nope")
    check("bad analysis name rejected", "error" in bad, bad)

    # --- live taps -------------------------------------------------------------
    import struct
    import time
    tdir = tempfile.mkdtemp()
    os.environ["MIXBUDDY_TAP_DIR"] = tdir
    sr, cap = 48000, 48000 * 10
    n = sr * 3
    tt = np.arange(n) / sr
    frames = np.zeros((cap, 2), dtype="<f4")
    frames[:n, 0] = 0.3 * np.sin(2 * np.pi * 330 * tt)
    frames[:n, 1] = frames[:n, 0]
    hdr = struct.pack("<8sIIIIII QQQQ", b"MBTAP001", 1, 2, sr, 2, cap, 0,
                      n, int(time.time() * 1000), 1, 0)

    lt = server.fl_list_taps()
    tp = (lt.get("taps") or [{}])[0]
    check("tap found on its track and slot",
          tp.get("track_name") == "verb" and tp.get("slot") == 1
          and tp.get("is_last_in_chain") is True, lt)
    import plugins as fl_plugins
    check("bridge sets Tap ID to the track number",
          fl_plugins.writes == [(2, 1, 0, 2 / 999.0)], fl_plugins.writes)
    check("fresh tap flagged as just assigned",
          any("just assigned" in p for p in lt.get("problems", [])), lt)

    # The plugin reopens tap_2.bin and audio flows (simulated here).
    with open(os.path.join(tdir, "tap_2.bin"), "wb") as fh:
        fh.write(hdr + frames.tobytes())
    lt2 = server.fl_list_taps()
    check("second look: no rewrite, tap live",
          len(fl_plugins.writes) == 1 and lt2["taps"][0]["live"] is True
          and not lt2["problems"], lt2)
    la = server.fl_analyze_track_live(2, seconds=3, analyses="loudness,spectrum")
    check("live analysis reads the tap",
          "integrated_loudness_lufs" in la.get("results", {}).get("loudness", {})
          and la.get("track", {}).get("name") == "verb" and "warning" not in la, la)
    nt = server.fl_analyze_track_live(1)
    check("track without a tap explains what to do",
          "No MixBuddy Tap" in nt.get("error", ""), nt)

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
