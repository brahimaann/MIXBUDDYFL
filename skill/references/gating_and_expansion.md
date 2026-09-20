# Noise Gates and Expanders

Use alongside `diagnostic_map.md` (metric -> action) and `techniques.md`
(chain order). This file covers the one dynamics tool the other two don't:
gates/expanders, and specifically the "breath noise bleeds through between
phrases" problem.

---

## Theory (what a gate/expander actually does)

A **compressor** turns down what's *above* its threshold. An **expander** is
the mirror image: it turns down what's *below* its threshold. Ratio works the
same way in both directions - a 2:1 expander turns a 1 dB drop below
threshold into a 2 dB drop in the output; push the ratio high enough (~10:1
or more) and it behaves like a **gate**, snapping shut instead of tapering.

Every gate/expander shares the same core controls:

| Control | What it does | Symptom if wrong |
|---|---|---|
| **Threshold** | Level the signal must clear to stay open | Too high: chops word starts / clips consonants. Too low: doesn't close, noise leaks through. |
| **Ratio** | How hard it turns down below threshold (2:1 gentle expander -> 10:1+ hard gate) | Too low: residual noise still audible when "closed." Too high: abrupt, unnatural cutoff. |
| **Range** | The *maximum* attenuation applied when fully closed (dB) | Too shallow (e.g. 15 dB): noise is only turned down, not removed. Too deep with a fast release: can sound like the track is cutting out. |
| **Attack** | How fast it opens once threshold is crossed | Too slow: clips the front of words/transients. |
| **Hold** | Minimum time to stay open once triggered | Too short: chatters on quick level dips mid-word. |
| **Release** | How fast it closes after the signal drops back below threshold | **Too long is the #1 cause of breath bleeding through** - the gate is still open from the tail of the last word when the singer inhales. |
| **Sidechain filter (HP/LP)** | Band-limits what the *detector* listens to, without filtering the audio itself | No filtering: low rumble or breath's broadband energy keeps re-triggering the gate open. |

Gating is a **volume tool that reduces dynamic range on the quiet end**, the
same way a compressor reduces it on the loud end. It should be inaudible when
set well - if you can hear it operating, it's usually too aggressive, too
slow to close, or missing a soft knee.

---

## Recipe: "Breath noise is bleeding through between phrases"

This is almost never a threshold problem first. Work in this order:

1. **Check release time first.** A long release (500 ms-1 s+, common on
   vocal levelers/multi-effects boxes tuned for musicality) keeps the gate
   open well past the end of a word - right through the inhale. Pull it down
   into the 100-300 ms range and re-check. If `analyze_noise_gate` reports a
   `median_gap_duration_ms`, keep release well under it (the tool's
   `gate_suggestion.release_ms` targets ~30% of the median gap).
2. **Increase Range and Ratio together** if breath is still audible once
   release is fixed. Range controls *how far down* closed gets; a shallow
   range (15-20 dB) leaves quiet breath clearly audible even with the gate
   correctly triggering. Push Range toward 30-40+ dB and Ratio toward 4:1+ for
   firmer suppression, rather than chasing it with Threshold alone (which
   risks clipping soft word onsets instead).
3. **High-pass the sidechain/detector, not the audio.** Breath carries a lot
   of low-frequency energy from proximity/room tone. Filtering the detector
   (not the vocal itself) around 150-200 Hz makes the gate less likely to
   trigger open on breath while staying just as responsive to the vocal's
   higher-energy content. This is a detector-only filter - it should not
   thin out the actual audio passing through.
4. **Only then touch Threshold**, and move it the smallest amount that
   works. Raising it (less negative) risks clipping quiet word starts; the
   goal is the minimum change needed once release/range/ratio/sidechain are
   already doing most of the work.
5. **Soft knee helps if available.** A hard knee gate that's borderline too
   aggressive can sound like the track is chopping; a soft knee (a dB or two
   of transition around threshold) smooths the open/close without giving up
   suppression.

### Using `analyze_noise_gate`

Call it on the vocal file. It measures the actual inter-phrase gaps rather
than guessing:

- `noise_floor_dbfs` - the file's quietest moments (true floor).
- `gap_level_dbfs` - what's actually sitting in the pauses between phrases.
- `breath_bleed_db` = `gap_level_dbfs - noise_floor_dbfs`. Large (>8 dB) means
  something audible (breath, room tone, hiss) is living in the gaps, not true
  silence.
- `breath_bleed_detected` is only `true` when that gap is *also* well below
  the active/phrase level (`active_level_dbfs`) - i.e. it's genuinely a pause
  with residual noise, not just a quiet word getting misread as a gap.
- `gate_suggestion` gives a starting threshold/ratio/range/attack/hold/release
  and, when bleed is detected, a `sidechain_highpass_hz` (150 Hz) - dial these
  in as a first pass, then use the release-time / range-and-ratio order above
  to fine-tune by ear.

If `gaps_detected_count` is 0, there's nothing for a gate to act on (either
the file has no pauses, or it's already silent between phrases).

---

## Standard vocal gate starting points

| Parameter | Starting value | Notes |
|---|---|---|
| Threshold | A few dB above the measured noise floor, well below phrase level | See `analyze_noise_gate`'s `threshold_db`. |
| Ratio | 2:1 (gentle) to 4:1+ (firmer, if bleed persists) | Higher ratio = more suppression of what's below threshold. |
| Range | 20-40 dB | Deeper if breath/noise is still audible once triggering correctly. |
| Attack | 1-5 ms | Fast enough not to clip consonant onsets. |
| Hold | 10-50 ms | Prevents chatter on quick within-word dips. |
| Release | 100-300 ms, and shorter than the gap it needs to close in | The most common fix for bleed - see recipe above. |
| Sidechain HP | 150-200 Hz | Only when low-frequency content (breath, rumble) is falsely triggering the gate open. |

These are starting points to dial in by ear, not fixed rules - a slow ballad
with long pauses tolerates a slower release than a fast, rhythmic vocal where
the next phrase comes in almost immediately.

---

## The gate's other three jobs

Breath bleed is the vocal case, but a gate has three classic uses worth
recognizing when the user describes a different problem:

1. **Kill noise** — amp hiss between phrases on a high-gain guitar, hum, room
   tone. Set the threshold so it closes as soon as the signal decays to where
   the noise is audible, without clipping the tail of the actual part.
2. **Kill bleed** — isolating drum mics from each other. Especially valuable on
   a snare with heavy reverb, where bleed from the rest of the kit gets
   drowned in the reverb tail and turns to mush.
3. **Shorten a sound deliberately** — as an effect, not a repair. Tightening a
   kick's tail is the mild version; **gated reverb** (a gate across a reverb
   return so the tail stops abruptly instead of decaying) is the famous one.

### Alternative: a noise suppressor instead of a gate

A spectral noise suppressor (the NS1-style single-slider kind) is often a
gentler answer than a gate for between-phrase noise on a recorded vocal — it
attenuates the noise floor continuously rather than opening and closing, so
there's no chatter and no threshold to miss. Reach for it when a gate keeps
either clipping word starts or letting breath through, and the noise is
steady-state rather than a discrete event.

---

## When NOT to gate

- **Suno / AI-generated or otherwise synthesized vocal stems** usually have no
  real noise floor to remove - there's nothing between phrases but silence
  already, and an aggressive gate risks stripping quiet consonants and breath
  that were never a problem. Check by ear (or with `analyze_noise_gate` - a
  `breath_bleed_db` near 0 means it's already clean) before reaching for a
  gate on this kind of source.
- **Heavily compressed sources** (parallel-compressed drum busses, already-
  squashed masters) can have their noise floor pulled up by the compression
  itself; gating after heavy compression fights the compressor instead of
  fixing the source. Address it earlier in the chain if possible.
- **Live-room ambience you want to keep** (a natural room tail, audience
  noise, intentional bleed) - a gate set for "clean" will remove exactly the
  character you're trying to preserve. Confirm with the user before defaulting
  to an aggressive gate on anything that isn't a close-mic'd, dry vocal.
