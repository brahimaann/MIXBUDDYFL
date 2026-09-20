"""
Validation tests for the DSP module using synthetic audio with KNOWN properties.

Strategy: generate signals where we know the ground truth (e.g., a tone at
exactly 400 Hz, a -20 dBFS sine wave) and assert the DSP functions recover it.
This catches hallucinations / math bugs that mock data would hide.
"""
import os
import sys
import tempfile

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))
import dsp  # noqa: E402

FS = 44100
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def write_temp(samples, fs=FS):
    path = os.path.join(tempfile.gettempdir(), f"_dsp_test_{np.random.randint(1e9)}.wav")
    sf.write(path, samples, fs)
    return path


def sine(freq, secs=2.0, amp=0.5, fs=FS):
    t = np.arange(int(secs * fs)) / fs
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


print("\n=== TEST: load_audio ===")
mono_sig = sine(440)
p = write_temp(mono_sig)
a = dsp.load_audio(p)
check("loads mono file", a.n_channels == 1, f"got {a.n_channels}")
check("correct sample rate", a.sample_rate == FS, f"got {a.sample_rate}")
check("correct duration", abs(a.duration_seconds - 2.0) < 0.01, f"got {a.duration_seconds}")
os.remove(p)

stereo_sig = np.column_stack([sine(440), sine(440)])
p = write_temp(stereo_sig)
a = dsp.load_audio(p)
check("loads stereo file", a.n_channels == 2, f"got {a.n_channels}")
os.remove(p)

print("\n=== TEST: missing file raises ===")
try:
    dsp.load_audio("C:/does/not/exist.wav")
    check("raises FileNotFoundError", False, "no exception")
except FileNotFoundError:
    check("raises FileNotFoundError", True)


print("\n=== TEST: integrated_loudness_lufs ===")
# A full-scale sine should be louder than a quiet one; both finite.
loud = dsp.integrated_loudness_lufs(sine(1000, amp=0.9), FS)
quiet = dsp.integrated_loudness_lufs(sine(1000, amp=0.05), FS)
check("louder signal has higher LUFS", loud > quiet, f"loud={loud:.1f} quiet={quiet:.1f}")
check("LUFS in plausible range", -40 < loud < 0, f"got {loud:.1f}")
# ~20 dB amplitude ratio (0.9 vs 0.09) -> ~20 LU difference.
loud2 = dsp.integrated_loudness_lufs(sine(1000, amp=0.9), FS)
quiet2 = dsp.integrated_loudness_lufs(sine(1000, amp=0.09), FS)
check("10x amplitude ~= 20 LU diff", abs((loud2 - quiet2) - 20) < 3, f"diff={loud2-quiet2:.1f}")
silence = dsp.integrated_loudness_lufs(np.zeros(FS), FS)
check("silence returns -70", silence == -70.0, f"got {silence}")


print("\n=== TEST: analyze_dynamics_metrics ===")
# A constant sine has crest factor ~3 dB (peak/rms of a sine = sqrt(2)).
d = dsp.analyze_dynamics_metrics(sine(440, amp=0.5), FS)
check("sine crest factor ~3 dB", abs(d["crest_factor_db"] - 3.0) < 1.0, f"got {d['crest_factor_db']}")
check("peak near -6 dBFS for amp 0.5", abs(d["peak_level_dbfs"] - (-6.02)) < 0.5, f"got {d['peak_level_dbfs']}")
check("low crest -> low ratio", d["compression_suggestion"]["suggested_ratio"] == "2:1", d["compression_suggestion"]["suggested_ratio"])
# Spiky signal: impulses -> high crest factor.
spiky = np.zeros(FS, dtype=np.float32)
spiky[::1000] = 0.9
d2 = dsp.analyze_dynamics_metrics(spiky, FS)
check("spiky signal high crest", d2["crest_factor_db"] > 15, f"got {d2['crest_factor_db']}")


print("\n=== TEST: detect_resonances_metrics ===")
# Tone + strong narrow resonance at 400 Hz should be detected & classified mud.
base = sine(150, amp=0.1) + sine(800, amp=0.1)
resonant = base + sine(400, amp=0.6)  # dominant peak at 400
r = dsp.detect_resonances_metrics(resonant, FS)
found_400 = any(abs(res["frequency_hz"] - 400) < 25 for res in r["resonances"])
check("detects 400 Hz resonance", found_400, f"peaks={[x['frequency_hz'] for x in r['resonances']]}")
mud_classified = any(
    abs(res["frequency_hz"] - 400) < 25 and res["classification"] == "mud"
    for res in r["resonances"]
)
check("classifies 400 Hz as mud", mud_classified)
# Sibilance region
sib = sine(200, amp=0.1) + sine(7000, amp=0.6)
r2 = dsp.detect_resonances_metrics(sib, FS)
sib_found = any(
    abs(res["frequency_hz"] - 7000) < 100 and "sibilance" in res["classification"]
    for res in r2["resonances"]
)
check("detects + classifies 7kHz sibilance", sib_found, f"peaks={[(x['frequency_hz'],x['classification']) for x in r2['resonances']]}")


print("\n=== TEST: multiband_energy ===")
# Energy concentrated at 100 Hz -> low_bass band should dominate.
bass = sine(100, amp=0.7)
mb = dsp.multiband_energy(bass, FS)
low_bass_e = mb["low_bass"]["energy_db"]
highs_e = mb["highs"]["energy_db"]
check("bass tone: low_bass > highs", low_bass_e > highs_e, f"low={low_bass_e} high={highs_e}")
check("centroid low for bass tone", mb["spectral_centroid_hz"] < 500, f"got {mb['spectral_centroid_hz']}")


print("\n=== TEST: analyze_vocal_clarity_metrics ===")
# Muddy vocal: strong 300 Hz, weak presence.
muddy = sine(300, amp=0.7) + sine(2500, amp=0.05)
vc = dsp.analyze_vocal_clarity_metrics(muddy, FS)
check("muddy signal high mud_index", vc["mud_index"] > 5, f"got {vc['mud_index']}")
has_mud_cut = any(s.get("frequency_hz") == 340.0 for s in vc["eq_suggestions"])
check("suggests mud cut", has_mud_cut)
# Clear vocal: strong presence, low mud.
clear = sine(3000, amp=0.7) + sine(300, amp=0.05)
vc2 = dsp.analyze_vocal_clarity_metrics(clear, FS)
check("clear signal higher clarity", vc2["clarity_score"] > vc["clarity_score"], f"clear={vc2['clarity_score']} muddy={vc['clarity_score']}")


print("\n=== TEST: analyze_stereo_metrics ===")
# Identical L/R = perfectly correlated (mono-summable).
ident = np.column_stack([sine(440), sine(440)])
p = write_temp(ident)
a = dsp.load_audio(p)
st = dsp.analyze_stereo_metrics(a)
check("identical channels corr ~1", st["overall_correlation"] > 0.98, f"got {st['overall_correlation']}")
os.remove(p)
# Inverted R = anti-correlated -> out of phase warning.
inv = np.column_stack([sine(440), -sine(440)])
p = write_temp(inv)
a = dsp.load_audio(p)
st2 = dsp.analyze_stereo_metrics(a)
check("inverted channels corr ~-1", st2["overall_correlation"] < -0.98, f"got {st2['overall_correlation']}")
check("inverted flags intervention", st2["requires_corrective_intervention"] is True)
os.remove(p)
# Mono file reported as monophonic.
p = write_temp(sine(440))
a = dsp.load_audio(p)
st3 = dsp.analyze_stereo_metrics(a)
check("mono file reported monophonic", st3.get("status") == "monophonic")
os.remove(p)


print("\n=== TEST: analyze_gate_settings_metrics ===")


def phrase_gap_signal(gap_amp: float, n_phrases: int = 4, fs: int = FS) -> np.ndarray:
    """Lead-in silence, then [phrase, gap] pairs. gap_amp=0 -> true silence gaps."""
    lead_in = np.zeros(int(0.3 * fs), dtype=np.float32)
    parts = [lead_in]
    rng = np.random.RandomState(0)
    for _ in range(n_phrases):
        parts.append(sine(220, secs=0.5, amp=0.5, fs=fs))
        if gap_amp > 0:
            parts.append((gap_amp * rng.standard_normal(int(0.4 * fs))).astype(np.float32))
        else:
            parts.append(np.zeros(int(0.4 * fs), dtype=np.float32))
    return np.concatenate(parts)


clean_sig = phrase_gap_signal(gap_amp=0.0)
g_clean = dsp.analyze_gate_settings_metrics(clean_sig, FS)
check(
    "clean gaps: no breath bleed",
    g_clean["breath_bleed_detected"] is False,
    f"bleed_db={g_clean['breath_bleed_db']}",
)
check("clean gaps: detected some gaps", g_clean["gaps_detected_count"] >= 3, g_clean["gaps_detected_count"])

breathy_sig = phrase_gap_signal(gap_amp=0.03)
g_breathy = dsp.analyze_gate_settings_metrics(breathy_sig, FS)
check(
    "breathy gaps: bleed detected",
    g_breathy["breath_bleed_detected"] is True,
    f"bleed_db={g_breathy['breath_bleed_db']}",
)
check(
    "breathy gaps: gap level well above clean noise floor",
    g_breathy["gap_level_dbfs"] > g_clean["gap_level_dbfs"] + 20,
    f"breathy={g_breathy['gap_level_dbfs']} clean={g_clean['gap_level_dbfs']}",
)
check(
    "breathy gaps: suggests higher ratio + sidechain HPF",
    g_breathy["gate_suggestion"]["ratio"] == "4:1"
    and g_breathy["gate_suggestion"]["sidechain_highpass_hz"] == 150.0,
    g_breathy["gate_suggestion"],
)
check(
    "clean gaps: no sidechain HPF suggested",
    g_clean["gate_suggestion"]["sidechain_highpass_hz"] is None,
)
check(
    "release suggestion shorter than the median gap",
    g_breathy["gate_suggestion"]["release_ms"] < g_breathy["median_gap_duration_ms"],
    f"release={g_breathy['gate_suggestion']['release_ms']} gap={g_breathy['median_gap_duration_ms']}",
)

too_short = dsp.analyze_gate_settings_metrics(sine(440, secs=0.05), FS)
check("too-short signal returns error", "error" in too_short)


print(f"\n{'='*40}\nRESULTS: {PASS} passed, {FAIL} failed\n{'='*40}")
# Guarded so an accidental `pytest tests/` collects this module instead of
# dying on SystemExit during import.
if __name__ == "__main__":
    sys.exit(1 if FAIL else 0)
