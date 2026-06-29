"""
Audio Mixing Analyzer - MCP Server

Exposes real DSP audio-analysis tools to an LLM via the Model Context Protocol.
All heavy lifting lives in dsp.py (unit-tested separately); this layer only
handles tool registration, input validation and JSON serialization.

Run:  python mcp_server/server.py
"""
from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

# Allow running both as a module and as a script.
sys.path.insert(0, os.path.dirname(__file__))
import dsp  # noqa: E402

mcp = FastMCP("audio-mixing-analyzer")


@mcp.tool()
def analyze_loudness(file_path: str) -> dict:
    """
    Measure EBU R128 / ITU-R BS.1770 integrated loudness (LUFS) of an audio file.

    Use this to check whether a track is too quiet or too loud for streaming
    (Spotify/Apple target around -14 LUFS; club/loud masters can be higher).

    Args:
        file_path: Absolute path to a WAV/AIFF/FLAC/OGG audio file.

    Returns:
        sample_rate, channels, duration_seconds, integrated_loudness_lufs.
    """
    try:
        audio = dsp.load_audio(file_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    lufs = dsp.integrated_loudness_lufs(audio.mono, audio.sample_rate)
    return {
        "sample_rate": audio.sample_rate,
        "channels": audio.n_channels,
        "duration_seconds": round(audio.duration_seconds, 2),
        "integrated_loudness_lufs": round(lufs, 2),
    }


@mcp.tool()
def analyze_dynamics(file_path: str) -> dict:
    """
    Measure peak/RMS levels, crest factor and dynamic range, then suggest
    compression settings (ratio, attack, release).

    Use this when the user asks about compression, dynamics, "punch", or a
    vocal/instrument that sounds uneven or uncontrolled.

    Args:
        file_path: Absolute path to the target audio file.

    Returns:
        peak_level_dbfs, rms_level_dbfs, crest_factor_db, dynamic_range_db,
        and a compression_suggestion block.
    """
    try:
        audio = dsp.load_audio(file_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    return dsp.analyze_dynamics_metrics(audio.mono, audio.sample_rate)


@mcp.tool()
def analyze_frequency_spectrum(file_path: str, deviation_factor: float = 2.0) -> dict:
    """
    Compute multi-band spectral energy and detect harsh resonant peaks using a
    dynamic standard-deviation threshold curve. Resonances are classified
    (mud, boxiness, sibilance, etc.) with suggested attenuation.

    Use this for general tonal-balance questions and to find problem frequencies.

    Args:
        file_path: Absolute path to the target audio file.
        deviation_factor: Sensitivity of resonance detection (1.0-2.5;
            higher = fewer, only the most extreme peaks).

    Returns:
        frequency_bands (energy per band), spectral_centroid_hz, and a
        resonances list.
    """
    try:
        audio = dsp.load_audio(file_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    bands = dsp.multiband_energy(audio.mono, audio.sample_rate)
    res = dsp.detect_resonances_metrics(
        audio.mono, audio.sample_rate, local_deviation_factor=deviation_factor
    )
    return {"frequency_bands": bands, **res}


@mcp.tool()
def analyze_vocal_clarity(file_path: str) -> dict:
    """
    Diagnose vocal balance: mud (200-500 Hz), presence (2-5 kHz) and sibilance
    (5-9 kHz). Returns clarity/mud/sibilance indices and concrete EQ moves.

    Use this when the user asks "how do I make my vocal clearer / cut through /
    less muddy / less harsh".

    Args:
        file_path: Absolute path to the vocal audio file (mono recommended).

    Returns:
        clarity_score, mud_index, sibilance_index, fundamental_warmth_db,
        and eq_suggestions.
    """
    try:
        audio = dsp.load_audio(file_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    return dsp.analyze_vocal_clarity_metrics(audio.mono, audio.sample_rate)


@mcp.tool()
def analyze_stereo_compatibility(file_path: str) -> dict:
    """
    Evaluate stereo correlation, interchannel delay and mono compatibility.
    Flags phase cancellation risk (especially in the sub-bass).

    Use this for width, phase, "disappears in mono", or panning issues.

    Args:
        file_path: Absolute path to a stereo audio file.

    Returns:
        overall_correlation, interchannel_time_delay_ms,
        sub_150hz_phase_correlation, phase_alignment_status,
        sub_bass_cancellation_risk, requires_corrective_intervention.
    """
    try:
        audio = dsp.load_audio(file_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    return dsp.analyze_stereo_metrics(audio)


@mcp.tool()
def compare_to_reference(target_path: str, reference_path: str) -> dict:
    """
    Compare a target mix against a professional reference: loudness differential
    and band-by-band spectral balance, with directional recommendations.

    Use this when the user wants their track to sound like a reference song.

    Args:
        target_path: Path to the user's (unfinished) mix.
        reference_path: Path to the professional reference track.

    Returns:
        loudness_differential_lu, target/reference LUFS, and spectral_difference
        per band with recommendations.
    """
    try:
        target = dsp.load_audio(target_path)
        reference = dsp.load_audio(reference_path)
    except (FileNotFoundError, RuntimeError) as exc:
        return {"error": str(exc)}

    t_lufs = dsp.integrated_loudness_lufs(target.mono, target.sample_rate)
    r_lufs = dsp.integrated_loudness_lufs(reference.mono, reference.sample_rate)

    t_bands = dsp.multiband_energy(target.mono, target.sample_rate)
    r_bands = dsp.multiband_energy(reference.mono, reference.sample_rate)

    spectral_diff = []
    for name in ("sub_bass", "low_bass", "low_mids", "mid_range", "high_mids", "highs"):
        if name in t_bands and name in r_bands:
            diff = t_bands[name]["energy_db"] - r_bands[name]["energy_db"]
            if diff > 1.5:
                rec = f"Cut {name} (~{diff:.1f} dB hotter than reference)."
            elif diff < -1.5:
                rec = f"Boost {name} (~{abs(diff):.1f} dB below reference)."
            else:
                rec = f"{name} matches reference."
            spectral_diff.append(
                {
                    "band": name,
                    "range_hz": t_bands[name]["range_hz"],
                    "difference_db": round(diff, 1),
                    "recommendation": rec,
                }
            )

    return {
        "loudness_differential_lu": round(t_lufs - r_lufs, 2),
        "target_loudness_lufs": round(t_lufs, 2),
        "reference_loudness_lufs": round(r_lufs, 2),
        "spectral_difference": spectral_diff,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
