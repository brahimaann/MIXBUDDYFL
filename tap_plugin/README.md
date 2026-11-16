# MixBuddy Tap (v0)

A passthrough plugin for FL Studio's mixer. It leaves the audio untouched and
keeps the last 10 seconds of what it hears in a memory-mapped file
(`%TEMP%\mixbuddy\tap_<id>.bin`), so the mix-buddy server can analyze a
mixer track while the song plays (`fl_list_taps`, `fl_analyze_track_live`).

## Build and install (Windows)

Close FL Studio first (Windows won't replace a plugin FL has loaded), then
double-click `build.bat`. It builds the VST3 and CLAP versions with Cargo,
then copies them to `C:\Program Files\Common Files\VST3` and `...\CLAP`
(Windows asks for admin rights). The log goes to `build_output.txt`.

Needs Rust (rustup) and the MSVC linker (Visual Studio Build Tools,
"Desktop development with C++").

## Use

1. In FL: Options > Manage plugins > Find plugins.
2. Add **MixBuddy Tap** as the **last** insert on each track you want Claude
   to hear (it hears everything before it in the chain, before the fader).
3. Play the song and ask Claude about the track.

Open the plugin to see its window: the track it is assigned to, whether
audio is reaching mix-buddy, and a level meter.

You don't set anything on the plugin. Its **Tap ID** shows "Unassigned"
until mix-buddy first looks for taps; the MixBuddy controller script then
sets it to the mixer track number (Master = 0). If you move the plugin to
another track, it is re-assigned the next time Claude checks.

## Design

- Audio thread: copies each block into the ring buffer, then publishes the
  write position with release ordering. No allocation or locking.
- When the Tap ID changes, the plugin reopens its file once inside the audio
  callback (a one-off click is possible at that moment).
- File layout is documented in `src/lib.rs`; the reader is
  `mcp_server/tap_reader.py`.

## Licence

The VST3 build links NIH-plug's VST3 bindings (vst3-sys, GPLv3), so this
plugin is GPL-3.0. For a permissively licensed release, ship only the CLAP
build or move to the MIT-licensed VST3 SDK.

## Tests

- `cargo test --lib`: ring buffer wraps and publishes correctly.
- `cargo run --release --example write_sine` writes a known sine through the
  real ring; `tests/test_fl_bridge.py` covers the Python side.
