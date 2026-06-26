# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from repo root via `make`, or directly inside `web/`:

```bash
make generate     # regenerate web/src/lib/data/bobs.json from the CSV (run after editing CSV)
make dev          # cd web && npm run dev (localhost:5173)
make build        # make generate + cd web && npm run build
make docker-build # build Docker image (cached via .docker-build-stamp)
make docker-run   # build + run container, prints mapped port
make docker-kill  # stop running container

cd web && npm test          # vitest run (unit tests)
cd web && npm run check     # svelte-check + tsc
```

Deploy on push to `main` via GitHub Actions (build → check → `flyctl deploy --remote-only`).

## Architecture

Static SvelteKit app (`adapter-static`) served by nginx on Fly.io with scale-to-zero. No backend; all state is client-side.

```
web/src/
  routes/+page.svelte        — layout: timeline slider + map + status table
  lib/Map.svelte             — SVG map renderer + ambient decorations
  lib/data/bobs.ts           — loads bobs.json, sorts by (bob, assumed_date)
  lib/data/coords.ts         — SYSTEM_COORDS: 10 known star systems (LY coordinates)
  lib/data/positions.ts      — computePositions(): interpolates Bob positions by date
  lib/data/bobs.json         — source of truth used at build time
data/
  bobs.json                  — raw data (for reference; web uses the copy in web/src/lib/data/)
  schema.md                  — field definitions
```

## Data Flow

`bobs.json` → `bobs.ts` (parse + sort) → `computePositions(records, selectedDate)` → `Map.svelte` + status table.

`computePositions` (parity with the legacy Python `app/data.py:35`): for each Bob, finds the last past entry and first future entry; if they're different systems, linearly interpolates position and computes heading angle `90 - atan2(dy,dx)*180/π`; otherwise stationary.

## Map Rendering (`Map.svelte`)

- SVG viewBox `960×720` with linear scales; Y is inverted (data up, SVG down).
- Traveling Bobs: probe-shaped marker (`PROBE_HULL` path) rotated by `angle`.
- Stationary Bobs: square marker.
- Dense stationary clusters (≥2 Bobs at same rounded coords): collapse to single marker + count badge; names shown on hover via `<title>`.
- Label de-collision: greedy upward-bump algorithm in `labelDy`.
- Ambient decorations: 70 dust motes + 6 shooting stars, pure CSS animation, generated once on mount — not data-driven.

## Adding Data

Edit `web/src/lib/data/bobs.json`. Each record needs `bob`, `system`, `assumed_date` (ISO `YYYY-MM-DD`, day always `01`).

`system` must match a key in `SYSTEM_COORDS` (`web/src/lib/data/coords.ts`) or it silently falls back to `(0, 0)`. To add a new star system, add it to `SYSTEM_COORDS` first.

## Key Notes

- Svelte 5 runes syntax (`$state`, `$derived`, `$props`) — not Svelte 4 reactive declarations.
- No chart library — all rendering is plain SVG.
- `data/bobs.json` (repo root) and `web/src/lib/data/bobs.json` are separate files; the web build only sees the one under `web/`.
- CI drops linting step (removed ruff); PR check runs `npm run build && npm run check`.
