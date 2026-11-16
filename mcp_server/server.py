"""
Audio Mixing Analyzer - MCP Server

Exposes real DSP audio-analysis tools to an LLM via the Model Context Protocol.
All heavy DSP lives in dsp.py and project state in memory.py (both unit-tested
separately); this layer handles tool registration, input validation, response
shaping (progressive disclosure) and JSON serialization.

Design notes (patterns borrowed from Producer Pal, see docs/):
  * Every analysis tool returns a compact OVERVIEW by default plus a one-line
    human-readable `summary`. Pass `include` (comma-separated) to add detail
    blocks. This keeps token usage low until the LLM actually needs the arrays.
  * Project memory uses read-then-replace semantics.

Run:  python mcp_server/server.py
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

import numpy as np

from mcp.server.fastmcp import FastMCP

# Allow running both as a module and as a script.
sys.path.insert(0, os.path.dirname(__file__))
import dsp  # noqa: E402
import memory  # noqa: E402
import fl_client  # noqa: E402
import plugin_notes  # noqa: E402
import tap_reader  # noqa: E402
import archive  # noqa: E402

mcp = FastMCP("audio-mixing-analyzer")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_include(include: str) -> set[str]:
    """Parse a comma-separated `include` string into a lowercase set."""
    if not include:
        return set()
    return {part.strip().lower() for part in include.split(",") if part.strip()}


def _load(file_path: str):
    """Load audio, returning (audio, None) or (None, error_dict)."""
    try:
        return dsp.load_audio(file_path), None
    except (FileNotFoundError, RuntimeError) as exc:
        return None, {"error": str(exc)}


# ---------------------------------------------------------------------------
# Analysis tools
# ---------------------------------------------------------------------------
@mcp.tool()
def analyze_loudness(file_path: str, include: str = "") -> dict:
    """
    Measure EBU R128 / ITU-R BS.1770 integrated loudness (LUFS) of an audio file.

    Use this to check whether a track is too quiet or too loud for streaming
    (Spotify/Apple target around -14 LUFS; club/loud masters can be higher).

    Args:
        file_path: Absolute path to a WAV/AIFF/FLAC/OGG audio file.
        include: Optional detail blocks (comma-separated). Valid: "format"
            (sample_rate, channels).

    Also returns true peak (dBTP, 4x oversampled) and PLR (peak-to-loudness
    ratio), which says how much of the loudness came from compression: chart
    pop sits near 9.3 LU, 1990s productions near 12.6 LU.

    Returns (overview): summary, integrated_loudness_lufs, true_peak_dbtp,
        plr_lu, duration_seconds.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    lufs = dsp.integrated_loudness_lufs(audio.samples, audio.sample_rate)

    # Human-readable verdict against the common streaming target.
    diff = lufs - (-14.0)
    if lufs <= -70.0:
        verdict = "effectively silent"
    elif diff < -2.0:
        verdict = f"quiet for streaming ({abs(diff):.1f} LU below -14 LUFS)"
    elif diff > 2.0:
        verdict = f"hot ({diff:.1f} LU above -14 LUFS)"
    else:
        verdict = "in the typical streaming range (~-14 LUFS)"

    # PLR contextualises the loudness: how much of it came from compression.
    tp = dsp.true_peak_dbfs(audio.samples, audio.sample_rate)
    plr = tp - lufs
    if plr < 8.0:
        density = "very dense/limited"
    elif plr < 11.0:
        density = "typical of modern commercial masters"
    else:
        density = "dynamically open"

    out = {
        "summary": (
            f"Integrated loudness {lufs:.1f} LUFS - {verdict}. "
            f"PLR {plr:.1f} LU ({density})."
        ),
        "integrated_loudness_lufs": round(lufs, 2),
        "true_peak_dbtp": round(tp, 2),
        "plr_lu": round(plr, 2),
        "duration_seconds": round(audio.duration_seconds, 2),
    }
    if "format" in inc:
        out["sample_rate"] = audio.sample_rate
        out["channels"] = audio.n_channels
    return out


@mcp.tool()
def analyze_dynamics(file_path: str, include: str = "") -> dict:
    """
    Measure peak/RMS levels, crest factor and dynamic range, then suggest
    compression settings (ratio, attack, release).

    Use this when the user asks about compression, dynamics, "punch", or a
    vocal/instrument that sounds uneven or uncontrolled.

    Args:
        file_path: Absolute path to the target audio file.
        include: Optional detail blocks (comma-separated). Valid: "levels"
            (peak_level_dbfs, rms_level_dbfs, dynamic_range_db).

    Returns (overview): summary, crest_factor_db, compression_suggestion.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    m = dsp.analyze_dynamics_metrics(audio.mono, audio.sample_rate)
    if "error" in m:
        return m

    cs = m["compression_suggestion"]
    if cs["requires_control"]:
        verdict = (
            f"dynamics are uneven (crest {m['crest_factor_db']:.0f} dB) - "
            f"compress ~{cs['suggested_ratio']}."
        )
    else:
        verdict = (
            f"already fairly controlled (crest {m['crest_factor_db']:.0f} dB) - "
            f"light {cs['suggested_ratio']} optional."
        )

    out = {
        "summary": f"Dynamics: {verdict}",
        "crest_factor_db": m["crest_factor_db"],
        "compression_suggestion": cs,
    }
    if "levels" in inc:
        out["peak_level_dbfs"] = m["peak_level_dbfs"]
        out["rms_level_dbfs"] = m["rms_level_dbfs"]
        out["dynamic_range_db"] = m["dynamic_range_db"]
    return out


@mcp.tool()
def analyze_frequency_spectrum(
    file_path: str, deviation_factor: float = 2.0, include: str = ""
) -> dict:
    """
    Compute multi-band spectral energy and detect harsh resonant peaks using a
    dynamic standard-deviation threshold curve. Resonances are classified
    (mud, boxiness, sibilance, etc.) with suggested attenuation.

    Use this for general tonal-balance questions and to find problem frequencies.

    Args:
        file_path: Absolute path to the target audio file.
        deviation_factor: Sensitivity of resonance detection (1.0-2.5;
            higher = fewer, only the most extreme peaks).
        include: Optional detail blocks (comma-separated). Valid: "bands"
            (full per-band energy table), "resonances" (full list, up to 10).

    Also returns the harmonic centroid (spectral centroid divided by the
    fundamental), which expresses brightness in harmonics and so is comparable
    across sources of different pitch; it is null for unpitched material.

    Returns (overview): summary, spectral_centroid_hz, harmonic_centroid,
        fundamental_hz, peaks_detected_count, top_resonances (the 3 worst).
        Use include for the full tables.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    bands = dsp.multiband_energy(audio.mono, audio.sample_rate)
    res = dsp.detect_resonances_metrics(
        audio.mono, audio.sample_rate, local_deviation_factor=deviation_factor
    )
    if "error" in res:
        return res

    centroid = bands.get("spectral_centroid_hz")
    resonances = res["resonances"]
    top = resonances[:3]

    if top:
        worst = top[0]
        verdict = (
            f"{res['peaks_detected_count']} resonance(s); worst at "
            f"{worst['frequency_hz']:.0f} Hz ({worst['classification']}), "
            f"cut ~{worst['suggested_attenuation_db']:.1f} dB."
        )
    else:
        verdict = "no harsh resonances detected; tonal balance looks even."

    out = {
        "summary": f"Spectrum: {verdict}",
        "spectral_centroid_hz": centroid,
        "harmonic_centroid": bands.get("harmonic_centroid"),
        "fundamental_hz": bands.get("fundamental_hz"),
        "peaks_detected_count": res["peaks_detected_count"],
        "top_resonances": top,
    }
    if "bands" in inc:
        out["frequency_bands"] = bands
    if "resonances" in inc:
        out["resonances"] = resonances
    return out


@mcp.tool()
def analyze_vocal_clarity(file_path: str, include: str = "") -> dict:
    """
    Diagnose vocal balance: mud (200-500 Hz), presence (2-5 kHz) and sibilance
    (5-9 kHz). Returns clarity/mud/sibilance indices and concrete EQ moves.

    Use this when the user asks "how do I make my vocal clearer / cut through /
    less muddy / less harsh".

    Args:
        file_path: Absolute path to the vocal audio file (mono recommended).
        include: Optional detail blocks (comma-separated). Valid: "raw"
            (fundamental_warmth_db).

    Returns (overview): summary, clarity_score, mud_index, sibilance_index,
        eq_suggestions.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    m = dsp.analyze_vocal_clarity_metrics(audio.mono, audio.sample_rate)
    if "error" in m:
        return m

    issues = []
    if m["mud_index"] > 5.0:
        issues.append("muddy")
    if m["sibilance_index"] > 6.0:
        issues.append("sibilant/harsh")
    if m["clarity_score"] < 0.6:
        issues.append("lacking presence")
    verdict = ", ".join(issues) if issues else "balanced"

    out = {
        "summary": (
            f"Vocal is {verdict} (clarity {m['clarity_score']}, "
            f"mud {m['mud_index']}/10, sibilance {m['sibilance_index']}/10)."
        ),
        "clarity_score": m["clarity_score"],
        "mud_index": m["mud_index"],
        "sibilance_index": m["sibilance_index"],
        "eq_suggestions": m["eq_suggestions"],
    }
    if "raw" in inc:
        out["fundamental_warmth_db"] = m["fundamental_warmth_db"]
    return out


@mcp.tool()
def analyze_stereo_compatibility(file_path: str, include: str = "") -> dict:
    """
    Evaluate stereo correlation, interchannel delay and mono compatibility.
    Flags phase cancellation risk (especially in the sub-bass).

    Use this for width, phase, "disappears in mono", or panning issues.

    Args:
        file_path: Absolute path to a stereo audio file.
        include: Optional detail blocks (comma-separated). Valid: "detail"
            (interchannel_time_delay_ms, sub_150hz_phase_correlation,
            sub_bass_cancellation_risk).

    Returns (overview): summary, overall_correlation, phase_alignment_status,
        requires_corrective_intervention.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    m = dsp.analyze_stereo_metrics(audio)

    if m.get("status") == "monophonic":
        out = {
            "summary": "File is mono; 100% mono-compatible.",
            "overall_correlation": m["correlation_coefficient"],
            "phase_alignment_status": m["phase_alignment_status"],
            "requires_corrective_intervention": False,
        }
        return out

    if m["requires_corrective_intervention"]:
        verdict = f"phase problem ({m['phase_alignment_status']}) - fix before mono playback."
    else:
        verdict = f"{m['phase_alignment_status']}; mono-safe."

    out = {
        "summary": f"Stereo: correlation {m['overall_correlation']}, {verdict}",
        "overall_correlation": m["overall_correlation"],
        "phase_alignment_status": m["phase_alignment_status"],
        "requires_corrective_intervention": m["requires_corrective_intervention"],
    }
    if "detail" in inc:
        out["interchannel_time_delay_ms"] = m["interchannel_time_delay_ms"]
        out["sub_150hz_phase_correlation"] = m["sub_150hz_phase_correlation"]
        out["sub_bass_cancellation_risk"] = m["sub_bass_cancellation_risk"]
    return out


@mcp.tool()
def analyze_noise_gate(file_path: str, include: str = "") -> dict:
    """
    Find pauses between phrases and measure what's left in them: the true
    noise floor, the level during gaps, and whether breath/room noise/hiss is
    bleeding through (gap level sits well above the floor but well below the
    phrase level). Returns concrete gate/expander settings (threshold, ratio,
    range, attack, hold, release, and a sidechain high-pass suggestion when
    bleed is detected).

    Use this when the user asks about noise gates, expanders, breath noise
    between phrases/words, or "my gate isn't closing enough."

    Args:
        file_path: Absolute path to the target audio file (vocal or any
            source with clear pauses between phrases).
        include: Optional detail blocks (comma-separated). Valid: "levels"
            (active_level_dbfs, noise_floor_dbfs, gap_level_dbfs).

    Returns (overview): summary, gaps_detected_count, breath_bleed_detected,
        gate_suggestion.
    """
    audio, err = _load(file_path)
    if err:
        return err

    inc = _parse_include(include)
    m = dsp.analyze_gate_settings_metrics(audio.mono, audio.sample_rate)
    if "error" in m:
        return m

    if m["gaps_detected_count"] == 0:
        out = {
            "summary": "No clear pauses between phrases found - nothing to gate.",
            "gaps_detected_count": 0,
            "breath_bleed_detected": False,
            "gate_suggestion": None,
        }
        return out

    if m["breath_bleed_detected"]:
        verdict = (
            f"breath/noise is bleeding through {m['gaps_detected_count']} gap(s) "
            f"({m['breath_bleed_db']:.1f} dB above the noise floor) - "
            f"tighten with {m['gate_suggestion']['ratio']} ratio and a "
            f"{m['gate_suggestion']['sidechain_highpass_hz']:.0f} Hz sidechain high-pass."
        )
    else:
        verdict = f"{m['gaps_detected_count']} gap(s) close cleanly - no bleed detected."

    out = {
        "summary": f"Gate: {verdict}",
        "gaps_detected_count": m["gaps_detected_count"],
        "breath_bleed_detected": m["breath_bleed_detected"],
        "median_gap_duration_ms": m["median_gap_duration_ms"],
        "gate_suggestion": m["gate_suggestion"],
    }
    if "levels" in inc:
        out["active_level_dbfs"] = m["active_level_dbfs"]
        out["noise_floor_dbfs"] = m["noise_floor_dbfs"]
        out["gap_level_dbfs"] = m["gap_level_dbfs"]
    return out


@mcp.tool()
def compare_to_reference(
    target_path: str, reference_path: str, include: str = ""
) -> dict:
    """
    Compare a target mix against a professional reference: loudness differential
    and band-by-band spectral balance, with directional recommendations.

    Use this when the user wants their track to sound like a reference song.

    Args:
        target_path: Path to the user's (unfinished) mix.
        reference_path: Path to the professional reference track.
        include: Optional detail blocks (comma-separated). Valid: "all_bands"
            (include bands that already match, not just the off ones).

    Returns (overview): summary, loudness_differential_lu, target/reference LUFS,
        and spectral_difference for bands that are off by >1.5 dB.
    """
    target, err = _load(target_path)
    if err:
        return err
    reference, err = _load(reference_path)
    if err:
        return err

    inc = _parse_include(include)

    t_lufs = dsp.integrated_loudness_lufs(target.samples, target.sample_rate)
    r_lufs = dsp.integrated_loudness_lufs(reference.samples, reference.sample_rate)

    t_bands = dsp.multiband_energy(target.mono, target.sample_rate)
    r_bands = dsp.multiband_energy(reference.mono, reference.sample_rate)

    show_all = "all_bands" in inc
    spectral_diff = []
    off_bands = []
    for name in ("sub_bass", "low_bass", "low_mids", "mid_range", "high_mids", "highs"):
        if name in t_bands and name in r_bands:
            diff = t_bands[name]["energy_db"] - r_bands[name]["energy_db"]
            if diff > 1.5:
                rec = f"Cut {name} (~{diff:.1f} dB hotter than reference)."
                off_bands.append(name)
            elif diff < -1.5:
                rec = f"Boost {name} (~{abs(diff):.1f} dB below reference)."
                off_bands.append(name)
            else:
                rec = f"{name} matches reference."
            if show_all or abs(diff) > 1.5:
                spectral_diff.append(
                    {
                        "band": name,
                        "range_hz": t_bands[name]["range_hz"],
                        "difference_db": round(diff, 1),
                        "recommendation": rec,
                    }
                )

    lu = t_lufs - r_lufs
    loud_txt = (
        f"{abs(lu):.1f} LU {'louder' if lu > 0 else 'quieter'} than reference"
        if abs(lu) > 1.0
        else "loudness matches reference"
    )
    band_txt = (
        f"off bands: {', '.join(off_bands)}" if off_bands else "spectral balance matches"
    )

    return {
        "summary": f"Vs reference: {loud_txt}; {band_txt}.",
        "loudness_differential_lu": round(lu, 2),
        "target_loudness_lufs": round(t_lufs, 2),
        "reference_loudness_lufs": round(r_lufs, 2),
        "spectral_difference": spectral_diff,
    }


# ---------------------------------------------------------------------------
# FL Studio live tools (read-only bridge, see fl_bridge/README.md)
# ---------------------------------------------------------------------------
_fl = None


def _safe(fn, *a, **kw):
    """Run an archive call; the archive must never break a tool."""
    try:
        return fn(*a, **kw)
    except Exception:  # noqa: BLE001
        return None


def _changes_text(evs):
    return [e["summary"] for e in (evs or [])]


def _fl_call(cmd: str, args: dict | None = None):
    """Call the FL bridge, returning (result, None) or (None, error_dict)."""
    global _fl
    if _fl is None:
        _fl = fl_client.FLClient()
    try:
        resp = _fl.call(cmd, args)
        result = resp["result"]
        if isinstance(result, dict):
            name = (fl_client.project_from_titles(fl_client.fl_window_titles())
                    or resp.get("project"))
            if name and "fl studio" not in str(name).lower():
                result["project"] = name
            else:
                result.pop("project", None)
        return result, None
    except fl_client.FLBridgeError as exc:
        return None, {"error": str(exc)}
    except OSError as exc:
        return None, {"error": f"FL bridge file error: {exc}"}


def _peak_db(p):
    if p is None or p <= 0:
        return None
    import math
    return round(20 * math.log10(p), 1)


@mcp.tool()
def fl_status() -> dict:
    """
    Check the live connection to FL Studio and report its version.

    Call this first if any other fl_* tool errors. Requires FL Studio open,
    loopMIDI running with a "MixBuddy" port, and that port enabled in FL's MIDI
    settings with controller type "MixBuddy".

    Returns: summary, fl_version, api_version, track_count, bridge_version,
        round_trip_ms.
    """
    global _fl
    if _fl is None:
        _fl = fl_client.FLClient()
    try:
        resp = _fl.call("ping")
    except (fl_client.FLBridgeError, OSError) as exc:
        return {"connected": False, "error": str(exc)}
    r = resp["result"]
    return {
        "connected": True,
        "summary": f"Connected to FL Studio {r.get('fl_version')}, project "
                   f"'{(fl_client.project_from_titles(fl_client.fl_window_titles()) or resp.get('project') or 'unknown')}' "
                   f"({r.get('track_count')} mixer tracks, "
                   f"{resp['round_trip_ms']} ms round trip).",
        **r,
        "round_trip_ms": resp["round_trip_ms"],
    }


@mcp.tool()
def fl_get_mixer(include: str = "") -> dict:
    """
    Read the live FL Studio mixer: every track in use, its fader (dB), pan,
    mute/solo, the plugins in its insert slots, and where it routes.

    Start here to understand a mix before diagnosing anything. Use the track
    `index` values with fl_get_track_chain / fl_get_plugin_params.

    Args:
        include: Optional detail (comma-separated). Valid: "levels" (current
            peak meter, stereo separation, raw fader value), "empty" (also list
            unused insert tracks).

    Notes: the peak meter is a momentary post-fader reading, so it is only
    meaningful while the song is playing. Insert slots sit before the fader.

    Returns (overview): summary, tracks[{index, name, volume_db, pan, muted,
        solo, plugins[{slot, plugin}], routes_to[{to, to_name, level_norm}]}].
    """
    inc = _parse_include(include)
    r, err = _fl_call("mixer", {"include_empty": "empty" in inc})
    if err:
        return err
    names = {t["index"]: t["name"] for t in r["tracks"]}
    tracks = []
    n_plugins = 0
    for t in r["tracks"]:
        plugs = [{"slot": p["slot"], "plugin": p["plugin"],
                  **({"name": p["user_name"]} if p.get("user_name")
                     and p["user_name"] != p["plugin"] else {})}
                 for p in t["plugins"]]
        n_plugins += len(plugs)
        rec = {
            "index": t["index"], "name": t["name"], "volume_db": t["volume_db"],
            "pan": round(t["pan"], 2) if t.get("pan") is not None else None,
            "muted": bool(t.get("muted")), "solo": bool(t.get("solo")),
            "plugins": plugs,
            "routes_to": [{"to": x["to"], "to_name": names.get(x["to"]),
                           "level_norm": round(x["level_norm"], 3)
                           if x.get("level_norm") is not None else None}
                          for x in t.get("routes_to", [])],
        }
        if not t.get("fx_enabled", True):
            rec["fx_bypassed"] = True
        if "levels" in inc:
            rec["peak_dbfs"] = _peak_db(t.get("peak"))
            rec["stereo_sep"] = t.get("stereo_sep")
            rec["volume_norm"] = t.get("volume_norm")
        tracks.append(rec)
    muted = [t["name"] for t in tracks if t["muted"]]
    summary = (f"Project '{r.get('project') or 'unknown'}': "
               f"{len(tracks)} tracks in use, {n_plugins} plugins loaded"
               + (f"; muted: {', '.join(muted)}" if muted else "") + ".")
    out = {"summary": summary, "project": r.get("project"), "tracks": tracks,
           "fl_timing": r.get("timing")}
    changed = _changes_text(_safe(archive.observe_mixer, r.get("project"), r["tracks"]))
    if changed:
        out["changed_since_last_read"] = changed
    return out


@mcp.tool()
def fl_get_track_chain(track: int) -> dict:
    """
    List the insert chain on one FL Studio mixer track, in signal order
    (slot 0 is first), with each plugin's parameter count.

    Args:
        track: Mixer track index from fl_get_mixer (0 is Master).

    Returns: summary, index, name, volume_db, pan, slots[{slot, plugin,
        param_count}].
    """
    r, err = _fl_call("track", {"track": int(track)})
    if err:
        return err
    chain = " -> ".join(s["plugin"] for s in r["slots"]) or "no plugins"
    r["summary"] = (f"Project '{r.get('project') or 'unknown'}', track {r['index']} "
                    f"'{r['name']}': {chain}.")
    return r


@mcp.tool()
def fl_get_plugin_params(track: int, slot: int, filter: str = "",
                         include: str = "", limit: int = 150) -> dict:
    """
    Read one plugin's settings in real units, exactly as the plugin displays
    them (e.g. "98.25 Hz", "-20.4 dB", "4.84 ms", "Opto").

    Works for FL native and third-party plugins (FabFilter, Waves, UAD,
    Soundtoys...). EQ bands that are switched off are hidden by default.

    Args:
        track: Mixer track index.
        slot: Insert slot index (0-9) from fl_get_track_chain.
        filter: Only parameters whose name contains this text (case
            insensitive), e.g. "band 2", "threshold", "attack".
        include: Optional detail (comma-separated). Valid: "raw" (normalized
            0-1 value per parameter, needed later for exact writes),
            "all_bands" (turn off trimming: unused bands/taps, inactive
            modulators, switched-off modules and inactive dynamic-EQ settings
            are hidden by default).
        limit: Max parameters returned (default 150).

    Read `plugin_notes` before interpreting values: it says which way knobs
    go and what bare numbers mean (e.g. CLA-76 attack 7 is the FASTEST).

    Returns: summary, track_name, plugin, params[{i, name, display}],
        truncated (bool), plugin_notes.
    """
    inc = _parse_include(include)
    r, err = _fl_call("params", {"track": int(track), "slot": int(slot),
                                 "filter": filter})
    if err:
        return err
    params = r["params"]
    changed = _changes_text(_safe(archive.observe_params, r.get("project"), r["track"],
                                  r["slot"], r["plugin"], r["track_name"], params))
    total = len(params)
    if "all_bands" not in inc:
        params = fl_client.compact_params(params)
    hidden = total - len(params)
    out_params = []
    for p in params[: max(1, int(limit))]:
        rec = {"i": p["i"], "name": p["name"], "display": p["display"]}
        if "raw" in inc:
            rec["value"] = round(p["value"], 4) if p.get("value") is not None else None
        out_params.append(rec)
    truncated = len(params) > len(out_params)
    summary = (f"Project '{r.get('project') or 'unknown'}': "
               f"{r['plugin']} on track {r['track']} '{r['track_name']}' slot {r['slot']}: "
               f"{len(out_params)} parameters"
               + (f" ({hidden} from switched-off bands hidden)" if hidden else "")
               + ("; truncated, narrow with `filter`" if truncated else "") + ".")
    out = {"summary": summary, "project": r.get("project"),
           "track_name": r["track_name"], "plugin": r["plugin"],
           "params": out_params, "truncated": truncated}
    if changed:
        out["changed_since_last_read"] = changed
    note = plugin_notes.lookup(r["plugin"])
    if note:
        out["plugin_notes"] = note["notes"]
    else:
        out["plugin_notes"] = ("No notes for this plugin: read values literally and "
                               "don't guess knob directions or units.")
    return out


# ---------------------------------------------------------------------------
# Stems: connect bounced audio to FL mixer tracks
# ---------------------------------------------------------------------------
_AUDIO_EXT = (".wav", ".aif", ".aiff", ".flac", ".ogg")


def _norm(text: str) -> str:
    return "".join(ch for ch in (text or "").lower() if ch.isalnum())


def _match_stems(folder: str, tracks: list[dict]) -> dict:
    """Map audio files in `folder` to mixer tracks by name. FL's "Split mixer
    tracks" export names files after the project and the track, so a file
    matches a track when its normalized name ends with the track's normalized
    name. The longest matching track name wins (so "dbl bus" beats "bus")."""
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(_AUDIO_EXT))
    named = [(t["index"], t["name"], _norm(t["name"])) for t in tracks if _norm(t["name"])]
    matched, unmatched = [], []
    for f in files:
        stem = _norm(os.path.splitext(f)[0])
        best = None
        for idx, name, key in named:
            if stem.endswith(key) and (best is None or len(key) > len(best[2])):
                best = (idx, name, key)
        if best:
            matched.append({"file": os.path.join(folder, f), "track": best[0],
                            "track_name": best[1]})
        else:
            unmatched.append(f)
    return {"matched": matched, "unmatched": unmatched}


def _stems_folder(stems_folder: str) -> str | None:
    return stems_folder or os.environ.get("MIXBUDDY_STEMS_DIR") or None


@mcp.tool()
def fl_match_stems(stems_folder: str = "") -> dict:
    """
    Match bounced stems in a folder to the live FL Studio mixer tracks.

    In FL: File > Export > WAV with "Split mixer tracks" on writes one file
    per mixer track. Point this at that folder to see which file belongs to
    which track, then analyze one with fl_analyze_track_stem.

    Args:
        stems_folder: Absolute folder path. Defaults to the MIXBUDDY_STEMS_DIR
            environment variable.

    Returns: summary, matched[{file, track, track_name}], unmatched[file].
    """
    folder = _stems_folder(stems_folder)
    if not folder or not os.path.isdir(folder):
        return {"error": f"Stems folder not found: {folder!r}. Pass an absolute path."}
    r, err = _fl_call("mixer", {"include_empty": True})
    if err:
        return err
    m = _match_stems(folder, r["tracks"])
    m["summary"] = (f"{len(m['matched'])} stems matched to mixer tracks, "
                    f"{len(m['unmatched'])} unmatched.")
    return m


_STEM_ANALYSES = {
    "loudness": analyze_loudness,
    "dynamics": analyze_dynamics,
    "spectrum": analyze_frequency_spectrum,
    "vocal": analyze_vocal_clarity,
    "stereo": analyze_stereo_compatibility,
}


@mcp.tool()
def fl_analyze_track_stem(track: int, file_path: str = "", stems_folder: str = "",
                          analyses: str = "loudness,dynamics,spectrum") -> dict:
    """
    Analyze the bounced audio of one FL mixer track alongside its live chain,
    so a diagnosis can rest on measured sound AND the exact plugin settings.

    Give either file_path, or a stems_folder (FL "Split mixer tracks" export)
    and the file for this track is found by name.

    Args:
        track: Mixer track index from fl_get_mixer.
        file_path: Absolute path to this track's stem (optional).
        stems_folder: Folder of split-mixer-track stems (optional; defaults to
            MIXBUDDY_STEMS_DIR).
        analyses: Comma-separated. Valid: "loudness", "dynamics", "spectrum",
            "vocal" (vocal clarity / mud / sibilance), "stereo".

    Notes: the stem is what FL exported for that track, so it is only as
    current as the export. Re-export after changing the mix.

    Returns: summary, track{index, name, chain}, file, results{analysis:
        overview}.
    """
    want = [a.strip().lower() for a in (analyses or "").split(",") if a.strip()]
    bad = [a for a in want if a not in _STEM_ANALYSES]
    if bad:
        return {"error": f"Unknown analyses {bad}. Valid: {sorted(_STEM_ANALYSES)}"}

    info, err = _fl_call("track", {"track": int(track)})
    chain = None
    if info:
        chain = " -> ".join(s["plugin"] for s in info["slots"]) or "no plugins"

    path = file_path
    if not path:
        folder = _stems_folder(stems_folder)
        if not folder or not os.path.isdir(folder):
            return {"error": "Give file_path, or a stems_folder holding an FL "
                             "'Split mixer tracks' export."}
        if not info:
            return {"error": "Can't match stems by name without FL: "
                             + (err or {}).get("error", "FL not reachable")
                             + ". Pass file_path instead."}
        hits = [m for m in _match_stems(folder, [{"index": info["index"],
                                                  "name": info["name"]}])["matched"]]
        if not hits:
            return {"error": f"No stem in {folder} matches track {info['index']} "
                             f"'{info['name']}'."}
        if len(hits) > 1:
            return {"error": "Several stems match this track; pass file_path.",
                    "candidates": [h["file"] for h in hits]}
        path = hits[0]["file"]

    results = {}
    for a in want:
        results[a] = _STEM_ANALYSES[a](path)
    lines = [f"{a}: {r.get('summary') or r.get('error')}" for a, r in results.items()]
    name = info["name"] if info else f"track {track}"
    out = {
        "summary": f"Stem for '{name}' ({os.path.basename(path)}). " + " | ".join(lines),
        "track": ({"index": info["index"], "name": info["name"], "chain": chain,
                   "volume_db": info.get("volume_db")} if info else None),
        "file": path,
        "results": results,
    }
    if err:
        out["fl_warning"] = ("Analyzed the file, but couldn't read the track from FL: "
                             + err.get("error", ""))
    _safe(archive.record, (info or {}).get("project"), "analysis", out["summary"],
          data={"source": "stem", "file": path, "chain": chain},
          track=int(track), tool="fl_analyze_track_stem")
    return out


# ---------------------------------------------------------------------------
# Live audio from MixBuddy Tap plugins
# ---------------------------------------------------------------------------
def _sync_taps(track: int | None = None):
    """Ask FL to set every MixBuddy Tap's ID to its mixer track number, and
    return the taps found as (list, error)."""
    args = {} if track is None else {"track": int(track)}
    r, err = _fl_call("sync_taps", args)
    if err:
        if "unknown command" in err.get("error", ""):
            return None, {"error": "The MixBuddy controller script in FL is out of date. "
                                   "Copy fl_bridge/device_MixBuddy.py into FL's Hardware\\"
                                   "MixBuddy folder and click Reload script in FL."}
        return None, err
    return r["taps"], None


@mcp.tool()
def fl_list_taps() -> dict:
    """
    List MixBuddy Tap plugins in the FL mixer: which track and slot each sits
    on, and whether audio is flowing through it right now.

    Each tap's ID is set automatically to its mixer track number (Master = 0)
    whenever this or fl_analyze_track_live runs; the user never sets it.
    A tap hears whatever comes before it in the chain (put it last for the
    processed sound), and insert slots sit before the fader.

    Returns: summary, taps[{track, track_name, slot, live,
        seconds_since_audio, is_last_in_chain}], problems[str].
    """
    found, err = _sync_taps()
    if err:
        return err
    mix, _ = _fl_call("mixer", {"include_empty": True})
    last_slot = {t["index"]: max((p["slot"] for p in t["plugins"]), default=-1)
                 for t in (mix or {}).get("tracks", [])}
    files = {t["tap_id"]: t for t in tap_reader.list_taps()}
    taps, problems, per_track = [], [], {}
    for t in found:
        per_track.setdefault(t["track"], []).append(t["slot"])
        f = files.get(t["tap_id"])
        rec = {"track": t["track"], "track_name": t["track_name"], "slot": t["slot"],
               "live": bool(f and f["live"]),
               "seconds_since_audio": f["seconds_since_audio"] if f else None,
               "is_last_in_chain": last_slot.get(t["track"]) == t["slot"]}
        if t.get("error"):
            problems.append(f"'{t['track_name']}' slot {t['slot']}: {t['error']}.")
        elif f is None or t.get("changed"):
            problems.append(f"'{t['track_name']}': tap just assigned; play the song for "
                            "a few seconds so it fills.")
        taps.append(rec)
    for track, slots in per_track.items():
        if len(slots) > 1:
            problems.append(f"Track {track} has {len(slots)} taps (slots {slots}); they share "
                            "one audio file. Keep one, as the last insert.")
    live = sum(1 for t in taps if t["live"])
    summary = (f"{len(taps)} taps found, {live} receiving audio now."
               if taps else "No MixBuddy Tap plugins in the mixer.")
    return {"summary": summary, "taps": taps, "problems": problems}


@mcp.tool()
def fl_analyze_track_live(track: int, seconds: float = 8.0,
                          analyses: str = "loudness,dynamics,spectrum") -> dict:
    """
    Analyze what a mixer track sounds like right now, from the MixBuddy Tap
    plugin on that track (the last few seconds of audio, up to 10 s).

    Requires a MixBuddy Tap in one of the track's insert slots and the song
    playing (or just played) in FL. The tap's ID is assigned to the track
    automatically. For tracks without a tap, use fl_analyze_track_stem with an
    export instead.

    Args:
        track: Mixer track index from fl_get_mixer.
        seconds: How much recent audio to analyze (1-10, default 8).
        analyses: Comma-separated. Valid: "loudness", "dynamics", "spectrum",
            "vocal", "stereo".

    Notes: the tap hears the chain up to its slot (pre-fader). If it is not
    the last plugin, later plugins are not included; say so.

    Returns: summary, track{index, name, chain}, tap{slot, is_last_in_chain,
        seconds_since_audio}, results{analysis: overview}.
    """
    want = [a.strip().lower() for a in (analyses or "").split(",") if a.strip()]
    bad = [a for a in want if a not in _STEM_ANALYSES]
    if bad:
        return {"error": f"Unknown analyses {bad}. Valid: {sorted(_STEM_ANALYSES)}"}
    seconds = max(1.0, min(float(seconds), 10.0))
    info, err = _fl_call("track", {"track": int(track)})
    if err:
        return err
    plugs = [{"slot": s["slot"], "plugin": s["plugin"]} for s in info["slots"]]
    found, serr = _sync_taps(info["index"])
    if serr:
        return serr
    if not found:
        return {"error": f"No MixBuddy Tap on track {info['index']} '{info['name']}'. "
                         "Add it as the last insert (or use fl_analyze_track_stem)."}
    tap = found[-1]
    if tap.get("error"):
        return {"error": f"MixBuddy Tap on '{info['name']}': {tap['error']}."}
    tap["is_last_in_chain"] = tap["slot"] == max(p["slot"] for p in plugs)
    if tap.get("changed"):
        return {"error": f"The tap on '{info['name']}' was just assigned to this track. "
                         "Play the song for a few seconds, then ask again."}
    try:
        audio, sr, _h = tap_reader.read_tap(tap["tap_id"], seconds)
    except ValueError as exc:
        return {"error": str(exc)}
    status = {t["tap_id"]: t for t in tap_reader.list_taps()}.get(tap["tap_id"], {})
    if float(np.max(np.abs(audio))) < 1e-6:
        return {"error": "The tap captured only silence. Play the section you want "
                         "analyzed in FL, then ask again."}

    import soundfile as sf
    fd, tmp = tempfile.mkstemp(suffix=".wav", prefix="mixbuddy_live_")
    os.close(fd)
    try:
        sf.write(tmp, audio, sr, subtype="FLOAT")
        results = {a: _STEM_ANALYSES[a](tmp) for a in want}
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    chain = " -> ".join(p["plugin"] for p in plugs)
    lines = [f"{a}: {r.get('summary') or r.get('error')}" for a, r in results.items()]
    out = {
        "summary": (f"Live audio from '{info['name']}' ({len(audio) / sr:.1f} s via its "
                    "MixBuddy Tap). " + " | ".join(lines)),
        "track": {"index": info["index"], "name": info["name"], "chain": chain,
                  "volume_db": info.get("volume_db")},
        "tap": {"slot": tap["slot"],
                "is_last_in_chain": tap["is_last_in_chain"],
                "seconds_since_audio": status.get("seconds_since_audio")},
        "results": results,
    }
    if not tap["is_last_in_chain"]:
        out["warning"] = ("The tap is not the last plugin, so plugins after slot "
                          f"{tap['slot']} are not in this audio.")
    if status and not status.get("live"):
        out["note"] = (f"No new audio for {status.get('seconds_since_audio')} s: this is "
                       "the last thing played, not what is playing now.")
    _safe(archive.record, info.get("project"), "analysis", out["summary"],
          data={"source": "tap", "chain": chain, "volume_db": info.get("volume_db")},
          track=info["index"], tool="fl_analyze_track_live")
    return out


# ---------------------------------------------------------------------------
# Session archive: automatic change log, notes and lessons (see archive.py)
# ---------------------------------------------------------------------------
def _current_project(project: str = "") -> str | None:
    if project:
        return project
    name = _safe(lambda: fl_client.project_from_titles(fl_client.fl_window_titles()))
    if name and "fl studio" not in name.lower():
        return name
    return _safe(archive.last_project)


@mcp.tool()
def fl_snapshot(label: str = "", tracks: str = "") -> dict:
    """
    Read the whole session (every mixer track and every plugin's settings) and
    file it in the archive, reporting everything that changed since mix-buddy
    last saw it.

    Call at the START of a session (label "start"), after the user says they
    made changes ("what did I change?"), and before a bounce (label "bounce").
    This is how hand-made changes get logged even when no one asked about
    that plugin.

    Args:
        label: Short tag for this snapshot, e.g. "start", "after vocal pass",
            "bounce".
        tracks: Optional comma-separated track indexes to limit the read
            (faster). Default: all tracks in use.

    Returns: summary, project, changes[str], plugins_read, errors[str], seconds.
    """
    import time as _t
    t0 = _t.time()
    r, err = _fl_call("mixer", {"include_empty": False})
    if err:
        return err
    project = r.get("project")
    only = {int(x) for x in tracks.split(",") if x.strip().isdigit()} if tracks else None
    sel = [t for t in r["tracks"] if only is None or t["index"] in only]
    changes = _changes_text(_safe(archive.observe_mixer, project, sel))
    errors, n = [], 0
    for t in sel:
        for p in t["plugins"]:
            if str(p["plugin"]).lower().startswith("mixbuddy tap"):
                continue
            pr, perr = _fl_call("params", {"track": t["index"], "slot": p["slot"],
                                           "filter": ""})
            if perr:
                errors.append(f"track {t['index']} slot {p['slot']}: {perr['error']}")
                continue
            n += 1
            changes += _changes_text(_safe(archive.observe_params, project, t["index"],
                                           p["slot"], pr["plugin"], pr["track_name"],
                                           pr["params"]))
    secs = round(_t.time() - t0, 1)
    view = [{"index": t["index"], "name": t["name"], "volume_db": t["volume_db"],
             "pan": t.get("pan"), "chain": [p["plugin"] for p in t["plugins"]]}
            for t in sel]
    _safe(archive.record, project, "snapshot",
          f"Snapshot '{label or 'unlabeled'}': {len(sel)} tracks, {n} plugins, "
          f"{len(changes)} changes since last seen.",
          data={"tracks": view, "changes": changes[:200]}, label=label)
    return {"summary": (f"Project '{project or 'unknown'}': archived {len(sel)} tracks and "
                        f"{n} plugins in {secs} s; {len(changes)} settings changed since "
                        "mix-buddy last saw them."),
            "project": project, "changes": changes, "plugins_read": n,
            "errors": errors, "seconds": secs}


@mcp.tool()
def archive_history(project: str = "", kinds: str = "", session: str = "",
                    limit: int = 40) -> dict:
    """
    Read the session archive for a project: what changed, what was analyzed,
    what the user complained about, what was decided and how it turned out.

    Read this at the start of a session to pick up where the last one ended,
    and when the user asks "what did we do last time" or "what did I change".

    Args:
        project: Project name. Default: the project open in FL (or the most
            recently archived one when FL is closed).
        kinds: Comma-separated filter. Valid: change, analysis, snapshot,
            complaint, decision, outcome, lesson, note, read.
        session: Only one session, as YYYY-MM-DD.
        limit: Most recent N events (default 40).

    Returns: summary, project, sessions[{session, counts}], events[...].
    """
    proj = _current_project(project)
    ks = [k.strip().lower() for k in kinds.split(",") if k.strip()] or None
    evs = archive.history(proj, ks, limit, session or None)
    for e in evs:
        if e.get("kind") == "snapshot":
            e.pop("data", None)  # full track lists are too long to echo
    sess = archive.sessions(proj)
    return {"summary": (f"Archive for '{proj or 'unknown'}': {len(sess)} sessions; "
                        f"showing {len(evs)} events."),
            "project": proj, "sessions": sess, "events": evs}


@mcp.tool()
def archive_note(kind: str, text: str, tags: str = "", project: str = "") -> dict:
    """
    File what happened in this session so later sessions can learn from it.

    Use it as the session goes, without asking the user:
      * complaint - what the user said they don't like, in their words
        ("vocal sounds nasal", "ah vowels jump out").
      * decision  - a move the user accepted, with the exact settings.
      * outcome   - what the re-measurement or the user's ear said after a
        move ("nasal gone, 1-1.6 kHz down 2 dB, user: sounds better").
      * lesson    - a reusable rule learned, true beyond this song ("removing
        the 1 kHz cuts on a dark vocal brought back nasality"). Lessons are
        also shared across all projects.
      * note      - anything else worth keeping.

    Args:
        kind: complaint, decision, outcome, lesson or note.
        text: One or two plain sentences with numbers where they exist.
        tags: Comma-separated, e.g. "vocal,nasal,eq". Lessons are searched by tag.
        project: Default: the project open in FL.

    Returns: saved event.
    """
    proj = _current_project(project)
    try:
        ev = archive.note(proj, kind, text, [t for t in tags.split(",")])
    except ValueError as exc:
        return {"error": str(exc)}
    return {"summary": f"Filed {ev['kind']} for '{proj or 'unknown'}'.", "event": ev}


@mcp.tool()
def archive_lessons(tags: str = "", limit: int = 30) -> dict:
    """
    Read the lessons learned across ALL projects (what worked, what backfired),
    so advice improves over time instead of repeating mistakes.

    Read at the start of every session, and before proposing a move on a
    problem that has come up before (filter by tag, e.g. "nasal", "reverb").

    Args:
        tags: Optional comma-separated tag filter (any match).
        limit: Most recent N lessons (default 30).

    Returns: summary, lessons[{ts, project, text, tags}].
    """
    ts = [t.strip() for t in tags.split(",") if t.strip()] or None
    ls = archive.lessons(ts, limit)
    return {"summary": f"{len(ls)} lessons" + (f" tagged {ts}" if ts else "") + ".",
            "lessons": ls}


# ---------------------------------------------------------------------------
# Project memory tools
# ---------------------------------------------------------------------------
@mcp.tool()
def read_project_memory(project: str = "default") -> dict:
    """
    Read persisted project context (reference artists, target LUFS, recurring
    problems, free-form notes) so advice stays consistent across sessions.

    ALWAYS read before writing - writes replace the whole memory object.

    Args:
        project: Project name. Defaults to "default".

    Returns: project, exists (bool), memory (the stored object or a blank
        template if the project has never been written).
    """
    return memory.read_memory(project)


@mcp.tool()
def write_project_memory(content: dict, project: str = "default") -> dict:
    """
    REPLACE the entire memory object for a project. Read first, merge in your
    head, then write the complete object - unread fields will be lost.

    Suggested fields: reference_artists (list[str]), target_lufs (number),
    recurring_problems (list[str]), notes (string). Extra fields are allowed.

    Args:
        content: The complete memory object (JSON) to store.
        project: Project name. Defaults to "default".

    Returns: project, saved (bool), memory (what was stored, incl. _updated_at).
    """
    try:
        return memory.write_memory(content, project)
    except TypeError as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
