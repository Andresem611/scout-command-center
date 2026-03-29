---
name: scout-data-validator
description: |
  Validates Thoven prospect data integrity. Checks schema compliance, 
  finds duplicates, identifies stale records, and auto-fixes common issues.
triggers:
  - "validate prospect data"
  - "check data integrity"
  - "clean up prospects"
  - "find duplicates"
  - "data validation"
  - "stale prospects"
when_to_run:
  - Before syncing prospect data to dashboard
  - Weekly data hygiene checks
  - After bulk imports
  - Before outreach campaigns
  - When data quality issues suspected
validation_rules:
  schema:
    required_fields:
      - id
      - name
      - email
      - stage
      - source
      - created_at
      - updated_at
    field_types:
      id: string
      name: string
      email: string
      email_domain: string
      phone: string
      city: string
      state: string
      country: string
      source: enum
      stage: enum
      tags: array
      notes: string
      website: string
      instagram: string
      followers: number
      created_at: string (ISO 8601)
      updated_at: string (ISO 8601)
      last_contact_at: string (ISO 8601) or null
      last_reply_at: string (ISO 8601) or null
    enums:
      source:
        - instagram
        - facebook
        - twitter
        - youtube
        - tiktok
        - referral
        - manual
        - imported
        - other
      stage:
        - new
        - contacted
        - responded
        - interested
        - meeting_scheduled
        - onboarded
        - declined
        - no_response
        - disqualified
  duplicates:
    checks:
      - same_email_different_name
      - similar_name_same_email
    similarity_threshold: 0.85
  stale_data:
    thresholds:
      no_update_days: 30
      no_contact_no_reply_days: 14
    flag_conditions:
      - updated_at > 30 days ago
      - last_contact_at > 14 days ago AND last_reply_at is null
  auto_fixes:
    - trim_whitespace
    - lowercase_emails
    - standardize_stage_names
    - fill_missing_defaults
    - normalize_phone_numbers
---

# Scout Data Validator

Validates and cleans Thoven prospect data stored in `scout_data.json`.

## Quick Start

```bash
# Validate all data against schema
python3 ~/.openclaw/workspace/skills/scout-data-validator/scripts/validate_schema.py

# Check for duplicates
python3 ~/.openclaw/workspace/skills/scout-data-validator/scripts/check_duplicates.py

# Find stale records
python3 ~/.openclaw/workspace/skills/scout-data-validator/scripts/check_stale.py

# Auto-fix common issues
python3 ~/.openclaw/workspace/skills/scout-data-validator/scripts/fix_common.py
```

## Full Pipeline

```bash
cd ~/.openclaw/workspace/skills/scout-data-validator
python3 scripts/fix_common.py && \
python3 scripts/validate_schema.py && \
python3 scripts/check_duplicates.py && \
python3 scripts/check_stale.py
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed / fixes applied successfully |
| 1 | Validation errors found |
| 2 | Duplicates detected |
| 3 | Stale records found |
| 4 | File not found or unreadable |
| 5 | Schema definition missing |

## Output Format

All scripts output JSON to stdout:

```json
{
  "status": "success|warning|error",
  "message": "human-readable summary",
  "details": [...],
  "count": 0
}
```


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Run fix_common before other validators** — Cleans data first
2. **Duplicates: same email = merge, similar names = flag** — Different handling
3. **Stale >30 days = re-verify contact info** — Emails change
4. **Exit codes matter for scripting** — 0=OK, 1=errors, 2=dupes, 3=stale
5. 
