# Mix Buddy

An LLM-powered music mixing assistant: a Claude **skill** + a custom **MCP
server** that analyzes real audio files and gives concrete, parameter-level
mixing recommendations grounded in professional practice.

## What it does

Ask things like:
- "How can I make this vocal clearer? It sounds muddy."
- "What compression settings should I try on this rap vocal?"
- "Is my master loud enough for Spotify?"
- "Does this mix collapse in mono?"
- "Make my voice higher and airier like Brent Faiyaz."
- "Compare my mix to this reference track."
- "Breath noise is bleeding through between phrases on my vocal."

The skill measures your audio with the MCP server, then translates the numbers
into plain-language diagnosis + ordered fixes, explaining the *why* each time.

## Architecture

```
You + audio file
      |
      v
mix-buddy SKILL  (intent -> which tools -> interpret -> advise)
      |
      v
audio-mixing-analyzer MCP SERVER  (7 DSP tools + 2 memory tools)
      |
      v
dsp.py  (scipy/numpy: STFT, K-weighting LUFS, resonance detection, phase)
memory.py  (per-project context: reference artists, target LUFS, history)
```

- `mcp_server/dsp.py` - pure, tested DSP functions.
- `mcp_server/memory.py` - per-project memory (atomic JSON store).
- `mcp_server/server.py` - MCP tool layer (stdio), progressive disclosure.
- `skill/SKILL.md` + `skill/references/` - the reasoning layer & knowledge base.
- `tests/` - DSP unit tests, memory tests, MCP e2e tests, and a workflow demo.

## MCP tools

Analysis tools return a compact **overview** (with a one-line `summary`) by
default; pass `include` to expand detail (e.g. `include="bands,resonances"`).

| Tool | Returns |
|------|---------|
| `analyze_loudness` | Integrated LUFS (EBU R128), true peak, PLR |
| `analyze_dynamics` | Peak/RMS/crest factor + compression suggestion |
| `analyze_frequency_spectrum` | Band energies, harmonic centroid, classified resonances |
| `analyze_vocal_clarity` | Mud/clarity/sibilance indices + EQ moves |
| `analyze_stereo_compatibility` | Correlation, phase, mono safety |
| `analyze_noise_gate` | Inter-phrase gap/breath-bleed detection + gate settings |
| `compare_to_reference` | Loudness + spectral diff vs a reference |
| `read_project_memory` | Recall stored project context |
| `write_project_memory` | Persist project context (read-then-replace) |
| `fl_status` | Live FL Studio connection check |
| `fl_get_mixer` | Live mixer: tracks, faders, plugins, routing |
| `fl_get_track_chain` | One track's insert chain in signal order |
| `fl_get_plugin_params` | One plugin's settings in real units |

The `fl_*` tools read a live FL Studio 2025 session through a small
controller script and a loopMIDI port. Setup: `fl_bridge/README.md`.
Quick live check: double-click `fl_bridge/check.bat` with FL open.

## Setup

```
pip install -r requirements.txt
```

Register the server with your MCP client (see `skill/references/setup.md`),
pointing it at `mcp_server/server.py` and restart your client. For Claude Code:

```
claude mcp add --scope user audio-mixing-analyzer -- python "C:\Users\brahi\mix-buddy\mcp_server\server.py"
```

## Run the tests

```
python tests/test_dsp.py        # 44 DSP unit tests (synthetic ground truth)
python tests/test_memory.py     # 16 project-memory unit tests
python tests/test_mcp_e2e.py    # 17 end-to-end MCP protocol tests
python tests/demo_workflow.py   # human-readable workflow demo
```

## Notes / honesty

- Heuristic indices (`mud_index`, `clarity_score`, etc.) are **directional**,
  not absolute studio standards. Always paired with a concrete Hz/dB move.
- Tools read WAV/AIFF/FLAC/OGG. Convert MP3 to WAV first.
- The assistant advises; it does not render or edit audio.

## Credit / sources

DSP approach distilled and corrected from research notes (LLM2Fx-Tools,
ITO-Master, Fx-Encoder++ frameworks; EBU R128 / ITU-R BS.1770 loudness;
Bark/ERB perceptual scales) and mixing tutorials across pop, hip-hop and
Afro-beat vocal production.
