---
name: scout-drafting
description: Personalized outreach email drafting for Thoven's growth team. Use when writing cold outreach emails to prospective partners (influencers, educators, content creators) for Thoven's music education marketplace. Supports research, personalization, template selection, draft generation, and approval workflows.
---

# Scout Drafting

Write personalized outreach emails for Thoven partnership opportunities.

## Quick Start

```bash
# Research a prospect
python skills/scout-drafting/scripts/research_prospect.py --prospect <path/to/prospect.json>

# Generate email draft
python skills/scout-drafting/scripts/generate_email.py \
  --prospect <path/to/prospect.json> \
  --template mom-influencer \
  --output draft.json

# Preview for approval
python skills/scout-drafting/scripts/preview_draft.py --draft draft.json
```

## Workflow

### 1. Research
Gather prospect data before writing:
- Bio, content themes, recent posts
- Family/kids details (for personalization)
- Location, values, pain points
- Content gaps Thoven could fill

**Tool:** `scripts/research_prospect.py`

**Input:** Prospect JSON with `name`, `handle`, `platform`, `bio`, `recent_content`

**Output:** Structured research notes with personalization angles

### 2. Personalize
Select the best personalization hooks:
- Reference specific content they've shared
- Connect their values to Thoven's mission
- Show you've done your homework

**Reference:** See [personalization-patterns.md](references/personalization-patterns.md)

### 3. Generate
Create the draft email:
- Choose appropriate template
- Fill personalization variables
- Apply Thoven voice (Keri's tone)

**Tool:** `scripts/generate_email.py`

**Templates:** See [email-templates.md](references/email-templates.md)

**Voice Guidelines:** See [thoven-positioning.md](references/thoven-positioning.md)

### 4. Queue
Preview and approve before sending:
- Format for review
- Flag any concerns
- Queue for send or request edits

**Tool:** `scripts/preview_draft.py`

## Template Types

| Template | Use For |
|:---------|:--------|
| `mom-influencer` | Parenting/lifestyle influencers with kids 4-12 |
| `homeschool-influencer` | Homeschool educators, curriculum creators |
| `music-teacher` | Independent music teachers, studio owners |
| `content-creator` | General education/entertainment creators |

## Important Rules

1. **Never send without preview** — Always run through `preview_draft.py` first
2. **Escalate weak prospects** — Flag low-fit prospects for review
3. **Stay authentic** — No generic flattery; reference real content
4. **Voice check** — Must sound like Keri from Thoven (warm, direct, educator-first)
5. **CTA clarity** — One clear ask per email

## References

Load these when needed:

- **[email-templates.md](references/email-templates.md)** — Base templates and variables
- **[thoven-positioning.md](references/thoven-positioning.md)** — Key messages, voice, what NOT to say
- **[personalization-patterns.md](references/personalization-patterns.md)** — How to research and personalize authentically


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Homeschool angle converts 2x for ESA states** — Lead with ESA eligibility in AZ, FL, UT
2. **Reference specific post, not generic praise** — "Your post about chaotic mornings" > "Love your content"
3. **Keri's voice: warm, direct, educator-first** — Not salesy; focus on helping families
4. **Day 7 follow-up needs NEW angle** — Not just a bump; add value (feature, testimonial, different benefit)
5. **Fit score 65+ = auto-select template** — Below 65, flag for manual review
