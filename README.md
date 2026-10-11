# Operation Silent Dawn: The Eclipse Infiltration

CTF Play Box for IE3132 Penetration Testing, Assignment 02. Six stages across six domains, flag format `Eclipse{...}`.

> This repository holds build and solver scripts, so it contains answer material. Keep it private.

## Group

| # | Member | Student ID | Stages | Other work |
|---|---|---|---|---|
| 1 | Samaratunga S.A.J.D.M | IT24102137 | 1, 2 | CTF platform implementation, architecture and platform design |
| 2 | Binuwara H.B.M.M.L | IT24103624 | 3 | Challenge testing, architecture diagram |
| 3 | Ranaweera C.A | IT24100520 | 4 | Platform integration and testing, risks |
| 4 | Gunawardhana M.S.A | IT24103304 | 5, 6 | Platform and architecture design |

## The box

| Stage | ID | Title | Domain | Difficulty | Points | Type |
|---|---|---|---|---|---|---|
| 1 | STEG-01 | The Intercepted Frequency | Steganography | Easy | 100 | Static files |
| 2 | OSINT-02 | Ground Telemetry | OSINT | Easy to Moderate | 150 | Static file |
| 3 | WEB-03 | The Staging Drop | Web security | Moderate | 200 | Live web service |
| 4 | NET-04 | Operation Silent Frequency | Networking | Moderate | 250 | Static file |
| 5 | CRYPTO-05 | The Weak Cipher | Cryptography | Moderate to Hard | 300 | Static files |
| 6 | REV-06 | The Kill-Switch Binary | Reverse engineering | Hard | 400 | Static file |

Players sign in to the platform, read each case, download its files or open its access link, and submit flags there. The platform checks flags, charges points for hints and keeps the scoreboard.

The box has three parts:

- **Platform.** Sentinel CTF, a custom platform on Vercel with Supabase for login, database and file storage. It replaced the CTFd platform proposed in Assignment 01.
- **Five static stages.** Stages 1, 2, 4, 5 and 6 are files that players download from the platform.
- **One live stage.** Stage 3 is a web application in a Docker container, reached through a Cloudflare quick tunnel.

`architecture/as-built-diagram.png` shows how they connect, and `architecture/ports-and-services.md` lists every service and port.

## Folder map

| Path | Contents | Owner |
|---|---|---|
| `platform/` | Link to the platform's source repository and live site | IT24102137 |
| `challenges/stage1-steg/` | Stage 1, The Intercepted Frequency | IT24102137 |
| `challenges/stage2-osint/` | Stage 2, Ground Telemetry | IT24102137 |
| `challenges/stage3-web/` | Stage 3, The Staging Drop | IT24103624 |
| `challenges/stage4-net/` | Stage 4, Operation Silent Frequency | IT24100520 |
| `challenges/stage5-crypto/` | Stage 5, The Weak Cipher | IT24103304 |
| `challenges/stage6-rev/` | Stage 6, The Kill-Switch Binary | IT24103304 |
| `architecture/a1-approved-diagram.png` | Diagram approved in Assignment 01 | IT24103624 |
| `architecture/as-built-diagram.png` | Diagram of the box as built | IT24102137 |
| `architecture/ports-and-services.md` | Ports, services and network layout as built | IT24102137 |

Every stage folder has the same layout:

| Path | Contents |
|---|---|
| `README.md` | How it was built, flag placement, intended solution path, hints, reset |
| `build/` | Build script, source code, Docker files |
| `dist/` | The exact files players receive |
| `solve/` | The owner's solver or exploit script |

## Setup

Deploying the box takes three steps: the platform, the static files, and the Stage 3 container.

**Requirements**

| For | Needed |
|---|---|
| Platform | A Supabase account and a Vercel account (free plans are enough) |
| Stage 3 | Docker with Compose, and `cloudflared` |
| Build and solver scripts | Python 3. Each stage README lists its libraries |

**1. Platform.** The source is in the `sentinel-ctf` repository (see `platform/README.md`). Its `docs/SETUP.md` has every step in detail. In short:

1. Create a Supabase project. In the SQL editor run `supabase/schema.sql`, then `supabase/seed.sql`.
2. Create a private storage bucket named `challenge-files`, and turn off public sign-up.
3. Put the project URL and public key in `public/config.js`.
4. Import the repository into Vercel. Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `FLAG_PEPPER` and `CHALLENGE_BUCKET`, then deploy.
5. Create the first user in Supabase and set its role to `admin`. Create player accounts from the admin console.
6. Set the flag of each stage from the admin console (Sentinel Control, Challenges, key icon). The flags are in the stage READMEs.

**2. Static files.** Upload the files in each stage's `dist/` folder to the `challenge-files` bucket, at the paths listed in Sentinel Control, Evidence. Upload `signal_beta.wav` of Stage 1 to Google Drive instead, at the link built into `signal_alpha.wav`.

**3. Stage 3.** Build and start the container:

```
cd challenges/stage3-web/build
docker compose up -d --build
```

## Run

1. Start the Stage 3 container if it is not running: `docker compose up -d` in `challenges/stage3-web/build`.
2. Open a tunnel to it:
   ```
   cloudflared tunnel --url http://localhost:8080
   ```
   It prints a random `https://....trycloudflare.com` address.
3. In the platform, go to Sentinel Control, Access links, and set that address as the Stage 3 link.
4. Players sign in at the platform address and start with Stage 1.
5. When the session ends, stop `cloudflared`. The address stops working, and the next start gives a new one.

The platform and the five static stages need nothing started. They are always available once deployed.

## Reset

| Part | How to reset |
|---|---|
| One player | Sentinel Control, Responders, Reset score on that player. Clears their solves and opened hints |
| All players | Sentinel Control, Responders, Testing & reset. Reset leaderboard clears all solves and hints. Clear audit log clears all submissions. Full reset does both |
| Stage 3 | `docker compose down`, then `docker compose up -d --build` in `challenges/stage3-web/build`. The database is rebuilt with the image |
| Stage 1 | `python build/stage1_build.py --out dist` in `challenges/stage1-steg` (on Windows) |
| Stage 2 | `python build/stage2_build.py --images build/source-images --out dist` in `challenges/stage2-osint` |
| Stage 4 | Run `build/generate_stage4.py` in `challenges/stage4-net` |
| Stages 5 and 6 | Run the generator in the stage's `build/` folder |

A platform reset never touches accounts, challenges, flags, hints, files or links. The static stages hold no state that players can change, so their reset is only needed if a file is lost or damaged. Each stage README has the details and, where the build is repeatable, the file hashes to check against.

## Tools and credits

| Tool or service | Used for |
|---|---|
| Vercel | Hosting the platform |
| Supabase | Login, database and file storage |
| Cloudflare (`cloudflared` quick tunnel) | Public address for Stage 3 |
| Docker and Docker Compose | Running Stage 3 |
| Python 3, Flask, SQLite | Stage 3 application |
| Python 3 with NumPy, SciPy, Pillow | Stage 1 and Stage 2 build and solver scripts |
| Python 3 with Scapy | Stage 4 generator |
| Audacity, exiftool | Stage 1 and Stage 2 |
| Google Drive | Hosting the second Stage 1 file |
| Google Street View and Google Maps | Stage 2 images and route |
| Wireshark | Stage 4 |

Each stage README lists the tools for that stage in full.

## How to contribute

1. Work on your own branch, named with your student ID, for example `IT24103624-binuwara`.
2. Commit from your own GitHub account, with your own name and email.
3. Open a pull request into `main`.
4. Never commit `.env` files, API keys or the platform's service-role key.
