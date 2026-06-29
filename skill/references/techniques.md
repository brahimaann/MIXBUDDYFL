# Mixing Techniques

Practical recipes and chain orders distilled from professional tutorials
(pop, hip-hop, Afro-beat vocal mixing) and standard engineering practice.
Use alongside `diagnostic_map.md` and `frequency_guide.md`.

---

## Standard Vocal Chain (order matters)

The signal flows top to bottom. This order is near-universal across the
tutorials:

1. **Clean-up / gain staging** - trim silence, remove breaths/noise between
   phrases, set input around -18 dBFS average.
2. **Tuning** (if used) - Autotune/Melodyne. Tune before heavy compression so
   the tuner tracks pitch cleanly.
3. **Subtractive EQ** - high-pass (80-120 Hz), cut mud (250-400 Hz), tame
   boxiness (500-800 Hz). Remove problems before adding anything.
4. **Compressor 1 (leveler)** - gentle, catches the loud words. e.g. 2-3:1,
   slow-ish attack, 3-6 dB reduction. (1176-style or LA-2A-style.)
5. **Compressor 2 (optional, control)** - faster, for consistency on dynamic
   rap/pop vocals. Stacking two light compressors sounds more natural than one
   heavy one.
6. **De-esser** - tame 5-8 kHz sibilance dynamically.
7. **Additive / tone EQ** - presence boost (3 kHz), air shelf (10-12 kHz).
8. **Saturation** (optional) - subtle harmonic excitement / "expensive" sheen.
9. **Time FX (sends)** - reverb and delay on aux sends, not inserts, so you
   control the wet level independently.

> Tip from the tutorials: pros often "subtract to clean, then add to flavor."
> Resonance-suppression tools (e.g. Soothe-style dynamic resonance reducers)
> sit around step 3/6 to automatically tame harshness and mud.

---

## Compression Starting Points by Source

| Source | Ratio | Attack | Release | Notes |
|--------|-------|--------|---------|-------|
| Lead vocal (pop) | 3-4:1 | 10-20 ms | 100-150 ms | 3-6 dB GR; consider two stages. |
| Rap vocal | 4:1+ | 5-10 ms | 80-120 ms | Tighter control for consistency/energy. |
| Backing vocals | 2-3:1 | 15 ms | 150 ms | Glue them, then pull back in the mix. |
| Acoustic guitar | 2-3:1 | 20-30 ms | 150 ms | Slow attack preserves pick attack. |
| Drum bus | 2-4:1 | 10-30 ms | auto/100 ms | Attack controls punch. |
| Master/mix bus | 1.5-2:1 | slow | auto | 1-2 dB GR max for glue. |

Rule of thumb: **faster attack = more transient control but less punch;
slower attack = more punch; release short enough to recover before the next
hit, long enough to avoid pumping.**

---

## Recipe: "Make my vocal clearer / cut through"

1. High-pass at 80-120 Hz (removes mud foundation).
2. Cut 250-400 Hz by 2-4 dB, Q ~1.0 (the #1 cause of "muddy" vocals).
3. If boxy, narrow cut 500-700 Hz.
4. Boost 2.5-3 kHz by 1.5-3 dB (intelligibility / "in front of the beat").
5. Gentle air shelf +1.5-3 dB from 10-12 kHz.
6. Make sure the vocal level sits 1-3 dB above the busiest part of the beat.
7. Carve the **instrumental** to make room: a small 2-4 kHz dip on the beat
   (dynamic/side-chained to the vocal) opens a pocket so the vocal sits without
   pushing its level too high.

---

## Recipe: Compression help ("what settings?")

1. Run `analyze_dynamics`. Read crest_factor_db.
2. Start from the suggested ratio/attack/release.
3. Set threshold for 3-6 dB of gain reduction on the loudest words.
4. Match output level so bypass A/B is fair (loud always sounds "better").
5. Listen: pumping? lengthen release. Lost punch? slow the attack. Still
   uneven? add a second gentle compressor rather than pushing one harder.

---

## Recipe: Higher, airier, "floaty" vocal (Brent Faiyaz-style)

Be honest with the user: this sound is mostly **performance + arrangement +
the beat**, with mix moves on top. The mix techniques that get closest:

1. **Pitch up tastefully** - shift the vocal up a few semitones, OR layer a
   formant-shifted/pitched-up double under the lead. In a pitch tool
   (Melodyne, Little AlterBoy, FL Pitcher), raising **formant** separately from
   **pitch** gives that lighter, airier timbre without chipmunk artifacts.
2. **Pitched/octave-up doubles** - a quiet +12 (octave) or +5 harmony layer,
   panned and tucked low, adds shimmer and that ethereal stack.
3. **Heavy lush reverb + 1/4 or dotted-1/8 delay** on sends for the dreamy,
   spacious feel. Filter the reverb (high-pass ~300 Hz, low-pass ~8 kHz) so it
   stays clean.
4. **Air boost** - high shelf +2-4 dB from 10-12 kHz for breathy top.
5. **Saturation/exciter** - subtle, to add harmonics and sheen.
6. **Slight slowdown / detune layers** for the smooth, woozy R&B vibe.
7. **De-ess after pitching up** - pitching up exaggerates sibilance.

Technique check via tools: after pitching, run `analyze_vocal_clarity` to catch
new sibilance, and `analyze_frequency_spectrum` to confirm you added air
without harshness (watch spectral_centroid creeping too high).

---

## Recipe: Match a reference track

1. `compare_to_reference(target, reference)`.
2. First fix the **loudness_differential_lu** mentally (don't chase loudness
   with EQ).
3. Walk the `spectral_difference` bands: boost where you're below, cut where
   you're above, in small moves (1-2 dB).
4. Re-run to confirm convergence. Stop when bands are within ~1.5 dB and it
   sounds right. The goal is the *vibe*, not an identical curve.

---

## Things the pros stress (from the tutorials)

- **Get your tempo / timing right first** - everything downstream depends on it.
- **Gain staging before plugins** - feed processors a healthy, not hot, signal.
- **Use your ears, not just the meters** - the song, arrangement and performance
  matter more than any single setting.
- **Solo to find problems, but decide in context** (with the full mix playing).
- **Reference often** - compare to a pro track at matched loudness.
- **Less is more** - subtractive cleanup beats piling on boosts and effects.
