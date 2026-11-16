# Plugin notes: how to read the settings

What `fl_get_plugin_params` returns is each plugin's own display text. This
file says what those values mean, which way knobs go, and what is easy to
misread. The server attaches the matching section to every plugin read, so
keep each section short and factual. Sections match FL's plugin name by the
`match:` prefixes.

If a plugin is not listed here, read its values literally and do not guess
directions or units.

## FabFilter Pro-Q 4
match: Pro-Q
- Each band: Frequency, Gain (dB), Q, Shape (Bell, Low/High Shelf, Low/High
  Cut, Notch, Band Pass, Tilt...), Slope, Stereo Placement.
- Band Gain runs -30 to +30 dB.
- Q is a bare number: higher Q = narrower bell. Shelves use Q only to shape
  the curve.
- Dynamic Range (-30 to +30 dB) makes a Bell or Shelf band dynamic. Negative =
  extra cut when the band gets loud (compression); positive = expansion. 0 dB
  = static band (the server hides the unused dynamic settings then).
- Threshold "Auto" means Pro-Q sets threshold, attack and release from the
  audio. Spectral (Spectral Tilt / Spectral Density) means it only reacts to
  the specific frequencies inside the band that poke out.
- Gain Scale scales every band's gain (100% = as drawn). Auto Gain
  compensates level, so with it On a boost will not raise overall level.
- A Low Cut's Gain is always 0.00 dB; it is a filter, not a cut amount.

## Waves C6 Multiband Compressor
match: C6
- Four crossover bands (split by Low/Mid/High Crossover) plus two floating
  bands with their own Frequency and Q. In FL's readout the floating bands
  are the bands with a Frequency/Q parameter (here usually Band 1 and Band 6).
- Range is the maximum dynamic gain change: negative = compression
  (downward), positive = expansion (upward), 0 = no dynamics, only static
  Gain.
- Gain is static make-up/EQ gain per band (+/-18 dB), applied regardless of
  level. Positive Gain with negative Range = a boost that shrinks when the
  band gets loud.
- Threshold is where the band starts reacting. Behavior Opto/Electro and
  Release Manual/ARC work like the Renaissance Compressor.
- Gain reduction is not a parameter: the settings show how hard it could
  work, not how hard it is working.

## Waves Renaissance Compressor
match: RCompressor, Renaissance Compressor
- Classic controls: Threshold, Ratio, Attack, Release, Gain (make-up).
- ARC = automatic release: Release is a scaling value, ARC varies it with the
  material.
- Electro: release speeds up as gain reduction approaches zero (below about
  3 dB of GR) - louder, denser. Opto: release slows as GR returns to zero -
  smoother.
- Warm adds low-frequency harmonics as compression deepens; Smooth avoids
  them.
- Mix is a wet/dry percentage (parallel compression below 100). Trim is a
  final output trim after the limiter.

## Brainworx bx_console SSL 4000 E
match: bx_console SSL 4000 E
- A full channel strip: filters, dynamics, EQ, plus console colour.
- Dynamics: "LC" parameters are the compressor/limiter (Ratio, Threshold,
  Release, Attack, Mix). "GE" parameters are the gate/expander (GE Mode
  Expander or Gate, Range, Threshold). A GE Threshold near -60 dB means the
  gate/expander is effectively not doing anything on normal material.
- EQ: High, High Mid, Low Mid, Low bands with Gain/Frequency/Q; High and Low
  can be Shelf or Bell. EQ Type Black or Brown is the E-series EQ flavour.
- EQ Position Post Dyn = EQ after the compressor; FLT Position Input = filters
  before everything.
- HPF at 16 Hz and LPF at 22 kHz are effectively off.
- Virtual Gain and THD add console noise/saturation. Virtual Gain at its
  minimum (-90 dB) and THD at -60 dB add almost nothing.

## Waves CLA Vocals
match: CLA Vocals
- Macro faders, each with a Color mode. Bass, Treble, Compress range +/-10.
- Bass and Treble are neutral at 0. The other faders are NOT off at 0: they
  stay at Chris Lord-Alge's default amount. A section is only off when its
  Color is Clear (Bypass/Mute).
- Compress Colors: Push (lighter, punch), Spank (harder), Wall (heaviest,
  limiter-like). The internal ratios and times are not published.
- Pitch is a pitch-modulation effect (doubling/widening) with Colors such as
  Wide; Reverb/Delay Color Mute = off.
- Sensitivity sets the input level into the processing.
- Do not translate fader numbers into dB or Hz; Waves does not publish them.

## Waves CLA-76
match: CLA-76
- 1176-style FET compressor. There is no threshold knob: Input pushes the
  signal into a fixed threshold. Higher Input (closer to 0) = more
  compression. -30 dB is the default.
- Output is make-up level.
- Attack and Release run 1 (slowest) to 7 (fastest). The numbers are
  backwards from most compressors: 7 is fastest. Attack 1 = about 1 ms,
  7 = under 50 microseconds; Release 1 = about 1 s, 7 = 50 ms.
- Ratio 4, 8, 12, 20 or All (all-buttons-in, aggressive).
- Revision Blacky/Bluey are two hardware revisions. Analog adds modelled
  noise.
- Whether it is compressing depends on the level arriving at it, which the
  settings cannot show. Ask for audio or the GR meter before calling it
  inactive.

## FabFilter Saturn 2
match: Saturn
- Multiband saturation. Num Active Bands says how many bands are in use; the
  server hides the rest. Crossover Frequency is the top edge of each band;
  the last active band's crossover value is unused.
- Per band: Style (Tape, Tube, Amp... flavours), Drive (%), Mix, Level, and
  tone controls Bass / Mid / Treble / Presence in dB that shape that band's
  saturation colour.
- Dynamics: positive values add upward compression-like density; 0 = none.
- Feedback adds resonance at Feedback Frequency; 0% = off.
- Global Mix is wet/dry for the whole plugin. Output Gain trims the result.
- Large tone boosts inside a band (e.g. Mid +8 dB) are a real EQ move
  applied to the saturated signal, scaled by the global Mix.

## Slate Digital Fresh Air
match: Fresh Air
- Dynamic high-frequency exciter. Mid Air lifts the upper mids/presence,
  High Air the top end. Both are percentages, not dB.
- Because it is dynamic, it adds level as you raise it; Trim compensates.

## FabFilter Pro-C 3
match: Pro-C
- Style sets the compression algorithm. Modern: Clean, Smooth, Punch,
  Upward, TTM (multiband, OTT-like). Classic: Op-El, Vari-Mu, Classic, Opto.
  Utility: Vocal (automatic knee and ratio, ratio control inactive),
  Mastering, Bus, Pumping.
- Threshold, Ratio, Knee, Attack, Release, Range, Lookahead, Hold, Wet/Dry
  read literally. Auto Threshold On means threshold follows the material.
- Character adds analog saturation; its Drive is linked against Threshold.
- Side Chain EQ bands only shape what the detector hears, not the audio.

## Wavesfactory Trackspacer
match: Trackspacer
- Sidechain-driven EQ: analyses the sidechain input's spectrum and carves the
  inverse curve out of the track it sits on. Needs a sidechain feeding it in
  FL, or it does nothing.
- Ratio (0-100%) = how deeply it carves.
- Low-cut and High-cut limit the frequency range it works in.
- Freeze holds the current curve.

## Softube Tube-Tech CL 1B
match: Tube-Tech CL 1B, CL 1B
- Optical tube compressor, smooth and program-dependent.
- Threshold "Off" disables compression completely: the plugin then only
  passes audio (with its tube colour). Check this before assuming it levels.
- Ratio is a fixed-step knob (e.g. 2:1 to 10:1). Gain is make-up level.
- Attack and Release are bare knob numbers; Select Attack Release picks
  Fixed (preset opto timing), Fixed-Manual, or Man (manual knobs).
- Gain reduction is not a parameter; ask the user to read the plugin's
  meter, or compare crest factor before and after.

## FabFilter Pro-DS
match: Pro-DS
- De-esser. Mode Single Vocal (focused on one voice) or Allround.
- Threshold sets where it reacts; Range is the most it will reduce (dB).
- High-Pass and Low-Pass Frequency set the detection band. Above about
  5 kHz it works on sibilance, not on presence (2-4 kHz).
- Lookahead lets it catch the start of an "s"; Stereo Link Mode Mid
  processes the centre.

## LiquidSonics Seventh Heaven
match: Seventh Heaven
- Reverb modelled on the Bricasti M7. Dry/Wet "Wet" means 100% wet: normal
  for a reverb on a send/return track, wrong on an insert of the dry track.
- Decay Time in seconds; Early/Late Level balances early reflections against
  the tail.

## Soundtoys EchoBoy
match: EchoBoy
- Tape/analog-style echo. Mix 100% means fully wet, normal on a send/return
  track.
- Echo time, Feedback and the Style/saturation settings read literally.

## FabFilter Timeless 3
match: Timeless
- Tape-style delay. Delay Time and Delay Offset (e.g. 150% = dotted) set the
  echo; Delay Sync Free = milliseconds rather than note values.
- Feedback (%) sets the number of repeats. Filters (Used ones only) shape the
  repeats; Filter Routing Serial/Parallel.
- Effect modules (Drive, Lo-Fi, Diffuse, Dynamics, Pitch Shift) only matter
  when their Enabled switch is On; the server hides the ones that are Off.
- Mix is wet/dry for the plugin; XLFOs and XY controllers are modulation
  sources.

## Soundtoys Little AlterBoy
match: Little AlterBoy
- Pitch (semitones) and Formant (semitones) shift independently; Drive adds
  saturation; Mix sets wet/dry.

## Soundtoys PanMan
match: PanMan
- Auto-panner. Mix 100% = full effect. Input/Output Gain trims.

## Brainworx bx_glue
match: bx_glue
- Bus compressor for gluing groups. Input/Output Gain and the usual
  compressor controls; values without units are the plugin's own scale.

## Antares Auto-Tune Pro
match: Auto-Tune
- Key and Scale set the target notes. Retune Speed in ms: lower = faster,
  harder correction (0 = the robotic hard-tune effect); higher = more
  natural.
- Detune sets the reference pitch (440.0 = standard A).
- Humanize and Flex-Tune keep longer notes or small deviations natural.

## Antares Auto-Key
match: Auto-Key
- Detects the song's key/scale. Send passes the detected key to Auto-Tune
  instances; Key/Scale "Chromatic" means no key detected or set.
