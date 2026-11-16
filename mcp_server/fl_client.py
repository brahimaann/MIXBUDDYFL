"""
Client side of the MixBuddy FL Studio bridge.

FL Studio 2025's controller-script sandbox blocks sockets but allows file I/O,
so requests travel through two JSON files in the controller script's folder:

    1. write mb_request.json  {"id", "cmd", "args"}
    2. send a MIDI "doorbell" (CC 119 on channel 16) to the loopMIDI port
       that FL has assigned to the MixBuddy controller script
    3. poll mb_response.json until its "id" matches

The doorbell uses Windows' built-in winmm.dll through ctypes, so there is
nothing to pip install. Tests can inject their own doorbell function.

Config (environment variables, all optional):
    MIXBUDDY_FL_DIR    folder containing device_MixBuddy.py
    MIXBUDDY_MIDI_PORT loopMIDI output port name (default "MixBuddy")
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid

REQUEST = "mb_request.json"
RESPONSE = "mb_response.json"
DEFAULT_PORT = "MixBuddy"


class FLBridgeError(RuntimeError):
    """Raised with a message written for the user (what to check next)."""


# ---------------------------------------------------------------- locating FL

def find_script_dir() -> str:
    env = os.environ.get("MIXBUDDY_FL_DIR")
    if env:
        return env
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    cands = [
        os.path.join(home, "OneDrive", "Documents", "Image-Line", "FL Studio",
                     "Settings", "Hardware", "MixBuddy"),
        os.path.join(home, "Documents", "Image-Line", "FL Studio",
                     "Settings", "Hardware", "MixBuddy"),
    ]
    for c in cands:
        if os.path.isfile(os.path.join(c, "device_MixBuddy.py")):
            return c
    raise FLBridgeError(
        "Could not find the MixBuddy controller script. Expected device_MixBuddy.py in "
        "one of: " + "; ".join(cands) + ". Set MIXBUDDY_FL_DIR if FL's user data "
        "folder is somewhere else.")


# ---------------------------------------------------------------- MIDI doorbell

class WinMidiDoorbell:
    """Sends one MIDI CC to a named output port via winmm.dll."""

    STATUS = 0xBF  # control change, channel 16
    CC = 119

    def __init__(self, port_name: str = DEFAULT_PORT):
        if sys.platform != "win32":
            raise FLBridgeError("The MIDI doorbell needs Windows (winmm.dll).")
        import ctypes
        from ctypes import wintypes

        class MIDIOUTCAPSW(ctypes.Structure):
            _fields_ = [("wMid", wintypes.WORD), ("wPid", wintypes.WORD),
                        ("vDriverVersion", wintypes.UINT),
                        ("szPname", wintypes.WCHAR * 32),
                        ("wTechnology", wintypes.WORD), ("wVoices", wintypes.WORD),
                        ("wNotes", wintypes.WORD), ("wChannelMask", wintypes.WORD),
                        ("dwSupport", wintypes.DWORD)]

        self._ct = ctypes
        w = ctypes.WinDLL("winmm")
        w.midiOutGetNumDevs.restype = wintypes.UINT
        w.midiOutGetDevCapsW.argtypes = [ctypes.c_size_t, ctypes.POINTER(MIDIOUTCAPSW),
                                         wintypes.UINT]
        w.midiOutGetDevCapsW.restype = wintypes.UINT
        w.midiOutOpen.argtypes = [ctypes.POINTER(ctypes.c_void_p), wintypes.UINT,
                                  ctypes.c_size_t, ctypes.c_size_t, wintypes.DWORD]
        w.midiOutOpen.restype = wintypes.UINT
        w.midiOutShortMsg.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        w.midiOutShortMsg.restype = wintypes.UINT
        w.midiOutClose.argtypes = [ctypes.c_void_p]
        w.midiOutClose.restype = wintypes.UINT
        self._w = w

        names = []
        dev_id = None
        for i in range(w.midiOutGetNumDevs()):
            caps = MIDIOUTCAPSW()
            if w.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
                names.append(caps.szPname)
                if dev_id is None and caps.szPname.strip().lower() == port_name.lower():
                    dev_id = i
        if dev_id is None:
            for i, n in enumerate(names):  # loose match, e.g. "MixBuddy 1"
                if port_name.lower() in n.lower():
                    dev_id = i
                    break
        if dev_id is None:
            raise FLBridgeError(
                "MIDI port %r not found. Is loopMIDI running with that port? "
                "Ports seen: %s" % (port_name, names or "none"))
        self.port = names[dev_id]
        handle = ctypes.c_void_p()
        rc = w.midiOutOpen(ctypes.byref(handle), dev_id, 0, 0, 0)
        if rc != 0:
            raise FLBridgeError("Could not open MIDI port %r (winmm error %d)."
                                % (self.port, rc))
        self._h = handle
        self._n = 0

    def __call__(self):
        self._n = (self._n + 1) % 128
        msg = self.STATUS | (self.CC << 8) | (self._n << 16)
        rc = self._w.midiOutShortMsg(self._h, msg)
        if rc != 0:
            raise FLBridgeError("MIDI send failed (winmm error %d)." % rc)

    def close(self):
        try:
            self._w.midiOutClose(self._h)
        except Exception:
            pass


# ---------------------------------------------------------------- project name

def fl_window_titles() -> list[str]:
    """Titles of visible top-level windows that belong to FL Studio. FL's
    script API does not expose the project file name, but FL's main window
    title does. Windows only; returns [] elsewhere or on any failure."""
    if sys.platform != "win32":
        return []
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        titles = []
        EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def exe_of(hwnd):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            h = kernel32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
            if not h:
                return ""
            try:
                buf = ctypes.create_unicode_buffer(512)
                n = psapi.GetProcessImageFileNameW(h, buf, 512)
                return buf.value[:n].lower() if n else ""
            finally:
                kernel32.CloseHandle(h)

        def cb(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            exe = exe_of(hwnd)
            if "fl64" in exe or "fl.exe" in exe or "fl studio" in buf.value.lower():
                titles.append(buf.value)
            return True

        user32.EnumWindows(EnumProc(cb), 0)
        return titles
    except Exception:
        return []


def project_from_titles(titles: list[str]) -> str | None:
    """Pull the project name out of FL window titles such as
    'KEEP GOING 2.flp - FL Studio 2025' or 'FL Studio 2025 - KEEP GOING 2'."""
    for t in titles:
        m = re.search(r"([^\\/]+?\.flp)", t, re.I)
        if m:
            return m.group(1).strip()
    for t in titles:
        parts = [x.strip() for x in re.split(r"\s+[-\u2013\u2014]\s+", t) if x.strip()]
        rest = [x for x in parts if not re.match(r"(?i)^fl studio", x)]
        if rest and len(parts) > 1:
            return rest[0]
    return None


# ---------------------------------------------------------------- client

def _replace_with_retry(src: str, dst: str, tries: int = 100, wait: float = 0.01):
    """os.replace, retried while FL briefly has dst open. On Windows a file
    another process is reading can't be replaced (PermissionError 13); FL
    holds the request file for a few ms while it reads it."""
    for i in range(tries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == tries - 1:
                raise FLBridgeError("FL kept the request file locked for over a second "
                                    "(%s). Try again." % dst)
            time.sleep(wait)


class FLClient:
    def __init__(self, script_dir: str | None = None, doorbell=None,
                 timeout: float = 8.0, poll: float = 0.01):
        self.script_dir = script_dir
        self._doorbell = doorbell
        self.timeout = timeout
        self.poll = poll

    def _dir(self) -> str:
        if not self.script_dir:
            self.script_dir = find_script_dir()
        return self.script_dir

    def _ring(self):
        if self._doorbell is None:
            self._doorbell = WinMidiDoorbell(os.environ.get("MIXBUDDY_MIDI_PORT",
                                                            DEFAULT_PORT))
        self._doorbell()

    def call(self, cmd: str, args: dict | None = None, timeout: float | None = None):
        d = self._dir()
        rid = uuid.uuid4().hex[:12]
        req_path = os.path.join(d, REQUEST)
        resp_path = os.path.join(d, RESPONSE)
        tmp = req_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"id": rid, "cmd": cmd, "args": args or {}}, f)
        _replace_with_retry(tmp, req_path)

        t0 = time.perf_counter()
        self._ring()
        deadline = t0 + (timeout or self.timeout)
        rang_again = False
        while time.perf_counter() < deadline:
            time.sleep(self.poll)
            try:
                with open(resp_path, "r", encoding="utf-8") as f:
                    resp = json.loads(f.read())
            except (OSError, ValueError):
                continue  # not there yet, or FL is mid-write
            if resp.get("id") != rid:
                # A dropped doorbell is possible; ring once more after 1 s.
                if not rang_again and time.perf_counter() - t0 > 1.0:
                    self._ring()
                    rang_again = True
                continue
            resp["round_trip_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            if not resp.get("ok"):
                raise FLBridgeError("FL reported an error: %s" % resp.get("error"))
            return resp
        raise FLBridgeError(
            "FL Studio did not answer within %.0f s. Check that FL is open, loopMIDI "
            "is running, and the MIDI input is enabled with controller type "
            "'MixBuddy'." % (timeout or self.timeout))


# ---------------------------------------------------------------- shaping

_BAND = re.compile(r"^Band (\d+) ")
_DYN_WORDS = ("Dynamic", "Dynamics", "Threshold", "Attack", "Release", "Side Chain",
              "Spectral", "External Side Chain")
_ZERO_DB = re.compile(r"^[+-]?0(\.0+)?\s*dB$")
_USED = re.compile(r"^(.+?) (\d+) Used$")
_NUM_ACTIVE = re.compile(r"^Num Active (.+?)s$")
_STEP = re.compile(r"^XLFO \d+ Step \d+ ")
_ENABLED = re.compile(r"^([A-Za-z][A-Za-z /-]*?) Enabled$")


def _num(display):
    m = re.match(r"^\s*(\d+)", display or "")
    return int(m.group(1)) if m else None


def compact_params(params: list[dict]) -> list[dict]:
    """Shrink big plugins for the LLM without hiding anything that is active.

    Rules (each only fires when the plugin exposes the matching parameter, so
    plugins without them pass through unchanged):
      * "<X> N Used" = 0       -> drop every "<X> N ..." parameter
                                  (Pro-Q bands, Timeless taps/filters,
                                  Pro-C side-chain EQ bands)
      * "Num Active <X>s" = k  -> drop "<X> N ..." for N > k
                                  (Saturn bands, XLFOs, EGs, XY controllers)
      * XLFO step-sequencer values are always dropped
      * "<Module> Enabled" = Off (module name without a number) -> drop that
        module's settings (Timeless Lo-Fi, Diffuse, Pitch Shift...)
      * "<X> Feedback Amount" = 0 -> drop its Feedback Frequency (Saturn)
      * Pro-Q bands with 0 dB "Dynamic Range" -> drop dynamic/side-chain settings
      * surround-only "Band N Speakers"
    """
    by_name = {p["name"]: p for p in params}
    unused, static = set(), set()          # (prefix, n) / band numbers
    limits = {}                            # prefix -> max active index
    off_modules = []
    no_feedback = set()
    for p in params:
        name = p["name"]
        disp = (p.get("display") or "").strip()
        m = _USED.match(name)
        if m and (p.get("value") or 0) < 0.5:
            unused.add((m.group(1), m.group(2)))
        m = _NUM_ACTIVE.match(name)
        if m and _num(disp) is not None:
            limits[m.group(1)] = _num(disp)
        m = re.match(r"^Band (\d+) Dynamic Range$", name)
        if m and _ZERO_DB.match(disp):
            static.add(m.group(1))
        m = _ENABLED.match(name)
        if m and disp.lower() == "off" and not re.search(r"\d", m.group(1)):
            mod = m.group(1)
            if mod in by_name or any(n.startswith(mod + " ") and n != name for n in by_name):
                off_modules.append(mod)
        if name.endswith(" Feedback Amount") and _num(disp) == 0:
            no_feedback.add(name[: -len(" Amount")] + " Frequency")

    out = []
    for p in params:
        name = p["name"]
        if _STEP.match(name):
            continue
        if name in no_feedback:
            continue
        skip = False
        for prefix, n in unused:
            if name.startswith(f"{prefix} {n} "):
                skip = True
                break
        if not skip:
            for prefix, k in limits.items():
                m = re.search(rf"(?:^|[ /]){re.escape(prefix)} (\d+)(?: |/|$)", name)
                if m and int(m.group(1)) > k:
                    skip = True
                    break
        if not skip:
            for mod in off_modules:
                if name == mod or (name.startswith(mod + " ") and name != mod + " Enabled"):
                    skip = True
                    break
        if not skip:
            m = _BAND.match(name)
            if m:
                rest = name[m.end():]
                if rest == "Speakers":
                    skip = True
                elif m.group(1) in static and rest.startswith(_DYN_WORDS):
                    skip = True
        if not skip:
            out.append(p)
    return out
