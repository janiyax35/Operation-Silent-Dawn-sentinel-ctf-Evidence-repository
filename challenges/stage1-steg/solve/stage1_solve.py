#!/usr/bin/env python3
# Stage 1 (STEG-01) solver
#
# what it does:
#   1. reads the metadata of signal_alpha.wav
#   2. the Artist tag is a brainfuck program -> run it -> get the drive link
#   3. downloads signal_beta.wav from that link (or use --beta if you have it)
#   4. alpha - beta, this is the same as "invert + mix" in audacity
#   5. saves the result as a wav and as a spectrogram picture.
#      the real flag is readable in the picture
#   6. prints the Comment tag of beta, it is needed for stage 2
#
# need:  pip install numpy Pillow
# run :  python3 stage1_solve.py signal_alpha.wav
#        python3 stage1_solve.py signal_alpha.wav --beta signal_beta.wav

import argparse
import re
import struct
import sys
import urllib.request

import numpy as np
from PIL import Image


def read_wav(path):
    # go through the RIFF chunks one by one, keep the tags and the samples
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError(path + " is not a wav file")

    tags, samples, rate = {}, None, None
    pos = 12
    while pos + 8 <= len(data):
        name = data[pos:pos + 4]
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]

        if name == b"fmt ":
            rate = struct.unpack("<I", body[4:8])[0]
        elif name == b"data":
            samples = np.frombuffer(body, dtype="<i2").astype(np.int32)
        elif name == b"LIST" and body[:4] == b"INFO":
            p = 4
            while p + 8 <= len(body):
                tag = body[p:p + 4].decode()
                tsize = struct.unpack("<I", body[p + 4:p + 8])[0]
                tags[tag] = body[p + 8:p + 8 + tsize].rstrip(b"\x00").decode("latin-1")
                p += 8 + tsize + (tsize % 2)

        pos += 8 + size + (size % 2)     # chunks are padded to an even size
    return tags, samples, rate


def write_wav(path, samples, rate):
    fmt = struct.pack("<HHIIHH", 1, 1, rate, rate * 2, 2, 16)
    body = samples.astype("<i2").tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(body)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<I", 16) + fmt)
        f.write(b"data" + struct.pack("<I", len(body)) + body)


def run_brainfuck(code):
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


def download_from_drive(link, save_as):
    # a drive "view" link opens a web page, so take the file id out of it
    # and ask for the direct download instead
    found = re.search(r"/d/([A-Za-z0-9_-]+)", link)
    if not found:
        raise ValueError("no file id in the link")
    url = "https://drive.google.com/uc?export=download&id=" + found.group(1)

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if data[:4] != b"RIFF":
        raise ValueError("drive did not send a wav file")
    with open(save_as, "wb") as f:
        f.write(data)


def save_spectrogram(samples, path):
    # cut the sound into short overlapping pieces and take the FFT of each one.
    # every piece becomes one column of the picture
    size, step = 1024, 256
    window = np.hanning(size)
    columns = []
    for start in range(0, len(samples) - size, step):
        piece = samples[start:start + size] * window
        columns.append(np.abs(np.fft.rfft(piece)))
    spec = np.array(columns).T              # rows = frequency, columns = time

    spec = 20 * np.log10(spec + 1.0)        # to dB, the +1 avoids log(0)
    spec = spec / spec.max() * 255
    spec = spec[::-1, :]                    # high frequency on top, like audacity

    img = Image.fromarray(spec.astype(np.uint8))
    img = img.resize((1600, 600), Image.LANCZOS)
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description="solve stage 1")
    ap.add_argument("alpha", help="signal_alpha.wav from the platform")
    ap.add_argument("--beta", help="signal_beta.wav if it is already downloaded")
    args = ap.parse_args()

    # step 1 and 2
    alpha_tags, alpha, rate = read_wav(args.alpha)
    print("[1] tags in " + args.alpha + ":")
    for tag, text in alpha_tags.items():
        print("      " + tag + " = " + (text if len(text) < 70 else text[:67] + "..."))

    link = run_brainfuck(alpha_tags.get("IART", ""))
    print("[2] Artist tag is brainfuck, it prints:")
    print("      " + link)

    # step 3
    beta_path = args.beta
    if not beta_path:
        beta_path = "signal_beta.wav"
        print("[3] downloading " + beta_path + " ...")
        try:
            download_from_drive(link, beta_path)
        except Exception as e:
            print("[!] download failed (" + str(e) + ")")
            print("    open the link in a browser, download the file, then run again with --beta")
            return 1
    else:
        print("[3] using " + beta_path)

    beta_tags, beta, _ = read_wav(beta_path)
    if len(alpha) != len(beta):
        print("[!] the two files are not the same length")
        return 1

    # step 4
    # both files have the same noise and the same decoy.
    # subtracting removes them, only the real flag is left
    left = alpha - beta
    print("[4] alpha - beta done, loudest sample left = " + str(int(np.abs(left).max())))

    # step 5
    write_wav("stage1_result.wav", left, rate)
    save_spectrogram(left, "stage1_flag.png")
    print("[5] saved stage1_result.wav and stage1_flag.png")
    print("    open stage1_flag.png and read the flag")

    # step 6
    print("[6] Comment tag of beta (for stage 2):")
    print("      " + beta_tags.get("ICMT", "(no comment tag)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
