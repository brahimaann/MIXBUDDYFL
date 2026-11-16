# 10 Gain staging, loudness, translation and delivery (226-250)

### 226 Mix too quiet vs references
- **severity:** minor
- **says:** "my song is quieter than everything else", "not loud enough"
- **cause:** integrated loudness lower than references.
- **check:** analyze_loudness on the bounce and the reference.
- **fix:** limiter gain on the master after controlling peaks earlier; streaming normalises anyway (about -14 LUFS).
- **evidence:** practice, archive

### 227 Mix too loud for streaming
- **severity:** minor
- **says:** "Spotify turned it down", "sounds smaller on streaming"
- **cause:** very loud masters are turned down and lose punch vs dynamic ones.
- **check:** LUFS and PLR.
- **fix:** less limiting; aim for punch, not maximum loudness.
- **evidence:** practice

### 228 True-peak overs
- **severity:** major
- **says:** "distortion after upload"
- **cause:** inter-sample peaks over 0 dBTP.
- **check:** true peak.
- **fix:** true-peak limiter ceiling at -1 dBTP.
- **evidence:** practice

### 229 Hum in the final mix
- **severity:** minor
- **says:** "hum at the end", "buzz under everything"
- **cause:** a hum on one source (021).
- **check:** 60 Hz peaks; solo tracks to find the source.
- **fix:** de-hum the source track.
- **evidence:** practice

### 230 Hiss raised by gain
- **severity:** minor
- **says:** "hissy mix"
- **cause:** noisy sources raised.
- **check:** noise floor on solos.
- **fix:** noise reduction on the source.
- **evidence:** practice

### 231 Vocal too loud on phone speakers
- **severity:** minor
- **says:** "vocal is huge on my phone"
- **cause:** phones emphasise mids where the vocal lives.
- **check:** listen on phone; compare with a reference.
- **fix:** balance on several systems; small vocal level adjustments.
- **evidence:** practice

### 232 Vocal disappears in the car
- **severity:** minor
- **says:** "can't hear the vocal in the car"
- **cause:** the car exaggerates lows; vocal presence too low.
- **check:** low-end level vs reference.
- **fix:** lower the low end, raise presence slightly.
- **evidence:** practice

### 233 Bass disappears on laptops and phones
- **severity:** minor
- **says:** "no bass on my laptop"
- **cause:** no harmonics on the low elements (084).
- **check:** 808 above 150 Hz.
- **fix:** saturate the low end.
- **evidence:** practice

### 234 Harsh on earbuds
- **severity:** minor
- **says:** "hurts on earbuds"
- **cause:** see 125.
- **check:** 2-5 kHz vs reference.
- **fix:** dynamic cut.
- **evidence:** practice

### 235 Headphones vs speakers translation
- **severity:** minor
- **says:** "sounds different everywhere"
- **cause:** an unreliable monitoring chain.
- **check:** reference against a known commercial track.
- **fix:** reference regularly.
- **evidence:** practice

### 236 Elements vanish in mono
- **severity:** minor
- **says:** "the synth disappears on my phone"
- **cause:** phase-wide elements.
- **check:** stereo compatibility on the master.
- **fix:** reduce width on those elements.
- **evidence:** practice

### 237 Tracks clipping in FL's mixer
- **severity:** minor
- **says:** "the meter is red", "track clipping"
- **cause:** hot levels inside the chain (FL uses floating point, but some plugins misbehave when driven hot).
- **check:** fl_get_mixer include="levels" peaks.
- **fix:** lower track inputs or plugin outputs; keep peaks around -6 dBFS.
- **evidence:** practice

### 238 Saturation driven wrong
- **severity:** minor
- **says:** "saturator does nothing", "saturator too crunchy"
- **cause:** input level not where the saturation's character is.
- **check:** level arriving at the plugin.
- **fix:** gain-stage into it, then output trim.
- **evidence:** practice

### 239 Bounce differs from playback
- **severity:** minor
- **says:** "the export sounds different"
- **cause:** export settings, live-only plugins or tails.
- **check:** compare bounce with playback analysis.
- **fix:** check FL export settings (resampling, tails); bounce again.
- **evidence:** practice

### 240 Wrong export format
- **severity:** minor
- **says:** "the file is wrong format"
- **cause:** sample rate or bit depth.
- **check:** file format.
- **fix:** export 24-bit WAV at the project rate; dither only at the final 16-bit step.
- **evidence:** practice

### 241 Master ceiling choice
- **severity:** minor
- **says:** "what ceiling should I use", "is -3 dBTP right?"
- **cause:** a too-cautious or too-hot limiter ceiling.
- **check:** limiter ceiling; true peak.
- **fix:** -1 dBTP for release; bypass the limiter if sending to a mastering engineer.
- **evidence:** archive

### 242 Songs on an EP at different levels
- **severity:** minor
- **says:** "song 2 is louder than song 3"
- **cause:** masters at different loudness.
- **check:** LUFS of each song.
- **fix:** match loudness across the project.
- **evidence:** practice

### 243 Loudness range too small
- **severity:** minor
- **says:** "no build-up", "flat song"
- **cause:** over-compressed song-level dynamics.
- **check:** LRA (2-3 LU is very consistent).
- **fix:** allow more level change between sections.
- **evidence:** archive

### 244 Stems don't add up to the mix
- **severity:** minor
- **says:** "stems sound different from the mix"
- **cause:** master processing or sends missing from stems.
- **check:** sum the stems vs the mix.
- **fix:** export with sends and master bypassed consistently.
- **evidence:** practice

### 245 Mix bus compression changes the vocal balance
- **severity:** minor
- **says:** "vocal gets lower when the mix gets loud"
- **cause:** the bus compressor reacts.
- **check:** bus gain reduction.
- **fix:** less ratio, high-pass the sidechain.
- **evidence:** practice

### 246 CPU crackles on playback
- **severity:** major
- **says:** "crackling", "audio glitches", "FL stutters"
- **cause:** CPU overload on the laptop (Ryzen 7 3700U).
- **check:** FL CPU meter; heavy plugins (oversampling, linear phase).
- **fix:** bigger buffer; freeze/render heavy tracks; turn off oversampling while writing.
- **evidence:** practice

### 247 Latency makes recording impossible
- **severity:** minor
- **says:** "delay in my headphones"
- **cause:** lookahead or linear-phase plugins on the chain.
- **check:** plugin latency.
- **fix:** bypass heavy plugins while recording.
- **evidence:** practice

### 248 Mix sounds different the next day
- **severity:** minor
- **says:** "sounded great last night"
- **cause:** ear fatigue and changing listening level.
- **check:** compare at a fixed listening level.
- **fix:** take breaks; reference; check at low level.
- **evidence:** practice

### 249 Comparing a mix with a mastered reference
- **severity:** minor
- **says:** "my mix sounds weak next to the reference"
- **cause:** the reference is mastered and louder.
- **check:** LUFS of both.
- **fix:** level-match before comparing (compare_to_reference reports the difference).
- **evidence:** practice

### 250 Polarity-inverted element
- **severity:** minor
- **says:** "something disappears in mono", "weak low end"
- **cause:** one element's polarity flipped.
- **check:** stereo compatibility; mono sum.
- **fix:** flip polarity back.
- **evidence:** practice
