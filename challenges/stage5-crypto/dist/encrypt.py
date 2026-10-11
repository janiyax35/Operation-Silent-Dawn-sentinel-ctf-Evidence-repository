#!/usr/bin/env python3
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
