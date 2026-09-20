# Mix Buddy - Quick Start

**Mix Buddy** is your AI mixing engineer. Feed it audio files, get concrete mixing advice.

## ✅ Ready to use

Everything is installed and configured:
- ✓ Skill installed at `~/.jcode/skills/mix-buddy/`
- ✓ MCP server registered as `audio-mixing-analyzer` (Jcode + Claude Code)
- ✓ All 66 tests passing (33 DSP + 16 memory + 17 E2E)

## 🎯 How to use

**Start a new Claude Code session** (or restart Jcode/Claude Desktop) to load
the configuration — a server registered mid-session isn't picked up by that
session. Then:

```
"How can I make this vocal clearer? It sounds muddy."
[attach: my_vocal.wav]
```

Mix Buddy will:
1. Measure your audio with the MCP server (LUFS, dynamics, spectrum, phase)
2. Translate the numbers into plain-language diagnosis
3. Give you ordered, concrete moves (frequency, gain, ratio, etc.)
4. Explain the *why* each time

## 💡 What you can ask

- **Vocal clarity:** "make my vocal clearer / less muddy / less harsh"
- **Compression:** "what compression settings should I try on this rap vocal?"
- **Loudness:** "is my master loud enough for Spotify?"
- **Phase/mono:** "does this mix collapse in mono?"
- **Gating:** "breath noise is bleeding through between phrases"
- **Reference matching:** "make my voice higher and airier like Brent Faiyaz"
- **Compare:** "compare my mix to this reference track"

## 🛠 The 9 MCP tools

| Tool | What it measures |
|------|------------------|
| analyze_loudness | Integrated LUFS (EBU R128) |
| analyze_dynamics | Peak/RMS/crest + compression suggestion |
| analyze_frequency_spectrum | Band energies + classified resonances |
| analyze_vocal_clarity | Mud/clarity/sibilance + EQ moves |
| analyze_stereo_compatibility | Correlation, phase, mono safety |
| analyze_noise_gate | Inter-phrase gap/breath-bleed + gate settings |
| compare_to_reference | Loudness + spectral diff vs reference |
| read_project_memory | Recall stored project context |
| write_project_memory | Persist project context |

Each tool returns a compact **overview + one-line summary** by default.
Pass `include="detail"` to expand the heavy data only when needed.

## 📁 Your files

- **Project:** `C:\Users\brahi\mix-buddy\`
- **Memory store:** `C:\Users\brahi\.mix-buddy\memory.json` (created on first write)
- **Supported formats:** WAV, AIFF, FLAC, OGG (convert MP3 → WAV first)

## 🧪 Validate it works

Run the end-to-end test to confirm the MCP server is alive:
```bash
cd C:\Users\brahi\mix-buddy
python tests\test_mcp_e2e.py
```

Its first line should read `PASS  lists all 9 tools: [...]`, ending with
`MCP E2E: 17 passed, 0 failed`.

## 📚 Learn more

- `README.md` — architecture + setup
- `PROJECT_SUMMARY.md` — complete build story, DSP details, Producer Pal insights
- `skill/references/` — frequency guide, diagnostic map, mixing techniques
- `docs/producer-pal-architecture.md` — what we learned from Producer Pal

---

**Now restart your Claude client and try it!** 🎵
