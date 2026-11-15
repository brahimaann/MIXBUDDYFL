"""
End-to-end MCP test: spins up the server as a subprocess, connects via stdio,
lists tools, and calls each one against a generated test WAV file.

This verifies the full MCP plumbing works, not just the DSP math.
"""
import asyncio
import os
import sys
import tempfile

import numpy as np
import soundfile as sf

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(__file__)
SERVER = os.path.join(HERE, "..", "mcp_server", "server.py")
FS = 44100


def make_test_wav(stereo=False):
    t = np.arange(int(2.0 * FS)) / FS
    # Vocal-ish: fundamental + mud at 300 + presence + a little sibilance.
    sig = (
        0.5 * np.sin(2 * np.pi * 220 * t)
        + 0.3 * np.sin(2 * np.pi * 300 * t)
        + 0.15 * np.sin(2 * np.pi * 3000 * t)
        + 0.1 * np.sin(2 * np.pi * 7000 * t)
    ).astype(np.float32)
    if stereo:
        sig = np.column_stack([sig, sig * 0.95])
    path = os.path.join(tempfile.gettempdir(), f"_mcp_e2e_{'st' if stereo else 'mono'}.wav")
    sf.write(path, sig, FS)
    return path


def make_breathy_wav():
    """Phrases separated by audible breath noise in the gaps (for the gate tool)."""
    rng = np.random.RandomState(0)
    parts = [np.zeros(int(0.3 * FS), dtype=np.float32)]
    for _ in range(4):
        t = np.arange(int(0.5 * FS)) / FS
        parts.append((0.5 * np.sin(2 * np.pi * 220 * t)).astype(np.float32))
        parts.append((0.03 * rng.standard_normal(int(0.4 * FS))).astype(np.float32))
    sig = np.concatenate(parts)
    path = os.path.join(tempfile.gettempdir(), "_mcp_e2e_breathy.wav")
    sf.write(path, sig, FS)
    return path


async def main():
    mono_wav = make_test_wav(stereo=False)
    stereo_wav = make_test_wav(stereo=True)
    breathy_wav = make_breathy_wav()

    params = StdioServerParameters(command=sys.executable, args=[SERVER])
    passed, failed = 0, 0

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            expected = sorted([
                "analyze_loudness",
                "analyze_dynamics",
                "analyze_frequency_spectrum",
                "analyze_vocal_clarity",
                "analyze_stereo_compatibility",
                "analyze_noise_gate",
                "compare_to_reference",
                "read_project_memory",
                "write_project_memory",
                "fl_status",
                "fl_get_mixer",
                "fl_get_track_chain",
                "fl_get_plugin_params",
            ])
            if names == expected:
                print(f"  PASS  lists all {len(expected)} tools: {names}")
                passed += 1
            else:
                print(f"  FAIL  tool list mismatch.\n    got={names}\n    exp={expected}")
                failed += 1

            async def call(tool, args):
                res = await session.call_tool(tool, args)
                text = res.content[0].text
                import json
                return json.loads(text)

            # analyze_loudness (overview has summary, no format fields)
            r = await call("analyze_loudness", {"file_path": mono_wav})
            ok = (
                "integrated_loudness_lufs" in r
                and -40 < r["integrated_loudness_lufs"] < 0
                and "summary" in r
                and "sample_rate" not in r  # not included by default
            )
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_loudness -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # include="format" adds detail fields
            r = await call("analyze_loudness", {"file_path": mono_wav, "include": "format"})
            ok = r.get("sample_rate") == FS and "channels" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_loudness include=format -> sr {r.get('sample_rate')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_dynamics
            r = await call("analyze_dynamics", {"file_path": mono_wav})
            ok = "crest_factor_db" in r and "compression_suggestion" in r and "summary" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_dynamics -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_dynamics include=levels
            r = await call("analyze_dynamics", {"file_path": mono_wav, "include": "levels"})
            ok = "peak_level_dbfs" in r and "rms_level_dbfs" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_dynamics include=levels -> peak {r.get('peak_level_dbfs')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_frequency_spectrum (overview: top_resonances, no full bands)
            r = await call("analyze_frequency_spectrum", {"file_path": mono_wav})
            ok = (
                "top_resonances" in r
                and "summary" in r
                and "frequency_bands" not in r  # only with include=bands
            )
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_frequency_spectrum -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # include=bands,resonances adds full tables
            r = await call(
                "analyze_frequency_spectrum",
                {"file_path": mono_wav, "include": "bands,resonances"},
            )
            ok = "frequency_bands" in r and "resonances" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_frequency_spectrum include=bands,resonances")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_vocal_clarity
            r = await call("analyze_vocal_clarity", {"file_path": mono_wav})
            ok = "mud_index" in r and "eq_suggestions" in r and "summary" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_vocal_clarity -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_stereo_compatibility
            r = await call("analyze_stereo_compatibility", {"file_path": stereo_wav})
            ok = "overall_correlation" in r and "summary" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_stereo_compatibility -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_noise_gate: clean file has no gaps to report
            r = await call("analyze_noise_gate", {"file_path": mono_wav})
            ok = r.get("gaps_detected_count") == 0 and "summary" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_noise_gate (no gaps) -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_noise_gate: breathy file detects bleed + suggests settings
            r = await call("analyze_noise_gate", {"file_path": breathy_wav})
            ok = (
                r.get("breath_bleed_detected") is True
                and r.get("gate_suggestion", {}).get("sidechain_highpass_hz") == 150.0
            )
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_noise_gate (breathy) -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # include=levels adds the raw level fields
            r = await call("analyze_noise_gate", {"file_path": breathy_wav, "include": "levels"})
            ok = "gap_level_dbfs" in r and "noise_floor_dbfs" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_noise_gate include=levels -> gap {r.get('gap_level_dbfs')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # compare_to_reference
            r = await call("compare_to_reference", {"target_path": mono_wav, "reference_path": stereo_wav})
            ok = "loudness_differential_lu" in r and "spectral_difference" in r and "summary" in r
            print(f"  {'PASS' if ok else 'FAIL'}  compare_to_reference -> {r.get('summary')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # project memory round-trip through MCP
            proj = "_e2e_test_project"
            r = await call("read_project_memory", {"project": proj})
            ok = r.get("exists") is False and "memory" in r
            print(f"  {'PASS' if ok else 'FAIL'}  read_project_memory (new) -> exists={r.get('exists')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            r = await call(
                "write_project_memory",
                {"project": proj, "content": {"reference_artists": ["Brent Faiyaz"], "target_lufs": -14}},
            )
            ok = r.get("saved") is True
            print(f"  {'PASS' if ok else 'FAIL'}  write_project_memory -> saved={r.get('saved')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            r = await call("read_project_memory", {"project": proj})
            ok = r.get("exists") is True and r["memory"].get("target_lufs") == -14
            print(f"  {'PASS' if ok else 'FAIL'}  read_project_memory (after write) -> {r['memory'].get('reference_artists')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # error handling
            r = await call("analyze_loudness", {"file_path": "C:/nope/missing.wav"})
            ok = "error" in r
            print(f"  {'PASS' if ok else 'FAIL'}  missing-file returns error gracefully")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

    os.remove(mono_wav)
    os.remove(stereo_wav)
    os.remove(breathy_wav)

    # Clean up the test project written into the real memory store.
    try:
        store = os.path.join(os.path.expanduser("~"), ".mix-buddy", "memory.json")
        if os.path.exists(store):
            import json
            with open(store, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if "_e2e_test_project" in data:
                del data["_e2e_test_project"]
                with open(store, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=2)
    except Exception:
        pass

    print(f"\n{'='*40}\nMCP E2E: {passed} passed, {failed} failed\n{'='*40}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
