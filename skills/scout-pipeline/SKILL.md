---
name: scout-pipeline
description: Manage Thoven's prospect pipeline stages and stats. Use when (1) moving prospects between pipeline stages, (2) calculating pipeline metrics and stats, (3) syncing dashboard data, (4) validating stage transitions, or (5) querying prospect counts by stage/city/branch.
---

# Scout Pipeline

Pipeline management for Thoven music education marketplace outreach.

## Quick Start

**Update a prospect's stage:**
```bash
python3 skills/scout-pipeline/scripts/update_stage.py <prospect_id> <new_stage>
```

**Get pipeline stats:**
```bash
python3 skills/scout-pipeline/scripts/get_stats.py
```

**Sync dashboard data:**
```bash
python3 skills/scout-pipeline/scripts/sync_dashboard.py
```

## Stage Definitions

| Stage | Description |
|-------|-------------|
| **Prospected** | Initial discovery — identified as potential partner |
| **Contacted** | Outreach sent (email/DM/call) |
| **Replied** | Prospect responded — interested or needs info |
| **Negotiating** | Active discussion on terms, commission, onboarding |
| **Partner** | Signed up, actively referring students |
| **Declined** | Explicit no or ghosted after multiple attempts |

Read [references/stage-definitions.md](references/stage-definitions.md) for full transition rules.

## Data Schema

Read [references/pipeline-schema.md](references/pipeline-schema.md) for prospect data structure.

## Stage Transition Rules

Allowed transitions (forward progression or terminal):
- `Prospected` → `Contacted`
- `Contacted` → `Replied` | `Declined`
- `Replied` → `Negotiating` | `Declined`
- `Negotiating` → `Partner` | `Declined`
- `Partner` → *(terminal — no transitions)*
- `Declined` → *(terminal — no transitions)*

**Blocked transitions:**
- Never backward (e.g., `Contacted` → `Prospected`)
- Never skip ahead (e.g., `Prospected` → `Negotiating`)

## Stats Calculation

Pipeline metrics returned by `get_stats.py`:

| Metric | Description |
|--------|-------------|
| `total` | All non-declined prospects |
| `by_stage` | Count per active stage |
| `by_city` | Prospects grouped by city |
| `by_branch` | Prospects grouped by branch type |
| `conversion_rate` | Partner / (Partner + Declined) |

## Scripts Reference

### update_stage.py

```
python3 scripts/update_stage.py <prospect_id> <new_stage> [--data-path PATH]
```

- Validates transition against rules
- Updates `scout_data.json`
- Logs transition with timestamp to `transitions.log`
- Exits with error code 1 on invalid transition

### get_stats.py

```
python3 scripts/get_stats.py [--data-path PATH] [--format json|table]
```

- Calculates all pipeline metrics
- Outputs JSON (default) or formatted table

### sync_dashboard.py

```
python3 scripts/sync_dashboard.py [--data-path PATH]
```

- Validates all prospect records against schema
- Fills missing computed fields
- Reports inconsistencies found


---

## 🔑 KEY LEARNINGS (Max 5)

1. **No backward stage moves** — Forward only: Prospected → Contacted → Replied → Negotiating → Partner
2. **Stale >14 days = flag for re-engagement or drop** — Don't let prospects sit; make a decision
3. **Sync before any deploy** — scout_data.json must be valid before Vercel build
4. **Terminal stages: Partner, Declined** — No further action needed; archive learnings
5. **Validate data weekly** — Run validator before Monday morning batch
