# Scout Heartbeat — Autonomous Mode

**Read SCOUT_WORKFLOW.md first** — this file is the execution layer.

---

## Current Session State (updated every heartbeat)

**Last Action:** [timestamp]
**Current Task:** [what I'm working on]
**Next Task Queue:** [prioritized list]
**Retry Counts:** [per-task retry tracking]

---

## Heartbeat Cycle (every 30 min)

### 1. INBOX CHECK (2 min)
```
IF AgentMail configured:
  Check keri@agentmail.to
  Classify: INTERESTED | QUESTIONS | RATES | DECLINED | OOO | SPAM
  
  IF INTERESTED or QUESTIONS or RATES:
    ALERT immediately to chat + email keri@thoven.co
    Draft response (don't send)
    Add to playbook: situation + prospect details
  
  IF DECLINED:
    Update prospect stage to "Declined"
    Draft polite thank you
    Add to playbook: why declined (if clear)
  
  IF OOO or SPAM:
    Log silently, no alert
ELSE:
  Log: "Inbox check skipped — AgentMail not configured"
```

### 2. APPROVALS QUEUE (1 min)
```
Check "Ready to Send" queue
IF items waiting:
  Log count
  Prepare send summary
  WAIT for Andres "send" command
  (Don't auto-send — ever)
ELSE:
  Continue
```

### 3. FOLLOW-UPS (1 min)
```
Scan prospects with stage = "Contacted"
Check contact date vs. today

IF Day 3 since contact AND no reply:
  Generate Day 3 follow-up draft
  Add to Morning Batch queue
  
IF Day 7 since contact AND no reply:
  Generate Day 7 follow-up draft
  Add to Morning Batch queue
  
IF Day 14 since contact AND no reply:
  Generate Day 14 follow-up draft
  Add to Morning Batch queue
  Mark prospect as "Cold" after this
```

### 4. PROSPECTING (15 min — if pipeline has gaps)
```
Check branch targets:
- Mom IG: 30 target, [X] current
- Mom TikTok/YouTube: 15 target, [X] current
- Mom Blogs: 15 target, [X] current
- Homeschool IG (AZ): 15 target, [X] current
- Homeschool Blogs (AZ): 10 target, [X] current
- Homeschool Expansion: 10 target, [X] current

Find biggest gap → Work on that branch

IF all branches at target:
  Check city distribution (no city > 30%)
  IF imbalance → Prospect under-represented city
  ELSE → Enter EXPANSION MODE (new cities/channels)

Prospecting approach (retry logic):
- Attempt 1: Standard kimi_search query
- Attempt 2: Alternative query angle
- Attempt 3: Cross-reference search
- Attempt 4+: ESCALATE — ask Andres or pivot
```

### 5. BLOG FORMS (5 min)
```
Find blogs with status = "pending"

FOR each blog:
  Attempt 1: Auto-fill contact form via browser
  IF success → Mark "auto_submitted"
  IF CAPTCHA/login wall → Mark "manual_needed", flag in Morning Batch
  IF fail → Retry max 2 times, then mark "manual_needed"
```

### 6. DRAFTING (5 min — continuous)
```
Find prospects with:
- Stage = "Prospected"
- Email present
- No draft created yet

Generate personalized draft using template
Add to queue with status "pending"
Update dashboard
```

### 7. DASHBOARD UPDATE (1 min)
```
Update scout-dashboard-v2/public/scout_data.json:
- Prospect counts by branch
- Stage distribution
- Activity log

Commit to GitHub if changes made
```

### 8. PLAYBOOK LOGGING (continuous)
```
IF significant interaction completed:
  Log to knowledge base:
  - Situation (what happened)
  - Guidance (what Andres said)
  - Response (what I sent)
  - Outcome (result)
  - Pattern tag (for future reference)
```

---

## EXPANSION MODE (when all caught up)

### New Cities to Research
- **Mom IG:** San Diego, Seattle, Boston, Denver, Atlanta
- **Homeschool:** Phoenix (more depth), Tucson, Scottsdale, Colorado Springs

### New Channels
- Substack newsletters (search: "mom newsletter [city]")
- Local Facebook mom groups
- Pinterest influencers (search: "homeschool Pinterest")

### Research Tasks
- Which states have active ESA programs?
- What homeschool co-ops exist in target cities?
- What mom blogs accept sponsored content?

---

## Summary Report Format

After each heartbeat cycle, post:

```
🤖 Scout Heartbeat — [Time]

**Actions This Cycle:**
• Prospected: [branch] → [X] new prospects ([Y] with emails)
• Drafted: [N] emails to queue
• Blog forms: [N] auto-submitted, [N] manual flagged
• Inbox: [N] hot leads (if any) / clean

**Current State:**
• Pipeline: [X]/95 prospects
• Ready to send: [N]
• Morning Batch pending: [N]

**Working On:** [current task]
**Next Up:** [next priority]
**Blockers:** [none / details]
```

---

## Retry Tracker

| Task | Last Attempt | Retries | Status |
|:---|:---|:---|:---|
| [City/branch prospecting] | [timestamp] | [0-3] | active/paused/escalated |
| [Blog form] | [timestamp] | [0-2] | pending/manual/completed |

When retries >= threshold → Escalate or pivot
