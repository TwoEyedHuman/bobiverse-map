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
