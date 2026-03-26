# Scout Dashboard — Debugging Guide

## The Golden Rule
**When dashboard looks outdated → Follow this checklist IN ORDER. No skipping.**

---

## 🔴 Problem: Panel/Code Changes Not Showing

### Step 1: Verify GitHub (30 sec)
```bash
# Check latest commit on GitHub
open https://github.com/Andresem611/scout-command-center/commits/main/

# Verify your change is there
```
**If commit NOT on GitHub** → Push failed, check local git status  
**If commit IS on GitHub** → Continue to Step 2

### Step 2: Force Streamlit Deploy (1 min)
1. Open Streamlit Cloud dashboard
2. Click **"⋮"** (three dots) on your app
3. Click **"Reboot"**
4. Wait for "Your app is ready" (usually 30-60s)

**If still not showing** → Continue to Step 3

### Step 3: Hard Browser Refresh (10 sec)
- **Chrome/Edge:** `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
- **Firefox:** `Ctrl+F5`
- **Safari:** `Cmd+Option+R`

**If still not showing** → Continue to Step 4

### Step 4: Clear Streamlit Cache (via UI)
1. Open app
2. Click **"🔄 Refresh"** button in sidebar
3. Or add `?clear_cache=true` to URL

**If still not showing** → Continue to Step 5

### Step 5: Add Debug Marker
Add visible test code to verify deployment:
```python
# In streamlit_app.py, at top of Dashboard page:
st.markdown("<span style='color:#0f0;'>DEBUG: v1.X loaded</span>", unsafe_allow_html=True)
```
Push, reboot, refresh. If you DON'T see green text → Streamlit not deploying.

### Step 6: Nuclear Option
1. Delete app from Streamlit Cloud
2. Re-deploy from GitHub
3. This fixes 99% of ghost caching issues

---

## 🟡 Problem: Data Not Syncing

### Symptoms
- Pipeline shows 195 prospects
- Dashboard shows 62 prospects
- Stats don't match

### Root Cause
`scout_data.json` is the single source of truth for Streamlit. Markdown pipeline files are human-readable but NOT auto-synced.

### Fix
```bash
cd /root/.openclaw/workspace
python3 sync_pipeline.py  # Converts markdown → JSON
git add scout_data.json
git commit -m "Sync pipeline data"
git push
```

Then reboot Streamlit app.

---

## 🟢 Happy Path: Making Changes

### For Code Changes (UI, panels, logic)
1. Edit `streamlit_app.py`
2. Test locally if possible: `streamlit run streamlit_app.py`
3. `git add streamlit_app.py`
4. `git commit -m "Descriptive message"`
5. `git push origin main`
6. **Wait 30 sec** for GitHub webhook
7. Streamlit auto-deploys (check logs)
8. **Hard refresh** browser
9. Verify change

### For Data Changes (new prospects, status updates)
1. Update pipeline markdown files
2. Run `python3 sync_pipeline.py`
3. `git add -A`
4. `git commit -m "Update pipeline: +X prospects"`
5. `git push`
6. Reboot Streamlit app (data changes need reboot)
7. Verify numbers match

### For Agent Status (heartbeat, health)
1. Edit `heartbeat.py`
2. Test: `python3 heartbeat.py`
3. Commit + push
4. **No Streamlit reboot needed** (runs on cron, not Streamlit)

---

## 📋 Daily Health Check (Automated)

Scout should verify daily:
- [ ] Dashboard loads without errors
- [ ] Agent status panel shows recent heartbeat (< 30 min)
- [ ] Prospect count matches pipeline files
- [ ] No JavaScript console errors

Add to `heartbeat.py`:
```python
# After main tasks, log dashboard health
data['agent_status']['last_health_check'] = datetime.now().isoformat()
data['agent_status']['dashboard_version'] = "1.1.0"
```

---

## 🚨 Emergency Contacts

| Issue | Where to Check |
|:---|:---|
| GitHub not updating | github.com/Andresem611/scout-command-center |
| Streamlit deploy logs | share.streamlit.io → Manage app → Logs |
| Browser cache | DevTools → Network → Disable cache |
| Data file state | `cat scout_data.json \| python3 -m json.tool` |

---

## 📝 Change Log

| Date | Change | Version |
|:---|:---|:---|
| 2026-03-27 | Agent status panel added | 1.1.0 |
| 2026-03-27 | Created DEBUGGING.md | — |

---

**Remember: Cache is the enemy. When in doubt, reboot + hard refresh.**
