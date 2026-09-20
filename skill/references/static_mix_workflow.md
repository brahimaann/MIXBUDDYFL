# The Static Mix: Process Before Plugins

Distilled from a full three-day mix walkthrough (Jake Codewise / Caleb Loves,
mixing.com "Fix the Mix") plus workflow notes from Jason "Cheese" Goldberg
(NBA YoungBoy, Travis Scott). Use this *before* reaching for
`diagnostic_map.md` — most "my mix sounds bad" problems are balance and
arrangement problems, not EQ problems.

---

## The core discipline

**Push the song as far as it will go with gain, volume, panning and gain
automation alone — no plugins at all — before opening a single EQ or
compressor.**

Why it matters: the most common failure mode is opening a session, throwing
plugins on everything, and getting lost. A mixer who balances first arrives at
the plugin stage with a *roadmap* instead of a vague sense that something's
wrong. Gain and volume are the most powerful tools in the mix; everything
after is polish.

When advising a user who is reaching for EQ/compression early, ask what the
balance sounds like with everything flat. Often the answer is a fader move or
a mute, not a filter.

---

## Step 1: Gain staging (before anything else)

- **Normalize every region to peak no higher than -10 dBFS.** In Logic:
  Functions → Normalize Region Gain → individual regions, target -10. Most
  DAWs have this; **Ableton does not have a true region-normalize**, so set
  clip Gain per clip (or use Utility per track) until waveforms are healthy
  and consistent — don't squint at tiny waveforms, and don't use plugins to
  make things loud.
- **Gain ≠ volume.** Gain is at the top of the channel (before processing);
  volume is the fader (after). Headroom has to come from gain, or you'll be
  re-adjusting everything later.
- Target roughly **6 dB of headroom on the mix bus** once balanced.
- If a producer already gain-staged well and you like their balance, skip
  normalizing and start from what they sent.

## Step 2: Build the balance from one element

1. Pull **every fader to -∞**.
2. Bring in **one core element** first — usually kick, or whatever the song is
   built around (acoustic guitar, lead vocal). Set it to 0 (which is -10 dBFS
   after normalizing).
3. **Set the monitoring level once, then don't touch it.** Constantly riding
   the monitor volume forces your ears to recalibrate and destroys consistency.
4. Build everything else around that element, and **try not to push any other
   fader above 0**.

## Step 3: Two passes, macro then micro

- **Pass 1 — high-level balance.** Just make sure every element can be heard.
  No detail work.
- **Pass 2 — details and transitions.** Follow "the journey of the song":
  how instruments enter and exit at each section boundary (intro → verse →
  pre → chorus).

**Keep a punch list.** Every time you hear something you cannot fix with
volume/pan, write it down instead of fixing it now. That list becomes the
plugin-stage roadmap, and it's what keeps the plugin stage from becoming
aimless. Come back on fresh ears.

## Step 4: Arrangement decisions beat processing

The fastest fix for masking is usually **muting something**, not EQ-carving it.
In the walkthrough, a chorus electric guitar was masking the lead vocal — the
fix was muting it for that chorus entirely, not a notch filter.

- Think "prioritizing and compromising," not "fit everything in."
- Feature different elements in different sections (banjo in chorus 2, the
  guitar somewhere else) so the listener gets a journey and the mix gets room.
- Pop convention: establish the melody in chorus 1, **add harmonies in
  chorus 2**.
- Performance problems (tuning, timing, phrasing) are **not mixing**. They get
  fixed before the mix starts, or they're a separate (billable) job.

---

## The three dimensions

Panning is width, volume is depth, frequency is height (see
`frequency_guide.md` for the full framework). Two things worth calling out
because they're where most amateur mixes fail:

- **Depth is the neglected one.** The classic amateur trajectory is
  compressing everything and pushing everything forward until the mix is loud
  and flat. Some things should be further back and make the ear reach for
  them. That's a feature.
- **Height comes from balance, not EQ.** If a mix needs to sound "taller,"
  turning *up the instruments that already contain high-frequency information*
  is far more effective than any EQ move. Same for depth and width. The
  balance stage affects all three dimensions more than the plugin stage will.

---

## Automation rules

- **Automate gain, never the fader — "free the fader."** Fader automation
  locks the fader: you go to make a balance move, and it snaps back. Keep
  faders free for balance and put all rides on a gain plugin or clip gain.
- If you don't want automation to change how later plugins react, the gain
  plugin has to sit at the **bottom of the chain**.
- **Ride vocal levels before compression**, not after. Evening out the phrases
  by hand first means the compressor works less hard, which reads as more
  natural and less squashed.
- Drawing volume moves is more consistent than performing fader automation.
- **Bus-level impact moves:** send all instruments to one bus and automate it
  up ~2 dB on specific hits — the whole group lunges forward together.
- Gain-automate out distracting one-off artifacts (a growl at a phrase start,
  a string buzz) rather than processing the whole track to fix one moment.

---

## Referencing

- **Get a good volume balance first, then reference.** References pull you back
  to an objective standard once your ears have adapted to the track.
- Aim for the **ballpark**, not an identical curve. "Could this sit in a
  playlist with these?" is the question.
- Never stop using references, no matter how experienced.
- **Reading a spectrum analyzer:** a well-balanced track is *not* a flat line.
  It's a **gently sloping curve starting around 60 Hz and falling toward the
  top**, with the roll-off at the very end. Ignore small bumps. A curve with a
  big mid hump and weak extremes is the classic "needs low end and high end,
  less mid" picture.

---

## Working principles (from the pros in these sources)

- **Consistency of tools is your baseline.** Using the same chain/room/
  monitors every time means that when something sounds off you can trace it
  point to point instead of guessing. Cheese mixes hit records on a portable
  rig in hotel rooms — nearfields close, mixing quietly — because consistency
  beats the room.
- **Commit.** Bounce production decisions to audio and "draw a line in the
  sand" before mixing. The power of limitation is real: more songs are ruined
  by rabbit-holing than by committing too early. Ask clients for **wet and dry
  stems** — start from wet (their vision), pull dry only when needed.
- **Process the minority of tracks, not the majority.** Most tracks in a good
  session need nothing.
- **Color-code by song section** (intro/outro, hooks, verses) so repeated
  parts are visible at a glance.
- **Print effects as audio** where it's faster than automating a send —
  duplicate the lead onto a track with the delay/reverb baked in and fade it.
- Replace a hopelessly inconsistent source (e.g. a wildly uneven kick) rather
  than fighting it with dynamics.
- Balance is what makes mastering possible: a master can't reach competitive
  loudness without dynamic and frequency balance already in the mix.
