# Ports and services (as built)

Written by Samaratunga S.A.J.D.M (IT24102137). The diagram for this page is `as-built-diagram.png` in the same folder.

## Services

| Component | Runs on | Port / protocol | Purpose | Reachable from |
|---|---|---|---|---|
| Sentinel CTF platform (static site and `/api` functions) | Vercel, `ctf.janith.qzz.io` | 443/TCP, HTTPS | Login page, challenges, hints, flag submission, scoreboard, admin console | Internet. Every page with content needs a signed-in account |
| Supabase Auth | Supabase cloud | 443/TCP, HTTPS | Email and password sign-in | The browser, with the public key. Public sign-up is turned off |
| Supabase database | Supabase cloud | 443/TCP, HTTPS | Challenges, flag hashes, hints, solves, audit log | Only the platform's `/api` functions, with the service-role key. Row-level security blocks the public key |
| Supabase Storage, bucket `challenge-files` | Supabase cloud | 443/TCP, HTTPS | Files for Stages 1, 2, 4, 5 and 6 | A signed link from the platform, valid for 60 seconds |
| Stage 3 web app, container `stage3-staging-drop` | Docker on the Stage 3 owner's machine | 8080/TCP, HTTP | The intentionally vulnerable web application | The host machine and its local network (the port is published as `8080:8080`) |
| Cloudflare quick tunnel (`cloudflared`) | Same machine as the Stage 3 container | Outbound connection to Cloudflare. Players use 443/TCP, HTTPS, on a random `trycloudflare.com` address | Carries player traffic to `localhost:8080` | Internet, for anyone who has the address |
| Google Drive | Google | 443/TCP, HTTPS | Hosts `signal_beta.wav` for Stage 1 | Anyone who has the link from the Stage 1 metadata |

Stages 1, 2, 4, 5 and 6 are static files. They have no service and open no port.

## Network layout

The box has no shared lab network. Its parts talk to each other over HTTPS:

1. A player's browser opens the platform on Vercel and signs in through Supabase Auth.
2. The browser calls the platform's `/api` functions. Only those functions talk to the database and storage.
3. For a file download, the platform returns a signed Supabase Storage link and the browser fetches the file directly.
4. For Stage 3, the case page shows an access link. It points to the Cloudflare quick tunnel, which forwards to the container on port 8080.
5. For Stage 1, the player follows a Google Drive link that they decode from the first file.

### Stage 3 container

From `challenges/stage3-web/build/docker-compose.yml` and `Dockerfile`:

| Setting | Value |
|---|---|
| Network | `stage3_net`, a Docker bridge network used only by this container |
| Published port | `8080:8080` |
| User | `65532:65532` (not root) |
| Limits | 1 CPU, 512 MB memory |
| Security option | `no-new-privileges` |
| Restart policy | `unless-stopped` |
| Database | SQLite file created when the image is built |

### What is exposed

- The quick tunnel forwards one thing only: HTTP on `localhost:8080`. Nothing else on the host is reachable through it.
- The tunnel is an outbound connection, so no port is opened on the router.
- The tunnel address is random and changes every time `cloudflared` is started. The admin puts the current address on the Stage 3 case page under Sentinel Control, Access links. Only signed-in players can see it.
- A quick tunnel has no login step of its own. Anyone who has the address can reach the Stage 3 app while the tunnel is running, so the tunnel is started for a session and stopped when the session ends.
- Port 8080 is also published on the host, so the app can be reached from the host's local network.

## Differences from the Assignment 01 port table

| Assignment 01 | As built | Change |
|---|---|---|
| CTFd platform, 443/TCP, on the lab Docker host | Sentinel CTF platform, 443/TCP, on Vercel with Supabase | CTFd was replaced by the custom platform |
| Stage 3 web service, 8080/TCP, inside the isolated network | Stage 3 container, 8080/TCP, reached through a Cloudflare quick tunnel on 443/TCP | Players reach it over the internet instead of a host-only network |
| Supporting file host, 80/TCP, serving the second Stage 1 file | No file host. `signal_beta.wav` is on Google Drive | One service fewer to run |
| One host-only network for the whole box, no internet path | No shared network. Managed cloud services for the platform, one container for Stage 3 | The platform moved from a lab host to cloud hosting |

The reasons for these changes are given in the video, in the design-changes part.
