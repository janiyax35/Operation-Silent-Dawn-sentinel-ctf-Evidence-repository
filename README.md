# Operation Silent Dawn: The Eclipse Infiltration

CTF Play Box for IE3132 Penetration Testing, Assignment 02. Six stages, flag format `Eclipse{...}`.

> This repository holds generator and solver scripts, so it contains answer material. Keep it private.

## Group

| # | Member | Student ID | Stages | Other work |
|---|---|---|---|---|
| 1 | Samaratunga S.A.J.D.M | IT24102137 | 1, 2 | CTF platform implementation, architecture and platform design |
| 2 | Binuwara H.B.M.M.L | IT24103624 | 3 | Challenge testing, architecture diagram |
| 3 | Ranaweera C.A | IT24100520 | 4 | Platform integration and testing, risks |
| 4 | Gunawardhana M.S.A | IT24103304 | 5, 6 | Platform and architecture design |

## Folder map

| Path | Contents | Owner |
|---|---|---|
| `platform/` | CTF platform source and setup guide | IT24102137 |
| `challenges/stage1-steg/` | Stage 1, The Intercepted Frequency | IT24102137 |
| `challenges/stage2-osint/` | Stage 2, Ground Telemetry | IT24102137 |
| `challenges/stage3-web/` | Stage 3, The Staging Drop | IT24103624 |
| `challenges/stage4-net/` | Stage 4, Operation Silent Frequency | IT24100520 |
| `challenges/stage5-crypto/` | Stage 5, The Weak Cipher | IT24103304 |
| `challenges/stage6-rev/` | Stage 6, The Kill-Switch Binary | IT24103304 |
| `architecture/a1-approved-diagram.png` | Diagram approved in Assignment 01 | IT24103624 |
| `architecture/as-built-diagram.png` | Diagram of the box as built | IT24103624 |
| `architecture/ports-and-services.md` | Ports, services and network layout as built | IT24103304 |

Every stage folder has the same layout:

| Path | Contents |
|---|---|
| `README.md` | How it was built, flag placement, intended solution path, hints, reset command |
| `build/` | Generator script, source code, Docker files |
| `dist/` | The exact files players receive |
| `solve/` | The owner's solver or exploit script |

## Setup

_To be written._

## Run

_To be written._

## Reset

_To be written._

## Tools and credits

_Each member lists the external tools, frameworks, images and references they used._

## How to contribute

1. Work on your own branch, named with your student ID, for example `IT24103624/stage3`.
2. Commit from your own GitHub account, with your own name and email.
3. Open a pull request into `main`.
4. Never commit `.env` files, API keys or the platform's service-role key.
