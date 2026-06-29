# MCP Server Setup

The `mixing-assistant` skill relies on the **audio-mixing-analyzer** MCP server
to analyze real audio files. Set it up once.

## Prerequisites

- Python 3.10+
- Install dependencies:
  ```
  pip install -r mixing-assistant/requirements.txt
  ```
  (numpy, scipy, soundfile, mcp)

## Register the server

### Claude Desktop
Edit `claude_desktop_config.json`:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add (use the absolute path to `server.py`):

```json
{
  "mcpServers": {
    "audio-mixing-analyzer": {
      "command": "python",
      "args": ["C:\\Users\\brahi\\mixing-assistant\\mcp_server\\server.py"]
    }
  }
}
```

Restart Claude Desktop. The tools should appear (hammer icon).

### Claude Code / Jcode CLI
Add an MCP server entry pointing `command` to `python` and `args` to the
absolute path of `mcp_server/server.py`, transport `stdio`.

## Verify it works

From the repo root:

```
python tests/test_mcp_e2e.py
```

You should see all checks pass (lists 6 tools, each returns valid data).

## Available tools

| Tool | Purpose |
|------|---------|
| `analyze_loudness` | Integrated LUFS (EBU R128) |
| `analyze_dynamics` | Peak/RMS/crest + compression suggestion |
| `analyze_frequency_spectrum` | Band energies + resonance detection |
| `analyze_vocal_clarity` | Mud/clarity/sibilance + EQ suggestions |
| `analyze_stereo_compatibility` | Correlation, phase, mono safety |
| `compare_to_reference` | Loudness + spectral diff vs a reference |

All tools take absolute file paths to WAV/AIFF/FLAC/OGG files.

## Troubleshooting

- **"File not found"**: pass an absolute path, escaped backslashes on Windows.
- **Tools not appearing**: confirm `python` is on PATH and the path to
  `server.py` is correct; check Claude's MCP logs.
- **Decode error on MP3**: convert to WAV first (soundfile does not read MP3 by
  default). `ffmpeg -i in.mp3 out.wav`.
