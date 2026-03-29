# Stage Definitions

## Pipeline Stages

```
Prospected → Contacted → Replied → Negotiating → Partner
                ↓           ↓            ↓
            Declined    Declined     Declined
```

### Prospected
**Entry point.** Prospect identified as potential music education partner.

- Source: Research, referrals, maps, directories
- Action: Add to pipeline with full contact info
- Exit: Contacted (outreach sent)

### Contacted
**Outreach initiated.** First touchpoint made.

- Email sent, DM sent, or call attempted
- Waiting for response
- Exit: Replied (they respond) or Declined (explicit no / 3+ follow-ups with no response)

### Replied
**Engagement established.** Prospect responded.

- Shows interest or asks questions
- May need info about Thoven, commission structure, onboarding
- Exit: Negotiating (serious interest) or Declined (decided against)

### Negotiating
**Active deal flow.** Discussing terms and onboarding.

- Commission rate discussions
- Onboarding process walkthrough
- Integration questions
- Exit: Partner (signed up) or Declined (couldn't agree on terms)

### Partner
**Closed-won.** Active referring partner.

- Onboarded to Thoven
- Receiving student referrals
- Earning commissions
- Terminal state — no further transitions

### Declined
**Closed-lost.** Prospect will not become a partner.

- Explicit "no thanks"
- Ghosted after multiple attempts
- Couldn't agree on terms
- Terminal state — no further transitions

## Allowed Transitions

| From Stage | Allowed To |
|:-----------|:-----------|
| Prospected | Contacted |
| Contacted | Replied, Declined |
| Replied | Negotiating, Declined |
| Negotiating | Partner, Declined |
| Partner | *(terminal)* |
| Declined | *(terminal)* |

## Blocked Transitions

These are **never allowed**:

- **Backward moves**: Contacted → Prospected, Replied → Contacted, etc.
- **Skip ahead**: Prospected → Negotiating, Contacted → Partner, etc.
- **Exit terminal**: Partner → anything, Declined → anything

## Why Strict Forward Progression?

1. **Clean data** — Prevents pipeline gaming
2. **Accurate metrics** — Conversion rates reflect real funnel
3. **Honest reporting** — Andres sees true state of outreach
4. **Process discipline** — Forces proper nurturing at each stage
