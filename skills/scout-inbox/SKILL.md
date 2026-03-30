---
name: scout-inbox
description: |
  Check AgentMail inbox, classify replies, alert on hot leads.
  Use when: Checking for prospect replies, classifying email responses,
  identifying hot leads (INTERESTED/QUESTIONS/RATES).
  Triggers on: "check inbox", "new replies", "hot lead", "classify reply".
---

# Scout Inbox

Check AgentMail inbox for prospect replies and classify them.

## Workflow

**Check → Classify → Alert/Log**

### Step 1: Check Inbox

Call AgentMail API:
```bash
GET /inboxes/{inbox_id}/messages
```

Filter out:
- Emails from addresses containing 'keri' or 'thoven' (our own emails)
- Emails marked as `read: true`

### Step 2: Classify Reply

For each unread reply from prospects:

| Classification | Keywords |
|:---|:---|
| **INTERESTED** | "interested", "yes", "sounds good", "tell me more", "schedule", "call", "zoom" |
| **QUESTIONS** | "question", "how much", "what is", "can you", "do you", "price", "cost", "?" |
| **RATES** | "rate", "payment", "compensation", "fee", "budget", "afford" |
| **DECLINED** | "not interested", "pass", "no thanks", "not right now", "busy", "not a fit" |
| **OOO** | "ooo", "out of office", "vacation" (in subject) |
| **SPAM** | "unsubscribe", "marketing", "promotion" |
| **OTHER** | (default fallback) |

### Step 3: Store Reply

Save to `scout_data.json`:
```json
{
  "replies": [
    {
      "id": "message_id",
      "from": "sender@email.com",
      "subject": "Re: Partnership opportunity",
      "body": "...",
      "classification": "INTERESTED",
      "received_at": "2026-03-30T...",
      "processed_at": "2026-03-30T...",
      "status": "unread"
    }
  ]
}
```

### Step 4: Alert (Hot Leads Only)

If classification is **INTERESTED**, **QUESTIONS**, or **RATES**:

1. **ALERT immediately to chat:**
   ```
   🔔 HOT LEAD: [Name] ([Classification])
   
   They said: [1-2 sentence summary]
   Full message: [their reply]
   
   Drafting response now...
   ```

2. **Draft response** (don't send yet):
   - Use skill-drafting to create personalized reply
   - Add to queue with status "pending_approval"
   - Show Andres for approval

3. **Log to playbook** (skill-playbook):
   - Situation: Reply type, prospect info
   - Guidance: What Andres says to do
   - Response: What you draft
   - Outcome: (to be filled when known)
   - Pattern tag: e.g., "pricing question from mom influencer"

### Step 5: Handle Non-Hot Replies

| Classification | Action |
|:---|:---|
| **DECLINED** | Update prospect stage to "Declined". Draft polite thank you. Log to playbook. |
| **OOO** | Log silently. Keep follow-up schedule. No alert. |
| **SPAM** | Archive. No alert. No logging. |
| **OTHER** | Store in replies. Review during next heartbeat. |

## Script

```bash
# Check inbox and classify replies
python3 skills/scout-inbox/scripts/check_inbox.py

# Check specific message
python3 skills/scout-inbox/scripts/check_inbox.py --message-id <id>
```

## KEY LEARNINGS (max 5)

1. **Hot lead response time matters** — Alert within minutes, not hours
2. **Classification accuracy** — When unsure between QUESTIONS and RATES, default to RATES (higher intent)
3. **Declined prospects** — Always send polite thank you, leave door open for future
4. **OOO handling** — Don't bump follow-ups; wait for return
5. **SPAM detection** — Better to false-positive (alert) than miss hot lead
