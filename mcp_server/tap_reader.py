"""
Reader for MixBuddy Tap files (written by tap_plugin, see tap_plugin/src/lib.rs).

Each tap instance keeps the last ~10 s of its mixer track in
<temp dir>/mixbuddy/tap_<id>.bin. This module lists the taps and copies the
most recent N seconds out as a float32 array, without disturbing the plugin.
"""
from __future__ import annotations

import glob
import mmap
import os
import struct
import tempfile
import time

import numpy as np

MAGIC = b"MBTAP001"
HEADER = 64
_HDR = struct.Struct("<8sIIIIII QQQQ")  # 64 bytes, see layout in lib.rs
STALE_AFTER_S = 1.5


def tap_dir() -> str:
    return os.environ.get("MIXBUDDY_TAP_DIR") or os.path.join(tempfile.gettempdir(),
                                                               "mixbuddy")


def _header(buf) -> dict | None:
    if len(buf) < HEADER:
        return None
    (magic, version, tap_id, sr, ch, cap, _r, pos, updated, seq, _r2) = _HDR.unpack_from(buf, 0)
    if magic != MAGIC:
        return None
    return {"version": version, "tap_id": tap_id, "sample_rate": sr, "channels": ch,
            "capacity_frames": cap, "write_pos": pos, "updated_ms": updated, "seq": seq}


def list_taps() -> list[dict]:
    """All tap files with their status. `live` means audio arrived recently
    (i.e. FL is playing through that track)."""
    out = []
    now_ms = time.time() * 1000
    for path in sorted(glob.glob(os.path.join(tap_dir(), "tap_*.bin"))):
        try:
            with open(path, "rb") as f:
                h = _header(f.read(HEADER))
        except OSError:
            continue
        if not h:
            continue
        age = (now_ms - h["updated_ms"]) / 1000 if h["updated_ms"] else None
        out.append({
            "tap_id": h["tap_id"],
            "path": path,
            "sample_rate": h["sample_rate"],
            "seconds_buffered": round(min(h["write_pos"], h["capacity_frames"])
                                      / max(1, h["sample_rate"]), 2),
            "seconds_since_audio": None if age is None else round(age, 2),
            "live": age is not None and age < STALE_AFTER_S,
        })
    return out


def read_tap(tap_id: int, seconds: float = 8.0) -> tuple[np.ndarray, int, dict]:
    """Return (audio[frames, 2] float32, sample_rate, header) for the newest
    `seconds` of a tap. Raises ValueError with a user-facing message."""
    path = os.path.join(tap_dir(), f"tap_{int(tap_id)}.bin")
    if not os.path.isfile(path):
        raise ValueError(f"No tap file for Tap ID {tap_id} ({path}). Is MixBuddy Tap "
                         "loaded on that track with this Tap ID?")
    with open(path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            for _attempt in range(5):
                h = _header(mm)
                if not h or h["channels"] != 2:
                    raise ValueError(f"Tap file {path} is not a valid MixBuddy Tap file.")
                cap, sr, pos = h["capacity_frames"], h["sample_rate"], h["write_pos"]
                want = min(int(seconds * sr), cap, pos)
                if want <= 0:
                    raise ValueError(f"Tap {tap_id} has no audio yet. Play the song in FL "
                                     "so audio passes through the tap.")
                start = pos - want
                idx = (np.arange(start, pos) % cap).astype(np.int64)
                data = np.frombuffer(mm, dtype="<f4", count=cap * 2, offset=HEADER)
                audio = data.reshape(cap, 2)[idx].astype(np.float32, copy=True)
                del data  # release the view so the mapping can close
                # If the writer lapped the region we copied, try again.
                pos_after = _header(mm)["write_pos"]
                if pos_after - start <= cap:
                    return audio, sr, h
            raise ValueError("Tap kept overwriting the requested audio; try fewer seconds.")
        finally:
            mm.close()
