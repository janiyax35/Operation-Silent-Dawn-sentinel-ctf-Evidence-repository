# Stage 2 - Ground Telemetry (OSINT-02)

| | |
|---|---|
| Owner | Samaratunga S.A.J.D.M (IT24102137) |
| Domain | OSINT |
| Difficulty | Easy to Moderate |
| Points | 150 |

## How it was built

The challenge file `telemetry_route.log` looks like a log file, but it is a password-protected Zip archive holding four dashcam-style images of a road route. It is built in two steps.

**Step 1, metadata.** The four images in `build/source-images/` are street-level frames taken along a real route, from the starting point to the destination gate. `build/inject_metadata.sh` uses exiftool to make them look like dashcam captures:

| Image | Timestamp (2026-09-18, +05:30) | GPS position |
|---|---|---|
| `image0_starting_point.jpg` | 13:00:00 | 6.854381 N, 80.078970 E |
| `image1.jpg` | 13:07:00 | none |
| `image2.jpg` | 13:10:00 | none |
| `image04_destination.jpg` | 13:12:00 | none |

All four carry the same camera details (BlackVue DR900X Plus). Only the first image has a GPS position, so players get the starting point and have to trace the rest of the route from what the images show.

**Step 2, packing.** `build/stage2_build.py` compresses the four images into a Zip archive, encrypts each entry with the standard Zip password scheme (ZipCrypto, the same one `zip -e` uses), and saves the result as `telemetry_route.log`. The password is the passphrase from the Comment tag of `signal_beta.wav` in Stage 1.

The script uses a fixed file time and fixed header bytes, so it produces the same archive on every run. It refuses to run if an image has no timestamp, if the first image has no GPS position, or if any other image has one. This catches the case where step 1 was skipped.

## Flag placement

The flag is not stored in any file. It is the original name of the facility at the end of the route.

The gate in `image04_destination.jpg` shows only the facility's present-day signage. Older street-level imagery of the same gate, from around 2015, shows the original nameboard: `SATELLITE EARTH STATION - PADUKKA`.

Flag: `Eclipse{satellite_earth_station_padukka}`

The flag is checked case-insensitively.

## Intended solution path

1. Download `telemetry_route.log` and check what it really is:
   `file telemetry_route.log`
   It reports a Zip archive, not text.
2. Try to extract it. It asks for a password.
3. Use the passphrase from Stage 1. It is in the Comment tag of `signal_beta.wav`:
   `exiftool signal_beta.wav`
4. Extract the images:
   `unzip telemetry_route.log -d route`
5. Read their metadata:
   `exiftool route/*.jpg`
   The timestamps give the order of the images. Only `image0_starting_point.jpg` has a GPS position.
6. Open that position in a mapping service and switch to street-level view.
7. Follow the road in the direction the images show, matching each frame in time order, until the gate in the last image.
8. At the gate, open the older imagery dates and go back to around 2015. Read the original nameboard.
9. Write the name in lowercase with underscores and submit it.

`solve/stage2_solve.py` automates steps 1 to 6. It identifies the file type from its first bytes, reads the passphrase from `signal_beta.wav`, extracts the images, lists them in time order with their camera details, and prints the starting point as a map link. Steps 7 to 9 are manual.

```
python solve/stage2_solve.py dist/telemetry_route.log --beta ../stage1-steg/dist/signal_beta.wav
```

## Hints

| Hint | Cost | Text on the platform |
|---|---|---|
| 1 | 15 | A file that calls itself a log has made no promises about what it contains. |
| 2 | 30 | Some record of what a place used to be called tends to linger online even after the sign out front has changed. |

Hint 2 is locked until hint 1 is opened. Hint 1 points to the file type deception at the start. Hint 2 points to the historical imagery step at the end, which is the hardest part, so it costs more.

## Reset

Stage 2 is a static file with no live service, so players cannot change its state. The platform's admin reset clears player progress only.

If the challenge file is lost or damaged, rebuild it from the images in this repository:

```
python build/stage2_build.py --images build/source-images --out dist
```

The output is identical every time. The script prints the SHA-256, which must match:

| File | SHA-256 |
|---|---|
| `telemetry_route.log` | `ce68d08d1c4517a54eb10b4fe186f4e7fc1ca66498901423f80da5723aa867f0` |

The images in `build/source-images/` already carry their metadata, so `inject_metadata.sh` is only needed when starting again from fresh captures. In that case run it inside the images folder first:

```
cd build/source-images
bash ../inject_metadata.sh
```

The passphrase in `stage2_build.py` must stay the same as `STAGE2_PASSPHRASE` in the Stage 1 build script.

## Dependency

The archive can be downloaded at any time, but it cannot be opened without the passphrase from Stage 1. A player who has not finished Stage 1 can still work on the other stages.

## Folder contents

| Folder | Contents |
|---|---|
| `build/` | `inject_metadata.sh`, `stage2_build.py` and `source-images/` with the four images |
| `dist/` | `telemetry_route.log`, the exact file players receive |
| `solve/` | `stage2_solve.py`, the solver |

## Tools and credits

| Tool or source | Used for |
|---|---|
| Google Street View | Source of the four route images and of the historical imagery used in the solve |
| Google Maps | Tracing the route from the starting point |
| exiftool | Writing and reading the image metadata |
| Python 3 with Pillow | Build script and solver |
| unzip, file | Identifying and extracting the archive in the manual solve |
