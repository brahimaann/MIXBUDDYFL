# Practising (and testing mix-buddy) with free multitracks

The Cambridge-MT "Mixing Secrets" library (Mike Senior) has 500+ free raw
multitracks: [cambridge-mt.com/ms3/mtk](https://cambridge-mt.com/ms3/mtk/).
Each project links to a "Mixes & Discussion" thread in the Cambridge-MT
Discussion Zone, where other people post their mixes of the same raw tracks.
That makes it the best way to compare your fix for a problem with other
people's.

## The library's usage terms

From the [library FAQ](https://cambridge-mt.com/ms/mtk-faq), summarised:

- **Personal mixing practice and education are fine.** Non-profit
  tutorials, classes and informal forum mix-offs are allowed.
- **Don't use your mixes of these tracks in a portfolio or for promotion**
  without the artist's permission.
- **Research is not covered.** Contact the contributors first, especially
  for commercial research. So mix-buddy does **not** ship these files, test
  data built from them, or a scraper that harvests their download links.
- **Link to the project page** (the `#ArtistName` anchor), not the raw ZIP
  URL, since files get renamed and rehosted. Don't stockpile ZIPs; they're
  updated over time.

## Where to start

The [newbie list](https://cambridge-mt.com/ms/mtk-newbies) groups projects
into Entry Level, Small-Scale and Larger-Scale.

- **Sound On Sound Demo, 'Mystery'** (Hip-Hop/R&B, Entry Level). Already
  balanced but completely dry, so it's for practising reverb, delay and
  width (atlas 176-200).
- **West End Blend** (Soul/Funk, Larger-Scale) is a step up.
- Many projects have Mix Rescue or Session Notes write-ups with audio
  demos.

## Workflow in FL Studio with mix-buddy

1. Download one project from its page and unzip it into its own folder.
2. Drag the WAVs into FL. Give each its own mixer track, named like the
   file (fl_match_stems matches by name).
3. Put a MixBuddy Tap last on each track you want measured, and on the
   master.
4. Start a session: `fl_snapshot(label="start")`, then mix stage by stage
   (see the mix order in SKILL.md, step 3). Ask mix-buddy what it hears at
   each stage.
5. When you're done, bounce, then compare your bounce with a mix from the
   project's Discussion Zone thread using `compare_to_reference`.
   Level-match first.
6. File what you learned: `archive_note(kind="lesson", ...)`. Lessons from
   practice carry over to your own songs.
