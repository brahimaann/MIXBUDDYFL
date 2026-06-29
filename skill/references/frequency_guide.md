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
