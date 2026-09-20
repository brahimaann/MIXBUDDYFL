# MCP Server Setup

The `mix-buddy` skill relies on the **audio-mixing-analyzer** MCP server to
analyze real audio files. Set it up once per environment (Claude Code,
Claude Desktop, or the Jcode CLI each keep their own MCP registration).

## Prerequisites

- Python 3.10+
- Install dependencies:
  ```
  pip install -r mix-buddy/requirements.txt
  ```
  (numpy, scipy, soundfile, mcp)

## Register the server

### Claude Code CLI (recommended - one command)

```
claude mcp add --scope user audio-mixing-analyzer -- python "C:\Users\brahi\mix-buddy\mcp_server\server.py"
```

`--scope user` registers it for every project, matching how `producer-pal` is
registered. Start a **new** Claude Code session afterward - a server added
mid-session isn't picked up by that session's already-fixed tool list.
Verify with `claude mcp list` (should show `audio-mixing-analyzer ... Connected`).

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
      "args": ["C:\\Users\\brahi\\mix-buddy\\mcp_server\\server.py"]
    }
  }
}
```

Restart Claude Desktop. The tools should appear (hammer icon).

### Jcode CLI

Registered in `~/.jcode/mcp_servers.json` under `audio-mixing-analyzer`,
pointing `command` to `python` and `args` to the absolute path of
`mix-buddy/mcp_server/server.py`. This is a separate registration from
Claude Code's own config above - both can point at the same `server.py`.

## Verify it works

From the repo root (these are standalone scripts with their own pass/fail
runner, not pytest suites - run them directly):

```
python tests/test_dsp.py
python tests/test_memory.py
python tests/test_mcp_e2e.py
```

You should see all checks pass (`test_mcp_e2e.py` lists 9 tools, each returns
valid data).

## Available tools

| Tool | Purpose |
|------|---------|
| `analyze_loudness` | Integrated LUFS (EBU R128) |
| `analyze_dynamics` | Peak/RMS/crest + compression suggestion |
| `analyze_frequency_spectrum` | Band energies + resonance detection |
| `analyze_vocal_clarity` | Mud/clarity/sibilance + EQ suggestions |
| `analyze_stereo_compatibility` | Correlation, phase, mono safety |
| `analyze_noise_gate` | Inter-phrase gap/breath-bleed detection + gate settings |
| `compare_to_reference` | Loudness + spectral diff vs a reference |
| `read_project_memory` / `write_project_memory` | Per-project context (read-then-replace) |

All file-based tools take absolute file paths to WAV/AIFF/FLAC/OGG files.

## Troubleshooting

- **"File not found"**: pass an absolute path, escaped backslashes on Windows.
- **Tools not appearing in Claude Code**: confirm `claude mcp list` shows it
  Connected, then make sure you're in a **new** session - registering a
  server does not add its tools to a session already in progress.
- **Tools not appearing elsewhere**: confirm `python` is on PATH and the path
  to `server.py` is correct; check the client's MCP logs.
- **Decode error on MP3**: convert to WAV first (soundfile does not read MP3
  by default). `ffmpeg -i in.mp3 out.wav`.
