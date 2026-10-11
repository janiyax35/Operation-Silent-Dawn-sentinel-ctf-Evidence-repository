#!/usr/bin/env python3
"""Stage 4 solver (NET-04, "Operation Silent Frequency") - Ranaweera C.A (IT24100520)

Automates the intended player path for raw_telemetry_dump.txt:

  1. strip the "[SDR_LOG_HEX] " prefix from every line   (sed)
  2. join the hex and convert it back to bytes            (tr + xxd -r -p)
  3. identify the file by its first bytes                 (file)
  4. read the TCP conversation that carries data          (Wireshark > Follow TCP Stream)
  5. pull the Eclipse{...} flag out of the stream

Usage:
    python3 solve_stage4.py raw_telemetry_dump.txt [decoded.bin]

Needs: Python 3 and scapy  (pip install scapy)
"""
import re
import sys
from collections import defaultdict

from scapy.all import IP, TCP, rdpcap

PREFIX = "[SDR_LOG_HEX] "
# first 4 bytes of a pcap file, little-endian and big-endian
PCAP_MAGICS = {bytes.fromhex("d4c3b2a1"): "pcap (little-endian)",
               bytes.fromhex("a1b2c3d4"): "pcap (big-endian)"}
FLAG_RE = re.compile(r"Eclipse\{[^}]+\}")


def strip_and_decode(path):
    """Steps 1 and 2: remove the label, join the lines, hex -> bytes."""
    hex_parts = []
    with open(path) as f:
        for number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            if not line.startswith(PREFIX):
                sys.exit(f"[!] line {number} does not start with {PREFIX!r}")
            hex_parts.append(line[len(PREFIX):])
    try:
        return bytes.fromhex("".join(hex_parts))
    except ValueError:
        sys.exit("[!] the text after the label is not valid hex")


def identify(raw):
    """Step 3: what `file` does - compare the first bytes to known signatures."""
    return PCAP_MAGICS.get(raw[:4])


def follow_streams(pcap_path):
    """Step 4: rebuild each TCP conversation, like Follow TCP Stream.

    Packets are grouped by (source, source port, destination, destination port),
    ordered by TCP sequence number, and their payloads joined together.
    Only directions that actually carry data are returned.
    """
    segments = defaultdict(list)
    for pkt in rdpcap(pcap_path):
        if pkt.haslayer(IP) and pkt.haslayer(TCP):
            payload = bytes(pkt[TCP].payload)
            if payload:
                key = (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
                segments[key].append((pkt[TCP].seq, payload))

    streams = {}
    for key, parts in segments.items():
        parts.sort(key=lambda p: p[0])
        streams[key] = b"".join(data for _, data in parts)
    return streams


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out_path = sys.argv[2] if len(sys.argv) > 2 else "decoded.bin"

    raw = strip_and_decode(sys.argv[1])
    print(f"[+] steps 1-2: decoded {len(raw)} bytes -> {out_path}")
    with open(out_path, "wb") as f:
        f.write(raw)

    kind = identify(raw)
    if kind is None:
        sys.exit(f"[!] step 3: first bytes {raw[:4].hex()} are not a known capture signature")
    print(f"[+] step 3: first bytes {raw[:4].hex()} -> {kind}")

    streams = follow_streams(out_path)
    if not streams:
        sys.exit("[!] step 4: no TCP data found in the capture")

    for (src, sport, dst, dport), data in streams.items():
        print(f"[+] step 4: stream {src}:{sport} -> {dst}:{dport} ({len(data)} bytes)")
        text = data.decode("utf-8", errors="replace")
        print("\n" + text + "\n")
        match = FLAG_RE.search(text)
        if match:
            print(f"[+] step 5: flag = {match.group(0)}")
            return
    sys.exit("[!] step 5: no Eclipse{...} flag found in any stream")


if __name__ == "__main__":
    main()