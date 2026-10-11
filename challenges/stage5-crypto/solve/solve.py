#!/usr/bin/env python3
"""
Operation Silent Dawn - Stage 5 Exploit Solver
Target: CRYPTO-05 (The Weak Cipher)
Technique: Known-Plaintext Attack (KPA) + Exhaustive 16-bit PRNG Search
"""

import sys
import time
import random

KNOWN_PREFIX = b"Eclipse{"
KEYSPACE_LIMIT = 65536  # 16-bit unsigned range: 0x0000 - 0xFFFF


def break_cipher(encrypted_file_path: str):
    print(f"[*] Loading encrypted telemetry: {encrypted_file_path}")
    try:
        with open(encrypted_file_path, "rb") as f:
            ciphertext = f.read()
    except FileNotFoundError:
        print(f"[-] Error: {encrypted_file_path} not found.")
        return

    prefix_len = len(KNOWN_PREFIX)
    if len(ciphertext) < prefix_len:
        print("[-] Error: Ciphertext is shorter than the known flag header.")
        return

    target_prefix = ciphertext[:prefix_len]
    print(f"[*] Targeting known prefix: {KNOWN_PREFIX.decode()} ({prefix_len} bytes)")
    print(f"[*] Initiating brute-force search over {KEYSPACE_LIMIT} seed states...")

    start_time = time.time()
    recovered_seed = None

    # Exhaustive search over the 16-bit seed boundary
    for candidate_seed in range(KEYSPACE_LIMIT):
        # Initialize PRNG identically to the syndicate script
        prng = random.Random(candidate_seed)
        candidate_keystream = bytes(prng.randint(0, 255) for _ in range(prefix_len))

        # Check if XOR matches the known header
        if bytes(c ^ k for c, k in zip(target_prefix, candidate_keystream)) == KNOWN_PREFIX:
            recovered_seed = candidate_seed
            break

    elapsed = time.time() - start_time

    if recovered_seed is None:
        print("[-] Exploit failed: No matching seed found within 16-bit range.")
        return

    print(f"\n[+] VULNERABILITY EXPLOITED SUCCESSFULLY!")
    print(f"[+] Recovered Seed : {recovered_seed} (Hex: {hex(recovered_seed)})")
    print(f"[+] Attack Duration: {elapsed:.3f} seconds")

    # Decrypt entire payload with recovered seed
    prng = random.Random(recovered_seed)
    full_keystream = bytes(prng.randint(0, 255) for _ in range(len(ciphertext)))
    decrypted_record = bytes(c ^ k for c, k in zip(ciphertext, full_keystream)).decode("utf-8", errors="replace")

    print("\n" + "=" * 55)
    print("DECRYPTED TELEMETRY ARTEFACT")
    print("=" * 55)
    print(decrypted_record.strip())
    print("=" * 55)

    # Extract flag line
    for line in decrypted_record.splitlines():
        if line.startswith("Eclipse{"):
            print(f"\n[★] SUBMISSION FLAG: {line}")
            break


if __name__ == "__main__":
    target_path = "../dist/telemetry.enc" if len(sys.argv) < 2 else sys.argv[1]
    break_cipher(target_path)