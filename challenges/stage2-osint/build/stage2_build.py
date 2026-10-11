#!/usr/bin/env python3
# Stage 2 (OSINT-02) - Ground Telemetry
# packs the four dashcam images into the challenge file
#
#   telemetry_route.log  -> looks like a log file, but it is a password protected zip
#
# the password is the passphrase hidden in the Comment tag of signal_beta.wav
# (stage 1), so the player needs stage 1 to open this file
#
# this script only does the packing. run inject_metadata.sh on the images first,
# that script writes the dashcam metadata and the gps position
#
# need:  pip install Pillow
# run :  python3 stage2_build.py
#        python3 stage2_build.py --images "Location images" --out dist

import argparse
import hashlib
import os
import random
import struct
import sys
import zlib

from PIL import Image

# must be the same as STAGE2_PASSPHRASE in stage1_build.py
PASSPHRASE = "Sentinel_Telemetry_Override_8021"

# in the order of the route
IMAGES = [
    "image0_starting_point.jpg",
    "image1.jpg",
    "image2.jpg",
    "image04_destination.jpg",
]

OUTPUT_NAME = "telemetry_route.log"

# fixed values, so every run gives exactly the same file (same sha256)
SEED = 0xEC11B5E
ZIP_DATE = ((2026 - 1980) << 9) | (9 << 5) | 18     # 2026-09-18
ZIP_TIME = (13 << 11) | (12 << 5)                   # 13:12:00


def check_metadata(folder):
    # stop early if inject_metadata.sh was not run.
    # every image needs a timestamp, and only the first one has gps
    for i, name in enumerate(IMAGES):
        exif = Image.open(os.path.join(folder, name)).getexif()
        taken = exif.get_ifd(0x8769).get(0x9003)     # DateTimeOriginal
        has_gps = 2 in exif.get_ifd(0x8825)          # GPSLatitude
        if not taken:
            return name + " has no timestamp, run inject_metadata.sh first"
        if i == 0 and not has_gps:
            return name + " has no gps position, run inject_metadata.sh first"
        if i > 0 and has_gps:
            return name + " has a gps position, only the first image should have one"
    return None


# ---- old style zip password (ZipCrypto), this is what "zip -e" uses ----

CRC_TABLE = []
for n in range(256):
    c = n
    for _ in range(8):
        c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
    CRC_TABLE.append(c)


def zip_encrypt(data, password):
    # three keys that change after every byte
    k0, k1, k2 = 0x12345678, 0x23456789, 0x34567890

    def update(byte):
        nonlocal k0, k1, k2
        k0 = CRC_TABLE[(k0 ^ byte) & 0xFF] ^ (k0 >> 8)
        k1 = ((k1 + (k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
        k2 = CRC_TABLE[(k2 ^ (k1 >> 24)) & 0xFF] ^ (k2 >> 8)

    for byte in password:          # mix the password into the keys first
        update(byte)

    out = bytearray()
    for byte in data:
        t = k2 | 2
        out.append(byte ^ (((t * (t ^ 1)) >> 8) & 0xFF))
        update(byte)
    return bytes(out)


def pack(folder, out_path):
    rng = random.Random(SEED)
    password = PASSPHRASE.encode()
    file_part = b""          # the files, one after another
    index_part = b""         # the index at the end of the zip

    for name in IMAGES:
        with open(os.path.join(folder, name), "rb") as f:
            data = f.read()
        crc = zlib.crc32(data)

        squeezer = zlib.compressobj(9, zlib.DEFLATED, -15)
        small = squeezer.compress(data) + squeezer.flush()

        # 12 extra bytes go in front of every encrypted file. the last one is
        # part of the crc, unzip uses it to tell if the password is wrong
        header12 = bytes(rng.randrange(256) for _ in range(11)) + bytes([crc >> 24])
        locked = zip_encrypt(header12 + small, password)

        offset = len(file_part)
        fname = name.encode()
        # 20 = zip version, 1 = "encrypted" flag, 8 = deflate
        common = struct.pack("<HHHHHIIIHH", 20, 1, 8, ZIP_TIME, ZIP_DATE,
                             crc, len(locked), len(data), len(fname), 0)
        file_part += b"PK\x03\x04" + common + fname + locked
        index_part += (b"PK\x01\x02" + struct.pack("<H", 20) + common
                       + struct.pack("<HHHII", 0, 0, 0, 0, offset) + fname)

    end = b"PK\x05\x06" + struct.pack("<HHHHIIH", 0, 0, len(IMAGES), len(IMAGES),
                                      len(index_part), len(file_part), 0)
    with open(out_path, "wb") as f:
        f.write(file_part + index_part + end)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description="build the stage 2 challenge file")
    ap.add_argument("--images", default="source-images", help="folder with the four images")
    ap.add_argument("--out", default=".", help="output folder (default: current folder)")
    args = ap.parse_args()

    for name in IMAGES:
        if not os.path.exists(os.path.join(args.images, name)):
            print("[!] missing " + os.path.join(args.images, name))
            return 1

    problem = check_metadata(args.images)
    if problem:
        print("[!] " + problem)
        return 1

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, OUTPUT_NAME)
    print("[i] packing, this takes a few seconds ...")
    pack(args.images, out_path)

    print("[+] images inside the archive:")
    for name in IMAGES:
        print("    " + sha256(os.path.join(args.images, name)) + "  " + name)
    print("[+] " + out_path)
    print("    sha256 " + sha256(out_path))
    print("[i] upload " + OUTPUT_NAME + " to the platform")
    return 0


if __name__ == "__main__":
    sys.exit(main())
