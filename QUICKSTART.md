# Mix Buddy - Quick Start

**Mix Buddy** is your AI mixing engineer. Feed it audio files, get concrete mixing advice.

## ✅ Ready to use

Everything is installed and configured:
- ✓ Skill installed at `~/.jcode/skills/mix-buddy/`
- ✓ MCP server registered as `audio-mixing-analyzer`
- ✓ All 55 tests passing (25 DSP + 16 memory + 14 E2E)

## 🎯 How to use

**Restart Jcode/Claude Desktop** to load the new configuration, then:

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
- **Reference matching:** "make my voice higher and airier like Brent Faiyaz"
- **Compare:** "compare my mix to this reference track"

## 🛠 The 8 MCP tools

| Tool | What it measures |
|------|------------------|
| analyze_loudness | Integrated LUFS (EBU R128) |
| analyze_dynamics | Peak/RMS/crest + compression suggestion |
| analyze_frequency_spectrum | Band energies + classified resonances |
| analyze_vocal_clarity | Mud/clarity/sibilance + EQ moves |
| analyze_stereo_compatibility | Correlation, phase, mono safety |
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

Run the validation test to confirm the MCP server is alive:
```bash
cd C:\Users\brahi\mix-buddy
python tests\validate_mcp.py
```

Should print: `✓ MCP server running: 8 tools`

## 📚 Learn more

- `README.md` — architecture + setup
- `PROJECT_SUMMARY.md` — complete build story, DSP details, Producer Pal insights
- `skill/references/` — frequency guide, diagnostic map, mixing techniques
- `docs/producer-pal-architecture.md` — what we learned from Producer Pal

---

**Now restart your Claude client and try it!** 🎵
