"""
Audio DSP utilities for music mixing analysis.

Pure functions for loading audio and computing mixing-relevant metrics.
Kept separate from the MCP server layer so they can be unit-tested directly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import soundfile as sf
from scipy.signal import find_peaks, lfilter


# ---------------------------------------------------------------------------
# Audio loading
# ---------------------------------------------------------------------------
@dataclass
class AudioData:
    """Container for decoded audio."""

    samples: np.ndarray  # float32, shape (n,) mono or (n, channels)
    sample_rate: int

    @property
    def n_channels(self) -> int:
        return 1 if self.samples.ndim == 1 else self.samples.shape[1]

    @property
    def duration_seconds(self) -> float:
        return len(self.samples) / self.sample_rate

    @property
    def mono(self) -> np.ndarray:
        """Down-mix to mono by averaging channels."""
        if self.samples.ndim == 1:
            return self.samples
        return np.mean(self.samples, axis=1)


def load_audio(file_path: str) -> AudioData:
    """
    Load an audio file (WAV/AIFF/FLAC/OGG) as float32 in range [-1, 1].

    Raises:
        FileNotFoundError: if the path does not exist.
        RuntimeError: if the file cannot be decoded.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    try:
        # always_2d=False keeps mono as 1-D; dtype float32 normalizes ints.
        samples, sample_rate = sf.read(file_path, dtype="float32", always_2d=False)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the caller
        raise RuntimeError(f"Failed to read audio file: {exc}") from exc

    return AudioData(samples=samples, sample_rate=int(sample_rate))


# ---------------------------------------------------------------------------
# Loudness (EBU R128 / ITU-R BS.1770 K-weighting)
# ---------------------------------------------------------------------------
def _k_weighting_coeffs(fs: int):
    """
    Return (b1, a1, b2, a2) K-weighting filter coefficients.

    Stage 1: high-shelf (head/ear modelling). Stage 2: high-pass (RLB).
    Coefficients are computed analytically so any sample rate works, not just
    44.1/48 kHz (fixes the hard-coded-rate bug in the source research).

    Based on ITU-R BS.1770-4 bilinear-transformed analog prototypes.
    """
    # Pre-warped bilinear transform of the two BS.1770 analog stages.
    # Stage 1: high frequency shelving boost.
    f0 = 1681.974450955533
    G = 3.999843853973347
    Q = 0.7071752369554196

    K = np.tan(np.pi * f0 / fs)
    Vh = 10 ** (G / 20.0)
    Vb = Vh ** 0.4996667741545416
    a0 = 1.0 + K / Q + K * K
    b1 = [
        (Vh + Vb * K / Q + K * K) / a0,
        2.0 * (K * K - Vh) / a0,
        (Vh - Vb * K / Q + K * K) / a0,
    ]
    a1 = [
        1.0,
        2.0 * (K * K - 1.0) / a0,
        (1.0 - K / Q + K * K) / a0,
    ]

    # Stage 2: high-pass (RLB weighting curve).
    f0 = 38.13547087602444
    Q = 0.5003270373238773
    K = np.tan(np.pi * f0 / fs)
    a0 = 1.0 + K / Q + K * K
    b2 = [1.0, -2.0, 1.0]
    a2 = [
        1.0,
        2.0 * (K * K - 1.0) / a0,
        (1.0 - K / Q + K * K) / a0,
    ]
    return b1, a1, b2, a2


def integrated_loudness_lufs(mono: np.ndarray, fs: int) -> float:
    """
    Compute EBU R128 integrated loudness in LUFS with two-stage gating.

    Returns -70.0 for silence / too-short signals.
    """
    b1, a1, b2, a2 = _k_weighting_coeffs(fs)
    y = lfilter(b1, a1, mono)
    y = lfilter(b2, a2, y)

    block_size = int(0.4 * fs)
    step_size = int(0.1 * fs)
    if block_size <= 0 or len(y) < block_size:
        return -70.0

    num_blocks = (len(y) - block_size) // step_size + 1
    block_powers = np.empty(num_blocks, dtype=np.float64)
    for idx in range(num_blocks):
        start = idx * step_size
        block = y[start : start + block_size]
        block_powers[idx] = np.mean(block ** 2)

    # Absolute gate at -70 LUFS.
    absolute_threshold = 10 ** (-70.0 / 10.0)
    gated = block_powers[block_powers > absolute_threshold]
    if gated.size == 0:
        return -70.0

    # Relative gate at -10 LU below the ungated loudness.
    mean_power = np.mean(gated)
    relative_threshold = mean_power * 10 ** (-10.0 / 10.0)
    final = gated[gated > relative_threshold]
    if final.size == 0:
        return -70.0

    return float(10 * np.log10(np.mean(final)) - 0.691)


# ---------------------------------------------------------------------------
# Dynamics: RMS, peak, crest factor, compression suggestions
# ---------------------------------------------------------------------------
def _to_db(x: float) -> float:
    return float(20 * np.log10(max(x, 1e-10)))


def analyze_dynamics_metrics(mono: np.ndarray, fs: int) -> dict:
    """
    Compute peak, RMS, crest factor and derive compression suggestions.

    Crest factor (peak - RMS in dB) drives the suggested ratio: a high crest
    factor implies uncontrolled transients that benefit from heavier control.
    """
    if mono.size == 0:
        return {"error": "Empty audio signal."}

    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    peak_db = _to_db(peak)
    rms_db = _to_db(rms)
    crest_db = peak_db - rms_db

    # Short-term RMS variation indicates how dynamic the performance is.
    win = max(1, int(0.05 * fs))  # 50 ms windows
    n_win = len(mono) // win
    if n_win > 1:
        trimmed = mono[: n_win * win].reshape(n_win, win)
        st_rms = np.sqrt(np.mean(trimmed ** 2, axis=1) + 1e-12)
        st_rms_db = 20 * np.log10(st_rms)
        # Loudness range proxy: spread of the loud vs quiet windows.
        dynamic_range_db = float(np.percentile(st_rms_db, 95) - np.percentile(st_rms_db, 10))
    else:
        dynamic_range_db = 0.0

    # Map crest factor -> compression suggestion.
    # Lower crest target for controlled vocals; heuristics from mixing practice.
    requires_control = crest_db > 12.0 or dynamic_range_db > 12.0
    if crest_db > 18:
        ratio = "4:1"
    elif crest_db > 14:
        ratio = "3:1"
    elif crest_db > 10:
        ratio = "2.5:1"
    else:
        ratio = "2:1"

    # Faster attack for spiky transients, slower release for higher dynamic range.
    attack_ms = round(float(np.clip(30 - (crest_db - 10) * 1.5, 3, 30)), 1)
    release_ms = round(float(np.clip(60 + dynamic_range_db * 8, 60, 300)), 1)

    return {
        "peak_level_dbfs": round(peak_db, 2),
        "rms_level_dbfs": round(rms_db, 2),
        "crest_factor_db": round(crest_db, 2),
        "dynamic_range_db": round(dynamic_range_db, 2),
        "compression_suggestion": {
            "requires_control": bool(requires_control),
            "suggested_ratio": ratio,
            "suggested_attack_ms": attack_ms,
            "suggested_release_ms": release_ms,
            "rationale": (
                f"Crest factor {crest_db:.1f} dB and dynamic range "
                f"{dynamic_range_db:.1f} dB."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Spectral analysis: resonance detection + multi-band energy
# ---------------------------------------------------------------------------
def _segment_for_fft(mono: np.ndarray, fs: int, seconds: float) -> np.ndarray:
    """Take a centered segment of the requested length (or the whole signal)."""
    window_len = min(len(mono), int(seconds * fs))
    if window_len <= 0:
        return mono
    center = len(mono) // 2
    start = max(0, center - window_len // 2)
    return mono[start : start + window_len]


def _classify_frequency(freq: float) -> str:
    """Map a frequency to a mixing-relevant category."""
    if freq < 200:
        return "low-end rumble/boom"
    if 200 <= freq <= 500:
        return "mud"
    if 500 < freq <= 800:
        return "boxiness"
    if 800 < freq <= 4000:
        return "presence"
    if 4000 < freq <= 10000:
        return "natural sibilance"
    if 10000 < freq <= 16000:
        return "synthetic sibilance/air"
    return "ultra-high"


def detect_resonances_metrics(
    mono: np.ndarray, fs: int, local_deviation_factor: float = 2.0
) -> dict:
    """
    Detect harsh resonant peaks via a dynamic standard-deviation threshold curve.

    Averages the magnitude spectrum across multiple windows spanning the whole
    file (fixes the source bug where only the center 2 s was analyzed).
    """
    if mono.size < 512:
        return {"error": "Audio too short for spectral analysis."}

    # Average power spectrum across the whole file (Welch-style averaging).
    n_fft = 8192
    hop = n_fft // 2
    window = np.hanning(n_fft)
    n_frames = max(1, (len(mono) - n_fft) // hop + 1)
    accum = np.zeros(n_fft // 2 + 1, dtype=np.float64)
    counted = 0
    for i in range(n_frames):
        start = i * hop
        frame = mono[start : start + n_fft]
        if len(frame) < n_fft:
            break
        spec = np.abs(np.fft.rfft(frame * window))
        accum += spec ** 2
        counted += 1
    if counted == 0:
        # Signal shorter than one FFT frame: pad and analyze once.
        frame = np.zeros(n_fft)
        frame[: len(mono)] = mono
        accum = np.abs(np.fft.rfft(frame * window)) ** 2
        counted = 1

    mag = np.sqrt(accum / counted)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / fs)
    db_spectrum = 20 * np.log10(mag + 1e-10)

    # Smooth the spectrum to build a moving-average baseline (~500 Hz window).
    smooth_len = int(500 * n_fft / fs)
    smooth_len = max(5, smooth_len + (smooth_len + 1) % 2)  # force odd, >=5
    kernel = np.ones(smooth_len) / smooth_len
    smoothed = np.convolve(db_spectrum, kernel, mode="same")

    # Vectorized local standard deviation via running sums (fixes O(n) loop).
    half = smooth_len // 2
    padded = np.pad(db_spectrum, half, mode="edge")
    csum = np.cumsum(np.insert(padded, 0, 0.0))
    csum_sq = np.cumsum(np.insert(padded ** 2, 0, 0.0))
    win = 2 * half + 1
    local_mean = (csum[win:] - csum[:-win]) / win
    local_mean_sq = (csum_sq[win:] - csum_sq[:-win]) / win
    local_var = np.maximum(local_mean_sq - local_mean ** 2, 0.0)
    local_std = np.sqrt(local_var)[: len(db_spectrum)]

    threshold = smoothed + local_deviation_factor * local_std
    peaks, _ = find_peaks(
        db_spectrum, height=threshold, distance=max(1, int(100 * n_fft / fs))
    )

    resonances = []
    for idx in peaks:
        freq = float(freqs[idx])
        if not (100.0 <= freq <= 16000.0):
            continue
        db_val = float(db_spectrum[idx])
        excess = db_val - float(threshold[idx])
        resonances.append(
            {
                "frequency_hz": round(freq, 1),
                "peak_magnitude_db": round(db_val, 1),
                "excess_db": round(excess, 1),
                "suggested_attenuation_db": round(-excess * 0.75, 1),
                "classification": _classify_frequency(freq),
            }
        )

    resonances.sort(key=lambda r: r["excess_db"], reverse=True)
    return {
        "peaks_detected_count": len(resonances),
        "resonances": resonances[:10],
    }


def multiband_energy(mono: np.ndarray, fs: int) -> dict:
    """Compute average energy (dB) across standard mixing frequency bands."""
    segment = _segment_for_fft(mono, fs, seconds=10.0)
    n_fft = 1
    while n_fft < len(segment):
        n_fft <<= 1
    window = np.hanning(len(segment))
    spec = np.abs(np.fft.rfft(segment * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / fs)
    power = spec ** 2

    bands = {
        "sub_bass": (20, 60),
        "low_bass": (60, 200),
        "low_mids": (200, 500),
        "mid_range": (500, 2000),
        "high_mids": (2000, 6000),
        "highs": (6000, 20000),
    }
    out = {}
    for name, (lo, hi) in bands.items():
        mask = (freqs >= lo) & (freqs < hi)
        if np.any(mask):
            energy = np.mean(power[mask])
            out[name] = {
                "range_hz": f"{lo}-{hi}",
                "energy_db": round(_to_db(np.sqrt(energy)), 1),
            }
    # Spectral centroid: brightness indicator.
    total_power = np.sum(power) + 1e-12
    centroid = float(np.sum(freqs * power) / total_power)
    out["spectral_centroid_hz"] = round(centroid, 1)
    return out


# ---------------------------------------------------------------------------
# Vocal clarity
# ---------------------------------------------------------------------------
def analyze_vocal_clarity_metrics(mono: np.ndarray, fs: int) -> dict:
    """
    Evaluate vocal balance: mud (200-500 Hz), presence (2-5 kHz), sibilance.

    Produces indices and EQ suggestions tailored to vocal intelligibility.
    """
    if mono.size < 512:
        return {"error": "Audio too short for vocal analysis."}

    segment = _segment_for_fft(mono, fs, seconds=10.0)
    n_fft = 1
    while n_fft < len(segment):
        n_fft <<= 1
    window = np.hanning(len(segment))
    spec = np.abs(np.fft.rfft(segment * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / fs)
    power = spec ** 2

    def band_energy(lo: float, hi: float) -> float:
        mask = (freqs >= lo) & (freqs < hi)
        return float(np.mean(power[mask])) if np.any(mask) else 1e-12

    total = band_energy(80, 16000) + 1e-12
    mud = band_energy(200, 500)
    warmth = band_energy(120, 250)
    presence = band_energy(2000, 5000)
    sibilance = band_energy(5000, 9000)

    # Indices on a 0-10 scale relative to overall energy.
    mud_index = round(min(10.0, (mud / total) * 40.0), 1)
    sibilance_index = round(min(10.0, (sibilance / total) * 60.0), 1)
    # Clarity = presence energy relative to mud (higher is clearer).
    clarity_score = round(min(1.0, presence / (mud + 1e-12)), 2)
    warmth_db = round(_to_db(np.sqrt(warmth)), 1)

    suggestions = []
    suggestions.append(
        {
            "action": "cut",
            "frequency_hz": 90.0,
            "type": "high_pass",
            "slope_db_oct": 18,
            "description": "High-pass to remove rumble and proximity boom.",
        }
    )
    if mud_index > 5.0:
        suggestions.append(
            {
                "action": "cut",
                "frequency_hz": 340.0,
                "q": 1.0,
                "gain_db": round(-min(4.0, mud_index * 0.4), 1),
                "description": "Attenuate low-mid mud for a cleaner vocal.",
            }
        )
    if clarity_score < 0.6:
        suggestions.append(
            {
                "action": "boost",
                "frequency_hz": 3000.0,
                "q": 1.2,
                "gain_db": round(min(3.0, (0.6 - clarity_score) * 6), 1),
                "description": "Boost presence for intelligibility and edge.",
            }
        )
    if sibilance_index > 6.0:
        suggestions.append(
            {
                "action": "de-ess",
                "frequency_hz": 7000.0,
                "threshold_reduction_db": round(-min(5.0, sibilance_index * 0.5), 1),
                "description": "De-ess harsh sibilance with a dynamic high band.",
            }
        )

    return {
        "clarity_score": clarity_score,
        "mud_index": mud_index,
        "sibilance_index": sibilance_index,
        "fundamental_warmth_db": warmth_db,
        "eq_suggestions": suggestions,
    }


# ---------------------------------------------------------------------------
# Stereo / phase compatibility
# ---------------------------------------------------------------------------
def analyze_stereo_metrics(audio: AudioData) -> dict:
    """Evaluate stereo correlation, interchannel delay and mono compatibility."""
    if audio.n_channels < 2:
        return {
            "status": "monophonic",
            "correlation_coefficient": 1.0,
            "phase_alignment_status": "coherent",
            "analysis": "File is mono; 100% mono compatible.",
        }

    left = audio.samples[:, 0].astype(np.float64)
    right = audio.samples[:, 1].astype(np.float64)
    fs = audio.sample_rate

    num = np.sum(left * right)
    den = np.sqrt(np.sum(left ** 2) * np.sum(right ** 2))
    rho = float(num / den) if den != 0 else 0.0

    # Interchannel delay via generalized cross-correlation (phase transform).
    seg = min(len(left), int(1.0 * fs))
    center = len(left) // 2
    ls = left[center - seg // 2 : center + seg // 2]
    rs = right[center - seg // 2 : center + seg // 2]
    n_fft = 1
    while n_fft < len(ls):
        n_fft <<= 1
    XL = np.fft.fft(ls, n=n_fft)
    XR = np.fft.fft(rs, n=n_fft)
    cross = XL * np.conj(XR)
    R = cross / (np.abs(cross) + 1e-10)
    corr = np.fft.ifft(R).real
    raw_delay = int(np.argmax(corr))
    if raw_delay > n_fft // 2:
        raw_delay -= n_fft
    time_delay_ms = (raw_delay / fs) * 1000.0

    freqs = np.fft.fftfreq(n_fft, d=1.0 / fs)
    low_mask = (freqs >= 20.0) & (freqs <= 150.0)
    low_phase_corr = float(np.mean(R[low_mask].real)) if np.any(low_mask) else 1.0

    warning = False
    status = "coherent"
    if rho < 0.0:
        warning = True
        status = "severe out-of-phase"
    elif rho < 0.3:
        status = "wide / uncorrelated stereo field"

    sub_bass = "safe"
    if low_phase_corr < 0.0:
        sub_bass = "vulnerable to bass cancellation"
        warning = True

    return {
        "overall_correlation": round(rho, 3),
        "interchannel_time_delay_ms": round(time_delay_ms, 3),
        "sub_150hz_phase_correlation": round(low_phase_corr, 3),
        "phase_alignment_status": status,
        "sub_bass_cancellation_risk": sub_bass,
        "requires_corrective_intervention": warning,
    }
