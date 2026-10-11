# Stage 4 - Operation Silent Frequency (NET-04)

| | |
|---|---|
| Owner | Ranaweera C.A (IT24100520) |
| Domain | Networking |
| Difficulty | Moderate |
| Points | 250 |

## How it was built

`build/generate_stage4.py` uses Scapy to build one complete TCP session between a syndicate relay (192.168.1.100, port 52341) and an observatory server (172.30.0.10, port 9001): the three-way handshake, one data packet carrying an incident memo, the server's acknowledgement, and the closing handshake. That is 8 packets.

The capture is written as a pcap file, read back as bytes, and turned into hex text. The hex is cut into lines of 32 bytes (64 hex characters), and every line is prefixed with `[SDR_LOG_HEX] ` so the file looks like an ordinary radio log. The result, `raw_telemetry_dump.txt`, is what players receive.

All values are fixed: the addresses, ports, MAC addresses, sequence numbers, and the capture start time (`FIXED_START_TIME`). So the script produces an identical file on every run. Without the fixed start time, the timestamps in each run would differ.

## Flag placement

The flag is the `AUTHORIZATION TOKEN` line of a plain-text incident memo. The memo is carried in a single PSH/ACK segment of 555 bytes, from 192.168.1.100:52341 to 172.30.0.10:9001. It is not visible in the text file: it exists only as bytes inside a capture that is hidden in hex.

Flag: `Eclipse{c0v3rt_h3x_p4ck3t_str34m_d3c0d3d}`

## Intended solution path

1. Download `raw_telemetry_dump.txt`. Every line is `[SDR_LOG_HEX] ` followed by hex.
2. Strip the label, join the lines and convert the hex back to bytes:
   `sed 's/^\[SDR_LOG_HEX\] //' raw_telemetry_dump.txt | tr -d '\n' | xxd -r -p > decoded.bin`
3. Identify the file: `file decoded.bin` reports a pcap capture. The file begins with the bytes `d4c3b2a1`, the pcap signature.
4. Open `decoded.bin` in Wireshark. Only the packet with `Len=555` carries data.
5. Right-click that packet and choose Follow, then TCP Stream. The memo shows in plain text.
6. Submit the `Eclipse{...}` token from the memo.

`solve/solve_stage4.py` automates steps 1 to 5. It strips the label, converts the hex, checks the pcap signature, rebuilds each TCP stream in sequence order, and prints the flag.

## Hints

| Hint | Cost | Text on the platform |
|---|---|---|
| 1 | 25 | The file is raw hex wrapped in log headers. Strip the headers before reconstruction. |
| 2 | 50 | Use xxd -r -p or Wireshark's text2pcap to build a readable .pcap, then follow the TCP stream. |

Hint 2 is locked until hint 1 is opened. Hint 1 points to the file's form (hex with a label on each line). Hint 2 names the conversion tool and the final step, so it gives away most of the path and costs more.

## Reset

Stage 4 is a static file with no live service, so it holds no state that players can change. The platform's admin reset clears player progress only.

If the challenge file is lost or damaged, regenerate it by running `build/generate_stage4.py`. The output is identical every time, which can be checked by comparing hashes (`shasum`) with the copy on the platform.

## Folder contents

| Folder | Contents |
|---|---|
| `build/` | `generate_stage4.py`, the generator |
| `dist/` | `raw_telemetry_dump.txt`, the exact file players receive |
| `solve/` | `solve_stage4.py`, the solver |

## Tools and credits

Python 3 and Scapy (building and reading the capture), sed, tr, xxd, file, and Wireshark (the player path).