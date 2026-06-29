# Mixing Assistant - Project Summary

_Last updated: 2026-06-29_

A complete, tested **LLM music-mixing assistant** for a music producer. It pairs
a Claude **skill** (the reasoning/knowledge layer) with a custom **MCP server**
(real DSP audio analysis) so the assistant can measure actual audio files and
return concrete, parameter-level mixing advice grounded in professional practice.

---

## 1. What it is and why

**Goal:** help with real mixing decisions - vocal clarity, compression settings,
loudness for streaming, stereo/phase safety, and "make it sound like [artist]"
reference matching (e.g. the airy Brent Faiyaz vocal sound).

**Design philosophy (chosen with the user):**
- **Option A - custom MCP server** (not a generic plugin) so tools are tailored
  to mixing.
- **Option B - DSP-first, real implementation.** No mock data, no hallucinated
  numbers. Every measurement comes from the actual waveform via numpy/scipy.

The source research came from three gathered files; we deliberately **rejected**
the version with mock-data TypeScript and **built on** the one with real Python
scipy/numpy DSP, then fixed its bugs (see section 6).

---

## 2. Architecture

```
You + an audio file (WAV/AIFF/FLAC/OGG)
      |
      v
mixing-assistant SKILL          intent -> pick tools -> interpret -> advise
  (SKILL.md + references/)       teaches Claude how to reason about mixing
      |
      v
audio-mixing-analyzer MCP SERVER (stdio)   6 DSP tools + 2 memory tools
  (mcp_server/server.py)         validation, progressive disclosure, summaries
      |
      v
dsp.py        pure numpy/scipy DSP (LUFS, STFT, resonance, phase)
memory.py     per-project context store (atomic JSON, read-then-replace)
```

**Separation of concerns:** all heavy math lives in `dsp.py`, all persistence in
`memory.py`, and both are unit-tested independently of the MCP plumbing. The
server layer only validates input, shapes responses, and serializes JSON.

---

## 3. The MCP tools (8 total)

Analysis tools return a compact **overview** plus a one-line human-readable
`summary`. Pass the optional `include` argument (comma-separated) to expand the
heavy detail blocks only when needed - this keeps token usage low.

| Tool | Overview returns | `include` options |
|------|------------------|-------------------|
| `analyze_loudness` | integrated LUFS + verdict vs -14 | `format` |
| `analyze_dynamics` | crest factor + compression suggestion | `levels` |
| `analyze_frequency_spectrum` | centroid, top 3 resonances | `bands`, `resonances` |
| `analyze_vocal_clarity` | clarity/mud/sibilance + EQ moves | `raw` |
| `analyze_stereo_compatibility` | correlation, phase, mono safety | `detail` |
| `compare_to_reference` | loudness + spectral diff vs reference | `all_bands` |
| `read_project_memory` | stored project context | - |
| `write_project_memory` | persists context (read-then-replace) | - |

Example summaries the tools actually produce:
- `"Integrated loudness -7.6 LUFS - hot (6.4 LU above -14 LUFS)."`
- `"Vocal is muddy, sibilant/harsh, lacking presence (clarity 0.01, mud 10.0/10...)."`
- `"Vs reference: loudness matches reference; off bands: sub_bass, mid_range."`

---

## 4. The DSP, briefly

- **Loudness:** EBU R128 / ITU-R BS.1770 K-weighting with two-stage gating.
  K-weighting coefficients are computed **analytically** so any sample rate
  works (not just 44.1/48 kHz).
- **Dynamics:** peak/RMS/crest factor + a short-term RMS spread for dynamic
  range; crest factor drives the suggested compression ratio/attack/release.
- **Spectrum/resonance:** Welch-style averaged power spectrum across the whole
  file; resonances found against a dynamic (smoothed mean + local std-dev)
  threshold curve, then classified (mud, boxiness, presence, sibilance, etc.).
- **Vocal clarity:** band-energy ratios -> mud/clarity/sibilance indices ->
  concrete EQ/de-ess suggestions.
- **Stereo/phase:** correlation coefficient, interchannel delay via GCC-PHAT,
  and sub-150 Hz phase correlation to flag bass cancellation / mono risk.

---

## 5. The skill layer (knowledge base)

`skill/SKILL.md` is the operating manual that tells Claude how to behave:
measure-then-advise, explain the *why*, trust ears over meters, stay in scope
(advise, don't render audio), and be concise/structured (Diagnosis -> Do this ->
Why -> Listen for).

`skill/references/`:
- `frequency_guide.md` - what every frequency range means (mud, presence, air...).
- `diagnostic_map.md` - metric -> action lookup table.
- `techniques.md` - chain order, compression starting points by source, effect
  recipes including the **Brent Faiyaz** higher/airier vocal pitch+formant move.
- `setup.md` - how to register the MCP server.

The skill now also teaches **progressive disclosure** (when to use `include`)
and **project memory** (read-then-replace continuity across sessions).

---

## 6. Bugs fixed from the source research

The chosen research code had real DSP but several bugs we corrected:
- **Missing `os` import** (would crash on load).
- **Center-only 2 s analysis** -> now whole-file Welch-style averaging.
- **Hard-coded sample rates** -> now analytical K-weighting for any rate.
- **O(n) std-dev loop** -> now vectorized via cumulative sums.

---

## 7. Project memory (new)

`mcp_server/memory.py` persists per-project context to
`~/.mixing-assistant/memory.json` (atomic temp-file + replace, never corrupts).

- Fields: `reference_artists`, `target_lufs`, `recurring_problems`, `notes`
  (extra fields allowed).
- **Semantics (borrowed from Producer Pal):** writes REPLACE the whole object,
  so the assistant always reads first and merges. Multiple projects are isolated.
- Survives corrupt files gracefully (returns an empty template, never crashes).

This makes advice consistent across sessions: the assistant can recall "your
target is -9 LUFS, reference is Brent Faiyaz, you tend to get boxy low-mids."

---

## 8. Tests (all green)

| Suite | Count | What it checks |
|-------|-------|----------------|
| `tests/test_dsp.py` | 25 | DSP math vs synthetic audio with known ground truth |
| `tests/test_memory.py` | 16 | memory round-trip, replace-not-merge, isolation, corruption |
| `tests/test_mcp_e2e.py` | 14 | full MCP protocol: lists 8 tools, overview vs `include`, memory |
| `tests/demo_workflow.py` | - | human-readable demo; detects planted mud + sibilance |

**Total: 55 automated assertions passing.** The demo plants a 320 Hz mud peak
and 7 kHz sibilance and confirms the pipeline detects and prescribes fixes.

Run them:
```
python tests/test_dsp.py
python tests/test_memory.py
python tests/test_mcp_e2e.py
python tests/demo_workflow.py
```

(Note: tests are standalone scripts using their own pass/fail runner and a
module-level `sys.exit`, so they are not run via `pytest` directly.)

---

## 9. Installation state

- Skill installed at `~/.jcode/skills/mixing-assistant/` (SKILL.md + references)
  and registered in `_index.json`.
- MCP server registered in `~/.jcode/mcp_servers.json` as
  `audio-mixing-analyzer` (`python .../mcp_server/server.py`). Config was backed
  up before editing and validated as JSON.
- The user already runs `livepilot` (Ableton control, port 9001) alongside it.

---

## 10. How this fits with Ableton (Producer Pal investigation)

We reverse-engineered Adam Murray's **Producer Pal** `.amxd` to learn patterns.
It is a Max for Live device running a Node.js MCP server (port 3350, HTTP) that
controls Ableton's Live Object Model via 23 control tools (verb x object grid).

Key realization: Producer Pal / livepilot are the **WRITE half** (control the
DAW); our analyzer is the **READ half** (DSP on rendered audio). Together they
close the loop: **analyze audio (ours) -> recommend (skill) -> apply in
Ableton (control server).**

What we adopted from it:
- **Progressive disclosure** ("overview by default; `include` for detail").
- **Project memory** with read-then-replace semantics.

Full notes: `docs/producer-pal-architecture.md`.

---

## 11. Repository layout

```
mixing-assistant/
  README.md                      quick start + tool table
  PROJECT_SUMMARY.md             this document
  requirements.txt               numpy, scipy, soundfile, mcp
  .gitignore
  docs/
    producer-pal-architecture.md reverse-engineering notes
  mcp_server/
    dsp.py                       pure DSP (tested)
    memory.py                    per-project memory (tested)
    server.py                    MCP tool layer (stdio)
  skill/
    SKILL.md                     reasoning/operating manual
    references/                  frequency guide, diagnostic map, techniques, setup
  tests/
    test_dsp.py                  25 DSP unit tests
    test_memory.py               16 memory unit tests
    test_mcp_e2e.py              14 end-to-end MCP tests
    demo_workflow.py             human-readable demo
    test_imports.py              import sanity check
```

---

## 12. Possible next steps

- **Apply-to-DAW bridge:** after diagnosing, emit the exact `livepilot` /
  Producer Pal tool calls to create an EQ/compressor with the recommended
  settings - gated behind explicit user confirmation (never auto-edit a session).
- **MP3 support** (currently asks the user to convert to WAV first).
- **Batch/stem analysis** across a folder of stems with a combined report.
- Wire the still-pending deep-research findings into `references/` once they land.
