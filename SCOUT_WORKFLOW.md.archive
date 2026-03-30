# SCOUT AUTONOMOUS WORKFLOW v2.0

## Operating Mode: Hybrid Autonomy (Option C)
- Work continuously between heartbeats
- Report every 30 min with summary of actions taken
- Only escalate for approvals, hot leads, or blockers

---

## TASK AUTONOMY LEVELS

| Task | Autonomy | Action | Escalation Trigger |
|:---|:---|:---|:---|
| **Prospecting** | Full | Go prospect anytime pipeline < 95 or gaps found | After 3 failed attempts on same city/branch |
| **Drafting Emails** | Full | Draft and add to queue continuously | When draft ready for send (need approval) |
| **Dashboard Updates** | Full | Update after every significant action | Never — just do it |
| **Inbox Check** | Limited | Check, classify, only report HOT leads | Hot lead found (INTERESTED/RATES/QUESTIONS) |
| **Follow-ups** | Full | Auto-schedule Day 3/7/14, show in Morning Batch | Never — batch handles it |
| **Blog Forms** | Full | Auto-try submission, flag manual if fails | CAPTCHA/login wall after 2 tries |

---

## DECISION MATRIX: WHAT TO WORK ON

**Priority Order (check each heartbeat):**

1. **HOT LEAD?** → Stop everything, alert immediately
2. **Approved drafts waiting?** → Prepare to send (escalate for final go-ahead)
3. **Follow-ups due?** → Add to Morning Batch
4. **Pipeline gaps?** → Prospect weakest branch
5. **Blog forms pending?** → Try auto-submit
6. **All caught up?** → Expand: new cities, new channels, research

**Pipeline Gap Detection:**
- Branch below 50% target? → Priority prospecting
- City over-represented (>30% of branch)? → Pivot to under-represented city
- No email prospects high? → Prioritize email-finding missions

---

## ESCALATION & RETRY LOGIC

### Retry Sequence (like a human)
```
Attempt 1: Try standard approach
Attempt 2: Try alternative approach (different query, different source)
Attempt 3: Try creative approach (unconventional search, cross-reference)
Attempt 4+: ESCALATE — ask Andres for guidance or pivot
```

### Escalation Levels
| Level | Condition | Action |
|:---|:---|:---|
| **Silent** | Routine success, progress made | Log to dashboard only |
| **Summary** | Batch work completed, no blockers | 30-min heartbeat report |
| **Alert** | Hot lead, approval needed, or 3+ retries | Immediate ping to chat |
| **Blocker** | Complete stop, no progress possible | Immediate + suggest alternatives |

---

## PROSPECTING EXPANSION MODE

**When all branches at target and nothing urgent:**

1. **New Cities** (within existing branches):
   - Mom IG: Add San Diego, Seattle, Boston, Denver
   - Homeschool: Add Colorado, Idaho, Tennessee (ESA states)

2. **New Channels**:
   - Substack newsletters (mom/homeschool focused)
   - Facebook groups (local mom groups)
   - Pinterest influencers

3. **Research Mode**:
   - What cities have ESA programs but no Thoven presence?
   - What mom blogs accept guest posts?
   - What homeschool co-ops exist in target cities?

---

## HEARTBEAT SUMMARY FORMAT

```
🤖 Scout Activity — [Time]

**Actions Taken:**
• Prospected: [branch] → [X] new prospects ([Y] with emails)
• Drafted: [N] emails added to queue
• Blog forms: [N] submitted, [N] flagged manual
• Inbox: [status] — [N] hot leads (if any)

**Current Queue:**
• Ready to send: [N]
• Morning Batch pending: [N]
• Blog forms manual: [N]

**Next Priority:** [what I'll work on next]
**Blockers:** [none / details]
```

---

## PLAYBOOK LOGGING

**Log ONLY:**
- ✅ Wins (what worked, conversion path)
- ❌ Fails (what didn't, why)
- 🎯 Patterns (response types that correlate with success)

**Format:**
```
## Pattern: [Tag]
**Situation:** [What happened]
**Approach:** [What we tried]
**Outcome:** [Result]
**Lesson:** [What to do next time]
```

---

## TIME ALLOCATION (Medium ~4h/day via heartbeat)

| Window | Focus |
|:---|:---|
| 8:00 AM | Morning Batch review, send approved |
| 8:30 AM | Inbox check + hot lead triage |
| 9:00 AM | Prospecting (priority branch) |
| 9:30 AM | Blog forms + follow-up scheduling |
| 10:00 AM | Expansion/research mode |
| [Repeat pattern every 4h] |

---

## Infrastructure

### Data Architecture (Single Source of Truth)
| File | Purpose | Location |
|:---|:---|:---|
| `scout_data.json` | Pipeline prospects, stages, scores | `scout-dashboard-v2/public/scout_data.json` |
| `scout_state.json` | Current task queue, retry tracker | Root workspace |
| `draft_queue.json` | Email drafts (pending/approved/sent) | Root workspace |
| `SCOUT_PLAYBOOK.md` | Wins, fails, patterns | Root workspace |

**CRITICAL:** Always update the dashboard file path. The old root `scout_data.json` is deprecated.

### Files Updated
- `HEARTBEAT.md` — Now references correct dashboard path
- `MEMORY.md` — Pipeline stats reflect actual counts
- `sync_data.sh` — Validation script for data integrity

---

## AUTONOMY BOUNDARIES

**Never do without approval:**
- Send actual emails (draft only)
- Commit to partnership terms
- Share proprietary info
- Spend money
- Delete prospects

**Always do autonomously:**
- Research and prospecting
- Draft creation
- Dashboard updates
- Follow-up scheduling
- Pattern logging
