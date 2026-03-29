---
name: scout-followup
description: Thoven sales follow-up cadence manager. Use when managing outreach follow-ups for music teacher prospects, checking which prospects need follow-up, generating follow-up messages (Day 3 bump, Day 7 value-add, Day 14 soft close), and scheduling next follow-up dates. Triggers on phrases like "check follow-ups", "who needs follow-up", "generate follow-up message", "schedule next follow-up", "Day 3/7/14 follow-up".
---

# Scout Follow-Up Skill

Manage Thoven's prospect follow-up cadence with systematic Day 3, 7, 14 touchpoints.

## Quick Start

### Check for Due Follow-ups
```bash
python3 skills/scout-followup/scripts/check_due_followups.py --prospects <path/to/prospects.csv>
```

### Generate Follow-up Message
```bash
python3 skills/scout-followup/scripts/generate_followup.py --day 3 --prospect "Music Academy Name" --thread-id <thread_id>
```

### Schedule Next Follow-up
```bash
python3 skills/scout-followup/scripts/schedule_next.py --prospect-id <id> --current-day 3
```

## Cadence Rules

| Day | Message Type | Goal | Tone |
|:---|:---|:---|:---|
| **3** | Gentle Bump | Get a response | Light, assumptive |
| **7** | Value-Add | Different angle | Helpful, new insight |
| **14** | Soft Close | Final attempt | Direct, respectful |

### Stage Definitions

- `New` → Not yet contacted
- `Contacted` → Initial outreach sent, in follow-up sequence
- `Responded` → Prospect replied, move to active conversation
- `Qualified` → Good fit, potential partner
- `Declined` → Not interested, archive
- `Partner` → Signed up, onboarded

### Follow-up Tracking Fields

Each prospect record should have:
- `stage`: Current stage in pipeline
- `contact_date`: Date of first contact (ISO 8601)
- `next_followup_date`: When to follow up next
- `followup_count`: Number of follow-ups sent (0, 1, 2, 3)
- `thread_id`: Email/LinkedIn thread reference
- `last_message_date`: Date of last interaction

## Scripts Reference

| Script | Purpose |
|:---|:---|
| `scripts/check_due_followups.py` | Scan prospects and list those needing follow-up today |
| `scripts/generate_followup.py` | Generate context-aware follow-up messages |
| `scripts/schedule_next.py` | Update prospect record with next follow-up date |

## Message Templates

For detailed message templates, see [references/followup-templates.md](references/followup-templates.md).

## Workflow

1. **Daily**: Run `check_due_followups.py` to see who needs follow-up
2. **Review**: Check prospect context (previous messages, website, etc.)
3. **Generate**: Use `generate_followup.py` to create message
4. **Send**: Review with Andres before sending (external comms require approval)
5. **Schedule**: Run `schedule_next.py` to set next follow-up date
6. **Update**: Mark prospect stage if they respond

## Data Format

Prospects CSV/JSON expected fields:
```json
{
  "id": "unique-id",
  "name": "Music Academy Name",
  "contact_name": "Director Name",
  "email": "contact@example.com",
  "stage": "Contacted",
  "contact_date": "2025-03-20",
  "next_followup_date": "2025-03-23",
  "followup_count": 0,
  "thread_id": "email-thread-ref",
  "notes": "Context from initial research"
}
```
