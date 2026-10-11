"""
Operation Silent Dawn - Stage 5 Validation & Negative Testing Suite
Author: Gunawardhana M.S.A. (IT24103304)
Confirms challenge robustness, determinism, and absence of accidental leaks.
"""

import sys
import os

# Automatically append the current directory ('organizer') to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import time
import hashlib
import unittest

from generate_stage5 import (
    main as run_generator,
    MASTER_SEED,
    FLAG,
    generate_keystream,
    encrypt_payload,
    TELEMETRY_RECORD
)


class TestStage5QualityAssurance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate clean challenge artefacts
        run_generator()
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.dist_dir = os.path.abspath(os.path.join(cls.base_dir, "..", "dist"))
        cls.enc_file = os.path.join(cls.dist_dir, "telemetry.enc")
        cls.script_file = os.path.join(cls.dist_dir, "encrypt.py")
        cls.zip_file = os.path.join(cls.dist_dir, "stage05_weak_cipher.zip")

    def test_01_files_exist_and_non_empty(self):
        """Verify all deliverables exist and contain data."""
        for path in [self.enc_file, self.script_file, self.zip_file]:
            self.assertTrue(os.path.exists(path), f"Missing deliverable: {path}")
            self.assertGreater(os.path.getsize(path), 0, f"File is empty: {path}")

    def test_02_negative_test_no_plaintext_leak_in_script(self):
        """Confirm that neither the seed nor the flag appears in encrypt.py."""
        with open(self.script_file, "r", encoding="utf-8") as f:
            script_content = f.read()

        self.assertNotIn(str(MASTER_SEED), script_content, "CRITICAL: Master seed leaked in source code!")
        self.assertNotIn("Eclipse{", script_content, "CRITICAL: Flag string leaked in source code!")

    def test_03_negative_test_no_strings_leak_in_ciphertext(self):
        """Confirm that the flag and telemetry strings are fully encrypted in telemetry.enc."""
        with open(self.enc_file, "rb") as f:
            ciphertext = f.read()

        self.assertNotIn(b"Eclipse{", ciphertext, "CRITICAL: Plaintext flag visible in ciphertext!")
        self.assertNotIn(b"OBSERVATORY", ciphertext, "CRITICAL: Plaintext log visible in ciphertext!")

    def test_04_execution_benchmark_under_three_seconds(self):
        """Verify the solver breaks the cipher in under 3.0 seconds (Doc Section 6.5)."""
        with open(self.enc_file, "rb") as f:
            ciphertext = f.read()

        target_prefix = ciphertext[:8]
        start_time = time.time()

        recovered_seed = None
        for s in range(65536):
            ks = generate_keystream(8, s)
            if bytes(c ^ k for c, k in zip(target_prefix, ks)) == b"Eclipse{":
                recovered_seed = s
                break

        elapsed = time.time() - start_time
        print(f"\n[BENCHMARK] Keyspace search completed in {elapsed:.3f}s")

        self.assertEqual(recovered_seed, MASTER_SEED, "Solver failed to recover the authentic seed.")
        self.assertLess(elapsed, 3.0, f"Solver took {elapsed:.2f}s, exceeding the 3.0s specification!")

    def test_05_deterministic_reset_and_recovery(self):
        """Confirm re-running the generator yields byte-identical SHA256 checksums."""
        def get_sha256(filepath):
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                h.update(f.read())
            return h.hexdigest()

        hash1 = get_sha256(self.enc_file)
        run_generator()  # Re-run generator
        hash2 = get_sha256(self.enc_file)

        self.assertEqual(hash1, hash2, "Generator is non-deterministic! Files differ across runs.")


if __name__ == "__main__":
    unittest.main()