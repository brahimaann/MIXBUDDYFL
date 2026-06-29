"""
Demo: simulate the full mixing-assistant workflow on a synthetic "muddy vocal".

Generates a realistic-ish vocal-like signal with a deliberate mud problem and a
sibilance problem, runs the DSP analysis the skill would call via MCP, and
prints the diagnosis + recommendations the skill would synthesize.

This is a human-readable smoke test of the end-to-end value, not a unit test.
"""
import os
import sys
import tempfile

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))
import dsp  # noqa: E402

FS = 44100


def make_muddy_vocal():
    """Vocal-like: fundamental + harmonics, heavy mud at ~320 Hz, harsh 7 kHz."""
    t = np.arange(int(4.0 * FS)) / FS
    # Wobble the fundamental a little so it reads like a voice, not a tone.
    f0 = 180 + 5 * np.sin(2 * np.pi * 5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / FS
    voice = (
        0.4 * np.sin(phase)
        + 0.25 * np.sin(2 * phase)
        + 0.15 * np.sin(3 * phase)
    )
    mud = 0.45 * np.sin(2 * np.pi * 320 * t)       # the problem: mud buildup
    sibilance = 0.2 * np.sin(2 * np.pi * 7000 * t) # the problem: harsh "S"
    # Amplitude envelope (phrasing) to create dynamics.
    env = 0.5 + 0.5 * (np.sin(2 * np.pi * 0.8 * t) > 0)
    sig = (voice + mud + sibilance) * env
    sig = (sig / np.max(np.abs(sig)) * 0.7).astype(np.float32)
    path = os.path.join(tempfile.gettempdir(), "_demo_muddy_vocal.wav")
    sf.write(path, sig, FS)
    return path


def main():
    path = make_muddy_vocal()
    audio = dsp.load_audio(path)

    print("=" * 64)
    print("USER: \"How can I make this vocal clearer? It sounds muddy.\"")
    print(f"FILE: {path}")
    print("=" * 64)

    # Skill maps intent -> these tools.
    clarity = dsp.analyze_vocal_clarity_metrics(audio.mono, audio.sample_rate)
    spectrum = dsp.detect_resonances_metrics(audio.mono, audio.sample_rate)
    dynamics = dsp.analyze_dynamics_metrics(audio.mono, audio.sample_rate)
    loud = dsp.integrated_loudness_lufs(audio.mono, audio.sample_rate)

    print("\n--- RAW ANALYSIS (what the MCP tools return) ---")
    print(f"Loudness: {loud:.1f} LUFS")
    print(f"Clarity: score={clarity['clarity_score']} mud_index={clarity['mud_index']} "
          f"sibilance_index={clarity['sibilance_index']}")
    print(f"Crest factor: {dynamics['crest_factor_db']} dB")
    print("Top resonances:")
    for r in spectrum["resonances"][:4]:
        print(f"  {r['frequency_hz']} Hz  +{r['excess_db']} dB  [{r['classification']}]  "
              f"-> cut {r['suggested_attenuation_db']} dB")

    print("\n--- SYNTHESIZED RECOMMENDATION (what the skill says) ---")
    print("Diagnosis:")
    if clarity["mud_index"] > 5:
        print(f"  - Muddy: low-mid buildup (mud_index {clarity['mud_index']}/10).")
    if clarity["clarity_score"] < 0.6:
        print(f"  - Buried: presence is weak relative to mud (clarity {clarity['clarity_score']}).")
    if clarity["sibilance_index"] > 6:
        print(f"  - Harsh: sibilance present (index {clarity['sibilance_index']}/10).")

    print("\nDo this (in order):")
    for i, s in enumerate(clarity["eq_suggestions"], 1):
        if s["action"] == "high_pass" or s.get("type") == "high_pass":
            print(f"  {i}. High-pass at {s['frequency_hz']:.0f} Hz "
                  f"({s.get('slope_db_oct','')} dB/oct) - remove rumble/boom.")
        elif s["action"] == "cut":
            print(f"  {i}. Cut {s['frequency_hz']:.0f} Hz by {s['gain_db']} dB "
                  f"(Q {s.get('q')}) - {s['description']}")
        elif s["action"] == "boost":
            print(f"  {i}. Boost {s['frequency_hz']:.0f} Hz by {s['gain_db']} dB "
                  f"(Q {s.get('q')}) - {s['description']}")
        elif s["action"] == "de-ess":
            print(f"  {i}. De-ess at {s['frequency_hz']:.0f} Hz "
                  f"({s['threshold_reduction_db']} dB) - {s['description']}")

    cs = dynamics["compression_suggestion"]
    print(f"  {len(clarity['eq_suggestions'])+1}. Compress: {cs['suggested_ratio']}, "
          f"attack {cs['suggested_attack_ms']} ms, release {cs['suggested_release_ms']} ms "
          f"for ~3-6 dB GR.")

    print("\nListen for: vocal sitting on top of the beat without raising its fader;")
    print("no boxiness; 'S' sounds smooth, not piercing.")

    os.remove(path)

    # Sanity: the demo must actually have detected the planted problems.
    ok = clarity["mud_index"] > 5 and any(
        abs(r["frequency_hz"] - 320) < 40 for r in spectrum["resonances"]
    )
    print("\n" + ("DEMO OK: planted mud problem detected." if ok
                  else "DEMO WARN: planted problem NOT detected!"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
