# Data Flow Diagram

## Overview

This document describes the data flow from markdown pipeline files to the dashboard JSON.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SOURCE OF TRUTH                                │
│                    pipeline/PROSPECTS_*.md files                        │
│                          (Markdown Tables)                               │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PARSE MARKDOWN                                      │
│                   scripts/parse_markdown.py                              │
│                                                                          │
│  • Extract tables from markdown                                          │
│  • Parse follower counts (1.6M → 1600000)                               │
│  • Map status values (Uncontacted → Prospected)                         │
│  • Extract city/branch from headers                                     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       SYNC TO JSON                                       │
│                    scripts/sync_to_json.py                               │
│                                                                          │
│  • Transform to dashboard format                                        │
│  • Generate unique IDs                                                  │
│  • Calculate statistics (total, by stage, by city, by branch)           │
│  • Backup existing JSON files                                           │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│      DASHBOARD JSON             │   │         DATA JSON               │
│  scout-dashboard-v2/public/     │   │        data/scout_data.json     │
│      scout_data.json            │   │                                 │
└─────────────────────────────────┘   └─────────────────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        VALIDATION                                        │
│                    scripts/validate_sync.py                              │
│                                                                          │
│  • Compare markdown count vs JSON count                                 │
│  • Flag discrepancies                                                   │
│  • Validate JSON structure                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

## File Locations

| File | Path | Purpose |
|:---|:---|:---|
| Source Markdown | `pipeline/PROSPECTS_*.md` | Human-editable prospect data |
| Dashboard JSON | `scout-dashboard-v2/public/scout_data.json` | Dashboard consumption |
| Data JSON | `data/scout_data.json` | Backup/secondary usage |

## Sync Process

1. **Parse**: Read all `PROSPECTS_*.md` files in `pipeline/` directory
2. **Extract**: Parse markdown tables, extracting name, handle, followers, email, status
3. **Transform**: Convert to dashboard format with generated IDs and calculated fields
4. **Calculate**: Generate statistics (totals, breakdowns by stage/city/branch)
5. **Backup**: Save timestamped backup of existing JSON files
6. **Write**: Output to both dashboard and data JSON locations
7. **Validate**: Verify counts match between source and targets

## Field Mapping

| Markdown Field | JSON Field | Transform |
|:---|:---|:---|
| Name | name | As-is |
| Handle | handle | As-is |
| Followers | followers | Parse 1.6M → 1600000 |
| Email | contact_email | Null if "DM for collabs" |
| Status | stage | Map Uncontacted → Prospected |
| Section Header | city | Extract from "### NYC Prospects" |
| Section Context | branch | Mom Influencers / Mom Blogs / Homeschool |

## Status Mapping

| Markdown | JSON Stage |
|:---|:---|
| Uncontacted | Prospected |
| ✅ LIVE PARTNER | Partner |
| Contacted | Contacted |
| Replied | Replied |
| Negotiating | Negotiating |
| Declined | Declined |
