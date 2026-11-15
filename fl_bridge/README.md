# FL Studio bridge (read-only, v1)

Lets the mix-buddy MCP server read a live FL Studio session: mixer tracks,
faders, routing, and every insert plugin's settings in real units.

## How it works

FL Studio 2025's controller-script sandbox blocks sockets and ctypes but allows
file I/O (verified on v25.1.6 build 4997, API 38, Python 3.12.1). So:

1. The server writes `mb_request.json` into the controller script's folder.
2. It sends a MIDI "doorbell" (CC 119, channel 16) to the loopMIDI port.
3. `device_MixBuddy.py` wakes in `OnMidiMsg`, runs the request against FL's
   `mixer`/`plugins` API and writes `mb_response.json`.

FL never called `OnIdle` in testing, so the script can't poll on its own; the
doorbell is required. The doorbell uses Windows' built-in `winmm.dll`, so there
is nothing extra to install.

## Setup (Windows)

1. Install loopMIDI and create a port named `MixBuddy`. Leave loopMIDI running.
2. Copy `device_MixBuddy.py` to
   `<FL user data folder>\FL Studio\Settings\Hardware\MixBuddy\`.
   Find the user data folder in FL under Options > File settings
   (here it is `C:\Users\brahi\OneDrive\Documents\Image-Line`).
3. In FL: Options > MIDI settings. Select the `MixBuddy` input, enable it,
   and set Controller type to `MixBuddy`. Do not enable `MixBuddy` as an output.
4. Restart your MCP client so it picks up the new tools.

Optional environment variables: `MIXBUDDY_FL_DIR` (script folder, if
auto-detection fails) and `MIXBUDDY_MIDI_PORT` (port name, default `MixBuddy`).

## Tools

| Tool | Returns |
|------|---------|
| `fl_status` | Connection check, FL version, round-trip time |
| `fl_get_mixer` | Tracks in use: fader dB, pan, mute/solo, plugins, routing |
| `fl_get_track_chain` | One track's insert chain in signal order |
| `fl_get_plugin_params` | One plugin's settings as the plugin displays them |

`fl_get_plugin_params` hides switched-off EQ bands, and dynamic-EQ settings on
bands with 0 dB dynamic range, so a Pro-Q 4 with 8 bands comes back as ~84
parameters instead of 528.

## Known limits

- Read-only. Nothing in FL is changed.
- The mixer peak meter is a momentary post-fader reading; only useful during
  playback. Real audio analysis comes from the helper plugin (not built yet).
- Insert slots sit before the fader.

## Tests

`python tests/test_fl_bridge.py` runs the real controller script against a
fake FL API, no FL Studio needed.
