# Bobiverse Bob Tracker

A Streamlit app that visualizes Bob clone locations in space, chapter by chapter, from Dennis E. Taylor's Bobiverse series.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Repository Structure](#repository-structure)
3. [Technology Stack](#technology-stack)
4. [Environment Strategy](#environment-strategy)
5. [Pre-Flight Checklist](#pre-flight-checklist)
6. [Implementation Stories](#implementation-stories)
7. [Secrets & Config Management](#secrets--config-management)
8. [Definition of Done](#definition-of-done)

---

## Architecture Overview

```
Browser
  │
  ▼
Fly.io Machine (scale to zero)
  │
  ▼
Streamlit App (Python)
  │
  ├── Chapter selector (sidebar)
  ├── Interactive space map (plotly)
  └── Bob data (JSON/CSV flat file — no DB needed)
```

### Key Design Decisions

- **No database** — Bob location data is static (books don't change). A versioned JSON/CSV file in the repo is sufficient and simplest.
- **Scale to zero** — app is hosted on a Fly.io Machine with `min_machines_running = 0`. It costs nothing when idle and wakes in ~2-3 seconds on first request.
- **Streamlit only** — no Go proxy, no Caddy. Fly.io handles TLS and routing directly. The personal site embeds this via iframe using the Fly.io URL.
- **Extensibility** — adding a new book's data means adding rows to the data file and a new chapter range. No code change required.

---

## Repository Structure

```
bobiverse-tracker/
├── README.md
├── fly.toml                   ← Fly.io machine config (scale to zero)
├── Dockerfile
├── requirements.txt
├── .streamlit/
│   └── config.toml            ← disable toolbar for clean iframe embed
├── app/
│   ├── main.py                ← Streamlit entry point
│   ├── map.py                 ← map rendering logic
│   ├── data.py                ← data loading + filtering
│   └── components/
│       ├── chapter_selector.py
│       └── bob_info.py
└── data/
    ├── bobs.json              ← Bob clone data (name, location, chapter)
    └── schema.md              ← documents the data format
```

---

## Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| App framework | Streamlit | Already in use; great for interactive data apps |
| Map | Plotly | Interactive 3D/2D space map, works natively in Streamlit |
| Data | JSON flat file | Static data, no DB overhead |
| Hosting | Fly.io (scale to zero) | $0 when idle, fast cold start, Docker-native |
| CI/CD | GitHub Actions | Auto-deploy on push to `main` |

---

## Environment Strategy

| | Local | Production (Fly.io) |
|---|---|---|
| Run command | `streamlit run app/main.py` | Docker via Fly Machine |
| URL | `http://localhost:8501` | `https://bobiverse.brandonlocke.xyz` |
| Data | `data/bobs.json` | same file, baked into image |
| Secrets | none needed | none needed |

---

## Pre-Flight Checklist

```bash
# Python env set up
python --version  # 3.12+
pip install -r requirements.txt

# App runs locally
streamlit run app/main.py

# Docker builds
docker build -t bobiverse-tracker .
docker run -p 8501:8501 bobiverse-tracker

# Fly CLI installed
fly version
fly auth whoami
```

---

## Data Format

`data/bobs.json` — one entry per Bob per chapter appearance:

```json
[
  {
    "name": "Bob",
    "clone_id": "Bob-1",
    "book": 1,
    "chapter": 3,
    "system": "Sol",
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "notes": "Starting point"
  }
]
```

See `data/schema.md` for full field definitions. Adding a new book = adding rows to this file.

---

## Implementation Stories

---

### EPIC 1 — App Cleanup & Structure

**Epic Goal:** Existing local Streamlit app is refactored into a clean, maintainable structure ready for Dockerization and deployment.

---

#### Story 1.1 — Refactor Into Module Structure

**Context:** App currently exists as a single local Streamlit script. Need to split into modules before adding features or deploying.

**Assumptions:**
- Existing `app.py` (or equivalent) is the starting point
- No Docker setup exists yet

**Tasks:**
- Create directory structure per [Repository Structure](#repository-structure)
- Move existing map logic into `app/map.py`
- Move data loading into `app/data.py`
- Move chapter selector UI into `app/components/chapter_selector.py`
- `app/main.py` is the entry point — imports and composes the above
- Create `data/bobs.json` from existing data (or placeholder if data is inline)
- Write `data/schema.md` documenting all fields
- `requirements.txt` with pinned versions

**Out of Scope:** Any new features, Docker, deployment.

**Acceptance Criteria:**
- [ ] `streamlit run app/main.py` runs the app locally, same behavior as before refactor
- [ ] No logic in `main.py` — it only composes components
- [ ] `data/bobs.json` is valid JSON and matches schema in `data/schema.md`
- [ ] `pip install -r requirements.txt` installs all deps cleanly in a fresh venv

---

#### Story 1.2 — Streamlit Config for Iframe Embed

**Context:** Story 1.1 complete. App runs locally in modular form.

**Assumptions:**
- App will be embedded via iframe on the personal site
- Streamlit toolbar/hamburger menu should be hidden for clean embed

**Tasks:**
- Create `.streamlit/config.toml`:
  ```toml
  [server]
  headless = true
  address = "0.0.0.0"
  port = 8501

  [client]
  toolbarMode = "minimal"
  showSidebarNavigation = false

  [theme]
  # set a theme that matches personal site aesthetic
  ```
- Verify toolbar is hidden when running locally
- Set a color theme (dark preferred, to match personal site)

**Acceptance Criteria:**
- [ ] `streamlit run app/main.py` — no Streamlit toolbar visible
- [ ] App renders cleanly at a narrow viewport (iframe width ~800px)
- [ ] Theme does not clash with a dark background

---

### EPIC 1 Integration Gate

- [ ] `streamlit run app/main.py` — app loads, map renders, chapter selector works
- [ ] All Bob data visible and correct for at least 3 chapters
- [ ] No visible Streamlit toolbar
- [ ] App usable at 800px wide viewport

---

### EPIC 2 — Map Improvements

**Epic Goal:** Map is interactive, visually clear, and chapter navigation feels polished.

---

#### Story 2.1 — Chapter Navigation

**Context:** Epic 1 complete. App is structured and styled.

**Assumptions:**
- `data/bobs.json` has `book` and `chapter` fields per entry
- Plotly is available in requirements

**Tasks:**
- Sidebar: book selector (dropdown) → chapter slider updates to that book's range
- Map updates instantly when chapter changes (no page reload)
- Show chapter title or label if available in data
- "Previous / Next chapter" buttons below the slider

**Out of Scope:** Animations between chapters.

**Acceptance Criteria:**
- [ ] Selecting a book updates the chapter slider range correctly
- [ ] Moving the slider updates the map without full page reload
- [ ] Previous/Next buttons increment/decrement chapter
- [ ] Chapter 1 → Previous button disabled; final chapter → Next button disabled

---

#### Story 2.2 — Map Visual Polish

**Context:** Story 2.1 complete. Chapter navigation works.

**Assumptions:**
- Plotly is being used for the map
- Bob location data has x/y/z or star system coordinates

**Tasks:**
- Each Bob is a distinct color/marker on the map
- Hovering a Bob shows: name, clone ID, current system, chapter
- Star systems labeled (not just coordinates)
- Known star systems (Sol, Epsilon Eridani, etc.) shown as background reference points
- Map has a dark space background theme

**Acceptance Criteria:**
- [ ] Each Bob visually distinct (color + label)
- [ ] Hover tooltip shows name, system, chapter
- [ ] Reference star systems visible as muted background points
- [ ] Map looks good on dark background at 800px width

---

#### Story 2.3 — Bob Detail Panel

**Context:** Story 2.2 complete.

**Tasks:**
- Clicking a Bob on the map shows a sidebar panel with:
  - Clone name and ID
  - Current star system
  - Ship status (if in data)
  - Brief notes field (from data)
- Panel updates when chapter changes (Bob may have moved)
- If a Bob hasn't appeared yet in selected chapter, show "Not yet encountered"

**Acceptance Criteria:**
- [ ] Clicking a Bob on the map populates the detail panel
- [ ] Panel reflects correct state for the selected chapter
- [ ] Unencountered Bobs show placeholder text, not an error

---

### EPIC 2 Integration Gate

- [ ] Full user journey: select book → move to chapter 5 → click a Bob → detail panel shows
- [ ] Previous/Next chapter navigation updates map and detail panel
- [ ] No Python errors in terminal during normal use
- [ ] App usable on mobile viewport (600px)

---

### EPIC 3 — Dockerization

**Epic Goal:** App runs identically in Docker as it does locally. Ready for Fly.io deployment.

---

#### Story 3.1 — Dockerfile

**Context:** App is fully functional locally.

**Assumptions:**
- Python 3.12
- All deps in `requirements.txt`
- Data file is baked into the image (no external volume needed)

**Tasks:**
- Multi-stage Dockerfile:
  - Builder: install deps
  - Runner: `python:3.12-slim`, copy app + data, run Streamlit
- `HEALTHCHECK` via `curl http://localhost:8501/_stcore/health`
- Non-root user for security
- `.dockerignore` — exclude `.git`, `__pycache__`, `.streamlit` local overrides, venv

**Acceptance Criteria:**
- [ ] `docker build -t bobiverse-tracker .` succeeds
- [ ] `docker run -p 8501:8501 bobiverse-tracker` — app accessible at `http://localhost:8501`
- [ ] Healthcheck passes: `docker inspect --format='{{.State.Health.Status}}' <container>`
- [ ] Image size under 500MB
- [ ] App behavior identical to local `streamlit run`

---

### EPIC 3 Integration Gate

- [ ] `docker build` succeeds cleanly
- [ ] `docker run` — full app works, map renders, chapter nav works
- [ ] Healthcheck reports healthy after 30 seconds
- [ ] `docker stop` — container exits within 10 seconds

---

### EPIC 4 — Fly.io Deployment

**Epic Goal:** App is live at `https://bobiverse.brandonlocke.xyz`, scales to zero when idle, and auto-deploys on push to `main`.

---

#### Story 4.1 — Fly.io App Setup

**Context:** Story 3.1 complete. Docker image works locally.

**Assumptions:**
- `fly` CLI installed and authenticated
- Namecheap DNS available for `brandonlocke.xyz`
- Personal site's Fly.io account will host this as a separate app

**Tasks:**
- `fly launch` — new app, name `bobiverse-tracker`, nearest region
- Write `fly.toml`:
  ```toml
  [build]

  [[services]]
    internal_port = 8501
    protocol = "tcp"

    [[services.ports]]
      handlers = ["http"]
      port = 80

    [[services.ports]]
      handlers = ["tls", "http"]
      port = 443

    [services.concurrency]
      type = "connections"
      hard_limit = 10
      soft_limit = 5

  [[services.http_checks]]
    path = "/_stcore/health"
    interval = "15s"
    timeout = "5s"

  [machines]
    min_machines_running = 0   # scale to zero
  ```
- `fly deploy` — verify app is live at `.fly.dev` URL
- `fly certs add bobiverse.brandonlocke.xyz`
- Add Namecheap DNS CNAME: `bobiverse` → `bobiverse-tracker.fly.dev`

**Acceptance Criteria:**
- [ ] `fly deploy` succeeds
- [ ] `https://bobiverse-tracker.fly.dev` — app loads
- [ ] `https://bobiverse.brandonlocke.xyz` — app loads (after DNS propagation)
- [ ] `fly scale show` — `min_machines_running = 0` confirmed
- [ ] Stop all machines → wait 5 min → visit URL → app wakes within 5 seconds

---

#### Story 4.2 — GitHub Actions CI/CD

**Context:** Story 4.1 complete. App deployed manually.

**Tasks:**
- `.github/workflows/deploy.yml`:
  - Trigger: push to `main`
  - Jobs: lint (`ruff`) + deploy (`fly deploy --remote-only`)
- `.github/workflows/pr-check.yml`:
  - Trigger: pull request
  - Job: lint only
- `FLY_API_TOKEN` added to GitHub repository secrets

**Acceptance Criteria:**
- [ ] Push to `main` → deploy completes within 5 minutes
- [ ] `https://bobiverse.brandonlocke.xyz` reflects the change after deploy
- [ ] Lint failure → deploy blocked
- [ ] PR → lint runs, no deploy triggered

---

### EPIC 4 Integration Gate

- [ ] Full cold-start test: scale to zero → visit URL → app loads within 5 seconds
- [ ] Push a minor change (e.g. update a label) → GitHub Actions deploys → change visible on site
- [ ] `fly logs` — no errors during normal use
- [ ] Monthly cost estimate confirmed in Fly.io dashboard (should be near $0 for low traffic)

---

## Migration — Streamlit → Fast Static Web App

**Goal:** Eliminate the long startup time by moving from a Streamlit/Python server app to a static JavaScript web app.

The startup latency is **architectural**, not data-related. The dataset is tiny (`data/bobs.json`, ~120 entries / 10 systems) and all position math is trivial arithmetic. Four compounding costs cause the delay:

| Cause | Detail |
|---|---|
| **Fly cold start** | `min_machines_running = 0` + `auto_stop_machines = 'stop'` → container boots from cold on every idle visit. |
| **Python import cost** | `import streamlit, pandas, plotly` takes seconds on a 256mb shared-CPU VM, before any code runs. |
| **Streamlit runtime model** | Server boots → browser downloads a large JS bundle → opens a websocket → server re-runs the *entire* script per interaction. Slow even when warm. |
| **RAM-starved VM** | pandas + plotly in 256mb leaves little headroom. |

A static site removes all four: no server boot, no Python, no websocket, no cold machine. Assets served from a CDN; interactive on first paint.

### Target Architecture

```
Browser → CDN / Static Host (Cloudflare Pages) → static bundle (HTML + JS + bobs.json)
                                                    ├── Timeline slider (client state)
                                                    ├── Position compute (ported from app/data.py → JS)
                                                    ├── SVG map render (no chart server)
                                                    └── Status table (client state)
```

### Technology Choices

| Layer | Choice | Reason |
|---|---|---|
| Framework | **SvelteKit** (`adapter-static`) | Smallest runtime; first-class static export. Astro / SolidStart acceptable alternatives. |
| Chart | **Plain SVG** (D3 only for scales, optional) | Map is ~10 systems + N bobs + a few lines. SVG is tiny + instant; avoids Plotly.js (~3MB). |
| Data | `data/bobs.json` (unchanged) | Already static; shipped as a build asset. |
| Hosting | **Cloudflare Pages** | Free, global CDN, no cold start, Git-push deploys. GitHub Pages / Netlify equivalent. |
| CI/CD | GitHub Actions | Build + deploy on push to `main`. |

> **Decision point:** confirm **SvelteKit + SVG** before starting Epic 5. If interactive pan/zoom on the map is a hard requirement, swap SVG for lazy-loaded Plotly.js — but that reintroduces a large bundle and partly defeats the goal.

### What Carries Over

- **`data/bobs.json`** — used as-is, no schema change.
- **`SYSTEM_COORDS`** (`app/data.py:7`) — ported verbatim to a JS constant.
- **Position logic** (`compute_positions`, `app/data.py:35`) — ported verbatim to JS (pure arithmetic, no pandas).
- **Anti-stacking jitter** (`build_map`, `app/map.py:32`) — ported to JS.
- **Dark / iframe-clean theme** (`.streamlit/config.toml`) — recreated in CSS.

Retired at cutover: Streamlit, pandas, plotly, `Dockerfile`, the Fly app, the Python deploy workflow, redundant root `app.py`.

---

### EPIC 5 — Static App Scaffold

**Epic Goal:** A SvelteKit static project builds to a folder of static assets and serves a blank themed page locally and from a preview deploy.

---

#### Story 5.1 — Scaffold SvelteKit + Static Adapter

**Context:** Repo is currently Python-only. Introduce the JS app in a `web/` subfolder so the legacy app keeps running until cutover.

**Tasks:**
- `npm create svelte@latest web` — skeleton project, TypeScript optional.
- Install and configure `@sveltejs/adapter-static` for full static export.
- Add `web/.gitignore` (node_modules, build, .svelte-kit).
- Confirm `npm run dev` serves a blank page and `npm run build` produces static `web/build/`.

**Out of Scope:** Any map logic, data, or deploy.

**Acceptance Criteria:**
- [ ] `cd web && npm run dev` serves a page at `localhost:5173`
- [ ] `npm run build` produces a static `build/` directory (HTML/JS/CSS, no server)
- [ ] `npx serve web/build` serves the built page with no backend process

---

#### Story 5.2 — Base Layout, Theme & Iframe Embed

**Context:** Story 5.1 complete. App embeds via iframe on the personal site, so it must be clean and dark like the current Streamlit config.

**Tasks:**
- Global dark theme CSS matching `plotly_dark` (`#111` background, `#333` gridlines, light text).
- App title `🌌 Bobiverse Tactical Movement Map`.
- Responsive layout usable at ~800px (iframe) and ~600px (mobile).
- No external chrome/toolbar (parity with `toolbarMode = "minimal"`).

**Acceptance Criteria:**
- [ ] Page renders dark, full-bleed, no scroll chrome, at 800px width
- [ ] Renders cleanly inside a test `<iframe width="800">`
- [ ] Lighthouse Performance ≥ 95 on the blank themed page

---

### EPIC 5 Integration Gate

- [ ] `npm run build` → static folder serves with zero server processes
- [ ] Page loads dark-themed in an iframe at 800px
- [ ] First paint is effectively instant (no spinner, no websocket)

---

### EPIC 6 — Port Data & Domain Logic to JS

**Epic Goal:** All Python position logic runs in the browser against the existing `bobs.json`, producing identical results.

---

#### Story 6.1 — Data Loading & Coordinates

**Context:** `data/bobs.json` and `SYSTEM_COORDS` are the source of truth.

**Tasks:**
- Copy/symlink `data/bobs.json` into `web/static/` (or `src/lib/data/`) so it ships in the bundle.
- Port `SYSTEM_COORDS` (`app/data.py:7`) to a JS constant.
- Load + parse the JSON at runtime; parse `assumed_date` to JS `Date`; sort by `(bob, assumed_date)` — parity with `load_data()` (`app/data.py:25`).
- Derive `min_date` / `max_date` for the slider range.

**Acceptance Criteria:**
- [ ] All bobs and systems load from `bobs.json` with no hardcoded data
- [ ] Date range matches the current Streamlit slider bounds
- [ ] `get_coords` fallback to `(0,0)` for unknown systems preserved

---

#### Story 6.2 — Port Position Computation

**Context:** Story 6.1 complete. This is the core domain logic.

**Tasks:**
- Port `compute_positions` (`app/data.py:35`) to JS: for each bob at a selected date, find last past entry + first future entry; interpolate `(x, y)` by time fraction; compute heading `angle = 90 - atan2(dy, dx)*180/π`; set `is_traveling`, `status`, `last_date`, `path`.
- Port anti-stacking orbit jitter from `build_map` (`app/map.py:32`): cluster bobs by rounded coords; offset stationary co-located bobs around a 0.7 radius circle.
- Keep this as a pure function (df + date → positions) for testing.

**Acceptance Criteria:**
- [ ] For a fixed sample date, JS output matches Python `compute_positions` (coords within float tolerance, same status strings)
- [ ] Travel interpolation and heading angle match Python for a traveling bob
- [ ] Co-located stationary bobs get distinct jittered positions

---

### EPIC 6 Integration Gate

- [ ] Picking any date computes positions for every bob with no errors
- [ ] Spot-check 3 dates against the live Streamlit app → positions/status match

---

### EPIC 7 — Map Render & Interaction

**Epic Goal:** The SVG map and timeline reproduce the current app's behavior, instantly and interactively, with no server round-trip.

---

#### Story 7.1 — Render the Map (SVG)

**Context:** Epic 6 provides computed positions.

**Tasks:**
- Map domain coords → SVG pixel space (linear scales; D3 `scaleLinear` optional).
- Draw star systems: muted markers + `bottom center` labels (parity `app/map.py:18`).
- Draw bobs: triangle markers rotated by `angle`, per-bob color, `top center` label.
- Draw travel paths: dotted lines colored per bob (parity legendgroup behavior).
- Dark theme, gridlines, axis labels `LY (X)` / `LY (Y)`.

**Acceptance Criteria:**
- [ ] All 10 systems render labeled at correct relative positions
- [ ] Each bob is a distinct color with a rotated heading triangle
- [ ] Traveling bobs show a dotted path in their color
- [ ] Visual parity with the current Streamlit map at the same date

---

#### Story 7.2 — Timeline Slider & Reactive Update

**Context:** Story 7.1 complete.

**Tasks:**
- Timeline slider over `[min_date, max_date]`, `MMM YYYY` label (parity `chapter_selector.py`).
- Map re-renders reactively on slider change — pure client state, no reload, no network.
- Default to `min_date`.

**Acceptance Criteria:**
- [ ] Dragging the slider updates the map with no perceptible lag and no network call
- [ ] Slider label shows `MMM YYYY`
- [ ] Initial state matches the current app (earliest date)

---

#### Story 7.3 — Tactical Status Table

**Context:** Story 7.2 complete.

**Tasks:**
- Below the map: `Tactical Status: <date>` heading + table of `Bob | Status | Last Log` (parity `main.py:25`, `build_map` status list).
- Table updates with the slider.

**Acceptance Criteria:**
- [ ] Table lists every active bob with status + last-log date for the selected date
- [ ] Heading shows the selected date
- [ ] Table updates in sync with the map

---

### EPIC 7 Integration Gate

- [ ] Full journey: load → drag slider across timeline → map + table update live
- [ ] Side-by-side with Streamlit at 3 dates → visual + status parity
- [ ] No console errors; interaction is instant

---

### EPIC 8 — Static Deploy & Cutover

**Epic Goal:** The static app is live on a CDN with no cold start, auto-deploys on push, and the legacy Streamlit/Fly stack is retired.

---

#### Story 8.1 — Static Hosting + CI/CD

**Context:** Epic 7 complete. App builds to static assets.

**Tasks:**
- Set up Cloudflare Pages (or GitHub Pages / Netlify) pointing at `web/`.
- `.github/workflows/web-deploy.yml`: on push to `main` → `npm ci && npm run build` → publish `web/build`.
- PR workflow: build + lint only (no deploy).
- Verify a preview URL loads instantly.

**Acceptance Criteria:**
- [ ] Push to `main` → build + deploy completes in a few minutes
- [ ] Preview/prod URL loads with no cold start (cold visit ≤ ~1s to interactive)
- [ ] PR triggers build only, no deploy

---

#### Story 8.2 — Custom Domain & Iframe Embed

**Context:** Story 8.1 complete.

**Tasks:**
- Point the existing hostname (`bobiverse.brandonlocke.xyz`) at the new static host via DNS/CNAME.
- Update the personal site iframe `src` to the new URL.
- Confirm TLS and the dark iframe embed.

**Acceptance Criteria:**
- [ ] Custom domain serves the static app over HTTPS
- [ ] Personal site iframe shows the new app, dark and clean
- [ ] Cold-visit load dramatically faster than Streamlit (measure + record before/after)

---

#### Story 8.3 — Retire Legacy Streamlit Stack

**Context:** New app is live and verified. Remove dead weight.

**Tasks:**
- Remove (or archive) `app/`, root `app.py`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `Pipfile`, `Pipfile.lock`, `.streamlit/`, the Fly deploy workflow, `fly.toml`.
- Stop/destroy the Fly `bobiverse-tracker` app.
- Update this README's front matter (Architecture, Tech Stack, Environment) to describe the static architecture.
- Keep `data/bobs.json` + `data/schema.md` as the data source of truth.

**Acceptance Criteria:**
- [ ] No Python/Streamlit/Fly references remain in active config
- [ ] Fly app stopped/destroyed (no further billing)
- [ ] README front matter reflects the static architecture
- [ ] Repo builds and deploys solely via the JS toolchain

---

### EPIC 8 Integration Gate

- [ ] Cold-visit load time measured + recorded — before (Streamlit) vs after (static)
- [ ] Push a label change → auto-deploys → visible on the live domain
- [ ] Legacy stack fully removed; no orphaned Fly machine

> **Rollback:** The legacy Streamlit app stays deployable until Story 8.3. The new app lives in `web/` and deploys to a separate URL, so cutover is just a DNS + iframe `src` change. To roll back: point DNS at the Fly app and revert the iframe `src`. Do not run Story 8.3 until the static app is verified live on the production domain.

---

## Secrets & Config Management

No secrets required — all data is static and baked into the Docker image. If future features require an API key (e.g. for book data enrichment), add via:

```bash
fly secrets set MY_SECRET=value
```

And access in Python via `os.environ.get("MY_SECRET")`.

---

## Definition of Done

A story is complete when:

- [ ] All acceptance criteria pass
- [ ] App runs correctly via `streamlit run app/main.py`
- [ ] App runs correctly via `docker run`
- [ ] No secrets committed
- [ ] `data/schema.md` updated if data format changed
- [ ] Epic integration gate passes before moving to next epic
