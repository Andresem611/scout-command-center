# Markdown Schema Reference

## Overview

This document defines the expected markdown table format for prospect data.

## Table Format

### Standard Prospect Table

```markdown
| Name | Handle | Followers | Email | Status |
|:---|:---|:---|:---|:---|
| Zarna Garg | @zarnagarg | 1.6M | zarnagargfamily@gmail.com | Uncontacted |
| Audrey Mora | @audreyomora | 45K | audreyomora@gmail.com | ✅ LIVE PARTNER |
```

### Column Definitions

| Column | Type | Description | Example |
|:---|:---|:---|:---|
| Name | string | Prospect full name or blog name | `Zarna Garg` |
| Handle | string | Instagram/TikTok handle with @ | `@zarnagarg` |
| Followers | string | Follower count (various formats) | `1.6M`, `45K`, `N/A` |
| Email | string | Contact email or DM indicator | `email@example.com`, `DM for collabs` |
| Status | string | Outreach status | `Uncontacted`, `✅ LIVE PARTNER` |

## Follower Format

The parser handles these follower formats:

| Format | Parsed Value | Notes |
|:---|:---|:---|
| `1.6M` | 1600000 | Millions |
| `45K` | 45000 | Thousands |
| `2K+` | 2000 | Plus suffix stripped |
| `<1K` | 500 | Estimated |
| `N/A` | null | Missing data |
| `-` | null | Missing data |
| `120K (TikTok)` | 120000 | Platform note ignored |

## Status Values

| Markdown Status | Maps To | Description |
|:---|:---|:---|
| `Uncontacted` | `Prospected` | Not yet reached out |
| `✅ LIVE PARTNER` | `Partner` | Active partnership |
| `Contacted` | `Contacted` | Email sent |
| `Replied` | `Replied` | Response received |
| `Negotiating` | `Negotiating` | Terms discussion |
| `Declined` | `Declined` | Not interested |

## Section Headers

City is extracted from section headers:

```markdown
### NYC Prospects (18)     → City: NYC
### Miami Prospects (32)   → City: Miami  
### LA Prospects (22)      → City: LA
### SF/Bay Area Prospects  → City: SF/Bay Area
### Houston Prospects      → City: Houston
### Dallas Prospects       → City: Dallas
### Austin Prospects       → City: Austin
### Chicago Prospects      → City: Chicago
```

## Branch Detection

Branch is determined by section context:

| Section Context | Branch |
|:---|:---|
| `## MOM INFLUENCERS` | Mom Influencers |
| `## MOM BLOGS` | Mom Blogs |
| `## HOMESCHOOL INFLUENCERS` | Homeschool |
| `## HOMESCHOOL BLOGS` | Homeschool |

## Blog Table Format

For blog entries (different columns):

```markdown
| Blog Name | City | URL | Contact | Status |
|:---|:---|:---|:---|:---|
| Mommy Poppins | NYC/LA | mommypoppins.com | mommy@mommypoppins.com | Uncontacted |
```

## Special Email Values

| Value | Treatment |
|:---|:---|
| `DM for collabs` | contact_email = null |
| `Blog contact` | contact_email = null |
| `N/A` | contact_email = null |
| Empty string | contact_email = null |

## File Naming Convention

Files should be named:
```
PROSPECTS_YYYY-MM-DD.md
```

Example: `PROSPECTS_2026-03-26.md`

## Complete Example

```markdown
# Thoven Outreach Pipeline
*Generated: 2026-03-26*

---

## Pipeline Stats

| Branch | Target | Current | Gap |
|:---|:---|:---|:---|
| Mom Influencers (IG) - NYC | 8 | 18 | ✅ +10 |

---

## MOM INFLUENCERS (INSTAGRAM)

### NYC Prospects (18)

| Name | Handle | Followers | Email | Status |
|:---|:---|:---|:---|:---|
| Zarna Garg | @zarnagarg | 1.6M | zarnagargfamily@gmail.com | Uncontacted |
| Audrey Mora | @audreyomora | 45K | audreyomora@gmail.com | ✅ LIVE PARTNER |

---

## MOM BLOGS

| Blog Name | City | URL | Contact | Status |
|:---|:---|:---|:---|:---|
| Mommy Poppins | NYC/LA | mommypoppins.com | mommy@mommypoppins.com | Uncontacted |
```
