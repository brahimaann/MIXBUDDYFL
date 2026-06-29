# Mixing Assistant

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

The skill measures your audio with the MCP server, then translates the numbers
into plain-language diagnosis + ordered fixes, explaining the *why* each time.

## Architecture

```
You + audio file
      |
      v
mixing-assistant SKILL  (intent -> which tools -> interpret -> advise)
      |
      v
audio-mixing-analyzer MCP SERVER  (6 DSP tools)
      |
      v
dsp.py  (scipy/numpy: STFT, K-weighting LUFS, resonance detection, phase)
```

- `mcp_server/dsp.py` - pure, tested DSP functions.
- `mcp_server/server.py` - MCP tool layer (stdio).
- `skill/SKILL.md` + `skill/references/` - the reasoning layer & knowledge base.
- `tests/` - DSP unit tests, MCP e2e tests, and a workflow demo.

## MCP tools

| Tool | Returns |
|------|---------|
| `analyze_loudness` | Integrated LUFS (EBU R128) |
| `analyze_dynamics` | Peak/RMS/crest factor + compression suggestion |
| `analyze_frequency_spectrum` | Band energies + classified resonances |
| `analyze_vocal_clarity` | Mud/clarity/sibilance indices + EQ moves |
| `analyze_stereo_compatibility` | Correlation, phase, mono safety |
| `compare_to_reference` | Loudness + spectral diff vs a reference |

## Setup

```
pip install -r requirements.txt
```

Register the server with your MCP client (see `skill/references/setup.md`),
pointing it at `mcp_server/server.py`.

## Run the tests

```
python tests/test_dsp.py        # 25 DSP unit tests (synthetic ground truth)
python tests/test_mcp_e2e.py    # 8 end-to-end MCP protocol tests
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
