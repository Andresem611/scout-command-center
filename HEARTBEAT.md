# Scout Heartbeat — Trigger Only

**When this file is read:** Execute one heartbeat cycle.

## Loading Chain (READ IN ORDER)

1. **Read MEMORY.md** — restore current state (pipeline stats, A/B scores, pending items)
2. **Read memory/YYYY-MM-DD.md** — today's context, what happened earlier
3. **Read AGENTS.md** — load ROUTE decision tree and dispatch table
4. **Run AGENTS.md ROUTE** top-down — find first matching trigger
5. **AGENTS.md dispatches** to appropriate skill
6. **Execute skill** with Think-Act-Observe (max 5 cycles)
7. **Save state** to memory files
8. **Park** — wait for next heartbeat

## Quick Checklist (for logging)

- [ ] Inbox hot leads?
- [ ] Approved drafts waiting?
- [ ] Follow-ups due?
- [ ] Pipeline gaps below target?
- [ ] Data sync needed?

## Exit

After ROUTE execution completes, log summary and exit. Do not loop.

## Output Format

```
🤖 Scout Heartbeat — [Time]

**Actions This Cycle:**
• [What was dispatched]
• [What skill executed]
• [Result]

**Current State:**
• Pipeline: [X]/[target] prospects
• Ready to send: [N]
• Next priority: [from AGENTS.md ROUTE]

**Working On:** [current task from skill]
**Next Up:** [next from AGENTS.md dispatch]
**Blockers:** [none / details]
```
