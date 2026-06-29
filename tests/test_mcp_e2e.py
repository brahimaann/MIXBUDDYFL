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


async def main():
    mono_wav = make_test_wav(stereo=False)
    stereo_wav = make_test_wav(stereo=True)

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
                "compare_to_reference",
            ])
            if names == expected:
                print(f"  PASS  lists all 6 tools: {names}")
                passed += 1
            else:
                print(f"  FAIL  tool list mismatch.\n    got={names}\n    exp={expected}")
                failed += 1

            async def call(tool, args):
                res = await session.call_tool(tool, args)
                text = res.content[0].text
                import json
                return json.loads(text)

            # analyze_loudness
            r = await call("analyze_loudness", {"file_path": mono_wav})
            ok = "integrated_loudness_lufs" in r and -40 < r["integrated_loudness_lufs"] < 0
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_loudness -> {r.get('integrated_loudness_lufs')} LUFS")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_dynamics
            r = await call("analyze_dynamics", {"file_path": mono_wav})
            ok = "crest_factor_db" in r and "compression_suggestion" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_dynamics -> crest {r.get('crest_factor_db')} dB")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_frequency_spectrum
            r = await call("analyze_frequency_spectrum", {"file_path": mono_wav})
            ok = "frequency_bands" in r and "resonances" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_frequency_spectrum -> {r.get('peaks_detected_count')} peaks")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_vocal_clarity
            r = await call("analyze_vocal_clarity", {"file_path": mono_wav})
            ok = "mud_index" in r and "eq_suggestions" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_vocal_clarity -> mud {r.get('mud_index')}, clarity {r.get('clarity_score')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # analyze_stereo_compatibility
            r = await call("analyze_stereo_compatibility", {"file_path": stereo_wav})
            ok = "overall_correlation" in r
            print(f"  {'PASS' if ok else 'FAIL'}  analyze_stereo_compatibility -> corr {r.get('overall_correlation')}")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # compare_to_reference
            r = await call("compare_to_reference", {"target_path": mono_wav, "reference_path": stereo_wav})
            ok = "loudness_differential_lu" in r and "spectral_difference" in r
            print(f"  {'PASS' if ok else 'FAIL'}  compare_to_reference -> {r.get('loudness_differential_lu')} LU diff")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

            # error handling
            r = await call("analyze_loudness", {"file_path": "C:/nope/missing.wav"})
            ok = "error" in r
            print(f"  {'PASS' if ok else 'FAIL'}  missing-file returns error gracefully")
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

    os.remove(mono_wav)
    os.remove(stereo_wav)
    print(f"\n{'='*40}\nMCP E2E: {passed} passed, {failed} failed\n{'='*40}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
