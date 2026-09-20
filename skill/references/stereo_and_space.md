# Stereo Width and Effects Architecture

Width, depth and the reverb/delay send design that creates them. Sources: a
full pop/rap vocal mix in Ableton (Reed Stefon), a three-day full-band mix
walkthrough (mixing.com), David Gibson's *Art of Mixing* framework, an
Afrobeat vocal mix (producer Mica), and Jason "Cheese" Goldberg's session
notes.

---

## Panning: do it before plugins

Panning is worth "20% to 50% of the mix" on its own, and it costs nothing.
Set it during the balance stage (see `static_mix_workflow.md`), not after.

- Everything centered = a traffic jam in the middle lane. The main advantage
  of stacking vocals is not just size, it's **width**.
- **Doubles** go wide (most of the way L/R), **harmonies** less wide — build a
  stereo spread out of mono recordings.
- **Half-panning often beats full panning.** Try both; when you pan something
  hard it usually also needs ~2 dB down.
- Ad-libs live out of the lead's way, roughly 45-80% L/R.
- Background vocals: lower harmonies toward the center, higher harmonies
  toward the edges.
- L-C-R (hard left / center / hard right only) is a valid whole-mix strategy —
  throw sounds wide and let reverbs and delays fill the gaps.

---

## Making mono sources wide

### The short-delay (Haas / "fattening") trick

Leave one channel dry and delay the **other channel by roughly 10-40 ms**.
Under ~30 ms the ear can't resolve two events, so it hears one fat sound
stretched between the speakers rather than an echo. Above ~30 ms it becomes an
audible slap.

This is the go-to move for turning a mono double or harmony into a stereo one.
Its real value on vocals is **decluttering the center**: pushing the harmony
stack outward leaves the middle clear so the lead vocal stays intelligible.

It also makes a sound *more present*, which means you can turn it **down** and
still hear it — useful for anything you want audible but not forward.

Watch the mono fold-down: this is a phase trick, so check mono after using it.

### Other width moves

- **Swap L/R channels** on a stereo track that leans the same way as another
  one — instant separation without touching EQ or level. (Used twice in the
  walkthrough on two right-leaning electrics.)
- **Narrow an over-wide baked-in track** with a stereo width tool so you can
  control it, *then* process it.
- Widen a stereo-imager on a supporting element to sit it just outside the
  element it competes with (e.g. chug guitars pushed outside the acoustics).
- Auto-pan on a dry ad-lib channel for gentle left-right movement.
- Stagger the sides of a delay (~20 ms between L and R) so repeats come from
  around you rather than dead center.

---

## Effects send architecture

Build effects as **sends/aux tracks**, not inserts, so wet level is
independent. A workable default vocal set is three sends:

| Send | Setting |
|---|---|
| **Reverb** | A plate for lead vocal. Short/tight when lyric density is high. |
| **Slap** | 1/8 note. **Filter it: high-pass ~400 Hz, low-pass ~2.5 kHz** — kills low rumble and the "high-end slappy bathroom" quality. |
| **Delay** | 1/4 or 1/2 note, modest feedback, sides staggered ~20 ms for width. |

In Ableton, the idiom for parallel wet effects is an **Audio Effect Rack** with
a dedicated "dry" chain plus wet chains: set each wet plugin to 100% wet and
blend using the chain's level. Dry signal stays untouched and up front.

### Rules that matter more than the specific plugin

- **De-ess (or low-pass) the signal going *into* the reverb.** The unpleasant
  part of a reverb is reverb on the S's and T's; ducking those before the
  reverb darkens and smooths it. Three independent sources in this corpus do
  some version of this — it's one of the highest-value habits here.
- **EQ after the reverb too**, so the tail doesn't scatter everywhere.
- **Duck the reverb from the dry vocal** (sidechain the reverb return to the
  lead) so it stays out of the way while the singer is singing and blooms in
  the gaps.
- **Separate reverb sets per family** — one for vocals, one for instruments,
  one for drums. One reverb for everything sounds like the band is in a cave;
  a different reverb per track sounds disconnected. The middle is the sweet
  spot. Send a guitar solo to the *vocal* reverb when it's taking over as the
  star.
- **Bus the effect returns together into one compressor** so no single throw
  jumps out and nothing feels detached from the rest.
- **Tighter and shorter when lyric density is high.** There's no room for long
  tails in a fast rap or busy pop vocal; save the long stuff for gaps.
- **Delays add another element to a limited space.** Don't add them to an
  already busy mix, unless the genre is deliberately wall-of-sound.

### Momentary throws

For "just that one word echoes," put a **Utility (or any gain plugin) before
the delay** on the send and automate it. Utility goes to -∞ while most delay
input gains stop at -40 dB, which isn't enough to silence it. Automate it up
for the single word you want to throw.

Automate sends, don't leave them static: ramp the reverb up on a phrase tail
so it goes distant, then pull back as the next section lands. And automate
echo **mutes** so repeats don't ring out over a hard ending.

---

## Gibson's shapes (why space fills up)

Every sound occupies volume in the space between the speakers:

- **Spheres** — normal sounds. Bass instruments are *bigger* spheres and mask
  more; louder sounds also read as bigger. Ten bells coexist happily; three
  bass guitars is Mud City.
- **Lines** — a fattened sound (short delay split L/R) stretched between the
  speakers.
- **Rooms** — reverb, which takes up an enormous amount of space.

The space is finite, so mixing is **crowd control**. This is why muting beats
EQ-carving, and why adding reverb or a delay to a busy mix makes it worse even
though each one sounded good soloed.
