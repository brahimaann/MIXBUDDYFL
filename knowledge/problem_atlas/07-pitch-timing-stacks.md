# 07 Pitch, timing, doubles and stacks (151-175)

### 151 Unintended robotic tuning
- **severity:** major
- **says:** "too auto-tuned", "robotic", "T-Pain when I didn't want it"
- **cause:** retune speed too fast for the style.
- **check:** fl_get_plugin_params on Auto-Tune: Retune Speed near 0.
- **fix:** slower retune (20-50 ms or more), Humanize and Flex-Tune up.
- **evidence:** practice

### 152 Wrong key or scale in the tuner
- **severity:** major
- **says:** "notes jump to the wrong pitch", "tuning sounds off"
- **cause:** Auto-Tune set to the wrong key or scale.
- **check:** read the tuner's key and scale; compare to the beat's key (Auto-Key).
- **fix:** set the right key or use chromatic.
- **evidence:** practice

### 153 Warble on slides and vibrato
- **severity:** minor
- **says:** "warbly", "wobbly tuning"
- **cause:** the tuner fights intentional pitch movement.
- **check:** warble on slides.
- **fix:** Flex-Tune higher; graphic mode on those spots.
- **evidence:** practice

### 154 Chipmunk or formant shift
- **severity:** minor
- **says:** "chipmunk", "Alvin", "sounds fake when pitched"
- **cause:** pitch shifting without formant correction.
- **check:** formant preservation off.
- **fix:** formant correction on (Little AlterBoy, Auto-Tune formant).
- **evidence:** practice

### 155 Low pitched ad-libs muddy
- **severity:** minor
- **says:** "the deep ad-libs are muddy"
- **cause:** pitched-down vocals pile into 100-300 Hz.
- **check:** spectrum of the pitched track.
- **fix:** high-pass and band-limit the pitched layer.
- **evidence:** practice

### 156 Doubles flam on consonants
- **severity:** minor
- **says:** "messy doubles", "double consonants", "sloppy stack"
- **cause:** doubles' consonants not aligned with the lead.
- **check:** visible offsets of T/K/S between lead and doubles.
- **fix:** align (VocAlign) at partial tightness; trim S and T on doubles.
- **evidence:** practice

### 157 Doubles phasey on long notes
- **severity:** minor
- **says:** "swirly when the doubles come in"
- **cause:** near-identical pitch and timing cause comb filtering.
- **check:** swirl on sustained vowels.
- **fix:** slight detune or timing offset, or real separate takes.
- **evidence:** practice, story:boniver

### 158 Harmonies out of tune with each other
- **severity:** minor
- **says:** "harmonies sound sour"
- **cause:** stacked parts individually off.
- **check:** pitch of each layer.
- **fix:** tune each layer (graphic).
- **evidence:** practice

### 159 Doubles too loud
- **severity:** minor
- **says:** "lead lost focus", "doubles overpower"
- **cause:** doubles close to lead level.
- **check:** levels: doubles usually 6-12 dB below the lead.
- **fix:** lower doubles; darken them.
- **evidence:** practice

### 160 Stacked sibilance
- **severity:** minor
- **says:** "the S on the hook is huge"
- **cause:** every layer's S adds up.
- **check:** sibilance spikes on the stack bus.
- **fix:** de-ess doubles hard, or cut S off doubles.
- **evidence:** practice

### 161 Stacked breaths
- **severity:** minor
- **says:** "the hook has a big breath before it"
- **cause:** breaths on every layer add up.
- **check:** breath level on the bus.
- **fix:** remove breaths from doubles, keep the lead's.
- **evidence:** practice

### 162 Rap timing off the pocket
- **severity:** minor
- **says:** "off beat", "rushing", "dragging"
- **cause:** delivery ahead of or behind the beat.
- **check:** word onsets vs the grid.
- **fix:** move phrases, not every syllable; keep intended swing.
- **avoid:** quantizing everything (see Burial: off-grid can be the style).
- **evidence:** practice, story:burial

### 163 Whole vocal late
- **severity:** major
- **says:** "everything is a bit late"
- **cause:** recording latency (037).
- **check:** consistent offset.
- **fix:** nudge the track.
- **evidence:** practice

### 164 Ad-libs cluttered
- **severity:** minor
- **says:** "too many ad-libs", "messy"
- **cause:** ad-libs stepping on lead words.
- **check:** overlaps with the lead's phrases.
- **fix:** keep ad-libs in the gaps; pan and filter them.
- **evidence:** practice

### 165 Tuner glitches on breaths and noise
- **severity:** minor
- **says:** "weird chirps on breaths"
- **cause:** the pitch tracker locks onto noise.
- **check:** glitches on non-pitched sounds.
- **fix:** bypass tuning on breaths, or raise the tracking threshold.
- **evidence:** practice

### 166 Harmonies collapse in mono
- **severity:** minor
- **says:** "harmonies disappear on my phone"
- **cause:** wide stacks out of phase.
- **check:** analyze_stereo_compatibility on the stack bus.
- **fix:** use real separate takes panned, not delay-based widening.
- **evidence:** practice

### 167 Artificial doubler sounds chorusy
- **severity:** minor
- **says:** "fake double", "chorus-y", "metallic double"
- **cause:** plugin doubler with modulation.
- **check:** fl_get_plugin_params on Doubler4: Direct level, voice detune and delay.
- **fix:** lower detune and modulation; use a real take.
- **evidence:** practice

### 168 Wide stack leaves the centre empty
- **severity:** minor
- **says:** "the lead feels set back", "middle is empty", "vocal feels far in the center"
- **cause:** lots of wide layers and a beat with strong centre mids mask the mono lead.
- **check:** vocal vs beat 630-800 Hz and 1-4 kHz with fader compensation.
- **fix:** carve the beat's centre where the lead lives (Trackspacer low cut lowered so it acts down to about 490 Hz).
- **evidence:** archive

### 169 Chopped vocals click at edits
- **severity:** minor
- **says:** "clicks in my chops"
- **cause:** edits not on zero crossings, no fades.
- **check:** clicks at edit points.
- **fix:** short fades at every edit.
- **evidence:** practice

### 170 Clicks at comp edits
- **severity:** minor
- **says:** "tiny clicks"
- **cause:** missing crossfades.
- **check:** clicks between comped takes.
- **fix:** crossfade 5-20 ms.
- **evidence:** practice

### 171 Time-stretch artifacts
- **severity:** minor
- **says:** "warbly", "robotic after stretching", "phasey"
- **cause:** stretch algorithm unsuited to vocals.
- **check:** artifacts after stretching in FL.
- **fix:** pick a vocal-friendly stretch mode (Elastique Pro in FL); stretch less.
- **evidence:** practice, story:burial

### 172 Comped takes don't match
- **severity:** minor
- **says:** "the comp sounds stitched"
- **cause:** takes with different tone and energy.
- **check:** spectral and level differences.
- **fix:** clip-gain and EQ-match pieces.
- **evidence:** practice

### 173 Hook overstuffed with layers
- **severity:** minor
- **says:** "the hook is a blur"
- **cause:** too many layers.
- **check:** count layers; masking.
- **fix:** mute layers until it gets clearer, then add back.
- **evidence:** practice

### 174 Harmonies clash with the sample
- **severity:** minor
- **says:** "harmony sounds wrong with the beat"
- **cause:** harmony notes clash with sample chords.
- **check:** key and chord check.
- **fix:** retune or rewrite the harmony.
- **evidence:** practice

### 175 Vibrato flattened by tuning
- **severity:** minor
- **says:** "lost my vibrato", "too straight"
- **cause:** fast retune kills vibrato.
- **check:** pitch trace flat.
- **fix:** Humanize up or slower retune on sustained notes.
- **evidence:** practice
