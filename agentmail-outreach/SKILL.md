---
name: agentmail-outreach
description: Send and manage outreach emails via AgentMail API for Thoven partnership workflows. Use when sending emails, checking inbox for prospect replies, classifying responses, or handling email-based outreach. Triggers on "send email", "check inbox", "draft reply", "follow up", "prospect responded", or when interacting with keri@agentmail.to inbox.
---

# AgentMail Outreach Skill

Handle all Thoven partnership email operations via AgentMail.

## Quick Start

```python
# Send an email
from scripts.send_email import send_email
success, msg_id = send_email(
    to="prospect@example.com",
    subject="Partnership opportunity",
    body="Hi...",
    from_inbox="keri@agentmail.to"
)

# Check for replies
from scripts.check_inbox import check_inbox, classify_reply
replies = check_inbox("keri@agentmail.to")
for reply in replies:
    category = classify_reply(reply['body'], reply['subject'])
    # category: INTERESTED | QUESTIONS | RATES | DECLINED | OOO | OTHER
```

## Prerequisites

**Required environment variables** (loaded from `.env`):
```
AGENTMAIL_API_KEY=am_us_...
AGENTMAIL_INBOX_ID=keri@agentmail.to
```

**API Key location:** `/root/.openclaw/workspace/.env` (secured with 600 permissions)

**Never:** Log, display, or commit the API key.

## Core Workflows

### 1. Send Outreach Email

**Pre-flight checks:**
- ✅ Draft approved by Andres (required — never send without approval)
- ✅ Valid email address
- ✅ Personalization tokens filled

**Usage:**
```python
from scripts.send_email import send_email

success, msg_id, error = send_email(
    to=prospect['email'],
    subject=f"Partnership: Music Education for {prospect['city']} Families",
    body=generate_email_body(prospect),
    from_inbox="keri@agentmail.to"
)

if success:
    update_prospect_stage(prospect, 'Contacted', msg_id)
else:
    log_failure(prospect, error)
```

### 2. Check Inbox for Replies

**Auto-classification:**
```python
from scripts.check_inbox import check_inbox, classify_reply

replies = check_inbox("keri@agentmail.to", since_hours=24)

for reply in replies:
    category = classify_reply(reply['body'], reply['subject'])
    
    if category == 'INTERESTED':
        alert_andres_hot_lead(reply)
        draft_response(reply, tone='enthusiastic')
    
    elif category == 'QUESTIONS':
        alert_andres_hot_lead(reply)
        draft_response(reply, tone='helpful')
    
    elif category == 'RATES':
        alert_andres_hot_lead(reply)
        # Escalate to Andres for pricing decision
    
    elif category == 'DECLINED':
        update_stage(reply['from'], 'Declined')
        draft_polite_thank_you()
    
    elif category == 'OOO':
        schedule_follow_up(reply['from'], days=7)
```

### 3. Handle Hot Leads

**When to escalate to Andres:**
- Reply classification: INTERESTED, QUESTIONS, or RATES
- Prospect asks about pricing/partnership terms
- Prospect requests a call/meeting
- Any positive engagement

**Alert format:**
```
🔔 HOT LEAD — [Classification]
From: [prospect name/email]
Subject: [subject line]
Preview: [first 100 chars]

Drafted response: [attached]
Awaiting your approval to send.
```

## API Reference

See [references/agentmail-api.md](references/agentmail-api.md) for:
- Endpoint details
- Rate limits (100 req/min)
- Error codes and handling
- Response schemas

## Common Errors & Fixes

| Error | Cause | Fix |
|:---|:---|:---|
| `401 Unauthorized` | Invalid API key | Check `.env` file, key starts with `am_us_` |
| `404 Inbox not found` | Wrong inbox ID | Use email format: `keri@agentmail.to` |
| `429 Rate Limited` | Too many requests | Add 1s delay between sends, max 100/min |
| `500 Server Error` | AgentMail issue | Retry with exponential backoff, alert if persists |
| `Connection timeout` | Network issue | Retry up to 3 times, then skip and log |

## Reminders

**Before sending:**
- ☐ Draft approved by Andres
- ☐ Email address validated
- ☐ Subject line personalized with city
- ☐ Body references specific prospect details

**Before checking inbox:**
- ☐ API key configured in `.env`
- ☐ Inbox ID correct (`keri@agentmail.to`)

**Security:**
- ☐ API key never logged
- ☐ `.env` file has 600 permissions
- ☐ No credentials in git commits

## Integration with Scout

This skill is called by `heartbeat.py` every 30 minutes:
1. Check inbox → classify replies → alert on hot leads
2. Send approved drafts from queue
3. Update prospect stages

**Manual overrides:**
- Force inbox check: `python3 scripts/check_inbox.py`
- Send single email: `python3 scripts/send_email.py --to [email] --subject "..." --body "..."`
