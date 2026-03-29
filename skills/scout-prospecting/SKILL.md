---
name: scout-prospecting
description: |
  Find mom influencers, homeschool bloggers, and parenting content creators with contact info for Thoven outreach.
  Use when: (1) Searching for influencers by city/niche, (2) Extracting emails from bios/websites, 
  (3) Scoring prospect quality, (4) Building outreach lists for music education partnerships.
  Triggers on: "find influencers", "mom bloggers", "homeschool influencers", "extract email", 
  "score prospect", "prospecting", "outreach list".
---

# Scout Prospecting

Find and qualify mom influencers, homeschool bloggers, and parenting content creators for Thoven partnerships.

## Quick Start

```bash
# Search influencers by city
python3 scripts/search_influencers.py --city "Austin" --type mom

# Extract contact from URL
python3 scripts/extract_contact.py --url https://instagram.com/mom_blogger

# Score a prospect
python3 scripts/score_prospect.py --followers 50k --engagement 4.5 --content-fit high
```

## Workflow

**Search → Extract → Validate → Score**

1. **Search**: Use `search_influencers.py` to find candidates by city/type
2. **Extract**: Use `extract_contact.py` to pull emails from bios/websites
3. **Validate**: Verify contact info is current and relevant
4. **Score**: Use `score_prospect.py` to rank 1-5 based on Thoven criteria

## Scripts

### search_influencers.py

Find influencers using web search patterns.

```bash
python3 scripts/search_influencers.py --city "Denver" --type mom --limit 20
python3 scripts/search_influencers.py --city "Seattle" --type homeschool --limit 15
```

**Parameters:**
- `--city`: Target city (required)
- `--type`: `mom` | `homeschool` | `parenting` (required)
- `--limit`: Max results (default: 10)
- `--output`: JSON output file (optional)

**Output format:**
```json
{
  "influencers": [
    {
      "name": "Sarah Johnson",
      "handle": "@sarahmoms",
      "platform": "instagram",
      "followers": "45K",
      "city": "Austin",
      "bio": "Mom of 3 | Homeschool tips |...",
      "url": "https://instagram.com/sarahmoms"
    }
  ]
}
```

### extract_contact.py

Extract email addresses from social bios, websites, and press pages.

```bash
python3 scripts/extract_contact.py --url https://instagram.com/mom_blogger
python3 scripts/extract_contact.py --bio "Contact: hello@momlife.com | Mom of 2"
```

**Parameters:**
- `--url`: Social profile or website URL
- `--bio`: Raw bio text (alternative to URL)
- `--deep`: Crawl linked websites for contact info

**Output format:**
```json
{
  "emails": ["hello@momlife.com"],
  "sources": ["bio", "website"],
  "confidence": "high"
}
```

### score_prospect.py

Score prospects 1-5 based on Thoven-specific criteria.

```bash
python3 scripts/score_prospect.py --followers 50k --engagement 3.5 --content-fit medium
python3 scripts/score_prospect.py --file prospect.json
```

**Parameters:**
- `--followers`: Follower count (e.g., 50k, 1M)
- `--engagement`: Engagement rate percentage (e.g., 4.5)
- `--content-fit`: `high` | `medium` | `low` — alignment with music/ homeschool
- `--has-website`: Presence of blog/website
- `--file`: JSON file with prospect data

**Output format:**
```json
{
  "score": 4,
  "tier": "A",
  "reasoning": [
    "50K followers (good reach)",
    "4.5% engagement (above avg)",
    "Homeschool content (high fit)"
  ]
}
```

## Reference Materials

- **Search queries**: See [references/search-queries.md](references/search-queries.md) for query templates by city/type
- **Scoring rubric**: See [references/scoring-rubric.md](references/scoring-rubric.md) for 5-point scale details

## Thoven-Specific Criteria

**Ideal Prospect Profile:**
- Mom influencers with 10K-500K followers
- Content: homeschooling, parenting, kids activities, educational toys
- US-based (initial focus: Texas, Colorado, California)
- Active within last 30 days
- Email/contact in bio or website

**Red Flags (Auto-Reject):**
- <1% engagement rate
- No contact info and no website
- Inactive >90 days
- Content misaligned (adult-only, controversial)


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Search beats browser for $439 runway** — Instagram/TikTok login walls block browser approach; kimi_search + website extraction is viable
2. **Cross-reference "[name] contact" finds hidden emails** — Press pages and collaboration links often have emails not in bios
3. **Score 4+ = A-tier worth immediate draft** — Don't queue low scores; focus energy on high-fit prospects
4. **Blog forms often easier than direct email** — Mom blogs have contact forms ready; homeschool influencers prefer DMs
5. **No single city >30% of pipeline** — Spread across cities to reduce geographic risk
