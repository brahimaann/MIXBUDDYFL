# Mixing Techniques

Practical recipes and chain orders distilled from professional tutorials
(pop, hip-hop, Afro-beat vocal mixing) and standard engineering practice.
Use alongside `diagnostic_map.md` and `frequency_guide.md`.

---

## Standard Vocal Chain (order matters)

The signal flows top to bottom. This order is near-universal across the
tutorials:

1. **Clean-up / gain staging** - trim silence, gate/expand breath noise
   between phrases (see `gating_and_expansion.md` if it's bleeding through),
   set input around -18 dBFS average.
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

## Chain-Order Refinements (cross-confirmed across sources)

These sharpen the generic chain above. Each one showed up in more than one
professional walkthrough, which is why they're here rather than as one
engineer's preference.

- **Ride levels by hand before the compressor.** Gain-automate the phrases
  even *first*; the compressor then works less hard and reads as natural
  rather than squashed. See `static_mix_workflow.md`.
- **Subtractive EQ before compression, additive EQ after.** Cutting first
  stops the compressor reacting to problems you're about to remove; boosting
  after means the compressor isn't amplifying your boost.
- **De-ess twice, for two different reasons.** Once in the subtractive stage
  (before compression), and again *after* compression — compression pulls the
  sibilance back up, so the S's you already tamed return. This is separate
  from the two-band de-ess idea (sibilance ~8-10 kHz plus a 2 kHz "de-honk").
- **Set a de-esser's Range, not just its threshold.** Most de-esser defaults
  overdo it; limiting maximum attenuation to ~5 dB (3 dB on a bright vocal)
  keeps it natural. More than that gives the singer a lisp.
- **Many small stages beat one big one.** Compressor → different-style
  compressor → EQ → de-esser → de-esser at another frequency → compressor,
  each doing a little. Cheese runs a dozen light stages on a lead; Decker
  stacks a leveler and a peak stage. One heavy processor always sounds more
  processed than several gentle ones.
- **Doubles get the inverse EQ of the lead.** Pull down the bands you pushed
  up on the lead so the two carve a pocket for each other instead of stacking
  in the same place.
- **Ad-libs get the "telephone" treatment** — aggressive high-pass (~300 Hz)
  and often a high cut too, so the lead stays the brightest thing in the mix.
  Hit their ratio harder as well; ad-libs are more dynamic than leads.
- **Parallel compression on leads only**, not on doubles or stacks. Extreme
  settings (fast attack, fast release, all-buttons-in), mix knob at
  **5-10%** — barely there, but it holds the vocal in your face while the dry
  signal stays dynamic.
- **A limiter on the vocal bus** catching just the very peak tips is a
  finishing move, not a crutch.
- **Autotune retune speed is genre-dependent**: fast/hard (around 6, with a
  touch of humanize) for the deliberately-tuned Afrobeat sound; slow (around
  25, tracking ~25) for a natural pop lead. Find the song's key first and set
  the scale; let individual notes in per-channel where a harmony sits outside
  the scale. No autotune on ad-libs or spoken phrases.

---

## Saturation Stacking

Rather than one saturator on the master, put a light stage on **each bus** and
again on the mix bus — e.g. tape emulation per bus (a slower speed like 15 IPS
gives a bigger low end; 30 IPS is tighter) plus a console emulation on top.

Why it works: each group gets its own cohesion from sharing a saturation
stage, and the stages compound into perceived depth — the mix reads "taller,
wider, deeper" and loses the brittle, glassy digital quality. Drive each one
gently; it's seasoning, not an effect.

Diminishing returns are real, and it's genre-dependent — a deliberately clean,
tight EDM record may want none of it. A/B with your eyes closed.

---

## Compressor vs Limiter vs Clipper

| Tool | What it does to a transient |
|---|---|
| **Compressor** | Squeezes it down according to the ratio. |
| **Limiter** | The same thing at a very high ratio — almost nothing gets past. |
| **Clipper** | **Saws the top off** rather than turning it down. |

Clipping isn't inherently bad — it's very effective on transients, and a
clipper into a limiter is a standard modern loudness chain. Controlling drum
transients with a clipper at the mix stage makes the master easier later.

---

## Named Recipe: Decker's Template Vocal Chain

A concrete, numbers-first alternative to the general chain above, distilled
from Billy Decker's *Template Mixing and Mastering*. Useful when the user
wants a fixed starting chain to dial in rather than a set of general
principles - copy the lead vocal to a second, identical channel (see below)
rather than varying settings per take.

1. **Levelling compressor** (1176/76-style, or any "leveler"): input -27,
   output -18, slow attack, fast release, 4:1 ratio. This rides the overall
   level the way a mix engineer's fader hand would, before anything else
   touches the signal. Expect 10-20 dB of gain reduction - levelers are
   *meant* to be worked hard, unlike a peak-limiting compressor.
2. **Channel strip** (compressor + filter + 4-band EQ): peaks only, up to 3 dB
   max reduction. High-pass rumble, narrow cut on the muddy problem area,
   then a touch of high-end air. Narrow Q when cutting, wider Q when boosting.
3. **Vocal multi-effect / de-esser stage 1**: 8-10 kHz, up to 3 dB
   attenuation max - more than that gives the singer a lisp. Sweep a boosted
   narrow EQ through 8-10 kHz first if you're not sure exactly where the
   "esses" live, then de-ess there.
4. **De-esser stage 2 ("de-honk")**: fixed at 2 kHz, up to 3 dB max - tames
   nasal quality that stage 1 doesn't touch.
5. **Cloned lead vocal channel**: duplicate the entire chain above onto a
   second channel driven by the *same* take, both centre-panned, both fed to
   the same busses. Any setting changed on one must be mirrored on the other
   - the two are meant to reinforce, not to be two different performances (a
   double-tracked vocal is a different, separate technique - a second real
   take, usually panned apart, not this). Check the clone is truly identical
   by inverting the polarity of one channel with sends muted: if they're
   identical, the vocal disappears completely (a null test). Any residue
   means something differs between the two chains.

Two de-essers in series, targeting different frequencies, is deliberate: one
catches literal sibilance (8-10 kHz), the other catches the separate nasal/
honky quality that shows up around 2 kHz on many voices.

---

## Named Recipe: Decker's Gain-Staging Method ("kissing the threshold")

A visual, non-metering way to gain-stage before mixing, so every compressor's
fixed threshold gets fed the right level without ever touching the threshold
itself:

1. Set every compressor's threshold once and never move it again per-song.
2. For each track, use the clip-gain tool (not the fader) to raise or lower
   the *source audio* until its average waveform energy fills about 50% of
   the visual track height - a quarter of empty space above and below.
3. Watch the loudest transient peaks: they should just barely poke above the
   threshold line ("kissing" it), producing no more than ~3 dB of gain
   reduction on that one stage. Several stages each doing 2-3 dB adds up to
   serious cumulative control without any single stage killing the
   performance.
4. If a track wildly swings between quiet and loud sections and that swing
   isn't musically intentional, split the clip and gain-stage each section
   separately before re-checking the 50% rule across the whole track.

This turns "what threshold should I use?" into "is my input level right?" -
useful when a plugin's threshold is fixed or when you want every song to hit
the same chain the same way without re-tuning it each time.

---

## Named Recipe: A Complete Master-Channel Chain

A minimal, mix-preserving master chain (Decker's template; consistent with
the loudness-target guidance in `diagnostic_map.md`):

1. **EQ - HP/LP only by default.** High-pass ~30-35 Hz, low-pass ~20 kHz.
   Nothing else unless referencing against a commercial mix reveals a genuine
   tonal gap - mastering EQ is a last resort, not a default move, and any
   change here affects every instrument in that band at once.
2. **Buss compressor.** 2:1 ratio, fastest decay, for general glue; 3:1-4:1
   only for a deliberately tighter/more aggressive sound (rock, aggressive
   genres). Aim for the mix to just "kiss" the threshold - no more than ~1 dB
   of gain reduction for glue.
3. **Warmth/multiband stage (optional).** A second, parallel-mixed buss
   compressor (~35% wet) plus subtle valve/tape saturation (~35% wet) gets
   most of the way to a dedicated all-in-one mastering processor if you don't
   have one - the point is added punch and warmth blended back with the
   unprocessed signal, not more raw gain reduction.
4. **Peak limiter/maximizer.** Output ceiling around -0.1 dB, no more than
   ~1 dB of gain reduction. This is the loudness stage - see `diagnostic_map.md`
   for how much is appropriate for the target platform. Bypass or remove this
   stage entirely if the file is headed to a dedicated mastering engineer.

The whole point of a master chain: it should make the mix "a little wider,
deeper, and louder" - nothing more. If a change here shifts the *balance* of
the mix (an instrument suddenly more/less prominent), it's overreaching; pull
it back or fix it in the mix instead.

### Modern variant: clipper into limiter

For contemporary pop/rap/dance, a **clipper into a limiter** replaces (or
precedes) the single peak limiter above:

- **Load the master chain at the start of the mix and mix through it**, so
  nothing changes character at the end. Gain-stage the mix down to give the
  clipper ~3 dB to work with rather than driving its input.
- **Leave the clipper's ceiling off** — the limiter sets the final ceiling.
- **Saturation is the loudness key.** It doesn't raise metered loudness, it
  makes the track *feel* louder, which is how you get level without crushing.
- Limiter behaviour worth knowing: **slower attack sounds more open** but
  introduces more harmonic saturation; **slower release masks how squashed**
  it is; **transient link** all the way up lets drums take precedence over
  vocals, so back it toward ~50-60% to let vocals breathe.
- Check the **spectrogram** for retained hills and valleys — loud without
  obliterated dynamic range.

**Loudness targets are genre-dependent.** `diagnostic_map.md` treats ~-14 LUFS
integrated as the streaming reference, and that's right for most material, but
a modern pop/rap master is commonly ridden to around **-7 to -8 LUFS
short-term during the loudest section**. Streaming normalization will turn it
down; the point is the density and impact, not the meter. Tell the user the
tradeoff rather than enforcing one number.

---

## Mix/Master Frequency Coordination

When both a mix-stage presence boost and a mastering-stage de-harshing move
exist in the same signal path, centre them on *different* frequencies so they
don't cancel each other out or fight over the same band - e.g. a mix-stage
vocal presence boost around 3 kHz paired with a mastering-stage harshness cut
around 3.5 kHz. Keep at least a few hundred Hz of separation between any
mix-stage boost and a mastering-stage cut that could otherwise land on top of
it and quietly undo the earlier move.

---

## Things the pros stress (from the tutorials)

- **Get your tempo / timing right first** - everything downstream depends on it.
- **Gain staging before plugins** - feed processors a healthy, not hot, signal.
- **Use your ears, not just the meters** - the song, arrangement and performance
  matter more than any single setting.
- **Solo to find problems, but decide in context** (with the full mix playing).
- **Reference often** - compare to a pro track at matched loudness.
- **Less is more** - subtractive cleanup beats piling on boosts and effects.
