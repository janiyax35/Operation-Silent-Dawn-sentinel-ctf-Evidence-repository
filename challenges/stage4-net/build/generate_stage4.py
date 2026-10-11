#!/usr/bin/env python3
"""
=============================================================
  STAGE 4 — "Operation Silent Frequency"
  Challenge File Generator  (CTF MAKER USE ONLY)
=============================================================
  Generates: raw_telemetry_dump.txt

  Requirements:
      scapy  (pre-installed on Kali Linux)
      If missing: pip install scapy

  Run:
      python3 generate_stage4.py

  What this produces:
      raw_telemetry_dump.txt — A PCAP file encoded as raw hex,
      where every line is prefixed with [SDR_LOG_HEX].
      Participants strip the prefix, reconstruct the PCAP with
      xxd -r -p, then open it in Wireshark and filter for
      tcp.port == 9001 to find the flag in the TCP stream.

  DO NOT distribute this script to participants.
=============================================================
"""

import os
import sys
import time
import tempfile

# ── Dependency check ─────────────────────────────────────────
try:
    from scapy.all import Ether, IP, TCP, Raw, wrpcap, conf
    conf.verb = 0          # suppress scapy output
except ImportError:
    print("[!] scapy is not installed.")
    print("    Run: pip install scapy --break-system-packages")
    print("    (On Kali Linux, scapy is usually pre-installed.)")
    sys.exit(1)

# ── Configuration ────────────────────────────────────────────
OUTPUT_FILE      = "raw_telemetry_dump.txt"
FIXED_START_TIME  = 1789678390        # capture start time (unix seconds), pinned for reproducible resets
HEX_BYTES_PER_LINE = 32          # 32 bytes → 64 hex chars per line

FLAG    = "Eclipse{c0v3rt_h3x_p4ck3t_str34m_d3c0d3d}"
SRC_IP  = "192.168.1.100"        # Syndicate mobile uplink node
DST_IP  = "172.30.0.10"          # Observatory telemetry server
SPORT   = 52341                  # Source port (ephemeral)
DPORT   = 9001                   # Destination port (covert channel)

# Realistic incident memo — flag is the authorization token
MEMO = f"""\
INCIDENT MEMO — ECLIPSE SYNDICATE  [CLASSIFIED]
================================================
FROM   : Relay Node / Mobile Uplink (Horton Station)
TO     : Primary Exfiltration Handler
DATE   : 2026-08-11  02:47:33 UTC

STATUS : Satellite schematics package staged successfully.
         Integrity checksum : VERIFIED
         Dark-web auction   : 2026-08-12 00:00 UTC

AUTHORIZATION TOKEN : {FLAG}

Destroy this memo after confirmation receipt.
================================================
END OF TRANSMISSION
""".encode("utf-8")
# ─────────────────────────────────────────────────────────────


def build_tcp_session(src_ip, dst_ip, sport, dport, payload: bytes) -> list:
    """
    Build a complete, realistic TCP session:
      SYN → SYN-ACK → ACK  (3-way handshake)
      PSH+ACK (data)  → ACK (server confirms)
      FIN+ACK → FIN+ACK → ACK  (clean teardown)
    """
    pkts   = []
    seq_c  = 1000     # client Initial Sequence Number
    seq_s  = 5000     # server Initial Sequence Number
    ts     = FIXED_START_TIME   # fixed, so every run produces the identical file

    src_mac = "00:11:22:33:44:55"
    dst_mac = "66:77:88:99:aa:bb"

    def frame(s_ip, d_ip, sp, dp, flags, sq, ak, data=b""):
        """Helper: build one Ethernet/IP/TCP frame (+ optional payload)."""
        nonlocal ts
        eth = Ether(src=(src_mac if s_ip == src_ip else dst_mac),
                    dst=(dst_mac if s_ip == src_ip else src_mac))
        ip  = IP(src=s_ip, dst=d_ip, ttl=64)
        tcp = TCP(sport=sp, dport=dp, flags=flags, seq=sq, ack=ak, window=65535)
        p   = eth / ip / tcp / Raw(load=data) if data else eth / ip / tcp
        p.time = ts
        ts += 1
        return p

    # 1. SYN
    pkts.append(frame(src_ip, dst_ip, sport, dport, "S",  seq_c,     0))
    # 2. SYN-ACK
    pkts.append(frame(dst_ip, src_ip, dport, sport, "SA", seq_s,     seq_c + 1))
    seq_c += 1
    # 3. ACK  (handshake complete)
    pkts.append(frame(src_ip, dst_ip, sport, dport, "A",  seq_c,     seq_s + 1))
    seq_s += 1
    # 4. PSH+ACK — covert data transfer
    pkts.append(frame(src_ip, dst_ip, sport, dport, "PA", seq_c,     seq_s, payload))
    seq_c += len(payload)
    # 5. Server ACK
    pkts.append(frame(dst_ip, src_ip, dport, sport, "A",  seq_s,     seq_c))
    # 6. Client FIN+ACK
    pkts.append(frame(src_ip, dst_ip, sport, dport, "FA", seq_c,     seq_s))
    seq_c += 1
    # 7. Server FIN+ACK
    pkts.append(frame(dst_ip, src_ip, dport, sport, "FA", seq_s,     seq_c))
    seq_s += 1
    # 8. Final client ACK
    pkts.append(frame(src_ip, dst_ip, sport, dport, "A",  seq_c,     seq_s + 1))

    return pkts


def pcap_to_prefixed_hex(pcap_path: str, bytes_per_line: int) -> list[str]:
    """
    Read a PCAP binary file and return a list of strings:
        [SDR_LOG_HEX] <hex_chunk>
    Split into `bytes_per_line`-byte chunks.
    """
    with open(pcap_path, "rb") as f:
        raw = f.read()
    hex_full = raw.hex()
    chunk_len = bytes_per_line * 2    # each byte = 2 hex chars
    return [
        f"[SDR_LOG_HEX] {hex_full[i:i + chunk_len]}"
        for i in range(0, len(hex_full), chunk_len)
    ]


def main():
    print("=" * 60)
    print("  Stage 4 Challenge File Generator")
    print("  Operation: Silent Frequency — Eclipse CTF")
    print("=" * 60)

    # Build packets
    print("\n[*] Building TCP session...")
    packets = build_tcp_session(SRC_IP, DST_IP, SPORT, DPORT, MEMO)
    print(f"    {len(packets)} packets constructed.")

    # Write PCAP to temp file (scapy wrpcap requires a path)
    tmp_pcap = tempfile.mktemp(suffix=".pcap")
    print(f"[*] Writing PCAP to temp file ...")
    wrpcap(tmp_pcap, packets)

    # Convert to prefixed hex lines
    lines = pcap_to_prefixed_hex(tmp_pcap, HEX_BYTES_PER_LINE)
    os.unlink(tmp_pcap)
    print(f"[*] PCAP converted → {len(lines)} hex lines.")

    # Write challenge output file
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n[+] Challenge file written : {OUTPUT_FILE}")
    print(f"[+] Lines in file          : {len(lines)}")
    print(f"[+] Flag embedded          : {FLAG}")

    print(f"""
[!] DISTRIBUTE TO PARTICIPANTS:
    {OUTPUT_FILE}

[?] Intended participant solve path:
    # Strip log headers
    sed 's/\\[SDR_LOG_HEX\\] //g' {OUTPUT_FILE} > clean_hex.txt

    # Reconstruct PCAP
    xxd -r -p clean_hex.txt capture.pcap

    # Inspect in Wireshark or tshark
    tshark -r capture.pcap -Y "tcp.port == 9001" -z follow,tcp,ascii,0
""")


if __name__ == "__main__":
    main()