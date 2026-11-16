# 01 Room and recording environment (001-025)

### 001 Flutter echo
- **severity:** major
- **says:** "zing after every word", "sounds like a hallway", "metallic ringing", "boingy echo"
- **cause:** sound bouncing between two parallel hard surfaces creates fast repeating reflections.
- **check:** clap in the recording spot and listen for a buzzy tail; analyze_noise_gate shows gap level well above noise floor right after phrases.
- **fix:** move the mic away from parallel walls or angle yourself into a corner with clothes or a duvet behind you; in the mix, a narrow cut on the ring frequency plus a gentle expander (Pro-G, range 6-10 dB) for the tails.
- **avoid:** adding reverb to "hide" it; it multiplies the ring.
- **evidence:** practice, story:doja

### 002 Small-room boxiness
- **severity:** major
- **says:** "cardboard box", "sounds like a closet", "boxy", "small", "hollow"
- **cause:** early reflections from walls close to the mic build a peak around 300-600 Hz.
- **check:** live spectrum shows 300-600 Hz bump vs neighbouring octaves (above about +3 dB vs the 1 kHz anchor on a lead); sweep a narrow boost to find the ring.
- **fix:** dynamic Pro-Q band at the ring (Q 2-4, -2 to -4 dB dynamic) rather than a deep static cut; next session put absorption behind the singer (the mic hears what's behind you).
- **avoid:** wide static cuts that leave the vocal thin.
- **evidence:** practice, story:billie

### 003 Comb filtering from a nearby surface
- **severity:** minor
- **says:** "phasey", "swirly", "hollow", "like through a tube"
- **cause:** a desk, monitor screen or wall close to the mic reflects a delayed copy that cancels some frequencies.
- **check:** spectrum shows regularly spaced dips; changes when the singer moves a few inches.
- **fix:** at tracking, cover the desk/screen or turn the mic; in the mix it can't be removed, only softened with broad EQ and saturation to fill the notches.
- **evidence:** practice

### 004 Room-mode boom on a deep voice
- **severity:** major
- **says:** "boomy on certain words", "one note blows up", "woofy"
- **cause:** room dimensions reinforce specific low notes, so some sung pitches jump in the low end.
- **check:** level jumps on specific pitches; spectrum peak 80-200 Hz that comes and goes with the melody.
- **fix:** dynamic EQ band on the mode (narrow, triggered only when it rings); high-pass at 70-100 Hz; record further from walls and corners next time.
- **evidence:** practice

### 005 Room tail between phrases
- **severity:** minor
- **says:** "room sound", "echoey gaps", "not dry", "distant"
- **cause:** the room's reverb is captured after each phrase, then raised by compression.
- **check:** analyze_noise_gate: gap level vs noise floor (more than about 15 dB above the floor = audible room); worse after the compressor.
- **fix:** expander or gate before compression with a slow release; or a de-reverb tool sparingly; close-mic and sing quieter into it next time.
- **avoid:** aggressive de-reverb (see 025).
- **evidence:** practice, story:billie

### 006 HVAC / air-conditioner rumble
- **severity:** minor
- **says:** "low rumble", "air noise", "whoosh underneath"
- **cause:** broadband low-frequency noise from air handling.
- **check:** spectrum of a silent gap: energy below 120 Hz and broadband hiss.
- **fix:** high-pass 70-100 Hz; a noise-print reduction on gaps; turn the AC off while tracking.
- **evidence:** practice

### 007 Laptop or PC fan noise
- **severity:** minor
- **says:** "hiss", "fan whine", "computer noise"
- **cause:** fan noise and coil whine reach the mic, often with a tonal whine.
- **check:** gap spectrum shows a steady tone (often 1-6 kHz) and broadband hiss.
- **fix:** put the laptop behind the mic (cardioid rejection) or further away; narrow notch on the whine; expander for gaps.
- **evidence:** practice

### 008 Appliance hum
- **severity:** minor
- **says:** "hum", "buzz", "electric noise"
- **cause:** fridges, lights or dimmers adding a tone at mains frequency (60 Hz US) and harmonics.
- **check:** narrow peaks at 60/120/180 Hz in the gap spectrum.
- **fix:** narrow notches at the fundamental and first harmonics, or a dedicated de-hum; unplug the source while tracking.
- **evidence:** practice

### 009 Street and traffic bleed
- **severity:** minor
- **says:** "cars in the background", "outside noise"
- **cause:** low-frequency traffic noise passes through windows.
- **check:** intermittent low-end bursts in gaps.
- **fix:** high-pass; manual edits to remove bursts; record at quieter hours.
- **evidence:** practice

### 010 Household voices or TV bleed
- **severity:** minor
- **says:** "I can hear people talking", "TV in the background"
- **cause:** other voices recorded in the gaps or under quiet lines.
- **check:** listen solo to gaps; the gap level is above noise floor and has speech character.
- **fix:** cut the gaps by hand; if under singing, punch in that line again.
- **avoid:** treating everything as a defect; sometimes it's character (decide first).
- **evidence:** practice, story:fiona

### 011 Closet booth too dead
- **severity:** minor
- **says:** "muffled", "dead", "choked", "no air"
- **cause:** clothes absorb highs but not lows, so a closet makes a dark, boomy vocal.
- **check:** spectrum tilts down steeply above 4 kHz and the 150-300 Hz region is heavy.
- **fix:** high shelf or Fresh Air-style air boost, plus a cut at 200-300 Hz; saturation to regenerate upper harmonics if the source is very dark.
- **evidence:** practice, story:oldtownroad

### 012 Window or glass reflection
- **severity:** minor
- **says:** "harsh room", "brittle", "glassy"
- **cause:** hard glass reflects highs strongly back into the mic.
- **check:** brighter than expected 2-8 kHz with a short metallic tail.
- **fix:** hang a blanket over the window while tracking; soothe2 or dynamic EQ on the harsh zone.
- **evidence:** practice

### 013 Hard floor reflection
- **severity:** minor
- **says:** "thin and phasey", "weird hollow sound"
- **cause:** a wood or tile floor reflects up into the mic.
- **check:** comb notches like 003; better when a rug is down.
- **fix:** rug under the singer; angle the mic down slightly toward the mouth from above.
- **evidence:** practice

### 014 Sessions recorded in different rooms
- **severity:** major
- **says:** "verse sounds different from the hook", "two different vocals"
- **cause:** each room and mic position colours the voice differently.
- **check:** compare third-octave spectra of the two sections; differences over about 2 dB in a band are audible.
- **fix:** EQ-match section by section (Ozone Match EQ or a manual Pro-Q curve on one part); same compressor chain after the match.
- **evidence:** practice

### 015 Bathroom or kitchen recording
- **severity:** major
- **says:** "echoey", "shower sound", "too much reverb already"
- **cause:** tiled rooms have long, bright reverb.
- **check:** analyze_noise_gate: long tails; spectrum bright.
- **fix:** de-reverb lightly, gate the tails, use only short or no added reverb; re-record if it's the lead.
- **evidence:** practice

### 016 Recording in a car
- **severity:** minor
- **says:** "boomy", "boxy", "close and stuffy"
- **cause:** a small cabin with soft seats: boomy lows, dead highs, cabin resonances.
- **check:** strong 100-250 Hz, quick high roll-off.
- **fix:** high-pass, cut the cabin resonance, add air; works well dry for intimate verses.
- **evidence:** practice

### 017 Wind or breath blasts on an outdoor or phone recording
- **severity:** minor
- **says:** "thumps", "wind noise", "rumbly bursts"
- **cause:** air hitting the capsule.
- **check:** low-frequency bursts below 150 Hz not matching the singing.
- **fix:** steep high-pass, clip-gain the bursts down, or edit them out.
- **evidence:** practice

### 018 Reflection filter colouration
- **severity:** minor
- **says:** "boxy even with the shield", "cupped sound"
- **cause:** small curved reflection filters can add their own mid colour and do little for the room behind the singer.
- **check:** a peak in the 500 Hz-1.5 kHz range compared with recording without it.
- **fix:** put absorption behind the singer instead; EQ the peak.
- **evidence:** practice

### 019 Pets, birds, life in the background
- **severity:** minor
- **says:** "is that my dog", "random noise"
- **cause:** environmental sounds captured in the take.
- **check:** listen to gaps solo.
- **fix:** decide: remove by editing, or keep as texture.
- **evidence:** practice, story:fiona

### 020 Phone interference buzz
- **severity:** minor
- **says:** "digital buzzing", "chirping noise"
- **cause:** a mobile phone near cables or the interface induces bursts.
- **check:** rhythmic buzzy bursts, often in gaps.
- **fix:** edit out; keep phones away from the interface and mic cables when tracking.
- **evidence:** practice

### 021 Ground-loop hum from a laptop charger
- **severity:** major
- **says:** "hum only when plugged in", "constant buzz"
- **cause:** ground loop between laptop power and the interface or monitors.
- **check:** 60 Hz plus harmonics, disappears on battery.
- **fix:** record on battery; use a ground-isolated USB hub or DI; de-hum in the mix.
- **evidence:** practice

### 022 Room tone jumps between punch-ins
- **severity:** minor
- **says:** "background changes", "you can hear the edits"
- **cause:** punch-ins recorded with different noise or room sound.
- **check:** noise floor level differs between takes.
- **fix:** crossfades, a consistent gate/expander, or a little room tone under the edits.
- **evidence:** practice, story:fiona

### 023 The mixing room lies about the low end
- **severity:** major
- **says:** "bass is fine here but huge in the car", "mix is muddy everywhere else"
- **cause:** room modes at the listening position make some bass notes too loud and others vanish.
- **check:** compare the mix's octave balance (63-250 Hz) with a reference in analyze_frequency_spectrum.
- **fix:** decide low end on headphones plus a reference; set 808 and kick by meter and reference, not by the room.
- **evidence:** practice

### 024 Mixing only on headphones
- **severity:** minor
- **says:** "sounds wide and dry on headphones, weird on speakers"
- **cause:** headphones exaggerate width and hide reverb and low-mid build-up.
- **check:** analyze_stereo_compatibility (correlation, mono loss); check reverb level against a reference.
- **fix:** check mono, check on phone and car, reference often.
- **evidence:** practice

### 025 Over-processed de-reverb
- **severity:** minor
- **says:** "underwater", "watery", "warbly", "robot artifacts"
- **cause:** spectral de-reverb or noise reduction pushed too far creates artifacts.
- **check:** artifacts appear on sustained vowels and tails.
- **fix:** back off the amount; combine light de-reverb with an expander instead of heavy single-stage removal.
- **evidence:** practice
