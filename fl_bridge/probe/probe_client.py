"""Talk to the MixBuddy Probe script running inside FL Studio.

Usage (FL Studio open, "MixBuddy Probe" enabled in MIDI settings):
    python probe_client.py            ping FL and time the round trip
    python probe_client.py mixer      read a mixer snapshot
    python probe_client.py dump       dump every mixer plugin's parameters
"""
import json
import socket
import sys
import time

HOST, PORT = "127.0.0.1", 9876


def call(cmd, timeout=5.0):
    t0 = time.perf_counter()
    with socket.create_connection((HOST, PORT), timeout=timeout) as s:
        s.sendall((json.dumps({"cmd": cmd}) + "\n").encode("utf-8"))
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    ms = (time.perf_counter() - t0) * 1000.0
    return json.loads(buf.decode("utf-8")), ms, len(buf)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ping"
    try:
        if cmd == "ping":
            times = []
            reply = None
            for _ in range(10):
                reply, ms, _n = call("ping")
                times.append(ms)
            print(json.dumps(reply, indent=2))
            print("10 pings: min %.1f ms, avg %.1f ms, max %.1f ms"
                  % (min(times), sum(times) / len(times), max(times)))
        elif cmd == "mixer":
            reply, ms, n = call("mixer")
            print(json.dumps(reply, indent=2))
            print("%.1f ms, %d bytes" % (ms, n))
        elif cmd == "dump":
            reply, _ms, _n = call("dump")
            print("dump started:", reply.get("started"))
            while True:
                time.sleep(1.0)
                st, _ms, _n = call("status")
                if not st.get("running"):
                    print(json.dumps(st.get("last"), indent=2))
                    print("Full results: probe_plugins.json next to the FL script.")
                    break
                print("  plugins left:", st.get("plugins_left"))
        else:
            print(__doc__)
    except ConnectionRefusedError:
        print("Nothing is listening on %s:%d. Is FL Studio open with the "
              "MixBuddy Probe script enabled?" % (HOST, PORT))
    except socket.timeout:
        print("FL accepted the connection but did not answer in time.")


if __name__ == "__main__":
    main()
