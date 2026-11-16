# name=MixBuddy
# MixBuddy FL Studio bridge (read-only, v1).
#
# How it works: FL Studio 2025 blocks sockets inside controller scripts, but
# file reads/writes work. A client writes a request to mb_request.json in
# this folder. The script notices it either way:
#   * polling: device.setHasMeters() makes FL call OnUpdateMeters regularly,
#     and the script checks the request file's timestamp there (and in
#     OnIdle, if FL calls it), so a client only has to write the file;
#   * doorbell: a short MIDI message on the loopMIDI port wakes OnMidiMsg.
# It runs the request against FL's mixer/plugins API and writes
# mb_response.json. Every response names the open project.
#
# It only READS from FL, with one exception: "sync_taps" sets the Tap ID of
# MixBuddy Tap plugins to the number of the mixer track they sit on. It
# never changes any other plugin or mixer value.

VERSION = "0.3.0"
TAP_PREFIX = "mixbuddy tap"
TAP_MAX = 999  # Tap ID range is 0..TAP_MAX; TAP_MAX itself means "Unassigned"
REQUEST = "mb_request.json"
RESPONSE = "mb_response.json"
LOG = "mb_log.txt"
LOG_MAX_BYTES = 200000
SLOTS = 10

import json
import os
import sys
import time

import mixer
import plugins

try:
    import device
except ImportError:
    device = None

try:
    import general
except ImportError:
    general = None
try:
    import ui
except ImportError:
    ui = None

_S = {"base": None, "last_id": None, "handled": 0, "req_mtime": None,
      "polls": 0, "poll_source": None}


# ---------------------------------------------------------------- files

def _base_dir():
    if _S["base"]:
        return _S["base"]
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except BaseException:
        pass
    homes = []
    for var in ("USERPROFILE", "HOME"):
        v = os.environ.get(var)
        if v:
            homes.append(v)
    try:
        homes.append(os.path.expanduser("~"))
    except BaseException:
        pass
    for h in homes:
        for docs in (("OneDrive", "Documents"), ("Documents",)):
            cands.append(os.path.join(h, *docs) + "\\Image-Line\\FL Studio\\Settings"
                         "\\Hardware\\MixBuddy")
    for c in cands:
        try:
            if c and os.path.isfile(os.path.join(c, "device_MixBuddy.py")):
                _S["base"] = c
                return c
        except BaseException:
            pass
    _S["base"] = cands[0] if cands else "."
    return _S["base"]


def _path(name):
    return os.path.join(_base_dir(), name)


def _log(msg):
    line = time.strftime("%H:%M:%S ") + str(msg)
    print("[MixBuddy] " + line)
    try:
        p = _path(LOG)
        mode = "a"
        try:
            if os.path.getsize(p) > LOG_MAX_BYTES:
                mode = "w"
        except BaseException:
            pass
        with open(p, mode, encoding="utf-8") as f:
            f.write(line + "\n")
    except BaseException:
        pass


def _write_response(obj):
    # os.replace is not reliable inside FL's sandbox, so write in place.
    # The client re-reads until the JSON parses and the id matches.
    text = json.dumps(obj, ensure_ascii=False, default=str)
    with open(_path(RESPONSE), "w", encoding="utf-8") as f:
        f.write(text)


def _safe(fn, *args):
    try:
        return fn(*args)
    except BaseException:
        return None


# ---------------------------------------------------------------- FL reads

def _clean(s):
    if s is None:
        return None
    return str(s).replace(" ", " ").replace("\xa0", " ").strip()


def _vol_db(t):
    db = _safe(mixer.getTrackVolume, t, 1)
    if db is None:
        return None
    try:
        return round(float(db), 2)
    except BaseException:
        return None


def _peak(t):
    v = _safe(mixer.getTrackPeaks, t, 2)
    return None if v is None else round(float(v), 4)


def _slot_list(t):
    out = []
    for s in range(SLOTS):
        if _safe(plugins.isValid, t, s):
            out.append({"slot": s,
                        "plugin": _clean(_safe(plugins.getPluginName, t, s)),
                        "user_name": _clean(_safe(plugins.getPluginName, t, s, 1))})
    return out


def _project():
    """Best available name for the open project. FL exposes it in different
    places across versions, so try them in order and say which one worked."""
    for mod, fn in ((general, "getProjectTitle"), (ui, "getProjectTitle"),
                    (ui, "getProgTitle")):
        f = getattr(mod, fn, None) if mod else None
        if f is None:
            continue
        v = _safe(f)
        if v:
            return {"title": _clean(v), "source": fn}
    return {"title": None, "source": None}


def cmd_ping(args):
    return {
        "bridge_version": VERSION,
        "project": _project(),
        "polling": {"source": _S["poll_source"], "polls": _S["polls"]},
        "fl_version": _safe(ui.getVersion) if ui else None,
        "api_version": _safe(general.getVersion) if general else None,
        "track_count": _safe(mixer.trackCount),
        "python": sys.version.split()[0],
    }


def cmd_mixer(args):
    timing = {}
    t0 = time.time()
    n = mixer.trackCount()
    include_empty = bool(args.get("include_empty"))
    tracks = []
    for t in range(n):
        name = _clean(_safe(mixer.getTrackName, t))
        slots = _slot_list(t)
        rec = {
            "index": t,
            "name": name,
            "volume_db": _vol_db(t),
            "volume_norm": _safe(mixer.getTrackVolume, t),
            "pan": _safe(mixer.getTrackPan, t),
            "stereo_sep": _safe(mixer.getTrackStereoSep, t),
            "muted": _safe(mixer.isTrackMuted, t),
            "solo": _safe(mixer.isTrackSolo, t),
            "fx_enabled": _safe(mixer.isTrackSlotsEnabled, t),
            "peak": _peak(t),
            "plugins": slots,
        }
        tracks.append(rec)
    timing["tracks_ms"] = round((time.time() - t0) * 1000, 1)

    # Routing: which tracks feed which, and at what level.
    t1 = time.time()
    for src in tracks:
        sends = []
        for dst in range(n):
            if dst == src["index"]:
                continue
            if _safe(mixer.getRouteSendActive, src["index"], dst):
                lvl = _safe(mixer.getRouteToLevel, src["index"], dst)
                sends.append({"to": dst, "level_norm": lvl})
        src["routes_to"] = sends
    timing["routing_ms"] = round((time.time() - t1) * 1000, 1)

    if not include_empty:
        used = set()
        for tr in tracks:
            for r in tr["routes_to"]:
                used.add(r["to"])
        tracks = [tr for tr in tracks
                  if tr["index"] == 0 or tr["plugins"] or tr["index"] in used
                  or (tr["name"] and not str(tr["name"]).startswith("Insert "))]
    return {"track_count": n, "tracks": tracks, "timing": timing}


def cmd_track(args):
    t = int(args["track"])
    out = {"index": t, "name": _clean(_safe(mixer.getTrackName, t)),
           "volume_db": _vol_db(t), "pan": _safe(mixer.getTrackPan, t),
           "peak": _peak(t), "slots": []}
    for s in _slot_list(t):
        s["param_count"] = _safe(plugins.getParamCount, t, s["slot"])
        out["slots"].append(s)
    return out


def cmd_params(args):
    t = int(args["track"])
    s = int(args["slot"])
    if not plugins.isValid(t, s):
        raise ValueError("no plugin on track %d slot %d" % (t, s))
    flt = (args.get("filter") or "").lower()
    count = plugins.getParamCount(t, s)
    params = []
    t0 = time.time()
    for p in range(count):
        name = _safe(plugins.getParamName, p, t, s)
        if not name or str(name).startswith("MIDI CC") or str(name).startswith("MIDI Channel"):
            continue
        name = _clean(name)
        if flt and flt not in name.lower():
            continue
        params.append({"i": p, "name": name,
                       "value": _safe(plugins.getParamValue, p, t, s),
                       "display": _clean(_safe(plugins.getParamValueString, p, t, s))})
    return {"track": t, "slot": s,
            "track_name": _clean(_safe(mixer.getTrackName, t)),
            "plugin": _clean(_safe(plugins.getPluginName, t, s)),
            "user_name": _clean(_safe(plugins.getPluginName, t, s, 1)),
            "param_count": count, "params": params,
            "read_ms": round((time.time() - t0) * 1000, 1)}


def cmd_peaks(args):
    n = mixer.trackCount()
    return {"peaks": [{"index": t, "peak": _peak(t)} for t in range(n)]}


def _tap_param(t, s):
    count = _safe(plugins.getParamCount, t, s) or 0
    for p in range(min(count, 64)):
        if _safe(plugins.getParamName, p, t, s) == "Tap ID":
            return p
    return None


def cmd_sync_taps(args):
    """Find every MixBuddy Tap and set its Tap ID to its mixer track number."""
    only = args.get("track")
    n = mixer.trackCount()
    taps = []
    for t in range(n):
        if only is not None and t != int(only):
            continue
        for s in range(SLOTS):
            if not _safe(plugins.isValid, t, s):
                continue
            name = _clean(_safe(plugins.getPluginName, t, s)) or ""
            if not name.lower().startswith(TAP_PREFIX):
                continue
            rec = {"track": t, "track_name": _clean(_safe(mixer.getTrackName, t)),
                   "slot": s, "tap_id": t}
            p = _tap_param(t, s)
            if p is None:
                rec["error"] = "Tap ID parameter not found"
            elif t > TAP_MAX - 1:
                rec["error"] = "track number above %d" % (TAP_MAX - 1)
            else:
                before = _clean(_safe(plugins.getParamValueString, p, t, s))
                rec["was"] = before
                if before != str(t):
                    plugins.setParamValue(t / float(TAP_MAX), p, t, s)
                    rec["changed"] = True
            taps.append(rec)
    return {"taps": taps}


COMMANDS = {"ping": cmd_ping, "mixer": cmd_mixer, "track": cmd_track,
            "params": cmd_params, "peaks": cmd_peaks, "sync_taps": cmd_sync_taps}


# ---------------------------------------------------------------- request loop

def _serve():
    try:
        with open(_path(REQUEST), "r", encoding="utf-8") as f:
            req = json.loads(f.read())
    except BaseException as e:
        _log("could not read request: %s: %s" % (type(e).__name__, e))
        return
    rid = req.get("id")
    if rid is None or rid == _S["last_id"]:
        return  # nothing new
    _S["last_id"] = rid
    cmd = req.get("cmd")
    t0 = time.time()
    try:
        fn = COMMANDS.get(cmd)
        if fn is None:
            raise ValueError("unknown command: %r" % (cmd,))
        resp = {"id": rid, "ok": True, "result": fn(req.get("args") or {})}
    except BaseException as e:
        resp = {"id": rid, "ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    resp["fl_ms"] = round((time.time() - t0) * 1000, 1)
    resp["project"] = _project()["title"]
    try:
        _write_response(resp)
    except BaseException as e:
        _log("could not write response: %s: %s" % (type(e).__name__, e))
        return
    _S["handled"] += 1
    if not resp["ok"]:
        _log("%s failed: %s" % (cmd, resp["error"]))


# ---------------------------------------------------------------- FL callbacks

def _poll(source):
    """Serve a request if mb_request.json changed since we last looked."""
    _S["polls"] += 1
    if _S["poll_source"] is None:
        _S["poll_source"] = source
        _log("polling active via %s" % source)
    try:
        m = os.path.getmtime(_path(REQUEST))
    except BaseException:
        return
    if m != _S["req_mtime"]:
        _S["req_mtime"] = m
        _serve()


def OnInit():
    _log("MixBuddy bridge %s loaded, folder: %s" % (VERSION, _base_dir()))
    # Ask FL for regular OnUpdateMeters calls; we use them as a poll tick.
    if device is not None:
        try:
            device.setHasMeters()
        except BaseException as e:
            _log("setHasMeters failed: %r" % (e,))
    # Don't replay a request left over from before this load.
    try:
        _S["req_mtime"] = os.path.getmtime(_path(REQUEST))
        with open(_path(REQUEST), "r", encoding="utf-8") as f:
            _S["last_id"] = json.loads(f.read()).get("id")
    except BaseException:
        pass
    _log("open project: %s" % (_project(),))


def OnUpdateMeters():
    _poll("OnUpdateMeters")


def OnIdle():
    _poll("OnIdle")


def OnDeInit():
    _log("MixBuddy bridge unloaded after %d requests" % _S["handled"])


def OnMidiMsg(event):
    # Every message on this port is a doorbell; swallow it so it never plays notes.
    try:
        event.handled = True
    except BaseException:
        pass
    _serve()
