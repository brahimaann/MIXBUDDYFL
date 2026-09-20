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

### What commercial releases actually measure

-14 LUFS is the *streaming normalization* reference, not what hit records are
mastered to. A survey of 120 Billboard Year-End Hot 100 singles (Tint &
Dragulin 2025) measured:

| Decade | Integrated loudness | PLR (dynamics) |
|---|---|---|
| 1990 | -12.5 LUFS | 12.6 LU |
| 2000 | — | 10.6 LU |
| 2010 | **-8.0 LUFS** (loudness-war peak) | 9.3 LU |
| 2020 | **-8.8 LUFS** | 9.3 LU |

All-decade mean: -9.7 LUFS. Use these when a user asks "is my master
competitive?" — a modern pop/hip-hop master landing near -9 LUFS with a PLR
around 9 LU is normal, not broken, even though streaming will turn it down.
Tell them the tradeoff (density vs. dynamics) rather than enforcing -14.

### From `plr_lu` (peak-to-loudness ratio)

| Reading | Diagnosis | Action |
|---|---|---|
| < 8 LU | Very dense — heavily limited/clipped | Fine for aggressive genres; check for pumping and lost transients. |
| 8-11 LU | Typical of modern commercial masters | No action. |
| > 12 LU | Dynamically open (1990s-like, or unmastered) | Appropriate for acoustic/classical; if the goal is competitive loudness, there's room. |

PLR contextualises loudness: it separates "loud because it's dense" from
"loud because it's well balanced." Two masters at the same LUFS with PLRs of
7 and 12 are completely different records.

**Tonal balance has drifted too:** across the same dataset, 2020 productions
carry the most low and low-mid energy and the least high end, while 1990
productions had the least low end and the most high-mids. If a user's
reference is a recent hit, expect a darker, bass-heavier target curve than
older material.

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

**Prefer `harmonic_centroid` over `spectral_centroid_hz` when judging the
brightness of a single pitched source.** Raw centroid conflates "bright" with
"high-pitched" - a bass and a vocal with identical harmonic structure produce
completely different raw centroids. The harmonic centroid (centroid / f0,
Hermes 2017) expresses brightness in harmonics and is comparable across
sources. It is `null` for unpitched material and full mixes; fall back to the
raw centroid there.

**Known limitation - very broad low-frequency humps.** The resonance detector
finds peaks that stand out from a local baseline, so a *broad* (~2 octave)
buildup centred around 200 Hz is invisible to it: there isn't enough spectrum
below it to establish a baseline. Broad humps from ~800 Hz up are detected.
If a user reports boom or mud and `analyze_frequency_spectrum` reports no
resonance, do not conclude the low end is fine - compare `frequency_bands`
energies, or use `compare_to_reference`, which catches broad tilt by design.

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

## From `analyze_noise_gate`

| Reading | Diagnosis | Action |
|---------|-----------|--------|
| gaps_detected_count = 0 | No clear pauses found, or already silent between phrases | Nothing to gate. |
| breath_bleed_detected = true | Gap level sits well above the true noise floor and well below the phrase level - breath/room noise/hiss is leaking through the pauses | Apply `gate_suggestion` (threshold/ratio/range/attack/hold/release); if `sidechain_highpass_hz` is set, high-pass the gate's *detector*, not the audio. |
| breath_bleed_detected = false, gaps_detected_count > 0 | Gaps already close cleanly | No gating needed; don't add one just because the tool ran. |
| gate_suggestion.release_ms close to median_gap_duration_ms | Release barely fits inside the gap - risk of not fully closing before the next phrase | Favor the shorter end of the suggested range. |

The single most common fix for "breath bleeding through between phrases" is
release time, not threshold - see `gating_and_expansion.md` for the full
diagnostic order (release -> range/ratio -> sidechain filter -> threshold
last) and why threshold-first tends to clip quiet word onsets instead of
fixing the actual leak.

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

## Before you reach for any of this

Every table above prescribes *processing*. Check first whether the problem is
balance, panning or arrangement — "muddy", "buried", "cluttered" and "not
wide enough" usually are. A fader move, a pan move or muting a competing part
beats a filter, costs nothing, and can't introduce artifacts. See
`static_mix_workflow.md`.

Also note: a well-balanced full mix on an analyzer is **not a flat line**. It's
a gently sloping curve from around 60 Hz falling toward the top end. Don't
push a user toward a flat spectrum.

---

## Reference cleanup chain order (general "fix my mix")

1. **Gain staging** - get levels sane (peaks not clipping, healthy RMS).
2. **Gate/expand** - close up breath/noise between phrases before anything
   else amplifies it (compression in particular will pull noise floor up).
3. **Loudness** - note where you are vs target; don't maximize yet.
4. **Stereo/phase** - fix polarity and sub-bass mono first (foundation).
5. **Subtractive EQ** - remove mud/boxiness/resonances (clean).
6. **Dynamics** - compress for control and consistency.
7. **Additive EQ** - presence and air (enhance).
8. **FX** - reverb/delay for depth (last).
9. **Re-check** - re-run analysis to confirm the numbers moved the right way.
