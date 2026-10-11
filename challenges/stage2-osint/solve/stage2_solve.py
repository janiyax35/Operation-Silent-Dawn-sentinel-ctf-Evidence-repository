#!/usr/bin/env python3
# Stage 2 (OSINT-02) solver
#
# what it does:
#   1. looks at the first bytes of telemetry_route.log to find the real file type
#   2. gets the passphrase from the Comment tag of signal_beta.wav (stage 1)
#   3. extracts the images with that passphrase
#   4. reads the metadata of every image and puts them in time order
#   5. prints the gps position of the starting point as a map link
#
# the last part is manual: follow the road from the start point using the
# images, find the destination and read the name of the place. that is the flag
#
# need:  pip install Pillow
# run :  python3 stage2_solve.py telemetry_route.log --beta signal_beta.wav
#        python3 stage2_solve.py telemetry_route.log --password <passphrase>

import argparse
import os
import struct
import sys
import zipfile

from PIL import Image

# first bytes of some common file types
MAGIC = [
    (b"PK\x03\x04", "zip archive"),
    (b"\x1f\x8b", "gzip"),
    (b"7z\xbc\xaf", "7-zip archive"),
    (b"Rar!", "rar archive"),
    (b"\xff\xd8\xff", "jpeg image"),
    (b"\x89PNG", "png image"),
]


def real_type(path):
    with open(path, "rb") as f:
        start = f.read(8)
    for magic, name in MAGIC:
        if start.startswith(magic):
            return name
    return "unknown (maybe really a text file)"


def comment_of_wav(path):
    # the tags of a wav file are in the LIST/INFO chunk, ICMT is the comment
    with open(path, "rb") as f:
        data = f.read()
    pos = 12
    while pos + 8 <= len(data):
        name = data[pos:pos + 4]
        size = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]
        if name == b"LIST" and body[:4] == b"INFO":
            p = 4
            while p + 8 <= len(body):
                tsize = struct.unpack("<I", body[p + 4:p + 8])[0]
                if body[p:p + 4] == b"ICMT":
                    return body[p + 8:p + 8 + tsize].rstrip(b"\x00").decode("latin-1")
                p += 8 + tsize + (tsize % 2)
        pos += 8 + size + (size % 2)
    return ""


def to_degrees(value, ref):
    # gps is stored as degrees, minutes, seconds
    d, m, s = [float(x) for x in value]
    degrees = d + m / 60 + s / 3600
    return -degrees if ref in ("S", "W") else degrees


def read_image(path):
    exif = Image.open(path).getexif()
    gps = exif.get_ifd(0x8825)
    position = None
    if 2 in gps and 4 in gps:
        position = (to_degrees(gps[2], gps.get(1, "N")), to_degrees(gps[4], gps.get(3, "E")))
    return {
        "name": os.path.basename(path),
        "taken": exif.get_ifd(0x8769).get(0x9003, "?"),
        "camera": str(exif.get(0x010F, "?")) + " " + str(exif.get(0x0110, "")),
        "position": position,
    }


def main():
    ap = argparse.ArgumentParser(description="solve stage 2")
    ap.add_argument("file", help="telemetry_route.log from the platform")
    ap.add_argument("--beta", help="signal_beta.wav from stage 1")
    ap.add_argument("--password", help="the passphrase, if you already know it")
    ap.add_argument("--out", default="route", help="folder for the extracted images")
    args = ap.parse_args()

    # step 1
    kind = real_type(args.file)
    print("[1] " + args.file + " is really a: " + kind)
    if kind != "zip archive":
        print("[!] this solver only knows what to do with a zip")
        return 1

    # step 2
    password = args.password
    if not password and args.beta:
        comment = comment_of_wav(args.beta)
        print("[2] Comment tag of " + args.beta + ": " + comment)
        password = comment.split("=", 1)[-1]      # ARCHIVE_PASSPHRASE=xxxx
    if not password:
        print("[!] give --beta signal_beta.wav or --password")
        return 1

    # step 3
    try:
        with zipfile.ZipFile(args.file) as z:
            z.extractall(args.out, pwd=password.encode())
            names = z.namelist()
    except RuntimeError:
        print("[!] wrong passphrase")
        return 1
    print("[3] extracted " + str(len(names)) + " files into " + args.out + "/")

    # step 4
    images = [read_image(os.path.join(args.out, n)) for n in names]
    images.sort(key=lambda i: i["taken"])
    print("[4] images in time order:")
    for i in images:
        where = "no gps"
        if i["position"]:
            where = "%.6f, %.6f" % i["position"]
        print("      " + i["taken"] + "  " + i["name"].ljust(28) + i["camera"] + "  |  " + where)

    # step 5
    for i in images:
        if i["position"]:
            print("[5] starting point on the map:")
            print("      https://www.google.com/maps?q=%.6f,%.6f" % i["position"])
    print("[i] from there follow the road shown in the images, in time order,")
    print("    find the last place and read its name. flag = Eclipse{name_of_the_place}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
