#!/usr/bin/env python3
# Stage 1 (STEG-01) - The Intercepted Frequency
# builds the two challenge files
#
#   signal_alpha.wav  -> player gets this one from the platform
#   signal_beta.wav   -> uploaded to google drive, player has to find the link
#
# idea of the challenge:
#   alpha = noise + decoy flag + real flag (real one is very quiet)
#   beta  = noise + decoy flag
#   alpha - beta = only the real flag is left
#
# need:  pip install numpy scipy Pillow
# run :  python3 stage1_build.py
#        python3 stage1_build.py --out dist

import argparse
import hashlib
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import chirp

DECOY_FLAG = "Eclipse{f4k3_sp3ctr0gr4m_tr4p}"
REAL_FLAG = "Eclipse{ph4s3_c4nc3ll4t10n_succ3ss}"
STAGE2_PASSPHRASE = "Sentinel_Telemetry_Override_8021"

# where signal_beta.wav is hosted
DRIVE_LINK = "https://drive.google.com/file/d/1JqZCsZggwhQXcMpC-h_OhMOeXBvbfGN_/view?usp=sharing"

# brainfuck program that prints DRIVE_LINK, this goes into the Artist tag of alpha
BRAINFUCK = "+[----->+++<]>+.++++++++++++..----.+++.+[-->+<]>.-----------..[--->+<]>-.++++++++++++++.---------.[->++++++<]>.+[->+++<]>.[->+++<]>-.+[--->+<]>++.++++++++..--------.+++++.-------.[->+++<]>-.--[--->+<]>-.++++++++++++.--.+++[->+++++<]>-.[--->+<]>+.+++.+++.-------.[->+++<]>.[--->+<]>-.+[->+++<]>.++.+[-->+++<]>-.[--->+<]>+++.++[->+++<]>+.-[----->+<]>--.+[++++>---<]>.[->+++<]>+.[->++++<]>-..--[--->+<]>.+[->+++<]>.>-[--->+<]>----.+++++++.+++++++++++.-[->++++++<]>+.[--->+<]>+.----[->+++<]>-.-[--->++<]>+.[->++++++++<]>.---------.----------------.-[--->++++<]>.[---->+++<]>-.++.>--[----->+<]>-.-------------.[---->+++<]>.-------[->++<]>.[->+++<]>.++++.[--->++<]>+++.+++++++.[-->+++++++++<]>.-[-->+<]>.++[--->++<]>.[------>+<]>.----.[--->+<]>.+[-->+<]>+++.----[->++<]>-.--.---.[-->+<]>+++++.---[->++<]>-.-----------.-------.--[--->+<]>---.---------.+++++.-------."

# audio settings (mono, 16 bit)
RATE = 22050
SECONDS = 16.0
SEED = 0xEC11B5E      # fixed seed, so every run gives the same audio

# the flag text is drawn between these frequencies in the spectrogram
F_LOW, F_HIGH, F_STEP = 2500.0, 8500.0, 25.0

NOISE_LEVEL = 0.10
DECOY_LEVEL = 0.90    # loud, easy to see
REAL_LEVEL = 0.06     # very quiet, hidden under the decoy and the noise


def run_brainfuck(code):
    # small interpreter, only used to check the BRAINFUCK text above is correct
    jump, stack = {}, []
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            j = stack.pop()
            jump[i], jump[j] = j, i

    tape, ptr, pc, out = [0] * 30000, 0, 0, []
    while pc < len(code):
        c = code[pc]
        if c == ">":
            ptr += 1
        elif c == "<":
            ptr -= 1
        elif c == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif c == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif c == ".":
            out.append(chr(tape[ptr]))
        elif c == "[" and tape[ptr] == 0:
            pc = jump[pc]
        elif c == "]" and tape[ptr] != 0:
            pc = jump[pc]
        pc += 1
    return "".join(out)


# the text shape depends on the font. the files on the platform were built on
# windows (Courier New Bold), so build on windows to get the exact same bytes
FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    "/Library/Fonts/Courier New Bold.ttf",
    "C:\\Windows\\Fonts\\courbd.ttf",
    "C:\\Windows\\Fonts\\consolab.ttf",
]


def load_font(size):
    for path in FONTS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def text_picture(text, width, height):
    # draw the text as a black and white picture, values 0..1
    # row 0 = lowest frequency, so the picture is flipped at the end
    font = load_font(200)
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font)
    pad = 30
    img = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    ImageDraw.Draw(img).text((pad - x0, pad - y0), text, font=font, fill=255)
    img = img.resize((width, height), Image.LANCZOS)
    pixels = np.asarray(img, dtype=np.float64) / 255.0
    return pixels[::-1, :]


def text_to_sound(text, rng):
    # one sine wave for every frequency row of the picture.
    # the wave is loud where the picture is white and silent where it is black,
    # so the text shows up when the sound is viewed as a spectrogram
    n = int(RATE * SECONDS)
    t = np.arange(n) / RATE
    freqs = np.arange(F_LOW, F_HIGH, F_STEP)
    columns = int(SECONDS * 60)
    picture = text_picture(text, columns, len(freqs))
    column_time = np.linspace(0.0, SECONDS, columns)

    sound = np.zeros(n)
    for row, f in enumerate(freqs):
        if picture[row].max() < 0.02:
            continue
        loudness = np.interp(t, column_time, picture[row])
        sound += loudness * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))

    return sound / np.max(np.abs(sound))


def make_noise(rng):
    # white noise + some fake radio interference, same in both files
    n = int(RATE * SECONDS)
    t = np.arange(n) / RATE

    x = rng.normal(0.0, 1.0, n)
    x += 0.5 * np.sin(2 * np.pi * 50 * t)          # mains hum
    x += 0.3 * np.sin(2 * np.pi * 100 * t)
    am = 0.5 * (1 + np.sin(2 * np.pi * 0.7 * t))   # 1 kHz carrier
    x += 0.5 * am * np.sin(2 * np.pi * 1000 * t)

    for _ in range(9):                             # short frequency sweeps
        start = rng.uniform(0.2, SECONDS - 0.8)
        length = int(0.4 * RATE)
        i0 = int(start * RATE)
        tt = np.arange(length) / RATE
        f0, f1 = rng.uniform(300, 3000), rng.uniform(6000, 10500)
        x[i0:i0 + length] += 1.2 * chirp(tt, f0, tt[-1], f1) * np.hanning(length)

    pops = rng.choice(n, size=40, replace=False)   # crackle
    x[pops] += rng.choice([-1, 1], size=40) * rng.uniform(3, 4, 40)

    return x / np.std(x) * NOISE_LEVEL


def chunk(name, data):
    # RIFF chunk = 4 letter name + size + data (+ 1 pad byte if size is odd)
    pad = b"\x00" if len(data) % 2 else b""
    return name + struct.pack("<I", len(data)) + data + pad


def write_wav(path, samples, tags):
    # normal 16 bit mono wav, with a LIST/INFO chunk for the metadata.
    # exiftool shows these tags (IART = Artist, ICMT = Comment ...)
    fmt = struct.pack("<HHIIHH", 1, 1, RATE, RATE * 2, 2, 16)
    info = b"INFO"
    for name, text in tags.items():
        info += chunk(name.encode(), text.encode("latin-1") + b"\x00")
    body = (
        b"WAVE"
        + chunk(b"fmt ", fmt)
        + chunk(b"LIST", info)
        + chunk(b"data", samples.astype("<i2").tobytes())
    )
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(body)) + body)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description="build the stage 1 challenge files")
    ap.add_argument("--out", default=".", help="output folder (default: current folder)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    # make sure the brainfuck really prints the drive link before using it
    if run_brainfuck(BRAINFUCK) != DRIVE_LINK:
        print("[!] brainfuck does not print the drive link, fix it first")
        return 1

    rng = np.random.default_rng(SEED)
    noise = make_noise(rng)
    decoy = text_to_sound(DECOY_FLAG, rng) * (NOISE_LEVEL * DECOY_LEVEL * 4)
    real = text_to_sound(REAL_FLAG, rng) * (NOISE_LEVEL * REAL_LEVEL * 4)

    # round the shared part only once.
    # then alpha - beta is exactly the real flag, sample by sample
    shared = np.round((noise + decoy) * 32767).astype(np.int32)
    beta = shared
    alpha = shared + np.round(real * 32767).astype(np.int32)

    if max(np.abs(alpha).max(), np.abs(beta).max()) > 32767:
        print("[!] audio is clipping, lower NOISE_LEVEL or DECOY_LEVEL")
        return 1

    # tags are kept the same as the files already on the platform,
    # so the rebuilt files have the same sha256
    alpha_tags = {
        "IART": BRAINFUCK,
        "ICMT": "Sentinel intercept | ch=03 | mode=burst | status=UNRESOLVED",
        "ICRD": "2026-03-14",
        "INAM": "Rogue RF Burst 0419",
        "ISFT": "Lavf62.12.102",
    }
    beta_tags = {
        "INAM": "Carrier Reference 0419",
        "IART": "Sentinel Reference Unit",
        "ICMT": "ARCHIVE_PASSPHRASE=" + STAGE2_PASSPHRASE,   # used in stage 2
        "ISFT": "Sentinel IDS v2.4",
        "ICRD": "2026-03-14",
    }

    alpha_path = os.path.join(args.out, "signal_alpha.wav")
    beta_path = os.path.join(args.out, "signal_beta.wav")
    write_wav(alpha_path, alpha, alpha_tags)
    write_wav(beta_path, beta, beta_tags)

    print("[+] " + alpha_path)
    print("    sha256 " + sha256(alpha_path))
    print("[+] " + beta_path)
    print("    sha256 " + sha256(beta_path))
    print("[i] upload signal_alpha.wav to the platform")
    print("[i] upload signal_beta.wav to google drive: " + DRIVE_LINK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
