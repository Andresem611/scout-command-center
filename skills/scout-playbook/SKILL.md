---
name: scout-playbook
description: |
  Log wins, fails, patterns, and learnings from outreach interactions.
  Use when: After significant interaction, hot lead, declined prospect, or conversion.
  Triggers on: "log pattern", "playbook", "what worked", "what didn't".
---

# Scout Playbook

Log patterns and learnings from outreach interactions.

## When to Log

**Log ONLY:**
- ✅ **Wins** — What worked, conversion path
- ❌ **Fails** — What didn't, why
- 🎯 **Patterns** — Response types that correlate with success

**Don't log:**
- Routine actions (everyday prospecting)
- Successful sends (unless hot lead)
- System operations (syncs, updates)

## Log Format

```markdown
## Pattern: [Tag]
**Date:** YYYY-MM-DD
**Situation:** [What happened — reply type, prospect profile]
**Approach:** [What we tried — email template, angle, timing]
**Guidance:** [What Andres said to do]
**Response:** [What you sent]
**Outcome:** [Result — converted, declined, ghosted, negotiating]
**Lesson:** [What to do next time]
```

## Pattern Tags

Use consistent tags for searchability:

| Tag | Use For |
|:---|:---|
| `hot-lead-interested` | Immediate positive response |
| `hot-lead-questions` | Asked questions before committing |
| `hot-lead-rates` | Asked about compensation |
| `declined-not-fit` | Polite decline, wrong audience |
| `declined-timing` | "Not right now" — follow up later |
| `ghosted-after-send` | No reply after outreach sent |
| `conversion-partnership` | Successfully converted to partner |
| `template-mom-influencer` | Template worked for mom influencer |
| `template-homeschool` | Template worked for homeschool |
| `timing-morning` | Morning send got better response |
| `timing-afternoon` | Afternoon send got better response |

## Storage

Playbook entries stored in:
- `memory/LEARNINGS.md` — Wins and patterns
- `memory/FAILED_APPROACHES.md` — What didn't work
- `SCOUT_PLAYBOOK.md` — Full interaction logs

## Retrieval

Before drafting emails or making decisions:
1. Search playbook for similar past situation
2. Use pattern to inform approach
3. Log new outcome to improve pattern

## KEY LEARNINGS (max 5)

1. **Log immediately** — Don't wait, details fade fast
2. **Specificity wins** — "Mom influencer with 50k followers" > "influencer"
3. **Andres's guidance** — Record exactly what he said, not your interpretation
4. **Outcome tracking** — Go back and update when result known
5. **Pattern search** — Before any action, check if similar situation logged before
