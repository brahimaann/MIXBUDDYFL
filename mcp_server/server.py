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
import sys

from mcp.server.fastmcp import FastMCP

# Allow running both as a module and as a script.
sys.path.insert(0, os.path.dirname(__file__))
import dsp  # noqa: E402
import memory  # noqa: E402

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
    lufs = dsp.integrated_loudness_lufs(audio.mono, audio.sample_rate)

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
    tp = dsp.true_peak_dbfs(audio.mono, audio.sample_rate)
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

    t_lufs = dsp.integrated_loudness_lufs(target.mono, target.sample_rate)
    r_lufs = dsp.integrated_loudness_lufs(reference.mono, reference.sample_rate)

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
