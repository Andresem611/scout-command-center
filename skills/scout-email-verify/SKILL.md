---
name: scout-email-verify
description: |
  Email verification system for Thoven's growth outreach.
  
  Validates email addresses through multiple levels:
  1. Syntax validation with typo detection
  2. Domain verification (MX records, blacklist checks)
  3. Mailbox verification (where supported)
  
  Prevents wasted sends to invalid/disposable emails.
---

# scout-email-verify

Email verification for Thoven's outreach pipeline.

## Quick Start

```bash
# 1. Check single email format
python3 skills/scout-email-verify/scripts/check_format.py "prospect@example.com"

# 2. Verify domain (MX + blacklist)
python3 skills/scout-email-verify/scripts/verify_domain.py "example.com"

# 3. Batch verify a list
python3 skills/scout-email-verify/scripts/batch_verify.py emails.csv

# 4. Update blacklist from bounces
python3 skills/scout-email-verify/scripts/update_blacklist.py bounces.csv
```

## Verification Levels

| Level | What It Checks | Use Case |
|-------|---------------|----------|
| **Syntax** | Format, typos, valid characters | First-line filter |
| **Domain** | MX records, disposable detection, blacklists | Pre-send validation |
| **Mailbox** | SMTP handshake, catch-all detection | High-value targets only |

## File Structure

```
skills/scout-email-verify/
├── SKILL.md                          # This file
├── scripts/
│   ├── check_format.py               # Syntax + typo detection
│   ├── verify_domain.py              # MX + blacklist checks
│   ├── batch_verify.py               # Batch processing
│   └── update_blacklist.py           # Bounce tracking
└── references/
    ├── verification-levels.md        # Detailed level docs
    └── disposable-domains.md         # Throwaway domain list
```

## Output Format

All scripts output JSON:

```json
{
  "status": "valid|invalid|unknown",
  "email": "prospect@example.com",
  "checks": {
    "syntax": {"valid": true, "typos": []},
    "domain": {"mx_valid": true, "disposable": false, "blacklisted": false}
  },
  "reason": "Detailed explanation if invalid/unknown"
}
```

## Integration

Use in prospecting workflow:

1. Extract email from bio/website
2. Run `check_format.py` → reject obvious garbage
3. Run `verify_domain.py` → flag suspicious domains
4. Store with verification status in pipeline
5. Before send: re-check domain, skip if blacklisted


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Syntax check catches typos** — gmial.com → suggest gmail.com
2. **Disposable emails = immediate reject** — mailinator, tempmail, etc.
3. **Blacklist bounces immediately** — Protect sender reputation
4. **Batch verify before campaigns** — Don't discover bounces mid-send
5. 
