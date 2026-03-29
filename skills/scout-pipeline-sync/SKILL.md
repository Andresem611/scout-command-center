---
title: Scout Pipeline Sync
description: Parse markdown prospect files and sync to JSON for dashboard
tags: [pipeline, sync, prospects, dashboard]
author: Scout
version: 1.0.0
---

# Scout Pipeline Sync

Sync prospect data from markdown pipeline files to JSON for the Thoven dashboard.

## Quick Start

```bash
# Sync pipeline data to dashboard
cd /root/.openclaw/workspace/skills/scout-pipeline-sync
python3 scripts/sync_to_json.py

# Validate the sync
python3 scripts/validate_sync.py
```

## Workflow

```
pipeline/PROSPECTS_*.md 
    ↓
scripts/parse_markdown.py
    ↓
scripts/sync_to_json.py
    ↓
scout-dashboard-v2/public/scout_data.json
    ↓
Dashboard reflects current pipeline
```

## Scripts

| Script | Purpose |
|:---|:---|
| `parse_markdown.py` | Extract prospects from markdown tables |
| `sync_to_json.py` | Transform and write to JSON targets |
| `validate_sync.py` | Verify sync accuracy |

## Data Flow

See [references/data-flow.md](references/data-flow.md) for detailed architecture.

## Status Mapping

| Markdown Status | JSON Stage |
|:---|:---|
| `Uncontacted` | `Prospected` |
| `✅ LIVE PARTNER` | `Partner` |
| `Contacted` | `Contacted` |
| `Replied` | `Replied` |
| `Negotiating` | `Negotiating` |
| `Declined` | `Declined` |

## Follower Parsing

Handles formats like:
- `1.6M` → `1600000`
- `45K` → `45000`
- `2K+` → `2000`
- `<1K` → `500` (estimated)
- `N/A` → `null`
