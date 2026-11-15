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


# ---------------------------------------------------------------- client

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
        os.replace(tmp, req_path)

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


def compact_params(params: list[dict]) -> list[dict]:
    """Shrink multi-band EQs (FabFilter Pro-Q style) for the LLM:
      * drop every parameter of bands that are switched off ('Band N Used' = 0)
      * on bands whose 'Dynamic Range' is 0 dB, drop the dynamic-EQ and
        side-chain settings, which have no effect
      * drop surround-only 'Speakers' routing
    Plugins without 'Band N' parameters pass through unchanged."""
    unused, static = set(), set()
    for p in params:
        name = p["name"]
        m = re.match(r"^Band (\d+) Used$", name)
        if m and (p.get("value") or 0) < 0.5:
            unused.add(m.group(1))
        m = re.match(r"^Band (\d+) Dynamic Range$", name)
        if m and _ZERO_DB.match((p.get("display") or "").strip()):
            static.add(m.group(1))
    if not unused and not static:
        return params
    out = []
    for p in params:
        m = _BAND.match(p["name"])
        if m:
            band = m.group(1)
            rest = p["name"][m.end():]
            if band in unused:
                continue
            if rest == "Speakers":
                continue
            if band in static and rest.startswith(_DYN_WORDS):
                continue
        out.append(p)
    return out

