#!/usr/bin/env python3
"""
Operation Silent Dawn - Challenge REV-06 Generator
Produces a hardened, stripped 64-bit Linux ELF binary.
"""

import subprocess
import os

PASSKEY = b"ECL-SENTINEL-9942-ABORT"
FLAG = b"Eclipse{d34ct1v4t10n_s3qu3nc3_c0mpl3t3_2026}"

# Transformation: enc_passkey[i] = (PASSKEY[i] ^ (0x5A + (i * 7))) & 0xFF
enc_passkey = [((b ^ (0x5A + (i * 7))) & 0xFF) for i, b in enumerate(PASSKEY)]

# Flag encryption: enc_flag[i] = FLAG[i] ^ PASSKEY[i % len(PASSKEY)]
enc_flag = [(b ^ PASSKEY[i % len(PASSKEY)]) for i, b in enumerate(FLAG)]

c_code = f"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PASSKEY_LEN {len(PASSKEY)}
#define FLAG_LEN {len(FLAG)}

// Obfuscated arrays (no plaintext strings in .rodata)
static const unsigned char ENC_PASSKEY[PASSKEY_LEN] = {{
    {", ".join(f"0x{b:02X}" for b in enc_passkey)}
}};

static const unsigned char ENC_FLAG[FLAG_LEN] = {{
    {", ".join(f"0x{b:02X}" for b in enc_flag)}
}};

int main(int argc, char *argv[]) {{
    char input_buffer[128];
    unsigned char decrypted_flag[FLAG_LEN + 1];

    // Challenge Banner
    puts("=================================================");
    puts("[!] SENTINEL SYSTEM ALERT: EMERGENCY PURGE ACTIVE");
    puts("[!] Telemetry sectors slated for zero-fill purge.");
    puts("=================================================");
    printf("[*] Enter syndicate deactivation passkey: ");
    fflush(stdout);

    if (!fgets(input_buffer, sizeof(input_buffer), stdin)) {{
        return 1;
    }}

    // Strip trailing newline characters
    input_buffer[strcspn(input_buffer, "\\r\\n")] = '\\0';

    // Length validation
    if (strlen(input_buffer) != PASSKEY_LEN) {{
        puts("[-] AUTHENTICATION FAILED: Invalid passkey length.");
        puts("[-] Memory sectors purged.");
        return 1;
    }}

    // Inlined byte evaluation loop (Defeats ltrace and API monitors)
    for (int i = 0; i < PASSKEY_LEN; i++) {{
        unsigned char transformed = (unsigned char)((((unsigned char)input_buffer[i]) ^ (0x5A + (i * 7))) & 0xFF);
        if (transformed != ENC_PASSKEY[i]) {{
            puts("[-] INVALID PASSKEY SEQUENCE.");
            puts("[-] Emergency wipe proceeding...");
            return 1;
        }}
    }}

    // Key-dependent flag decryption:
    // If the check was bypassed by patching, input_buffer is wrong and flag will be garbage
    for (int i = 0; i < FLAG_LEN; i++) {{
        decrypted_flag[i] = ENC_FLAG[i] ^ (unsigned char)input_buffer[i % PASSKEY_LEN];
    }}
    decrypted_flag[FLAG_LEN] = '\\0';

    puts("\\n[+] VERIFICATION SUCCESSFUL: Syndicate purge aborted.");
    printf("[+] RECOVERED TELEMETRY FLAG: %s\\n", decrypted_flag);

    // Clean memory buffer
    memset(decrypted_flag, 0, sizeof(decrypted_flag));
    return 0;
}}
"""

with open("killswitch.c", "w") as f:
    f.write(c_code)

print("[*] Generated killswitch.c successfully.")

# Compile with optimization (-O2 inlines code and complicates decompilation)
cmd_compile = "gcc -O2 -fno-ident -Wall killswitch.c -o killswitch"
subprocess.run(cmd_compile, shell=True, check=True)
print("[*] Compiled binary: killswitch")

# Strip all symbols, section headers, and debug information
cmd_strip = "strip --strip-all killswitch"
subprocess.run(cmd_strip, shell=True, check=True)
print("[*] Stripped all symbol tables and debug references.")
print("[+] Challenge artifact ready: ./killswitch")