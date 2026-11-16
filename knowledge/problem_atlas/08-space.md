# 08 Reverb, delay and depth (176-200)

### 176 Washed-out, distant vocal
- **severity:** major
- **says:** "too much reverb", "washed out", "distant", "far away"
- **cause:** reverb level or decay too much while the vocal is singing.
- **check:** reverb level while singing vs in the gaps (on the verb tap).
- **fix:** lower the send; add pre-delay; duck the reverb with the vocal.
- **evidence:** archive, practice

### 177 Dry karaoke vocal
- **severity:** major
- **says:** "karaoke", "pasted on top", "too dry", "not in the beat"
- **cause:** no shared space with the beat.
- **check:** verb send level; listen in context.
- **fix:** short room (decay 0.3-0.8 s, short pre-delay) at low level, plus a tempo delay.
- **evidence:** practice, story:oldtownroad

### 178 Reverb tail muddies the next line
- **severity:** minor
- **says:** "the reverb gets in the way of the next words"
- **cause:** decay longer than the gaps between phrases.
- **check:** tail still loud at the next phrase onset.
- **fix:** shorter decay, or duck the reverb with the vocal.
- **evidence:** practice

### 179 Sibilance splashes in the reverb
- **severity:** minor
- **says:** "the S sprays in the reverb"
- **cause:** S hitting a bright reverb.
- **check:** reverb return sparkle on S.
- **fix:** de-ess the send, or low-pass the verb around 6-8 kHz.
- **evidence:** archive

### 180 Reverb too bright or metallic
- **severity:** minor
- **says:** "metallic reverb", "tinny verb"
- **cause:** an untamed bright algorithm.
- **check:** reverb return spectrum.
- **fix:** high-cut the return; a darker mode (1970s/1980s in VintageVerb).
- **evidence:** practice

### 181 Reverb muddy low end
- **severity:** minor
- **says:** "reverb is muddy"
- **cause:** unfiltered lows in the verb.
- **check:** return below 300 Hz.
- **fix:** high-pass the return.
- **evidence:** practice

### 182 No pre-delay smears the vocal
- **severity:** minor
- **says:** "blurry", "the reverb covers the words"
- **cause:** reverb starts with the dry sound.
- **check:** pre-delay at 0.
- **fix:** pre-delay 40-100 ms.
- **evidence:** archive

### 183 Delay off tempo or cluttered
- **severity:** minor
- **says:** "the echo is messy"
- **cause:** delay not synced or too much feedback.
- **check:** delay time vs tempo.
- **fix:** sync to 1/4 or 1/8; less feedback; filter the repeats.
- **evidence:** practice

### 184 Delay throws too loud or too quiet
- **severity:** minor
- **says:** "the echo on the last word is too much"
- **cause:** throw level not balanced.
- **check:** in context.
- **fix:** automate throw sends per phrase end.
- **evidence:** practice

### 185 Slapback comb filtering
- **severity:** minor
- **says:** "phasey echo", "metallic short delay"
- **cause:** very short delay times interfere with the dry signal.
- **check:** delay under about 30 ms.
- **fix:** longer slap (80-130 ms), or filter it.
- **evidence:** practice

### 186 Reverb doesn't match the beat's space
- **severity:** minor
- **says:** "the vocal is in a different room"
- **cause:** the beat has its own reverb character.
- **check:** listen; compare decay.
- **fix:** pick a reverb similar to the beat's ambience.
- **evidence:** practice

### 187 Reverb pumping
- **severity:** minor
- **says:** "the reverb breathes weird"
- **cause:** compression after the reverb or on the bus.
- **check:** chain order.
- **fix:** reverb on a send, compress before it.
- **evidence:** practice

### 188 Stereo reverb collapses in mono
- **severity:** minor
- **says:** "reverb disappears on phone"
- **cause:** a decorrelated stereo verb cancels in mono.
- **check:** analyze_stereo_compatibility on the verb return.
- **fix:** narrow the verb width slightly.
- **evidence:** practice

### 189 Wants a wash but keeps clarity
- **severity:** minor
- **says:** "how do I get a wash", "big dreamy reverb but clear vocal"
- **cause:** big reverb normally masks words.
- **check:** reverb level while singing vs in gaps.
- **fix:** a long hall (about 3-4 s) with 80+ ms pre-delay, the return high-cut around 7-8 kHz, ducked under the vocal so the wash fills the gaps.
- **evidence:** archive, story:grimes

### 190 Reverb needs ducking
- **severity:** minor
- **says:** "want the reverb only between lines"
- **cause:** the reverb competes while singing.
- **check:** n/a.
- **fix:** sidechain compression on the verb return keyed to the vocal.
- **evidence:** practice

### 191 Ad-libs not separated from the lead
- **severity:** minor
- **says:** "ad-libs blend into the lead"
- **cause:** same position, tone and space.
- **check:** pan, EQ and verb settings.
- **fix:** pan ad-libs, give them a different verb or delay.
- **evidence:** practice

### 192 Vocal sits in front of the beat, not in it
- **severity:** minor
- **says:** "doesn't sit in the beat", "not glued", "two separate things"
- **cause:** no shared processing or space.
- **check:** n/a.
- **fix:** short shared room, light bus compression on vocal + beat together, matched saturation.
- **evidence:** practice, story:oldtownroad

### 193 Doubles at a different distance
- **severity:** minor
- **says:** "doubles sound far away"
- **cause:** different reverb amounts.
- **check:** send levels.
- **fix:** match or deliberately set depth.
- **evidence:** practice

### 194 Stereo effects unfocus the lead
- **severity:** minor
- **says:** "the lead is blurry", "not centred"
- **cause:** wideners or chorus on the lead.
- **check:** analyze_stereo_compatibility on the lead.
- **fix:** keep the lead mono; widen only effects.
- **evidence:** practice

### 195 Reverb bus phasing
- **severity:** minor
- **says:** "phasey when the reverb is up"
- **cause:** latency on the send path or a dry signal in the verb.
- **check:** verb Mix at 100% on a send; plugin delay compensation.
- **fix:** Mix 100% wet on sends.
- **evidence:** practice

### 196 Recorded room plus added reverb
- **severity:** minor
- **says:** "too much space even with little reverb"
- **cause:** the room's reverb adds to the plugin's.
- **check:** analyze_noise_gate tails on the raw take.
- **fix:** less added reverb; expand the room first.
- **evidence:** practice

### 197 Delay feedback runaway
- **severity:** minor
- **says:** "the echo keeps building"
- **cause:** feedback too high.
- **check:** feedback near 100%.
- **fix:** reduce feedback; filter repeats.
- **evidence:** practice

### 198 Delays on every word
- **severity:** minor
- **says:** "too busy", "echoey everywhere"
- **cause:** a constant delay send.
- **check:** send level constant.
- **fix:** throws on phrase ends only.
- **evidence:** practice

### 199 Modulation makes it seasick
- **severity:** minor
- **says:** "wobbly", "seasick"
- **cause:** too much chorus or reverb modulation.
- **check:** modulation depth.
- **fix:** reduce depth and rate.
- **evidence:** practice, story:parker

### 200 Reverb tail cut off at the end
- **severity:** minor
- **says:** "the end cuts off"
- **cause:** export stops at the last note.
- **check:** bounce length vs tail.
- **fix:** in FL's export, set "Leave remainder" so tails ring out.
- **evidence:** practice
