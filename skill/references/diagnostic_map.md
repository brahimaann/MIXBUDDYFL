# Diagnostic Map

Metric -> diagnosis -> action lookup. Use this to translate MCP JSON output into
recommendations. All values are **starting points**; tell the user to fine-tune
by ear.

---

## From `analyze_loudness`

| Reading | Diagnosis | Action |
|---------|-----------|--------|
| integrated_loudness_lufs > -9 | Very loud / likely over-compressed for streaming | Pull master gain down; check for limiting artifacts. Streaming normalizes to ~-14 LUFS anyway. |
| -14 +/- 1 LUFS | On target for Spotify/Apple/YouTube | Good. Focus on tonal balance. |
| -14 to -18 LUFS | Slightly quiet for "loud" genres, fine for dynamic ones | Optional: gentle bus compression + limiter to taste. |
| < -20 LUFS | Quiet master | Add gain staging; if peaks already near 0 dBFS, use a limiter before the gain to avoid clipping. |

Target gain to hit a goal: `gain_dB = target_LUFS - integrated_LUFS`. If adding
that gain pushes true peak above -1 dBFS, put a limiter last.

---

## From `analyze_dynamics`

| Reading | Diagnosis | Action |
|---------|-----------|--------|
| crest_factor_db > 18 | Very spiky transients (uncontrolled vocal/drums) | Compress firmly: ~4:1, fast-ish attack (5-10 ms), medium release (80-150 ms). |
| crest_factor_db 12-18 | Moderately dynamic | 3:1, 10-20 ms attack, 100-150 ms release, 3-6 dB gain reduction. |
| crest_factor_db < 10 | Already controlled / dense | Light glue only (1.5-2:1) or none. Don't over-compress. |
| dynamic_range_db > 12 | Big loud/quiet swings | Consider automation + compression, or two-stage (slow leveler then fast peak). |

Use the tool's `compression_suggestion` block as the starting ratio/attack/
release, then adjust: faster attack = more transient control (less punch);
slower attack = more punch (less control). Set release so the meter returns to
0 by the next phrase/beat.

---

## From `analyze_frequency_spectrum`

For each entry in `resonances`:

| classification | Meaning | Action |
|----------------|---------|--------|
| low-end rumble/boom | Sub buildup, proximity, handling noise | High-pass; narrow cut at the flagged freq. |
| mud | 200-500 Hz congestion | Cut at flagged freq, Q ~1.0-2.0, by ~suggested_attenuation_db. |
| boxiness | 500-800 Hz "cardboard" | Narrow cut at flagged freq. |
| presence | Harsh upper-mid peak | Dynamic EQ or gentle static cut; don't kill all presence. |
| natural sibilance | 4-10 kHz harsh "S" | De-esser at the flagged freq (dynamic), not a static cut. |
| synthetic sibilance/air | 10-16 kHz harshness | Dynamic high shelf or de-esser; preserve air. |

Compare `frequency_bands` energies for overall balance: a band much hotter than
its neighbors is a candidate for subtractive EQ. Low `spectral_centroid_hz`
(< ~1.5 kHz for a full mix) = dull; very high = harsh/thin.

---

## From `analyze_vocal_clarity`

| Reading | Diagnosis | Action |
|---------|-----------|--------|
| mud_index > 5 | Vocal is muddy/boxy | Cut ~300-400 Hz (use the suggestion's freq), Q ~1.0. |
| clarity_score < 0.6 | Vocal lacks presence / buried | Cut mud first, then boost 2.5-3 kHz by 1.5-3 dB. |
| sibilance_index > 6 | Harsh "S"/"T" sounds | De-ess at ~5-8 kHz (dynamic), threshold to taste. |
| fundamental_warmth_db very low | Thin vocal | Ease off the high-pass or add a small 150-250 Hz bump. |

Always apply the tool's `eq_suggestions` in order: high-pass -> mud cut ->
presence boost -> de-ess. Subtractive before additive.

---

## From `analyze_stereo_compatibility`

| Reading | Diagnosis | Action |
|---------|-----------|--------|
| overall_correlation > 0.5 | Healthy, mono-safe | No action. |
| 0 to 0.5 | Wide / partly uncorrelated | Fine for FX/wide elements; verify it still sounds right in mono. |
| < 0 (negative) | Out of phase, will cancel in mono | Check polarity; flip one channel; align timing. |
| sub_bass_cancellation_risk = vulnerable | Lows cancel in mono | Sum everything below ~120 Hz to mono (mono-maker / utility). |
| interchannel_time_delay_ms != ~0 | Timing offset between L/R (comb filtering) | Nudge the lagging channel by the reported ms to realign. |

---

## Reference cleanup chain order (general "fix my mix")

1. **Gain staging** - get levels sane (peaks not clipping, healthy RMS).
2. **Loudness** - note where you are vs target; don't maximize yet.
3. **Stereo/phase** - fix polarity and sub-bass mono first (foundation).
4. **Subtractive EQ** - remove mud/boxiness/resonances (clean).
5. **Dynamics** - compress for control and consistency.
6. **Additive EQ** - presence and air (enhance).
7. **FX** - reverb/delay for depth (last).
8. **Re-check** - re-run analysis to confirm the numbers moved the right way.
