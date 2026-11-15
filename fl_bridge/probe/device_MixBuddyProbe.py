# name=MixBuddy Probe
# Throwaway test script for the mix-buddy FL Studio bridge. Safe to delete.
#
# What it checks, and where the answers go (same folder as this file):
#   probe_env.json      Python version, which modules import, whether a local
#                       TCP socket works inside FL, whether file writes work.
#   probe_plugins.json  Every mixer plugin's parameters: name, 0-1 value and
#                       FL's display string (the "real units" question).
#   probe_log.txt       Plain-text log of what happened, including errors.
#
# It only READS from FL. It never changes a mixer or plugin value.

PORT = 9876
HOST = "127.0.0.1"
PARAMS_PER_TICK = 200      # parameters read per OnIdle call, to keep FL responsive
MAX_STORED_PARAMS = 600    # named parameters kept per plugin in the output file
TRIGGER_NAME = "run_dump.txt"

_mods = {}
_import_errors = {}


def _try_import(name):
    try:
        _mods[name] = __import__(name)
        return True
    except BaseException as e:  # FL can raise non-standard errors on blocked modules
        _import_errors[name] = "%s: %s" % (type(e).__name__, e)
        return False


for _n in ("os", "sys", "json", "time", "socket", "_socket", "select", "struct",
           "mmap", "ctypes", "threading", "_thread"):
    _try_import(_n)

for _n in ("mixer", "plugins", "general", "ui"):
    _try_import(_n)

os = _mods.get("os")
sys = _mods.get("sys")
json = _mods.get("json")
time = _mods.get("time")
socket = _mods.get("socket")
mixer = _mods.get("mixer")
plugins = _mods.get("plugins")
general = _mods.get("general")
ui = _mods.get("ui")

_S = {
    "base": None,
    "server": None,
    "socket_error": None,
    "tick": 0,
    "trigger_mtime": None,
    "dump": None,
    "last_dump_summary": None,
}


# ---------------------------------------------------------------- files

def _base_dir():
    if _S["base"]:
        return _S["base"]
    cands = []
    if os:
        try:
            cands.append(os.path.dirname(os.path.abspath(__file__)))
        except BaseException:
            pass
        homes = []
        for var in ("USERPROFILE", "HOME"):
            try:
                v = os.environ.get(var)
                if v:
                    homes.append(v)
            except BaseException:
                pass
        try:
            homes.append(os.path.expanduser("~"))
        except BaseException:
            pass
        for h in homes:
            for docs in (("OneDrive", "Documents"), ("Documents",)):
                try:
                    cands.append(os.path.join(h, *docs) + "\\Image-Line\\FL Studio\\Settings"
                                 "\\Hardware\\MixBuddy Probe")
                except BaseException:
                    pass
        for c in cands:
            try:
                if c and os.path.isdir(c):
                    _S["base"] = c
                    return c
            except BaseException:
                pass
    _S["base"] = cands[0] if cands else "."
    try:
        print("[MixBuddy Probe] no candidate folder exists; tried: %r" % (cands,))
    except BaseException:
        pass
    return _S["base"]


def _path(name):
    if os:
        return os.path.join(_base_dir(), name)
    return name


def _log(msg):
    line = str(msg)
    try:
        if time:
            line = time.strftime("%H:%M:%S ") + line
    except BaseException:
        pass
    try:
        print("[MixBuddy Probe] " + line)
    except BaseException:
        pass
    try:
        with open(_path("probe_log.txt"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except BaseException:
        pass


def _write_json(name, data):
    try:
        text = json.dumps(data, indent=1, ensure_ascii=False, default=str)
        tmp = _path(name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        try:
            os.replace(tmp, _path(name))
        except BaseException:
            with open(_path(name), "w", encoding="utf-8") as f:
                f.write(text)
        return True
    except BaseException as e:
        _log("write %s failed: %s: %s" % (name, type(e).__name__, e))
        return False


def _safe(fn, *args):
    """Call an FL API function; return (value, error_text)."""
    try:
        return fn(*args), None
    except BaseException as e:
        return None, "%s: %s" % (type(e).__name__, e)


# ---------------------------------------------------------------- socket

def _socket_open():
    if not socket:
        _S["socket_error"] = "socket module did not import"
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except BaseException:
            pass
        s.bind((HOST, PORT))
        s.listen(4)
        s.setblocking(False)
        _S["server"] = s
    except BaseException as e:
        _S["socket_error"] = "%s: %s" % (type(e).__name__, e)
        _S["server"] = None


def _socket_selftest():
    """Connect to our own listener from inside FL and pass one message through."""
    srv = _S["server"]
    if not srv:
        return {"ok": False, "error": _S["socket_error"]}
    c = None
    conn = None
    try:
        t0 = time.time()
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.settimeout(1.0)
        c.connect((HOST, PORT))
        for _ in range(50):
            try:
                conn, _addr = srv.accept()
                break
            except BaseException:
                time.sleep(0.01)
        if conn is None:
            return {"ok": False, "error": "listener never accepted the test connection"}
        conn.settimeout(1.0)
        c.sendall(b"hello")
        got = conn.recv(16)
        conn.sendall(b"world")
        back = c.recv(16)
        return {"ok": got == b"hello" and back == b"world",
                "round_trip_ms": round((time.time() - t0) * 1000.0, 2)}
    except BaseException as e:
        return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    finally:
        for x in (conn, c):
            try:
                if x:
                    x.close()
            except BaseException:
                pass


def _socket_poll():
    srv = _S["server"]
    if not srv:
        return
    try:
        conn, _addr = srv.accept()
    except BaseException:
        return  # nothing waiting
    try:
        conn.settimeout(0.25)
        buf = b""
        while b"\n" not in buf and len(buf) < 65536:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
        try:
            req = json.loads(buf.decode("utf-8").strip() or "{}")
        except BaseException:
            req = {"cmd": "bad_json"}
        resp = _handle(req)
        conn.sendall((json.dumps(resp, default=str) + "\n").encode("utf-8"))
    except BaseException as e:
        _log("socket request failed: %s: %s" % (type(e).__name__, e))
    finally:
        try:
            conn.close()
        except BaseException:
            pass


def _handle(req):
    cmd = req.get("cmd")
    if cmd == "ping":
        return {"ok": True, "fl": _fl_info()}
    if cmd == "mixer":
        return {"ok": True, "mixer": _mixer_snapshot()}
    if cmd == "dump":
        return {"ok": True, "started": _dump_start()}
    if cmd == "status":
        d = _S["dump"]
        return {"ok": True, "running": bool(d and d["running"]),
                "plugins_left": len(d["queue"]) if d else 0,
                "last": _S["last_dump_summary"]}
    return {"ok": False, "error": "unknown cmd: %r" % (cmd,)}


# ---------------------------------------------------------------- FL reads

def _fl_info():
    info = {}
    if ui:
        info["fl_version"], err = _safe(ui.getVersion)
        if err:
            info["fl_version_error"] = err
    if general:
        info["api_version"], err = _safe(general.getVersion)
        if err:
            info["api_version_error"] = err
    if mixer:
        info["track_count"], err = _safe(mixer.trackCount)
        if err:
            info["track_count_error"] = err
    return info


def _track_basics(t):
    rec = {"index": t}
    rec["name"], _e = _safe(mixer.getTrackName, t)
    rec["volume_norm"], _e = _safe(mixer.getTrackVolume, t)
    rec["volume_db"], e = _safe(mixer.getTrackVolume, t, 1)
    if e:
        rec["volume_db_error"] = e
    rec["pan"], _e = _safe(mixer.getTrackPan, t)
    rec["peak_max"], _e = _safe(mixer.getTrackPeaks, t, 2)
    return rec


def _mixer_snapshot():
    out = {"tracks": []}
    n, err = _safe(mixer.trackCount)
    if err:
        return {"error": err}
    out["track_count"] = n
    for t in range(n):
        slots = []
        for s in range(10):
            ok, _e = _safe(plugins.isValid, t, s)
            if ok:
                nm, _e = _safe(plugins.getPluginName, t, s)
                slots.append({"slot": s, "name": nm})
        if slots or t == 0:
            rec = _track_basics(t)
            rec["plugins"] = slots
            out["tracks"].append(rec)
    return out


# ---------------------------------------------------------------- plugin dump

def _dump_start():
    d = _S["dump"]
    if d and d["running"]:
        return False
    if not (mixer and plugins):
        _log("dump skipped: mixer/plugins modules missing")
        return False
    n, err = _safe(mixer.trackCount)
    if err:
        _log("dump skipped: trackCount failed: " + err)
        return False
    queue = []
    for t in range(n):
        for s in range(10):
            ok, _e = _safe(plugins.isValid, t, s)
            if ok:
                queue.append((t, s))
    _S["dump"] = {"running": True, "queue": queue, "cur": None, "out": [],
                  "t0": time.time(), "total": len(queue)}
    _log("dump started: %d mixer plugins found" % len(queue))
    return True


def _dump_step():
    d = _S["dump"]
    if not d or not d["running"]:
        return
    cur = d["cur"]
    if cur is None:
        if not d["queue"]:
            _dump_finish()
            return
        t, s = d["queue"].pop(0)
        cur = {"track": t, "slot": s, "next": 0, "t0": time.time(), "params": [],
               "named": 0, "unnamed": 0, "midi_cc": 0, "with_display": 0, "errors": []}
        cur["track_name"], _e = _safe(mixer.getTrackName, t)
        cur["plugin_name"], e = _safe(plugins.getPluginName, t, s)
        if e:
            cur["errors"].append("getPluginName " + e)
        cur["user_name"], _e = _safe(plugins.getPluginName, t, s, 1)
        cnt, e = _safe(plugins.getParamCount, t, s)
        if e:
            cur["errors"].append("getParamCount " + e)
        cur["param_count"] = cnt or 0
        d["cur"] = cur

    t, s = cur["track"], cur["slot"]
    end = min(cur["next"] + PARAMS_PER_TICK, cur["param_count"])
    for p in range(cur["next"], end):
        name, e = _safe(plugins.getParamName, p, t, s)
        if e:
            if len(cur["errors"]) < 5:
                cur["errors"].append("getParamName[%d] %s" % (p, e))
            continue
        if not name:
            cur["unnamed"] += 1
            continue
        if str(name).startswith("MIDI CC"):
            cur["midi_cc"] += 1
            continue
        cur["named"] += 1
        val, e1 = _safe(plugins.getParamValue, p, t, s)
        disp, e2 = _safe(plugins.getParamValueString, p, t, s)
        if disp:
            cur["with_display"] += 1
        if len(cur["params"]) < MAX_STORED_PARAMS:
            rec = {"i": p, "name": name, "value": val, "display": disp}
            if e1:
                rec["value_error"] = e1
            if e2:
                rec["display_error"] = e2
            cur["params"].append(rec)
    cur["next"] = end

    if end >= cur["param_count"]:
        cur["seconds"] = round(time.time() - cur["t0"], 3)
        del cur["next"], cur["t0"]
        d["out"].append(cur)
        d["cur"] = None


def _dump_finish():
    d = _S["dump"]
    d["running"] = False
    plugs = d["out"]
    summary = {
        "plugins": len(plugs),
        "seconds": round(time.time() - d["t0"], 2),
        "per_plugin": [{"track": p["track"], "track_name": p["track_name"], "slot": p["slot"],
                        "plugin": p["plugin_name"], "param_count": p["param_count"],
                        "named": p["named"], "with_display": p["with_display"],
                        "seconds": p["seconds"]} for p in plugs],
    }
    _S["last_dump_summary"] = summary
    _write_json("probe_plugins.json", {"fl": _fl_info(), "summary": summary, "plugins": plugs})
    # Files are blocked inside FL 2025, so also print a compact report.
    print("=== MixBuddy plugin report: %d plugins, %.2fs ===" % (len(plugs), summary["seconds"]))
    for p in plugs:
        print("T%s %s | slot %s | %s | params %s, named %s, with display %s, %.2fs"
              % (p["track"], p["track_name"], p["slot"], p["plugin_name"], p["param_count"],
                 p["named"], p["with_display"], p["seconds"]))
        for q in p["params"][:4]:
            print("    %s = %s -> %r" % (q["name"], round(q["value"] or 0, 3), q["display"]))
    print("=== end of report ===")
    _log("dump finished: %d plugins in %.2fs -> probe_plugins.json"
         % (summary["plugins"], summary["seconds"]))


def _trigger_poll():
    if not os:
        return
    try:
        m = os.path.getmtime(_path(TRIGGER_NAME))
    except BaseException:
        return
    if _S["trigger_mtime"] is None:
        _S["trigger_mtime"] = m
        return
    if m != _S["trigger_mtime"]:
        _S["trigger_mtime"] = m
        _log("trigger file changed -> starting dump")
        _dump_start()


# ---------------------------------------------------------------- FL callbacks

try:
    print("[MixBuddy Probe] module loaded; output folder: %s" % _base_dir())
except BaseException as _e:
    print("[MixBuddy Probe] module loaded; folder lookup failed: %r" % (_e,))


def OnInit():
    _log("---- OnInit ----")
    env = {"imports_ok": sorted(k for k in _mods), "imports_failed": _import_errors}
    if sys:
        env["python"] = sys.version
        env["platform"] = sys.platform
    env["script_dir"] = _base_dir()
    env["fl"] = _fl_info()

    _socket_open()
    env["socket_listen"] = {"ok": _S["server"] is not None, "host": HOST, "port": PORT,
                            "error": _S["socket_error"]}
    env["socket_selftest"] = _socket_selftest()
    env["file_write_ok"] = _write_json("probe_env.json", env)
    _log("python: %s" % env.get("python"))
    _log("socket listen: %s" % env["socket_listen"])
    _log("socket selftest: %s" % env["socket_selftest"])
    _log("imports failed: %s" % (_import_errors or "none"))

    # Remember the trigger file's current state so an old one doesn't fire a dump.
    try:
        _S["trigger_mtime"] = os.path.getmtime(_path(TRIGGER_NAME))
    except BaseException:
        _S["trigger_mtime"] = 0


def OnDeInit():
    try:
        if _S["server"]:
            _S["server"].close()
    except BaseException:
        pass
    _S["server"] = None
    _log("---- OnDeInit ----")


def report():
    """Run the whole plugin report right now. Type report() in Script output."""
    if not _dump_start():
        d = _S["dump"]
        if not (d and d["running"]):
            print("report(): could not start (see messages above)")
            return
    guard = 0
    while _S["dump"]["running"] and guard < 100000:
        _dump_step()
        guard += 1


def OnIdle():
    _S["tick"] += 1
    if _S["tick"] == 1:
        print("[MixBuddy Probe] OnIdle is running")
    if _S["tick"] == 10:
        _dump_start()  # run the plugin report once, shortly after load
    _socket_poll()
    _dump_step()
    if _S["tick"] % 25 == 0:
        _trigger_poll()
