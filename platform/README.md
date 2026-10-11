# CTF Platform - Sentinel CTF

| | |
|---|---|
| Owner | Samaratunga S.A.J.D.M (IT24102137) |
| Source repository | https://github.com/janiyax35/sentinel-ctf |
| Live site | https://ctf.janith.qzz.io |

The platform source is kept in its own repository, linked above. The live site is deployed from that repository, and its full commit history is there.

## Where to look in the source repository

| Path | Contents |
|---|---|
| `docs/SETUP.md` | Deployment steps: Supabase, Vercel, first admin, flags, files |
| `api/` | Serverless functions. Flag validation is in `api/submit.js` and `api/_lib/util.js` |
| `public/` | Static site |
| `supabase/` | `schema.sql` and `seed.sql` |
| `tools/hash-flag.js` | Script that computes a flag hash the same way the server does |

No flags are stored in the platform source. They are set from the admin console after deployment. The flag of each stage is in that stage's README under `challenges/`.
