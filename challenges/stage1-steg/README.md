# Stage 1 - The Intercepted Frequency (STEG-01)

| | |
|---|---|
| Owner | Samaratunga S.A.J.D.M (IT24102137) |
| Domain | Steganography |
| Difficulty | Easy |
| Points | 100 |

## How it was built

`build/stage1_build.py` generates two WAV files (mono, 16-bit, 22050 Hz, 16 seconds):

| File | Contents | How players get it |
|---|---|---|
| `signal_alpha.wav` | noise + decoy flag + real flag | Downloaded from the platform |
| `signal_beta.wav` | noise + decoy flag | Google Drive, link hidden in the alpha metadata |

Both flags are text drawn into the spectrogram. The script renders the text as a picture, then plays one sine wave per frequency row between 2500 Hz and 8500 Hz. A wave is loud where the picture is white and silent where it is black, so the text appears when the sound is viewed as a spectrogram.

The noise (white noise, mains hum, a 1 kHz carrier, sweeps and crackle) and the decoy are identical in both files. The real flag is added to alpha only, at a much lower level than the decoy, so it cannot be seen or heard on its own. The shared part is rounded to 16-bit once and reused in both files, so `alpha - beta` leaves exactly the real flag, sample by sample.

The metadata links the stages together:

| File | Tag | Value |
|---|---|---|
| `signal_alpha.wav` | Artist (`IART`) | A Brainfuck program that prints the Google Drive link of `signal_beta.wav` |
| `signal_beta.wav` | Comment (`ICMT`) | `ARCHIVE_PASSPHRASE=...`, the password of the Stage 2 archive |

The random seed is fixed, so the script produces the same files on every run. Before writing anything, it runs the Brainfuck program and stops if the output is not the Drive link.

## Flag placement

The real flag exists only as quiet spectrogram text inside `signal_alpha.wav`, underneath the decoy and the noise. It becomes readable only after `signal_beta.wav` is inverted and mixed with alpha, which cancels everything the two files share.

| | Value |
|---|---|
| Real flag | `Eclipse{ph4s3_c4nc3ll4t10n_succ3ss}` |
| Decoy flag | `Eclipse{f4k3_sp3ctr0gr4m_tr4p}` |

The decoy is clearly visible in the spectrogram of alpha. Submitting it fails.

## Intended solution path

1. Download `signal_alpha.wav` and open it in Audacity. Switch the track to Spectrogram view. A flag is visible, but it is the decoy.
2. Read the metadata:
   `exiftool signal_alpha.wav`
   The Artist tag is a long string of `+ - < > [ ] .` characters, which is Brainfuck.
3. Run the Artist tag in a Brainfuck interpreter. It prints a Google Drive link.
4. Open the link and download `signal_beta.wav`.
5. In Audacity, import `signal_beta.wav` next to alpha. Select the beta track and apply Effect, Invert. Select both tracks and choose Tracks, Mix, Mix and Render.
6. View the mixed track as a spectrogram. The noise and the decoy are gone and the real flag is readable.
7. Submit the flag.
8. Run `exiftool signal_beta.wav` and note the Comment tag. It is needed to open the Stage 2 file.

`solve/stage1_solve.py` automates steps 2 to 6 and step 8. It reads the tags, runs the Brainfuck, subtracts beta from alpha, saves the result as `stage1_result.wav` and its spectrogram as `stage1_flag.png`, and prints the Comment tag of beta. Sample output is in `solve/output/`.

```
python solve/stage1_solve.py dist/signal_alpha.wav --beta dist/signal_beta.wav
```

Without `--beta`, the solver downloads the file from the decoded Drive link.

## Hints

| Hint | Cost | Text on the platform |
|---|---|---|
| 1 | 10 | Not everything visible in the spectrogram is genuine. Inspect the file metadata with command-line forensic utilities. |
| 2 | 20 | Two opposite waves of identical frequency cancel each other out. Look into Audacity's "Invert" effect. |

Hint 2 is locked until hint 1 is opened. Hint 1 says the visible flag is fake and points to the metadata. Hint 2 names the technique and the tool, so it costs more.

## Reset

Stage 1 is two static files with no live service, so players cannot change its state. The platform's admin reset clears player progress only.

If a file is lost or damaged, rebuild both:

```
python build/stage1_build.py --out dist
```

The script prints the SHA-256 of each file. They must match:

| File | SHA-256 |
|---|---|
| `signal_alpha.wav` | `98abba2b520f6e7293c4de08edf0483a3f570037feb71983645a89875205660f` |
| `signal_beta.wav` | `5e2cd0c1b73e4b0f25da10106990d0b26d0d19413227446761dbd348efee4dd1` |

Build on Windows. The text is drawn with Courier New Bold, and on Linux the script falls back to another font, which changes the audio and the hashes.

`signal_beta.wav` must stay at the same Google Drive link. If the Drive file is replaced under a new link, the Brainfuck program and `DRIVE_LINK` in the build script have to be updated together.

## Folder contents

| Folder | Contents |
|---|---|
| `build/` | `stage1_build.py`, the generator |
| `dist/` | `signal_alpha.wav` (on the platform) and `signal_beta.wav` (on Google Drive) |
| `solve/` | `stage1_solve.py`, the solver, and `output/` with its results |

## Tools and credits

| Tool | Used for |
|---|---|
| Python 3 with NumPy, SciPy and Pillow | Building the files and the solver |
| Audacity | Spectrogram view, invert and mix in the manual solve |
| exiftool | Reading the WAV metadata |
| A Brainfuck interpreter | Decoding the Artist tag |
| Google Drive | Hosting `signal_beta.wav` |
