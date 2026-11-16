# 04 Low and low-mid tone (076-100)

### 076 Sub rumble under the vocal
- **severity:** minor
- **says:** "rumble", "low noise under the vocal"
- **cause:** energy below about 60 Hz that the voice doesn't need.
- **check:** spectrum below 60 Hz on the vocal.
- **fix:** high-pass 60-90 Hz (rap) or 80-120 Hz (sung, higher voices).
- **evidence:** practice

### 077 Chesty or boomy vocal
- **severity:** minor
- **says:** "too much chest", "boomy", "heavy"
- **cause:** strong 100-200 Hz from proximity or a deep voice.
- **check:** 125-200 Hz bands well above the 1 kHz anchor.
- **fix:** low shelf cut or dynamic band at 120-180 Hz.
- **evidence:** practice

### 078 Muddy vocal
- **severity:** major
- **says:** "muddy", "muffled", "cloudy", "not clear"
- **cause:** build-up around 200-350 Hz.
- **check:** live spectrum 250-500 Hz vs 1 kHz (+5-6 dB measured on a muddy lead; +2-4 dB after fixing).
- **fix:** a broad cut or dynamic band around 250-350 Hz; also check whether saturation's low band is adding it.
- **evidence:** archive, practice

### 079 Boxy vocal
- **severity:** minor
- **says:** "boxy", "cardboard", "small"
- **cause:** 350-550 Hz resonance, often room-related (see 002).
- **check:** a narrow bump in that range.
- **fix:** narrow dynamic cut at the peak.
- **evidence:** practice

### 080 Low-mid build-up across the whole mix
- **severity:** major
- **says:** "the mix is muddy", "everything is blurry"
- **cause:** every track contributes 200-500 Hz and it adds up.
- **check:** compare the master's octave balance to a reference.
- **fix:** small cuts on several non-vocal tracks rather than one big master cut.
- **evidence:** practice

### 081 Vocal thin after high-pass
- **severity:** minor
- **says:** "thin", "no body", "weak"
- **cause:** high-pass set too high or too steep.
- **check:** fundamental region (100-250 Hz for most voices) missing.
- **fix:** lower the high-pass; a gentler slope (12 dB/oct).
- **evidence:** practice

### 082 Deep voice loses its warmth
- **severity:** minor
- **says:** "doesn't sound like me", "lost the bass in my voice"
- **cause:** generic high-pass settings cut a low voice's fundamental.
- **check:** the singer's fundamental frequency is below the high-pass corner.
- **fix:** set the high-pass under the lowest sung fundamental.
- **evidence:** practice

### 083 Kick and 808 fight
- **severity:** major
- **says:** "kick and 808 clash", "low end is a mess", "no punch"
- **cause:** both occupy the same frequency at the same moment.
- **check:** spectral overlap below 100 Hz on the same beats.
- **fix:** sidechain the 808 to the kick (short duck), or give each its own range; tune the kick to the song key.
- **evidence:** practice

### 084 808 inaudible on phones
- **severity:** major
- **says:** "no bass on my phone", "808 disappears on laptop"
- **cause:** small speakers can't reproduce the 808 fundamental.
- **check:** almost no 808 energy above about 150 Hz.
- **fix:** saturate or distort the 808 to add harmonics (Decapitator, Saturn); layer a mid-range version.
- **evidence:** practice

### 085 808 notes uneven
- **severity:** minor
- **says:** "some 808 notes are louder", "low notes disappear"
- **cause:** the sample, the room, or harmonics vary per note.
- **check:** per-note level differences in the low band.
- **fix:** compression or limiting on the 808; check on headphones (room issue 023).
- **evidence:** practice

### 086 808 flubs or distorts in the car
- **severity:** minor
- **says:** "the 808 farts out in the car", "distortion in the low end"
- **cause:** too much sub energy or clipping.
- **check:** sub-band level vs reference; clipping on the 808 channel.
- **fix:** bring the sub down; clip deliberately and controlled; check mono below about 120 Hz.
- **evidence:** practice

### 087 808 tail out of key or clashing
- **severity:** minor
- **says:** "808 sounds off", "out of tune bass"
- **cause:** 808 tuned wrong or tail rings into the next chord.
- **check:** 808 pitch vs song key.
- **fix:** retune the 808; shorten the decay.
- **evidence:** practice

### 088 Bass masks the vocal's fundamental
- **severity:** minor
- **says:** "the vocal has no weight in the mix"
- **cause:** bass or 808 harmonics sit on the vocal's 100-300 Hz.
- **check:** vocal vs beat masking at 125-315 Hz.
- **fix:** sidechain EQ on the bass in that range keyed to the vocal.
- **evidence:** practice

### 089 Stereo low end
- **severity:** minor
- **says:** "bass sounds weird in mono", "low end disappears on the club system"
- **cause:** stereo width or phase differences below about 120 Hz.
- **check:** analyze_stereo_compatibility sub phase.
- **fix:** mono the lows below about 120 Hz (Ozone Imager, bx_digital mono maker).
- **evidence:** practice

### 090 Sub too loud on headphones vs speakers
- **severity:** minor
- **says:** "bass is huge in headphones, missing on speakers"
- **cause:** headphone and speaker low-frequency response differ a lot.
- **check:** compare with a reference's sub level.
- **fix:** set the sub by reference and meter.
- **evidence:** practice

### 091 Kick lacks punch
- **severity:** minor
- **says:** "kick doesn't hit", "soft kick"
- **cause:** no click or attack, or the transient is lost under the 808.
- **check:** transient level in 2-5 kHz for the click.
- **fix:** transient shaping or a click layer; slower attack on the compressor.
- **evidence:** practice

### 092 Two-track beat muddy in the low-mids
- **severity:** major
- **says:** "the beat is muddy", "no room for my vocal"
- **cause:** a pre-mixed beat with heavy 200-500 Hz.
- **check:** the beat's octave balance vs reference.
- **fix:** gentle broad cut on the beat; dynamic cut keyed to the vocal.
- **evidence:** practice

### 093 Reverb return adds mud
- **severity:** minor
- **says:** "the reverb makes it muddy"
- **cause:** unfiltered reverb returns low-mids.
- **check:** reverb return's spectrum below 300 Hz.
- **fix:** high-pass the reverb return 200-400 Hz.
- **evidence:** practice

### 094 Stacks pile up low-mids
- **severity:** minor
- **says:** "the hook gets muddy when the stacks come in"
- **cause:** every double adds 200-400 Hz.
- **check:** bus spectrum when stacks enter.
- **fix:** high-pass doubles higher than the lead (150-250 Hz).
- **evidence:** practice

### 095 Wants warmth without mud
- **severity:** minor
- **says:** "make it warmer but not muddy"
- **cause:** warmth comes from harmonics and slight low-mid weight; mud is excess in 200-350 Hz.
- **check:** octave balance; harmonic content.
- **fix:** tape or tube saturation rather than a low-mid boost; a gentle shelf at 100-150 Hz.
- **evidence:** practice, research:safe

### 096 Sidechain pumping too strong
- **severity:** minor
- **says:** "the beat breathes too much", "pumping"
- **cause:** sidechain depth or release too much.
- **check:** level dips on every kick.
- **fix:** less depth, faster release, or a shorter duck.
- **evidence:** practice

### 097 Beat's low end shifts when the vocal comes in
- **severity:** minor
- **says:** "the bass drops when I rap"
- **cause:** a bus compressor reacting to the vocal.
- **check:** bus gain reduction rises with vocal entries.
- **fix:** high-pass the compressor's sidechain; less bus compression.
- **evidence:** practice

### 098 Kick and 808 layers cancel
- **severity:** minor
- **says:** "low end gets weaker when I add the layer"
- **cause:** phase cancellation between layered low sounds.
- **check:** summed low-band level drops.
- **fix:** align samples; flip polarity; pick one fundamental.
- **evidence:** practice

### 099 Low shelf bloat
- **severity:** minor
- **says:** "too bassy", "bloated"
- **cause:** a low shelf boost raised everything below the corner, including mud.
- **check:** low shelf gain on the EQ.
- **fix:** replace with a narrower bell at the fundamental.
- **evidence:** practice

### 100 One low note rings out
- **severity:** minor
- **says:** "one bass note sticks out"
- **cause:** an instrument or room resonance on one pitch.
- **check:** a narrow low-frequency peak.
- **fix:** narrow dynamic cut on that note.
- **evidence:** practice
