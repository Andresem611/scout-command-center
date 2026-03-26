# Scout Command Center - Deployment Package

## Files Included

| File | Purpose |
|:---|:---|
| `scout_data.json` | Shared data file (prospects, replies, stats) |
| `streamlit_app.py` | Streamlit dashboard (UI for approvals) |
| `heartbeat_priority.py` | Priority heartbeat (approvals → inbox → prospecting) |
| `app.py` | Original app (backup) |

## Deployment Steps

### 1. Deploy to Streamlit Cloud

```bash
# Login to Streamlit Cloud
# Upload these files:
# - streamlit_app.py
# - scout_data.json
# - requirements.txt (create with: streamlit)
```

### 2. Update Scout Data File Path

In `streamlit_app.py`, line 17:
```python
DATA_FILE = "scout_data.json"  # Change if deploying to different location
```

### 3. Configure Heartbeat

The cron job runs every 30 minutes:
- **Priority 1**: Check for approved drafts → send immediately
- **Priority 2**: Check inbox for replies
- **Priority 3**: Prospecting (if pipeline below 50)

## Current Pipeline Status

| Branch | Target | Current | Status |
|:---|:---|:---|:---|
| Mom Influencers (IG) | 30 | 23 | ✅ Good |
| Mom Influencers (TT/YT) | 15 | 0 | 🔴 Critical |
| Mom Blogs | 15 | 14 | ✅ Good |
| Homeschool Influencers (AZ) | 15 | 3 | 🔴 Critical |
| Homeschool Blogs (AZ) | 10 | 0 | 🔴 Critical |
| Homeschool Expansion | 10 | 0 | 🔴 Critical |
| **TOTAL** | **95** | **40** | **📊 42%** |

## Ready to Send (Have Emails)

Top prospects with valid emails:

1. **Irina Bromberg** (95) — Miami — pr@irinabromberg.com
2. **Christie Ferrari** (90) — Miami — christieferrari.com/services
3. **Elizabeth Inciarte** (88) — Miami — hi@byelinciarte.com
4. **Madison Fisher** (92) — LA — info@jakerosentertainment.com
5. **Jana Kramer** (90) — LA — Kathryn@kvwmanagement.com
6. **Sarah Auerswald** (88) — LA — Sarah@MomsLA.com
7. **Devon Kirby** (85) — Miami — hello@momapprovedmiami.com
8. **Valentina Tamayo** (85) — Miami — info@mvtrends.com
9. **Stacey Rodriguez** (86) — Houston — StaceyGarska@gmail.com
10. **Kim** (85) — NYC — Kim@beautyandthebumpnyc.com

## Next Steps

1. **Deploy Streamlit app** → Go to Morning Batch tab → Approve drafts
2. **Heartbeat sends** within 5 minutes of approval
3. **I continue prospecting** for remaining 55 gaps (TT/YT, homeschool, expansion)

## Workflow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  You approve    │────▶│  Heartbeat   │────▶│  Email sent │
│  in Streamlit   │     │  checks API  │     │  via Agent  │
└─────────────────┘     └──────────────┘     └─────────────┘
         │
         ▼
┌─────────────────┐
│  Scout checks   │
│  inbox 30 min   │
└─────────────────┘
```
