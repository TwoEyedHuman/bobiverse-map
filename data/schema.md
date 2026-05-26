# data/bobs.json Schema

Each record in `bobs.json` represents a single positional log entry for a Bob clone.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `bob` | string | Name of the Bob clone (e.g. `"Bob"`, `"Riker"`, `"Bill"`) |
| `system` | string | Star system name. Must match a key in `SYSTEM_COORDS` in `app/data.py` |
| `assumed_date` | string | ISO 8601 date (`YYYY-MM-DD`). Day is always `01` (month-level precision) |

## Example

```json
[
  {
    "bob": "Bob",
    "system": "Sol",
    "assumed_date": "2133-01-01"
  },
  {
    "bob": "Riker",
    "system": "Epsilon Eridani",
    "assumed_date": "2145-07-01"
  }
]
```

## Known Systems

Defined in `app/data.py` → `SYSTEM_COORDS`:

- Sol
- Alpha Centauri
- Epsilon Eridani
- Omicron Eridani
- Delta Eridani
- 82 Eridani
- Beta Hydri
- Sigma Draconis
- Tau Ceti
- Epsilon Indi

> **Note:** The source CSV contains a typo `"Epislon Indi"` for one Linus entry (Apr/2165).
> This is preserved as-is in `bobs.json`; that Bob will render at coords `(0, 0)` until corrected.

## Conventions

- Multiple records for the same Bob at the same date → last record wins after sort
- Dates are month-level precision; the app interpolates travel between consecutive entries
- No DB; this file is the source of truth. Edit directly and restart the app.
