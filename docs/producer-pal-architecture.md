# Producer Pal: Architecture Notes & What We Can Learn

Reverse-engineered from `Producer_Pal (1).amxd` (Max for Live device) on
2026-06-29 by extracting embedded strings. Repo: https://github.com/adamjmurray/producer-pal

## What Producer Pal actually is

A **Max for Live device** (`.amxd`) that boots a **Node.js MCP server**
(`mcp-server.mjs`, run via Max's `node.script`) on **port 3350** using a
**StreamableHTTP transport**. The AI (Claude Desktop, etc.) connects over HTTP;
the Node server bridges into Ableton's **Live Object Model (LOM)** via the Max
`LiveAPI` object. It ships its own Chat UI at `http://localhost:3350/chat`.

```
Claude  <--MCP/HTTP:3350-->  Node server (in Max)  <--LiveAPI-->  Ableton Live
```

Key implementation traits:
- MCP TypeScript SDK + Zod schemas (`looseObject`, `_enum`, `number().int()...`)
  for input validation -> JSON Schema. Returns structured JSON, with explicit
  MCP error codes (e.g. `-32602 Input validation error`).
- A **project "memory"** tool: persistent project context (song structure,
  creative direction, todos) injected into the AI. CRITICAL semantics: writes
  replace the entire memory, so it always reads first.
- Sample-folder scanning gate (user explicitly grants folders the AI may scan).
- An escape-hatch `ppal-live-api` tool: raw LOM access to read/modify ANY Live
  Set property ("use with care") to work around missing high-level tools.

## The full tool surface (23 tools)

Control/write-oriented, organized by verb x object:

| Verb | Objects |
|------|---------|
| read | live-set, track, scene, clip, device |
| create | track, scene, clip, device |
| update | live-set, track, scene, clip, device |
| delete | (tracks, scenes, clips, devices, drum-pads) |
| duplicate | (tracks, scenes, clips, devices) |
| other | connect, context (memory), playback, select, silence, library, live-api |

Design patterns worth copying:
- **Verb x object grid** keeps the tool count bounded and predictable.
- **"Returns overview by default; use `include` to add detail."** Every read
  tool is progressive-disclosure to keep token usage low. (We should adopt this.)
- One generic `delete`/`duplicate` that takes a `type` enum instead of N tools.
- Clear, imperative one-line tool descriptions with when-to-use guidance.

## How this relates to OUR project

Our `audio-mixing-analyzer` is the **opposite and complementary** half:

| | audio-mixing-analyzer (ours) | Producer Pal / livepilot |
|---|---|---|
| Direction | READ audio (DSP analysis) | WRITE to the DAW (LOM control) |
| Input | Rendered WAV/FLAC files | Live Ableton session |
| Output | LUFS, dB, Hz diagnoses + advice | Created/edited tracks, clips, devices |
| Truth source | The actual audio waveform | The session state |

Together they close the loop:
**analyze audio (ours) -> recommend moves (skill) -> apply in Ableton (control server)**

The user ALREADY has `livepilot` configured (Ableton control on port 9001), so
the control half exists. Producer Pal is an alternative control server, not
required.

## Concrete improvements to fold into our project

1. **Progressive disclosure on reads.** Add an optional `include` / `detail`
   arg to our analyze tools so the default response is compact and the LLM can
   request the heavy arrays (full band tables, raw resonance lists) only when
   needed. Mirrors Producer Pal's "overview by default."
2. **Explicit, typed input validation** with clear error payloads (we already
   return `{"error": ...}`; consider structured codes/messages).
3. **A "project memory" notion** for mixing: persist the user's reference
   artists, target LUFS, problem history per project so advice is consistent
   across sessions. (Could be a small JSON the skill reads/writes.)
4. **Bridge to the control layer (optional, future).** A skill workflow that,
   after diagnosing with our DSP tools, emits the exact `livepilot`/Producer Pal
   tool calls to create an EQ/compressor device with the recommended settings.
   This turns advice into one-click application. Gated behind explicit user
   confirmation (never auto-edit their session).

## Why we are NOT embedding into Max ourselves

Producer Pal lives in Max because it must reach the LOM. Our value is DSP on
rendered audio, which Python (numpy/scipy) does far better than Max/JS. Keeping
analysis in a Python stdio MCP server is the right call; we lean on
livepilot/Producer Pal for the write side rather than reinventing it.
