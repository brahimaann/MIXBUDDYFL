# 02 Microphone and tracking (026-050)

### 026 Plosive pops
- **severity:** major
- **says:** "popping on P and B", "popping", "pops on my Ps", "thumps on words", "bass bursts"
- **cause:** air bursts from P/B hit the capsule and produce a big low-frequency spike.
- **check:** sub-150 Hz spikes at word starts; peaks far above the phrase level.
- **fix:** clip-gain the pops down or high-pass just that region; a dynamic EQ band below 150 Hz that only reacts to bursts; next take: pop filter, mic slightly off-axis.
- **avoid:** a high-pass so high it thins the whole vocal.
- **evidence:** practice, story:peep

### 027 Proximity effect boom
- **severity:** major
- **says:** "too much bass on the vocal", "boomy up close", "chesty"
- **cause:** a directional mic very close to the mouth boosts the low end.
- **check:** 100-250 Hz well above the 1 kHz anchor (more than about +6 dB on a lead).
- **fix:** high-pass 80-120 Hz plus a low shelf cut; a dynamic band at 120-200 Hz that only acts when the singer leans in.
- **evidence:** practice

### 028 Distance changes between words
- **severity:** major
- **says:** "volume jumps", "tone changes on some words", "close then far"
- **cause:** the singer moves toward and away from the mic, changing level and tone.
- **check:** large word-to-word level spread (crest factor, dynamics analysis) and changing low end.
- **fix:** clip-gain rides first, then compression; dynamic EQ for the low end; next time mark the distance (a fist away).
- **evidence:** practice

### 029 Singing past the mic
- **severity:** minor
- **says:** "dull on some lines", "muffled words"
- **cause:** off-axis singing loses highs on most mics.
- **check:** some lines show less 5-10 kHz than others.
- **fix:** automate a high shelf on those lines, or punch them again.
- **evidence:** practice

### 030 Clipped recording
- **severity:** major
- **says:** "distorted", "crunchy on loud parts", "crackle on high notes"
- **cause:** input gain too high, the converter clipped.
- **check:** flat-topped peaks at 0 dBFS in the raw take; true-peak readout at or above 0.
- **fix:** re-record if possible; otherwise a declipper, then cover it with saturation so it reads as intentional.
- **avoid:** hoping compression hides it; it makes it more obvious.
- **evidence:** practice

### 031 Recorded too quiet
- **severity:** minor
- **says:** "hissy when I turn it up", "noisy vocal"
- **cause:** low recording level means the gain added later raises the noise floor.
- **check:** peaks below about -24 dBFS and an audible noise floor after makeup gain.
- **fix:** gentle noise reduction before compression; aim for peaks around -12 to -6 dBFS when tracking.
- **evidence:** practice

### 032 Headphone or click bleed
- **severity:** minor
- **says:** "I can hear the beat in the vocal", "ticking in the vocal"
- **cause:** loud headphones leak into the mic.
- **check:** the beat's transients visible in vocal gaps.
- **fix:** gate or edit the gaps; next time use closed-back headphones at lower level.
- **evidence:** practice

### 033 Beat bleed from speakers
- **severity:** major
- **says:** "the beat is in my vocal", "doubled drums", "phasey beat when vocal is on"
- **cause:** recording while the beat plays on speakers.
- **check:** vocal track contains the beat; flams with the real beat.
- **fix:** re-record on headphones; if impossible, gate hard and EQ the bleed's range.
- **evidence:** practice

### 034 Stand thumps and handling noise
- **severity:** minor
- **says:** "random thumps", "knocks"
- **cause:** touching the stand or holding the mic transmits vibration.
- **check:** low-frequency transients not linked to words.
- **fix:** edit or clip-gain; high-pass; shock mount next time.
- **evidence:** practice

### 035 Clothing or jewelry rustle
- **severity:** minor
- **says:** "rustling", "jingling", "scratchy noise"
- **cause:** movement noise near the mic.
- **check:** broadband scratchy noise in gaps or under quiet lines.
- **fix:** edit; spectral repair; remove jewelry and wear quiet fabric when tracking.
- **evidence:** practice

### 036 Phone or laptop built-in mic
- **severity:** major
- **says:** "sounds like a phone", "thin", "pumping volume", "lo-fi"
- **cause:** tiny capsules roll off lows and highs; automatic gain control and noise suppression pump and smear.
- **check:** little energy below about 150 Hz and above about 10 kHz; level pumping on loud lines.
- **fix:** decide whether it's the aesthetic; if so, lean in and build the beat around it; if not, saturation and doubles for size, gentle low shelf, and re-record key lines.
- **evidence:** practice, story:lacy, story:grimes

### 037 Vocal recorded late (latency)
- **severity:** major
- **says:** "vocal is behind the beat", "off-time everywhere"
- **cause:** recording latency not compensated, so the whole take lands a few milliseconds late.
- **check:** consistent offset between word onsets and the grid or beat transients.
- **fix:** nudge the whole take earlier by the measured offset; set the interface's latency compensation; record with low-latency mode.
- **evidence:** practice

### 038 Harsh cheap condenser
- **severity:** minor
- **says:** "sizzly", "harsh S", "brittle"
- **cause:** budget condensers often have a presence peak around 5-10 kHz.
- **check:** a fixed spectral peak in that range across every take.
- **fix:** static narrow cut or soothe2 on the peak, de-esser after.
- **evidence:** practice, story:billie

### 039 Dark dynamic mic
- **severity:** minor
- **says:** "dark", "no air", "muffled", "SM58 sound"
- **cause:** dynamic mics (SM57/58, SM7B) roll off the top end.
- **check:** steep fall above 6-8 kHz.
- **fix:** saturation before EQ to create upper harmonics, then a high shelf; don't force it to sound like a condenser if the dark tone suits the song.
- **evidence:** practice, story:boniver, archive

### 040 Low-output mic with a weak preamp
- **severity:** minor
- **says:** "hiss when I turn it up", "too quiet even at max gain"
- **cause:** low-output dynamic mics (SM7B) need more gain than budget interfaces give cleanly.
- **check:** high noise floor relative to the voice.
- **fix:** an inline booster; noise reduction; sing closer.
- **evidence:** practice

### 041 Sample-rate mismatch
- **severity:** major
- **says:** "vocal is slower or out of tune", "pitch is off after import"
- **cause:** a file recorded at 48 kHz played at 44.1 kHz (or the reverse).
- **check:** the whole take is consistently flat or sharp and slow or fast.
- **fix:** resample properly in FL (or Edison) to the project rate.
- **evidence:** practice

### 042 Clicks and dropouts while recording
- **severity:** major
- **says:** "pops in the vocal", "glitches", "little gaps"
- **cause:** buffer underruns from a small audio buffer or CPU overload.
- **check:** single-sample spikes or silences in the take.
- **fix:** edit or repair; record with a bigger buffer and fewer plugins running (Ryzen 3700U laptops hit this easily).
- **evidence:** practice

### 043 Fake stereo vocal
- **severity:** minor
- **says:** "vocal is on one side", "only left ear"
- **cause:** a mono mic recorded into one side of a stereo track.
- **check:** analyze_stereo_compatibility: one channel near silence.
- **fix:** take the good channel as mono; FL channel settings or a mono plugin.
- **evidence:** practice

### 044 Two mics on one vocal out of phase
- **severity:** minor
- **says:** "thin when both are on", "hollow"
- **cause:** two mic signals arriving at different times cancel.
- **check:** level and low end drop when both are summed.
- **fix:** time-align, flip polarity, or use one mic.
- **evidence:** practice

### 045 Pop filter or foam dulling
- **severity:** minor
- **says:** "muffled", "dull"
- **cause:** thick foam or a filter pressed against the mic absorbs highs.
- **check:** less 6-12 kHz than expected.
- **fix:** high shelf; next time move the filter 5-10 cm off the mic.
- **evidence:** practice

### 046 Makeshift pop filter (sock, shirt)
- **severity:** minor
- **says:** "dull but no pops"
- **cause:** fabric over the capsule blocks plosives but cuts highs.
- **check:** steep high roll-off.
- **fix:** saturation plus air; accept it as part of the sound.
- **evidence:** story:peep

### 047 Processing printed into the take
- **severity:** major
- **says:** "I can't undo the reverb", "tuning is wrong key"
- **cause:** effects or tuning recorded onto the track.
- **check:** compare with a dry take if one exists.
- **fix:** re-record dry; otherwise work around (gate the printed reverb, re-tune).
- **evidence:** practice

### 048 Takes recorded at different levels
- **severity:** minor
- **says:** "some lines are way louder"
- **cause:** gain changed between takes.
- **check:** clip-to-clip RMS differences.
- **fix:** clip-gain match before any compression.
- **evidence:** practice

### 049 Vocal from a voice memo or MP3
- **severity:** minor
- **says:** "swirly", "warbly highs", "underwater S"
- **cause:** lossy compression artifacts in the source.
- **check:** smeared highs on sibilance.
- **fix:** soften the top end; layer a re-recorded double; keep only if the take is irreplaceable.
- **evidence:** practice

### 050 DC offset or subsonic junk
- **severity:** minor
- **says:** "clicks at the start", "speaker moves without sound"
- **cause:** DC offset or energy below 20 Hz.
- **check:** waveform not centred; energy under 20 Hz.
- **fix:** high-pass 20-30 Hz (or a DC filter) early in the chain.
- **evidence:** practice
