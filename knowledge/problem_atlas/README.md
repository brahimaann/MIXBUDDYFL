# Mix problem atlas

250 mixing and recording problems. Each one maps what people say when they
hear it to its cause, a measurement that confirms it, and a fix that has
worked. It's written for vocal-led rap/R&B made in bedrooms, closets, cars
and laptops, mixed in FL Studio.

mix-buddy searches this atlas with the `lookup_mix_problem` tool when the user
describes a complaint. The atlas gives **candidates**, not verdicts: always
confirm with a measurement or a plugin read before advising.

## Files (25 problems each)

| File | Domain | IDs |
|---|---|---|
| `01-room.md` | Room and recording environment | 001-025 |
| `02-mic-tracking.md` | Microphone and tracking | 026-050 |
| `03-voice.md` | Voice, mouth and articulation | 051-075 |
| `04-low-end.md` | Low and low-mid tone | 076-100 |
| `05-mids-highs.md` | Mid, high-mid and high tone | 101-125 |
| `06-dynamics.md` | Dynamics and transients | 126-150 |
| `07-pitch-timing-stacks.md` | Pitch, timing, doubles and stacks | 151-175 |
| `08-space.md` | Reverb, delay and depth | 176-200 |
| `09-balance-masking.md` | Balance, masking and arrangement | 201-225 |
| `10-levels-translation.md` | Gain staging, loudness, translation, delivery | 226-250 |

## Entry format

```
### 057 Nasal vocal
- **severity:** minor | major
- **says:** "sounds nasal", "through the nose", "honky in the middle"
- **cause:** what is physically happening
- **check:** how to confirm it, with mix-buddy tools where possible
- **fix:** ordered moves
- **avoid:** the common wrong move (optional)
- **evidence:** keys from the list below
```

Frequencies are starting regions, not rules: every voice, mic and room
moves them. Sweep and measure.

## Evidence keys

- `practice`: standard engineering practice found across mixing texts and
  the communities below. Treat it as a starting point to verify by measuring.
- `archive`: learned in mix-buddy's own session archive, with measured
  before/after (KEEP GOING 2 and SWeeter than some, Sep-Nov 2026).
- `research:audiocommons`: AudioCommons timbral attribute work (University
  of Surrey). A literature review of 1,187 descriptors, reduced to 145
  timbral attributes. Hardness, depth and brightness were the most searched.
  Models exist in Python (`pip install timbral_models`) for hardness, depth,
  brightness, roughness, warmth, sharpness, booming and reverb.
  [AES paper](https://aes2.org/publications/elibrary-page/?id=18754),
  [models](https://pypi.org/project/timbral_models).
- `research:safe`: SAFE plugins (Birmingham City University and Queen Mary
  University of London). Producers labelled EQ, compression, distortion and
  reverb settings with words like warm and bright.
  [SAFE paper](https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/12589/De%20Man%20SAFE%20A%20SYSTEM%20FOR%202014%20Published.pdf?sequence=2).
- `research:socialfx`: SocialFX (Northwestern). Crowdsourced words for EQ,
  reverb and compression: 4,297 words from 1,233 users.
  [SocialFX paper](https://pseeth.github.io/public/papers/zheng_seetharaman_pardo_acmmm.pdf).
- `story:<name>`: a documented record made in an unconventional setting
  (see `success_stories.md`). These are cited for what the source actually
  says, never for techniques it doesn't mention.

## Sources and communities to mine next

Verified active as of November 2026:

- **Sound On Sound: Mix Rescue and Studio SOS.** Long-running series where
  engineers rework readers' home recordings, often with downloadable
  before/after audio. Examples: a mix in a reader's living room on a
  laptop with bundled plugins; a control room that doubles as a bedroom;
  "Overcoming The Room" (Feb 2020).
  [soundonsound.com/techniques](https://www.soundonsound.com/techniques/mix-rescue-overcoming-room).
- **Cambridge-MT "Mixing Secrets" library and Discussion Zone** (Mike
  Senior). More than 500 free multitracks, and a forum where people post
  mixes of the same raw tracks: the best place to compare fixes for one
  problem. Has an R&B/Soul sub-forum.
  [cambridge-mt.com/ms](https://cambridge-mt.com/ms).
- **Gearspace, "Rap + Hip Hop Engineering and Production"** (about 28K
  threads), plus Studio Building / Acoustics for room problems.
  [gearspace.com/forums](https://gearspace.com/forums/).
- **r/mixingmastering**: strict feedback rules, a wiki (including a primer
  on loudness, "-14 LUFS is quiet"), and community "Mix Camp" events where
  everyone mixes one song. Rap/trap/R&B feedback posts are common.
- **r/makinghiphop**: daily feedback thread (you must give feedback to
  get it), a beginner guide and a resources wiki.
- **r/audioengineering** (technical help desk) and
  **r/WeAreTheMusicMakers** (weekly feedback thread).
- **Image-Line forum**: FL-specific mixing threads, plus an FLP exchange
  where people share project files.
  [forum.image-line.com](https://forum.image-line.com/).
- **EngineEars** (MixedByAli): a platform and community for hip-hop/R&B
  engineers that grew out of mixing workshops.
- **Pro Audio Files**: rap-vocal and 808 mixing articles (e.g. Matthew
  Weiss's series), some with free hip-hop multitracks.
- **Research datasets:** the Mix Evaluation Dataset (De Man and Reiss:
  engineers' free-text comments on many mixes of the same songs; a
  derivative is on Hugging Face as MixologyDB) is the closest thing to
  labelled "problem -> words" data from real mixes. The EBU SQAM test
  recordings are free reference material for checking analyzers
  ([EBU Tech 3253](https://tech.ebu.ch/publications/tech3253)).

## Corrections to earlier research notes

- AudioCommons is 1,187 descriptors reduced to **145** attributes, not
  "249 descriptors".
- The success stories in earlier notes included unsourced details (a
  specific mic, room and EQ chain for Charlie Puth; strip-silencing and a
  dark chamber for Billie Eilish). Those details are removed here. See
  `success_stories.md` for what the sources actually support.
