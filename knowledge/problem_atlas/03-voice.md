# 03 Voice, mouth and articulation (051-075)

### 051 Harsh sibilance
- **severity:** major
- **says:** "S sounds pierce my ears", "hurts my ears", "hissy", "harsh S and T", "spitty"
- **cause:** sibilant energy, usually 5-9 kHz, much louder than the vowels.
- **check:** analyze_vocal_clarity sibilance; short spikes 5-9 kHz far above the vowel level.
- **fix:** de-ess before heavy compression, and a second light de-esser at the end of the chain; Pro-DS with the detector band on the S.
- **evidence:** practice

### 052 Sibilance that appears only after processing
- **severity:** minor
- **says:** "the S got worse after the chain", "fine raw, harsh mixed"
- **cause:** compression, saturation or air boosts raise sibilance after the de-esser.
- **check:** compare taps or stems before and after the chain.
- **fix:** move or add a de-esser after the brightening stage.
- **evidence:** practice, archive

### 053 Lisping, over-de-essed vocal
- **severity:** minor
- **says:** "sounds like a lisp", "S is gone", "dull"
- **cause:** the de-esser is too deep or too wide.
- **check:** de-esser range or threshold aggressive; 5-9 kHz dips on every S.
- **fix:** shallower range (3-6 dB), split-band mode, narrower detection.
- **evidence:** practice

### 054 Mouth clicks and lip smacks
- **severity:** minor
- **says:** "clicky", "wet mouth noise", "smacking"
- **cause:** saliva and lip noise picked up close-in, raised by compression.
- **check:** short spikes in gaps and at word starts.
- **fix:** de-click (spectral repair) or manual edits; hydrate before takes.
- **evidence:** practice

### 055 Loud breaths
- **severity:** minor
- **says:** "breathing too loud", "gasping between lines"
- **cause:** breaths captured close and raised by compression.
- **check:** analyze_noise_gate: gap level much higher than noise floor.
- **fix:** clip-gain breaths down 6-12 dB rather than deleting them; a breath-control or expander with a slow release.
- **avoid:** removing all breaths; it sounds unnatural.
- **evidence:** practice

### 056 Sharp gasp before a phrase
- **severity:** minor
- **says:** "the inhale is distracting"
- **cause:** a fast loud inhale right before a line.
- **check:** a burst just before the phrase onset.
- **fix:** fade or lower that single breath.
- **evidence:** practice

### 057 Nasal vocal
- **severity:** minor
- **says:** "nasal", "through the nose", "honky", "sounds congested"
- **cause:** too much energy around 1-1.6 kHz (singer's resonance, mic, or a removed cut).
- **check:** live spectrum: the 1-1.6 kHz bands above the octave neighbours; check whether an earlier cut was removed.
- **fix:** a narrow dynamic Pro-Q band near 1.2 kHz (Q about 3, small static cut, larger dynamic range) instead of a deep static cut.
- **avoid:** removing every 1 kHz cut for "body"; it brought the nasality back.
- **evidence:** archive

### 058 Throaty or strained tone
- **severity:** minor
- **says:** "strained", "tight", "pushing too hard"
- **cause:** constricted delivery adds rough upper-mid energy.
- **check:** roughness and 2-4 kHz energy rise on strained lines.
- **fix:** dynamic EQ on 2-4 kHz for those lines; best fixed by retaking.
- **evidence:** practice

### 059 Some vowels jump out (ah, oh)
- **severity:** minor
- **says:** "ah and oh feel off", "some words louder than others", "vowels uneven"
- **cause:** different vowels have formants in different regions (oh near 400-600 Hz, ah near 700-1100 Hz), so some poke through.
- **check:** level jumps in those bands on specific vowels.
- **fix:** dynamic EQ bands at each vowel's formant region that only act when it jumps.
- **evidence:** archive, practice

### 060 "Ee" vowel piercing
- **severity:** minor
- **says:** "ee sounds shrill", "feet and clean hurt"
- **cause:** the "ee" second formant sits in the 2-3.5 kHz sensitive region.
- **check:** jumps in 2-3.5 kHz on "ee" vowels.
- **fix:** a dynamic band there (Pro-Q band made dynamic); soothe2 gently.
- **evidence:** archive

### 061 Words unclear
- **severity:** major
- **says:** "can't understand the words", "mumbly", "not clear"
- **cause:** too little 2-5 kHz consonant energy relative to the vowels, or masking from the beat.
- **check:** analyze_vocal_clarity clarity; compare vocal vs beat in 2-5 kHz with fader compensation.
- **fix:** upper-mid lift or presence saturation on the vocal; carve 2-5 kHz in the beat (Trackspacer or dynamic EQ keyed to the vocal).
- **evidence:** practice

### 062 Word endings swallowed
- **severity:** minor
- **says:** "end of lines disappear", "trailing off"
- **cause:** the singer drops level at phrase ends; compression or the gate hides them further.
- **check:** level falls sharply at phrase ends.
- **fix:** clip-gain or automate the endings up; slower gate release.
- **evidence:** practice

### 063 Loud first syllable
- **severity:** minor
- **says:** "first word blasts", "jumpy starts"
- **cause:** the singer hits phrase starts harder than the compressor can catch.
- **check:** the first transient of each phrase is several dB above the rest.
- **fix:** faster attack (or a fast FET like CLA-76) before the slower opto; clip-gain the worst.
- **evidence:** practice

### 064 Whispered or soft delivery buried
- **severity:** major
- **says:** "the soft parts disappear", "can't hear the whisper"
- **cause:** quiet delivery has little energy, so the beat masks it.
- **check:** low RMS on those lines; masking against the beat.
- **fix:** heavy but slow compression or volume rides, and space in the beat; keep it close and dry.
- **evidence:** practice, story:billie, story:clairo

### 065 Belted or screamed sections harsh
- **severity:** minor
- **says:** "the loud parts hurt", "distorts on high notes"
- **cause:** loud singing has stronger upper harmonics and may clip the input.
- **check:** 2-5 kHz rises with level; check for clipping (030).
- **fix:** dynamic EQ that reacts only on loud notes; a level ride before the compressor.
- **evidence:** practice

### 066 Ad-libs don't match the lead's energy
- **severity:** minor
- **says:** "ad-libs sound weak", "ad-libs sound like a different song"
- **cause:** ad-libs recorded at different energy or position.
- **check:** compare spectra and level.
- **fix:** separate ad-lib chain: more saturation, narrower band, panned; level by ear in context.
- **evidence:** practice

### 067 Pitch drift at phrase tails
- **severity:** minor
- **says:** "goes flat at the end"
- **cause:** pitch sags as breath runs out.
- **check:** pitch trace sinks on tails.
- **fix:** graphic tuning on the tails, or a slower retune that catches only the drift.
- **evidence:** practice

### 068 Uneven vibrato
- **severity:** minor
- **says:** "wobbly", "shaky"
- **cause:** inconsistent vibrato width or speed.
- **check:** pitch trace.
- **fix:** graphic tuning to even it out, or leave it if it's emotional.
- **evidence:** practice

### 069 Spit and wet noises
- **severity:** minor
- **says:** "wet", "spitty"
- **cause:** saliva noise on consonants.
- **check:** crackly bursts on T and K.
- **fix:** de-click; edit.
- **evidence:** practice

### 070 Whistling S
- **severity:** minor
- **says:** "whistle on the S", "ringing S"
- **cause:** a very narrow tonal sibilance around 7-10 kHz (often teeth gaps).
- **check:** a narrow spike in that range on S.
- **fix:** narrow dynamic notch at the whistle frequency.
- **evidence:** practice

### 071 Rap verse sounds flat and monotone in the mix
- **severity:** minor
- **says:** "no energy", "boring", "doesn't hit"
- **cause:** delivery dynamics squashed or emphasis words not lifted.
- **check:** very low crest factor; no level difference on punch words.
- **fix:** volume rides on emphasis words, delay throws on line ends, less static compression.
- **evidence:** practice

### 072 Mumble delivery hard to hear
- **severity:** minor
- **says:** "too mumbly", "can't make out the words"
- **cause:** soft consonants and low articulation energy.
- **check:** low 2-5 kHz energy relative to the vowels.
- **fix:** presence saturation, light 3-4 kHz lift, beat carved in that range; but keep the style.
- **evidence:** practice

### 073 Voice cracks
- **severity:** minor
- **says:** "voice breaks", "crack on that note"
- **cause:** a register break in the take.
- **check:** pitch and level jump within a note.
- **fix:** comp from another take, or keep it if it sells emotion.
- **evidence:** practice

### 074 Preset chain doesn't fit this voice
- **severity:** minor
- **says:** "the preset sounds wrong on me", "worked for him, not me"
- **cause:** presets assume a voice, mic and room that don't match yours.
- **check:** compare your raw spectrum to the target before applying presets.
- **fix:** start from the measured problems, not a preset; use presets as a starting chain only.
- **evidence:** practice

### 075 Later takes duller or hoarse
- **severity:** minor
- **says:** "the second verse sounds tired"
- **cause:** vocal fatigue changes tone across a session.
- **check:** compare spectra of early and late takes.
- **fix:** EQ-match; record important parts early.
- **evidence:** practice
