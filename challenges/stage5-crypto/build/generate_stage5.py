"""
Operation Silent Dawn - Stage 5 (CRYPTO-05) Challenge Generator
Author: Gunawardhana M.S.A. (IT24103304)

This script deterministically generates:
1. dist/telemetry.enc (The encrypted challenge payload)
2. dist/encrypt.py (The sanitized script left by the syndicate)
3. dist/stage05_weak_cipher.zip (The CTFd distribution archive)
"""

import os
import random
import zipfile

# ---------------------------------------------------------
# DETERMINISTIC CHALLENGE PARAMETERS
# ---------------------------------------------------------
MASTER_SEED = 42814  # 16-bit integer (0x0000 - 0xFFFF)
FLAG = "Eclipse{prng_k3ystr34m_s33d_c0ll4ps3_982f}"

# Realistic Incident Response Telemetry Payload
TELEMETRY_RECORD = (
    f"{FLAG}\n"
    f"[OBSERVATORY-SENTINEL-TELEMETRY-DROP]\n"
    f"TIMESTAMP : 2026-09-28T03:14:08Z\n"
    f"STATION   : LEO-GROUND-ARRAY-04\n"
    f"TARGET_SAT: ECLIPSE-CORE-OBSERVER\n"
    f"AZIMUTH   : 142.84 DEG\n"
    f"ELEVATION : 67.12 DEG\n"
    f"BURST_ID  : 0x99A4F2\n"
    f"PAYLOAD   : CLASSIFIED_SATELLITE_SCHEMATICS_BLOB\n"
    f"STATUS    : EXFIL_TRANSMISSION_COMPLETE\n"
    f"[END OF RECORD]\n"
).encode("utf-8")


def generate_keystream(length: int, seed: int) -> bytes:
    """Generates a pseudorandom XOR keystream using Python's standard PRNG."""
    prng = random.Random(seed)
    return bytes(prng.randint(0, 255) for _ in range(length))


def encrypt_payload(data: bytes, seed: int) -> bytes:
    """Encrypts data via byte-wise XOR against the PRNG keystream."""
    keystream = generate_keystream(len(data), seed)
    return bytes(b ^ k for b, k in zip(data, keystream))


def write_player_script(output_path: str):
    """Writes the sanitized syndicate encryption script for CTF participants."""
    player_script_content = '''#!/usr/bin/env python3
"""
[SENTINEL INCIDENT RESPONSE LOG - RECOVERED SCRIPT]
ARTEFACT ID : AR-SYND-ENC-09
SOURCE      : Discarded utility on compromised telemetry host
NOTE        : Static audit revealed non-cryptographic PRNG usage.
              Seed configuration wiped prior to thread termination.
"""

import os
import sys
import random

# [SECURITY AUDIT NOTE]
# The syndicate generator relies on a legacy 16-bit hardware seed register.
# SEED_KEY = ??? (Unsigned 16-bit integer: 0x0000 to 0xFFFF / 0 to 65535)

def generate_keystream(length: int, seed: int) -> bytes:
    """Derives keystream using standard linear pseudorandom routines."""
    prng = random.Random(seed)
    return bytes(prng.randint(0, 255) for _ in range(length))

def encrypt(plaintext_bytes: bytes, seed: int) -> bytes:
    """Applies symmetric XOR stream transformation."""
    keystream = generate_keystream(len(plaintext_bytes), seed)
    return bytes(p ^ k for p, k in zip(plaintext_bytes, keystream))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_file> <16bit_seed>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        seed_param = int(sys.argv[2])
        if not (0 <= seed_param <= 65535):
            raise ValueError("Seed must fit inside 16-bit boundaries (0 - 65535).")
    except ValueError as e:
        print(f"[-] Invalid seed: {e}")
        sys.exit(1)

    with open(input_file, "rb") as f:
        data = f.read()

    ciphertext = encrypt(data, seed_param)

    out_name = input_file + ".enc"
    with open(out_name, "wb") as f:
        f.write(ciphertext)

    print(f"[+] Transformation complete -> {out_name}")
'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(player_script_content)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.abspath(os.path.join(base_dir, "..", "dist"))
    os.makedirs(dist_dir, exist_ok=True)

    enc_file_path = os.path.join(dist_dir, "telemetry.enc")
    script_file_path = os.path.join(dist_dir, "encrypt.py")
    zip_file_path = os.path.join(dist_dir, "stage05_weak_cipher.zip")

    # 1. Generate encrypted telemetry
    ciphertext = encrypt_payload(TELEMETRY_RECORD, MASTER_SEED)
    with open(enc_file_path, "wb") as f:
        f.write(ciphertext)
    print(f"[✓] Created encrypted file: {enc_file_path} ({len(ciphertext)} bytes)")

    # 2. Generate sanitized player script
    write_player_script(script_file_path)
    print(f"[✓] Created participant script: {script_file_path}")

    # 3. Package into distribution ZIP
    with zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(script_file_path, arcname="encrypt.py")
        zf.write(enc_file_path, arcname="telemetry.enc")
    print(f"[✓] Packaged CTFd release archive: {zip_file_path}")


if __name__ == "__main__":
    main()