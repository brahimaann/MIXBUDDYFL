# 05 Mid, high-mid and high tone (101-125)

### 101 Honky mids
- **severity:** minor
- **says:** "honky", "cupped hands", "megaphone"
- **cause:** excess 600-900 Hz.
- **check:** a bump in those bands vs neighbours.
- **fix:** dynamic or static cut, moderate Q.
- **evidence:** practice

### 102 Tinny or telephone tone
- **severity:** minor
- **says:** "tinny", "telephone", "small speaker sound"
- **cause:** strong 1-2 kHz with weak lows and highs.
- **check:** octave balance peaks in 1-2 kHz.
- **fix:** cut 1-2 kHz slightly; restore lows and highs.
- **evidence:** practice

### 103 Harsh upper mids
- **severity:** major
- **says:** "harsh", "painful", "ear fatigue", "edgy"
- **cause:** excess 2.5-5 kHz, often from mic, compression or saturation.
- **check:** spectrum 2.5-5 kHz above reference; worse at high volume.
- **fix:** soothe2 or dynamic EQ there; reduce saturation drive.
- **evidence:** practice, research:socialfx

### 104 Brittle, metallic top
- **severity:** minor
- **says:** "metallic", "brittle", "sizzly", "fizzy"
- **cause:** excess 6-9 kHz, often from exciters or aliasing.
- **check:** spectrum 6-9 kHz.
- **fix:** narrow cuts; check exciter settings and oversampling.
- **evidence:** practice

### 105 Dark vocal
- **severity:** major
- **says:** "dark", "dull", "muffled", "no air", "lifeless"
- **cause:** little energy above about 6 kHz (dark mic or room, or a dark recording).
- **check:** steep fall above 6 kHz; spectral centroid low.
- **fix:** saturation first to generate upper harmonics, then a high shelf or air boost (Fresh Air); EQ boosts alone can't add what isn't there.
- **evidence:** archive, story:boniver, story:peep

### 106 Lacks presence
- **severity:** major
- **says:** "behind the beat", "not in your face", "lacks presence"
- **cause:** too little 3-5 kHz relative to vowels, or masking.
- **check:** vocal vs beat 2-5 kHz with fader compensation.
- **fix:** a presence lift or upper-mid saturation; carve the beat.
- **evidence:** archive, practice

### 107 Too much air or breathiness
- **severity:** minor
- **says:** "hissy", "too airy", "breathy"
- **cause:** high shelf boosts emphasizing breath noise.
- **check:** above 10 kHz much higher than reference.
- **fix:** reduce the shelf; de-ess the air band.
- **evidence:** practice

### 108 Narrow resonances ringing
- **severity:** minor
- **says:** "whistling", "a weird ring", "piercing note"
- **cause:** narrow resonant peaks from the mic, room or voice.
- **check:** resonance list in the spectrum analysis (beware: harmonics of the sung note look like resonances).
- **fix:** narrow dynamic cuts or soothe2.
- **evidence:** practice

### 109 Harsh only on loud notes
- **severity:** minor
- **says:** "only harsh when I push"
- **cause:** upper harmonics rise with level.
- **check:** harshness tracks level.
- **fix:** dynamic EQ, not static.
- **evidence:** practice

### 110 Hi-hats fight the sibilance
- **severity:** minor
- **says:** "the hats and S are fighting", "too much top"
- **cause:** both live around 7-10 kHz.
- **check:** beat vs vocal masking in 6-10 kHz.
- **fix:** lower the hats; sidechain-duck the hats' top lightly to the vocal.
- **evidence:** practice

### 111 Synth or guitar clashing at 1-3 kHz
- **severity:** minor
- **says:** "the synth is in the way"
- **cause:** an instrument occupying the vocal's presence range.
- **check:** masking in 1-3 kHz.
- **fix:** dynamic EQ keyed to the vocal; pan the instrument off-centre.
- **evidence:** practice

### 112 Hollow from too many cuts
- **severity:** minor
- **says:** "hollow", "phasey", "thin and weird"
- **cause:** many narrow EQ cuts carve out the vocal's body.
- **check:** count active cuts; octave balance shows holes.
- **fix:** remove cuts that don't fix a measured problem.
- **evidence:** practice

### 113 Plastic, over-bright
- **severity:** minor
- **says:** "plastic", "fake", "too shiny"
- **cause:** stacked exciters and shelves.
- **check:** highs far above reference.
- **fix:** remove one brightening stage; replace with saturation.
- **evidence:** practice

### 114 Grainy highs from saturation
- **severity:** minor
- **says:** "grainy", "crunchy highs", "digital"
- **cause:** aliasing from saturation without oversampling.
- **check:** inharmonic energy in the top octave.
- **fix:** turn on oversampling (costs CPU) or lower drive.
- **evidence:** practice

### 115 Wants a lo-fi or telephone sound on purpose
- **severity:** minor
- **says:** "make it lo-fi", "old radio vibe", "phone vocal"
- **cause:** creative band-limiting is the goal.
- **check:** n/a.
- **fix:** band-pass around 300 Hz-3 kHz, saturation, slight bit-crush; keep the beat full-range for contrast.
- **evidence:** story:lacy, story:nigro

### 116 Vocal sounds small
- **severity:** minor
- **says:** "small", "weak", "not big enough"
- **cause:** lacks body and harmonic density.
- **check:** low crest density; little 150-300 Hz.
- **fix:** saturation, light compression, a double; not just EQ.
- **evidence:** practice

### 117 Harsh after streaming encoding
- **severity:** minor
- **says:** "sounds worse on Spotify"
- **cause:** lossy encoding stresses harsh highs and hot true peaks.
- **check:** true peak above -1 dBTP; harsh 6-10 kHz.
- **fix:** true-peak ceiling at -1 dBTP; tame the top.
- **evidence:** practice

### 118 Vocal sounds cheap
- **severity:** minor
- **says:** "cheap", "amateur", "demo-y"
- **cause:** usually several small things: uneven level, no density, mismatched space.
- **check:** run the cleanup chain: loudness, dynamics, spectrum, clarity.
- **fix:** level rides, saturation, one good reverb, de-essing.
- **evidence:** practice

### 119 Muffled from over-processing
- **severity:** minor
- **says:** "muffled after the chain"
- **cause:** soothe2, de-esser or multiband too deep.
- **check:** compare taps pre and post chain.
- **fix:** reduce depth and range.
- **evidence:** practice

### 120 Sterile, digital
- **severity:** minor
- **says:** "too clean", "digital", "sterile", "no vibe"
- **cause:** lack of harmonic colour.
- **check:** n/a.
- **fix:** tape or tube saturation, light vintage EQ.
- **evidence:** practice, story:nigro

### 121 Bright voice on a bright mic
- **severity:** minor
- **says:** "too bright", "harsh"
- **cause:** the mic's presence peak doubles the voice's own brightness.
- **check:** fixed peak across takes.
- **fix:** static cut on the mic peak.
- **evidence:** practice

### 122 Verses recorded on different days don't match
- **severity:** minor
- **says:** "the two verses sound different"
- **cause:** mic position or voice changed.
- **check:** third-octave comparison.
- **fix:** EQ match.
- **evidence:** practice, story:parker

### 123 Hollow after cutting too much around 1 kHz
- **severity:** minor
- **says:** "hollow", "scooped"
- **cause:** deep mid cuts remove body (the opposite of 057).
- **check:** a dip at 800 Hz-1.2 kHz relative to neighbours.
- **fix:** reduce the cut and make it dynamic.
- **evidence:** archive

### 124 Ad-libs too bright
- **severity:** minor
- **says:** "ad-libs are harsh", "ad-libs compete with the lead"
- **cause:** ad-libs processed as bright as the lead.
- **check:** ad-lib bus highs vs lead.
- **fix:** low-pass or darken ad-libs; give the lead the brightest top.
- **evidence:** practice

### 125 Harsh on earbuds
- **severity:** minor
- **says:** "hurts on AirPods"
- **cause:** earbuds emphasise 2-5 kHz.
- **check:** check on earbuds; spectrum 2-5 kHz vs reference.
- **fix:** gentle dynamic cut 2-5 kHz.
- **evidence:** practice
