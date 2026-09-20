# Frequency Guide

A map of the audible spectrum for mixing decisions. Use these ranges to
interpret `analyze_frequency_spectrum` and `analyze_vocal_clarity` output and to
explain recommendations in plain language.

## The Ranges

| Range | Name | What lives here | Too much sounds | Too little sounds |
|-------|------|-----------------|-----------------|-------------------|
| 20-60 Hz | Sub-bass | Rumble, 808 sub, kick body | Boomy, muddy, eats headroom | Thin, no weight |
| 60-200 Hz | Bass / low-end | Bass fundamentals, kick, vocal warmth root | Boomy, undefined | Weak, small |
| 200-500 Hz | Low-mids / **MUD** | Vocal body, guitar body | Muddy, boxy, congested | Hollow, thin |
| 500-800 Hz | **BOXINESS** | Lower mids of most sources | Boxy, "cardboard", honky | Lacks body |
| 800 Hz-2 kHz | Mids | Vocal intelligibility, attack | Nasal, "telephone", honky | Distant, dull |
| 2-5 kHz | **PRESENCE** | Vocal clarity, consonants, edge | Harsh, fatiguing, "in your face" | Buried, dull, muffled |
| 5-9 kHz | **SIBILANCE** | "S", "T", "SH" sounds, cymbals | Harsh, "essy", piercing | Lispy, dull |
| 9-12 kHz | Brilliance | Crispness, detail | Brittle, harsh | Lacks detail |
| 12-20 kHz | **AIR** | Sheen, openness, "expensive" top | Hissy, fatiguing | Closed, dull, dark |

## Vocal-Specific Landmarks

- **Fundamental of a male vocal:** ~85-180 Hz
- **Fundamental of a female vocal:** ~165-255 Hz
- **High-pass vocals:** 80-100 Hz (male), 100-120 Hz (female) to remove rumble
  and proximity boom. Steeper slope (18-24 dB/oct) cleans more aggressively.
- **Mud cleanup:** narrow-to-medium cut around 250-400 Hz
- **Boxiness:** cut around 500-800 Hz
- **Intelligibility / "cut through":** boost 2.5-4 kHz
- **Presence / "air":** high shelf from 10-12 kHz up
- **De-ess target:** typically 5-8 kHz (find the exact frequency of the harsh
  "S" first, then attenuate dynamically)

## How the analyzer indices map here

- `mud_index` high -> energy piled up in 200-500 Hz -> subtractive EQ there.
- `sibilance_index` high -> energy in 5-9 kHz -> de-ess, don't just static-cut.
- `clarity_score` low -> presence (2-5 kHz) weak relative to mud -> cut mud
  first, then gently boost presence.
- `spectral_centroid_hz` low -> dark/dull mix; high -> bright/harsh mix.

## Mental model (from David Gibson's visual framework)

Picture the mix as a 3D space: left-right (pan), front-back (level + reverb),
and bottom-top (low to high frequency). A clean mix gives each element its own
spot in all three dimensions so nothing masks anything else. Most "muddy mix"
problems are two sources fighting for the same frequency + pan position.

**The space is finite, and that's the whole point.** Imaging doesn't extend
past the speakers, more than a short distance in front of or behind them, or
above them (lows do come up through the floor). Everything has to fit in that
box, so mixing is **crowd control**. See `stereo_and_space.md` for the shapes
each element occupies and what that implies for masking.

### The six volume levels

A practical way to think about front-to-back placement. Levels are relative,
and every genre has its own traditions:

| Level | What lives there |
|---|---|
| 1 | Almost never used - explosions, primal screams. Usually a mistake. |
| 2 | Lead vocals in MOR / big band / folk / country / opera; the boom in rap; kick in heavy metal. |
| 3 | Primary rhythm parts; lead vocals in a lot of rock; snare in dance music. |
| 4 | Rhythm beds and pads, background vocals, strings, drums in jazz/easy rock; audible reverb. |
| 5 | Kick in jazz/big band; effects and reverb you only notice if you listen for them. |
| 6 | Barely detectable - whispers, subliminal texture. |

Useful patterns: the kick has climbed the scale over decades (level 4-5 in
jazz -> level 2 in metal -> effectively off the top in rap/hip-hop). **The
fewer instruments in a mix, the louder the bass can be** - a busy mix has no
room for it, and bass masks more than anything else.

Genres also differ in *spread*: some are mixed with a narrow gap between the
quietest and loudest element (new age, alt-rock, country, easy rock), others
deliberately wide (rock, big band). Match the song.

### Two techniques from this framework

- **Scan the spectrum across the whole mix, band by band.** First compare the
  relative brightness of *every* element, then the mids, then the bass. The
  bass pass is the one most commonly skipped - explicitly compare how much low
  end the kick has versus the bass guitar.
- **The establish-then-lower trick.** Bring an element up loud and clear early
  so the listener registers what it's doing, then set it back down. The brain
  keeps tracking it. Do this with several elements and the mix reads as though
  everything is loud and clear at once.

**Judge apparent volume, not fader position.** A chainsaw and a flute at
identical meter readings are nowhere near the same perceived loudness.
