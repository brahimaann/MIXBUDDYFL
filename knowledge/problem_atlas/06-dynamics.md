# 06 Dynamics and transients (126-150)

### 126 Words jump in level
- **severity:** major
- **says:** "uneven", "some words too loud", "volume all over the place"
- **cause:** natural delivery dynamics not controlled.
- **check:** analyze_dynamics crest factor (above about 14 dB on a lead is very uneven).
- **fix:** clip-gain rides first, then two gentle compressors (fast FET for peaks, opto for body) rather than one hard one.
- **evidence:** practice, archive

### 127 Over-compressed, lifeless
- **severity:** major
- **says:** "flat", "lifeless", "squashed", "no dynamics"
- **cause:** too much gain reduction or several compressors stacked.
- **check:** very low crest factor (under about 6 dB); count compressors in the chain.
- **fix:** less ratio or threshold; parallel compression instead of more.
- **evidence:** practice, story:clairo

### 128 Pumping and breathing
- **severity:** minor
- **says:** "pumping", "breathing", "level wobbles"
- **cause:** release too fast or slow for the material.
- **check:** audible level dips after loud words.
- **fix:** adjust release (or auto release); less gain reduction.
- **evidence:** practice

### 129 Compressor distorts low notes
- **severity:** minor
- **says:** "distorts on deep words", "gritty on low notes"
- **cause:** a very fast release tracks the waveform.
- **check:** distortion only on low-pitched content.
- **fix:** slower release.
- **evidence:** practice

### 130 Transients poke through
- **severity:** minor
- **says:** "consonants jump out", "spiky"
- **cause:** attack too slow lets the onset through.
- **check:** peaks above the phrase level.
- **fix:** faster attack, or a peak limiter before the main compressor.
- **evidence:** practice

### 131 Consonants dulled
- **severity:** minor
- **says:** "lost the punch on the words", "soft consonants"
- **cause:** attack too fast clamps the onset.
- **check:** transients reduced vs raw.
- **fix:** slower attack.
- **evidence:** practice

### 132 Vocal disappears in loud sections
- **severity:** major
- **says:** "the vocal gets lost in the hook"
- **cause:** the beat gets louder but the vocal doesn't.
- **check:** vocal vs beat level per section.
- **fix:** automate the vocal up in loud sections; duck the beat in the vocal's range.
- **evidence:** practice

### 133 Vocal too loud in quiet sections
- **severity:** minor
- **says:** "vocal is too loud in the intro"
- **cause:** static vocal level with a dynamic arrangement.
- **check:** per-section balance.
- **fix:** automation.
- **evidence:** practice

### 134 Noise rises between phrases
- **severity:** minor
- **says:** "hiss comes up between lines"
- **cause:** compressor makeup gain lifts the noise floor in gaps.
- **check:** analyze_noise_gate gap vs floor after vs before the compressor.
- **fix:** expander before the compressor.
- **evidence:** practice

### 135 Gate chops word tails
- **severity:** minor
- **says:** "words cut off", "choppy"
- **cause:** gate threshold too high or release too fast.
- **check:** tails ending abruptly.
- **fix:** lower threshold, longer hold and release, or use an expander with a limited range.
- **evidence:** practice

### 136 Gate chatter
- **severity:** minor
- **says:** "fluttering", "stuttering on quiet parts"
- **cause:** signal hovering at the threshold.
- **check:** rapid open/close in quiet passages.
- **fix:** hysteresis (if available), more hold, lower range.
- **evidence:** practice

### 137 Drum bus lacks punch
- **severity:** minor
- **says:** "drums are weak", "no knock"
- **cause:** transients lost or no bus glue.
- **check:** crest factor of drum bus.
- **fix:** slow-attack bus compression (bx_glue, SSL-style), transient shaping.
- **evidence:** practice

### 138 Mix squashed by the limiter
- **severity:** major
- **says:** "crushed", "flat master", "no punch after mastering"
- **cause:** too much limiting.
- **check:** PLR under about 8 LU; time at limiter ceiling.
- **fix:** less gain into the limiter; control peaks earlier.
- **evidence:** practice, archive

### 139 Clipping on master peaks
- **severity:** major
- **says:** "crackles on loud parts", "distorted master"
- **cause:** peaks over 0 dBFS or inter-sample overs.
- **check:** true peak above 0 dBTP.
- **fix:** limiter with true-peak ceiling (-1 dBTP for streaming).
- **evidence:** practice

### 140 Parallel compression phasey
- **severity:** minor
- **says:** "phasey when I blend the parallel"
- **cause:** latency mismatch between the dry and compressed paths.
- **check:** comb filtering when both paths play.
- **fix:** use the plugin's mix knob, or make sure FL's delay compensation is on for the bus.
- **evidence:** practice

### 141 Too many compressors stacked
- **severity:** minor
- **says:** "I have 5 compressors and it still sounds wrong"
- **cause:** stacked compressors interact and flatten.
- **check:** fl_get_track_chain; add up the gain reduction.
- **fix:** remove ones that aren't doing a distinct job.
- **evidence:** practice

### 142 Compressor isn't actually compressing
- **severity:** minor
- **says:** "I put a compressor on and nothing changed"
- **cause:** threshold Off, input too low, or bypassed.
- **check:** fl_get_plugin_params (CL 1B Threshold "Off" = no compression); compare crest factor before and after.
- **fix:** set threshold or input so it reaches 2-5 dB of reduction on loud words.
- **evidence:** archive

### 143 Sidechain duck too obvious
- **severity:** minor
- **says:** "you can hear the beat dip"
- **cause:** too much depth or too slow a release.
- **check:** beat level drop when vocal enters.
- **fix:** shallower duck, frequency-limited ducking (Trackspacer bands).
- **evidence:** practice

### 144 Rap verse lacks density
- **severity:** minor
- **says:** "not thick", "verse is weak", "needs more weight"
- **cause:** dynamics fine but not dense.
- **check:** compare RMS with a reference rap vocal.
- **fix:** parallel compression, saturation, a tight double.
- **evidence:** practice

### 145 Sung long notes swell too loud
- **severity:** minor
- **says:** "held notes get too loud"
- **cause:** sustained notes build RMS.
- **check:** level rises during long notes.
- **fix:** opto compression (slow release) or automation.
- **evidence:** practice

### 146 Plosive triggers the compressor
- **severity:** minor
- **says:** "the vocal ducks after P words"
- **cause:** low-frequency burst hits the detector.
- **check:** gain reduction spikes on P/B.
- **fix:** high-pass the sidechain or fix plosives before the compressor (026).
- **evidence:** practice

### 147 De-esser order confusion
- **severity:** minor
- **says:** "de-esser isn't working", "where should the de-esser go?"
- **cause:** de-esser placed before stages that add sibilance.
- **check:** chain order.
- **fix:** de-ess before compression for the main S, plus a light one at the end.
- **evidence:** practice

### 148 Breaths louder after compression
- **severity:** minor
- **says:** "the breaths came up"
- **cause:** compression narrows the gap between breath and voice.
- **check:** breath level vs voice before/after.
- **fix:** clip-gain breaths down before compression.
- **evidence:** practice

### 149 Transient designer overuse
- **severity:** minor
- **says:** "clicky", "thin and spiky"
- **cause:** too much attack boost.
- **check:** transient peaks.
- **fix:** reduce.
- **evidence:** practice

### 150 Compressor doing automation's job
- **severity:** minor
- **says:** "I need tons of compression to keep it even"
- **cause:** large level changes between sections handled by the compressor alone.
- **check:** compressor gain reduction varies a lot per section.
- **fix:** ride clip gain or automation first, compress less.
- **evidence:** practice
