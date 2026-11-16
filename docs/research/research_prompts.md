# mix-buddy research prompts

Two research jobs:

- **Prompt A, plugin knowledge.** Teaches mix-buddy every plugin you own,
  plus the popular ones you don't.
- **Prompt B, process.** Covers how to make the workflow more intuitive and
  creative, and how mix-buddy can learn from its own session archive.

**How to run them**

1. Paste Prompt A into a deep-research tool once per batch (A1, A2, ...).
   300+ plugins is too many for one run, and quality drops after about 25
   plugins per run.
2. Run Prompt B once.
3. Put every report into one NotebookLM notebook ("mix-buddy knowledge").
   Add primary sources too: plugin manuals (PDF), the FL Studio
   scripting/plugin docs, and the papers Prompt B surfaces. Then ask the
   notebook the "Verify" questions at the end of this file.
4. Give the finished reports to Claude in the mix-buddy repo. The
   `plugin_notes` blocks get merged into `skill/references/plugin_notes.md`
   (the server attaches these to every plugin read). The `playbook` blocks go
   into a new `skill/references/plugin_playbook.md`. Lessons that contradict
   the session archive get flagged rather than merged.

---

## Prompt A: plugin knowledge (one run per batch)

> I'm building **mix-buddy**, an open-source MCP server that lets Claude act
> as a mixing engineer for **FL Studio 2025 (v25.1.6, Windows)**. It reads
> the live mixer and every plugin's parameters through FL's Python
> scripting API: parameter names come from `plugins.getParamName` and values
> as the plugin's own display text from `plugins.getParamValueString`. It
> also measures real audio from a tap plugin on each track. Claude diagnoses
> what the user dislikes ("muddy", "nasal", "set back in the center") and
> proposes exact moves: track, slot, plugin, parameter, from value to value.
> Write control comes later.
>
> The machine is a laptop (Ryzen 7 3700U, 12 GB RAM), so CPU and latency
> matter. The music is rap/R&B/alternative, vocal-led, mixed in FL with
> mostly third-party plugins.
>
> For **each plugin in the batch below**, research the official manual,
> vendor docs and reputable engineering sources (manufacturer tutorials,
> Sound on Sound, Pro Audio Files, Mix with the Masters, Produce Like a
> Pro). Avoid forum hearsay unless it's the only source for a known quirk,
> and label it as such. Then produce the two blocks below, exactly in this
> format.
>
> **Block 1: `plugin_notes`** (read-time facts, max ~12 bullet lines)
> ```
> ## <Vendor> <Plugin name>
> match: <comma-separated name prefixes FL shows, e.g. "Pro-Q, FabFilter Pro-Q">
> - What each main parameter is called as a host/automation parameter (the
>   VST3 parameter names, not just the GUI labels), with its units and
>   range.
> - Which way bare numbers go (e.g. "CLA-76 attack 1 = slowest, 7 = fastest";
>   "Q higher = narrower"). Flag anything inverted, stepped or non-linear.
> - Which parameter values mean "this module/band is off or inactive", so a
>   reader can ignore its other settings.
> - What the settings can't tell you (e.g. "gain reduction is not a
>   parameter").
> - Gotchas for remote reading/writing: normalized 0-1 vs display units,
>   parameters that only take effect when another is switched on, latency or
>   oversampling changes, parameters that click or reset when automated.
> ```
>
> **Block 2: `playbook`** (decision-time knowledge)
> ```
> ### <Plugin name>
> - Character: what it is / emulates, what it sounds like in one line.
> - Solves (listener words -> mechanism): e.g. "harsh 's' -> split-band
>   de-essing 5-9 kHz".
> - Starting settings by source, with numbers: lead vocal, adlibs/doubles,
>   808/bass, drum bus, beat/instrumental bus, master. Skip sources it's not
>   for.
> - Where in the chain and why (before/after EQ, comp, saturation,
>   de-esser).
> - What to measure before and after to prove it worked (band levels,
>   crest factor, gain reduction, LUFS, correlation...).
> - When not to use it / common misuse / what it does badly.
> - Alternatives in my collection (from the full list below) and when each
>   is the better pick.
> - CPU and latency on a low-power laptop; lighter modes (eco, zero-latency,
>   no oversampling) and when they're fine.
> - Creative/sound-design uses beyond correction (one or two concrete
>   recipes).
> ```
>
> Rules:
> - Cite a source for every numeric claim, and say when a number is a common
>   starting point rather than a spec.
> - If you can't verify a parameter name or range, write "UNVERIFIED"
>   instead of guessing.
> - Mono/Stereo/Mono-Stereo variants of the same Waves plugin count as one
>   plugin; note any differences.
> - The same plugin as VST, VST3 and CLAP counts as one; note any parameter
>   naming differences between formats.
> - Where a plugin was updated recently (2025-2026), use the current version
>   and say what changed.
>
> **Batch:** <paste one batch list from below>

### Batches

Already covered in `plugin_notes.md`, so **verify and extend, don't
rewrite**: Pro-Q 4, C6, RCompressor, bx_console SSL 4000 E, CLA Vocals,
CLA-76, Saturn 2, Fresh Air, Pro-C 3, Trackspacer, Tube-Tech CL 1B, Pro-DS,
Seventh Heaven, EchoBoy, Timeless 3, Little AlterBoy, PanMan, bx_glue,
Auto-Tune Pro, Auto-Key.

**A1: your current vocal/mix chain (do first)**
FabFilter Pro-L 2, Pro-MB, Pro-G, Pro-R 2, Volcano 3, Micro, Simplon ·
ValhallaVintageVerb · Soundtoys Decapitator · Waves Doubler4, Doubler2,
CLA-2A, CLA-3A, H-Delay, H-Reverb, DeEsser, Renaissance Vox (RVox), Silk
Vocal, Clarity Vx Pro, DeBreath · oeksound soothe2 · Abbey Road Saturator ·
plus the 20 above for verification.

**A2: dynamics, EQ and channel strips**
Waves C1 (comp/gate/sc), C4, F6, H-Comp, H-EQ, L1, L2, L3 (Multi/Ultra/LL),
MV2, NS1, PuigChild 660/670, PuigTec EQP1A/MEQ5, RBass, RChannel, RDeEsser,
REQ, Renaissance Axx, SSL E-Channel (SSLChannel), SSL G-Channel, SSLComp,
SSLEQ, SSL EV2 Channel, Vitamin, MaxxBass · Brainworx bx_console AMEK 200,
AMEK 9099, Focusrite SC, N, SSL 4000 G, SSL 9000 J, bx_2098 EQ, bx_XL V2,
bx_digital V3, bx_hybrid V2, bx_dynEQ V2, bx_opto, bx_townhouse Buss
Compressor, bx_limiter (True Peak), bx_clipper, bx_masterdesk (Classic/Pro/
True Peak), bx_refinement, bx_panEQ, bx_cleansweep (Pro/V2), bx_subfilter,
bx_boom, bx_enhancer, bx_saturator V2.

**A3: master, stereo, tape and color**
iZotope Ozone 12 (full suite and each module: Maximizer, Dynamic EQ,
Imager, Clarity, Stabilizer, Impact, Low End Focus, Master Rebalance, Match
EQ, Bass Control, Spectral Shaper, Unlimiter, Stem EQ, Vintage Comp/EQ/
Limiter/Tape, Exciter, Equalizer, Dynamics) · LANDR Mastering Pro · Waves
S1 Imager/MS Matrix/Shuffler, Abbey Road J37 Tape, RS124, Aphex Vintage
Exciter, VU Meter · Slate Virtual Tape Machines · bx_stereomaker, bx_rooMS,
bx_meter, bx_control V2, bx_solo · dearVR MONITOR.

**A4: vocal tuning, harmony and character**
Antares Auto-Tune EFX+, Vocodist, Slice, Vocal Compressor, Vocal EQ,
SoundSoap, Harmony Engine, Mic Mod, AVOX (Articulator, Aspire, Choir, Duo,
Mutator, Punch, Sybil, Throat, Warm) · Waves Tune / Tune LT / Tune
Real-Time, UltraPitch · Synchro Arts VocAlign 6 Pro · bx_crispytuner,
bx_crispyscale · Xvox (Comp, DS, Pro, SFX, Space, Tone): identify the vendor
· "Vocal Reverb": identify the vendor.

**A5: creative / sound design and time-based**
Soundtoys Crystallizer, Devil-Loc (Deluxe), FilterFreak 1/2, MicroShift /
Little MicroShift, PrimalTap / Little PrimalTap, Radiator / Little Radiator,
PhaseMistress, Tremolator, EffectRack · Cableguys ShaperBox 3 · Xfer Serum 2
FX · Waves MannyM (Delay, Distortion, EQ, Reverb, Tone Shaper, TripleD),
OneKnob series, MetaFlanger, IR-L · Filterverse (identify the vendor) ·
Brainworx bx_bluechorus2, bx_delay2500, bx_megadual/megasingle, bx_shredspread
and the guitar pedals (lower priority).

**A6: FL Studio native effects (mixing-relevant)**
Fruity Parametric EQ 2, Fruity Limiter (comp/limit/gate modes), Maximus,
Fruity Compressor, Fruity Multiband Compressor, Soft Clipper, Transient
Processor, Fruity Reeverb 2, Luxeverb, Fruity Convolver, Fruity Delay 3,
Multiband Delay, Gross Beat, Pitcher, Newtone, Vocodex, Fruity Stereo
Shaper, Stereo Enhancer, Frequency Splitter, Low Lifter, Emphasis, Spreader,
Distructor, Hardcore, Fruity Blood Overdrive, Fruity WaveShaper, Fruity
Squeeze, Vintage Chorus, Vintage Phaser, Fruity Peak Controller, Patcher,
Edison, Wave Candy, Fruity Spectroman. For native plugins, also cover how
`plugins.getParamName` / `getParamValueString` expose them (some native
plugins expose few or oddly named parameters).

**A7: popular plugins you don't own (for reading and gap analysis)**
> Use the same two blocks, plus one line per plugin: "Fills a gap in this
> collection? yes/no and what". Be honest: most will be "no, X already
> covers it".
> First establish what's actually popular for vocal-led rap/R&B mixing in
> 2026: name your sources (vendor charts, engineer gear lists, KVR/Plugin
> Boutique best-sellers, survey data). Then cover the top ~20 from:
> Universal Audio (LA-2A, 1176, Pultec, Ocean Way, Lexicon 224, Capitol
> Chambers), oeksound spiff/bloom, iZotope Nectar 4/RX 11/Neutron 5, Baby
> Audio (Smooth Operator, Crystalline, Spaced Out), Valhalla Supermassive/
> Room/Delay, Sonible smart:EQ/comp/limit, Tokyo Dawn Labs (Nova,
> Kotelnikov, Limiter 6), Kiive Audio, Black Rooster, Goodhertz, Eventide
> (Blackhole, SplitEQ, H3000), Kilohearts, Arturia FX, Softube, SSL Native,
> Slate VMR/Fresh Air siblings, Polyverse, plus any new 2025-26 releases
> engineers are adopting (AI-assisted mixing plugins especially: what they
> automate and how well).

**Full installed list (for the "alternatives in my collection" field):**
FabFilter (Pro-Q 4, Pro-C 3, Pro-DS, Pro-G, Pro-L 2, Pro-MB, Pro-R 2,
Saturn 2, Timeless 3, Volcano 3, Micro, Simplon, One, Twin 3) · Waves (C1,
C4, C6, CLA Vocals, CLA-2A, CLA-3A, CLA-76, Clarity Vx/Vx Pro, DeBreath,
DeEsser, Doubler2/4, F6, H-Comp, H-Delay, H-EQ, H-Reverb, IR-L, L1, L1+, L2,
L3 family, MV2, MannyM series, MaxxBass, MetaFlanger, NS1, OneKnob series,
PuigChild, PuigTec, Renaissance series, S1 series, SSL series, Silk Vocal,
UltraPitch, VU Meter, Vitamin, Waves Tune, Abbey Road J37/RS124/Saturator,
Aphex Vintage Exciter) · Brainworx/Plugin Alliance (bx_console AMEK
200/9099, Focusrite SC, N, SSL 4000 E/G, SSL 9000 J; bx_2098, XL V2,
digital V3, hybrid V2, dynEQ V2, opto, glue, townhouse, limiter, clipper,
masterdesk, refinement, panEQ, cleansweep, subfilter, subsynth, boom,
enhancer, saturator V2, stereomaker, rooMS, meter, control V2, solo,
crispytuner, crispyscale, oberhausen, guitar amps/pedals; dearVR MONITOR) ·
Soundtoys (Decapitator, EchoBoy, Crystallizer, Devil-Loc, FilterFreak,
Little AlterBoy/MicroShift/PrimalTap/Radiator, MicroShift, PanMan,
PhaseMistress, PrimalTap, Radiator, Tremolator, EffectRack) · Antares
(Auto-Tune Pro, EFX+, Vocodist, Slice, Vocal Compressor, Vocal EQ,
SoundSoap, Harmony Engine, Mic Mod, AVOX series, Auto-Key 2) · iZotope
Ozone 12 + modules · oeksound soothe2 · Wavesfactory Trackspacer 2.5 ·
Valhalla VintageVerb · LiquidSonics Seventh Heaven Professional · Slate
Fresh Air, Virtual Tape Machines · Softube Tube-Tech CL 1B · Synchro Arts
VocAlign 6 Pro · Cableguys ShaperBox 3 · Xfer Serum 2 / Serum 2 FX · LANDR
Mastering Pro · Xvox series · Filterverse · Vocal Reverb · instruments:
Omnisphere, Roland ZENOLOGY, XLN Addictive Keys, Purity, FL natives (Sytrus,
Harmor, FLEX, FPC, Slicex, DirectWave, Transistor Bass, Kepler, Toxic
Biohazard, Morphine, Harmless, Sakura, PoiZone, GMS, 3x Osc) · all FL Studio
native effects.

---

## Prompt B: refining the process (run once)

> I'm building **mix-buddy**, an open-source MCP server that turns Claude
> into a mixing assistant for FL Studio 2025, inspired by Ableton's
> **Producer Pal**. Today it:
> - Reads the live mixer and every plugin's parameters in display units.
> - Measures live audio through a tap plugin on each track (loudness,
>   dynamics, third-octave spectrum, masking between buses, reverb level
>   while singing vs in gaps, vowel formant jumps).
> - Analyzes bounces.
> - Keeps an archive of every session: automatic change diffs whenever a
>   setting differs from the last read, plus complaints, decisions, outcomes
>   and cross-project lessons.
>
> The loop: the user names what they don't like, in their own words; Claude
> measures, finds culprits in the chain, proposes exact moves; the user
> makes them by ear; Claude re-measures. Write control (with approval and
> undo) is next. One producer-engineer, laptop (Ryzen 7 3700U), vocal-led
> rap/R&B.
>
> Research and report, with sources, on how to make this **more accurate,
> more intuitive, more creative, and self-improving**:
>
> 1. **Words -> sound.** Research on mapping listener descriptors to
>    measurable features and moves: muddy, boxy, honky, nasal, harsh, thin,
>    warm, airy, buried, set back, glued, wide, washed, dry. Cover SAFE
>    (Semantic Audio Feature Extraction), SocialFX, Audio Commons timbral
>    models, and any 2023-26 text-to-audio-effect work (Text2FX, LLM2Fx,
>    LLM-driven mixing agents). I want a table: descriptor -> frequency
>    region / feature -> typical move -> how to verify by measurement.
> 2. **Better measurements for decisions.** What should be measured beyond
>    what I have? Perceptual masking models (partial loudness,
>    Glasberg-Moore; how iZotope's masking meter or Trackspacer decide),
>    vocal intelligibility/presence metrics, sibilance and resonance
>    detection that ignores harmonics, reverb perception (clarity C50/C80,
>    wet/dry while singing), vocal-vs-beat loudness targets in current
>    commercial rap/R&B, and singing formant tables (F1/F2 for ah/oh/ee) for
>    vowel balance. For each: the algorithm, its cost on a laptop, and
>    whether a Python/numpy implementation exists.
> 3. **Intelligent / automatic mixing literature.** Josh Reiss and Brecht
>    De Man ("Intelligent Music Production"), differentiable mixing
>    (Martínez-Ramírez, Steinmetz, Diff-MST), mix-style transfer, reference
>    matching, recent LLM-agent mixing papers and datasets (MixAssist and
>    similar). What can a small tool borrow without training a model?
> 4. **Learning from its own history.** How should the session archive turn
>    into better advice over time? Compare case-based reasoning, preference
>    learning from accepted/rejected suggestions, simple per-user priors
>    ("this user always ends up cutting 1.2 kHz on leads"), and retrieval
>    over past sessions. Cover how to avoid overfitting to one song, and
>    which signals mean a move worked (re-measurement, user approval,
>    whether it was kept at the next session's snapshot).
> 5. **Intuitive UX for an AI mixing assistant.** Lessons from Producer
>    Pal, iZotope Assistant (Neutron/Nectar/Ozone), Sonible smart:,
>    Mastering assistants, and DAW copilots: how they phrase suggestions,
>    show before/after, handle A/B, and get approval. Design patterns for
>    write control: preview, approve, read-back verification, undo,
>    automation-safe parameter changes, never surprising the user mid-take.
> 6. **Creativity, not just correction.** How engineers and producers make
>    creative moves (ear candy, throws, automation rides, vocal effects
>    chains, sound design on the beat), and how an assistant can suggest
>    them without being cheesy. Include ways to propose 2-3 contrasting
>    directions ("dark and intimate" vs "wide and glossy") and how to
>    describe them.
> 7. **FL Studio specifics.** Current (2025-26) FL scripting API
>    capabilities and limits relevant here: mixer routing, plugin parameter
>    read/write, song position, markers, automation clips, undo history
>    (`general.saveUndo`?), project name, Patcher. Also community projects
>    doing similar things (FL MCP servers, FL scripting bridges), and what
>    they learned.
>
> Output: a report with a section per question. Each section has (a)
> findings with citations, (b) a concrete recommendation for mix-buddy, and
> (c) effort: small, medium or large. End with a prioritized roadmap of the
> top 10 changes.

---

## Verify questions for NotebookLM (once reports are loaded)

- Where do the reports disagree on a plugin's parameter names, ranges or
  knob direction? List each conflict with both sources.
- Which numeric starting settings have no citation?
- For lead vocals, which plugins in my collection overlap most (same job),
  and what's the deciding factor between them?
- Which listener descriptors map to the same frequency region but need
  different moves, and how do you tell them apart by measurement?
- What do the sources say about a nasal lead vocal around 1-1.6 kHz, and
  does it agree with this lesson: "a dynamic band near 1.2 kHz beat a static
  cut"?
