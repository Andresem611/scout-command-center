---
name: scout-dashboard-deploy
description: Deploy the Thoven Scout dashboard to Vercel. Use when deploying the Next.js dashboard (scout-dashboard-v2), syncing prospect data, checking deployment status, or troubleshooting Vercel builds. Triggers on "deploy dashboard", "update dashboard", "sync scout data", "check deployment status", "vercel deploy".
---

# Scout Dashboard Deploy

Deploy and manage the Thoven Scout prospecting dashboard on Vercel.

## Quick Start

```bash
# 1. Build → 2. Test → 3. Deploy
python3 ~/.openclaw/workspace/skills/scout-dashboard-deploy/scripts/build.py
python3 ~/.openclaw/workspace/skills/scout-dashboard-deploy/scripts/check_status.py
python3 ~/.openclaw/workspace/skills/scout-dashboard-deploy/scripts/deploy.py
```

## Environment Variables

Create `.env.local` in `scout-dashboard-v2/`:

```
POSTGRES_URL=postgresql://user:pass@host:port/db
```

For Vercel deployment, set env vars via:
```bash
vercel env add POSTGRES_URL
```

### Required Variables

| Variable | Purpose | Source |
|----------|---------|--------|
| `POSTGRES_URL` | Postgres connection | Vercel Postgres dashboard |

## API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Pipeline stats, agent heartbeat |
| `/api/status` | POST | Update agent status |
| `/api/prospects` | GET | Filterable prospect list |

### Response Formats

See [references/api-routes.md](references/api-routes.md) for full specs.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `vercel: command not found` | CLI not installed | `npm i -g vercel` |
| `Not authorized` | Token expired | `vercel login` |
| Build fails | TypeScript errors | Check `next.config.ts` has `ignoreBuildErrors: true` |
| 500 on API | Missing scout_data.json | Run `sync_data.py` |
| Data out of sync | Local/prod mismatch | Re-run `sync_data.py` |

## Files

- `scripts/build.py` — Build the dashboard
- `scripts/deploy.py` — Deploy to Vercel
- `scripts/sync_data.py` — Sync scout_data.json
- `scripts/check_status.py` — Health check
- `references/vercel-setup.md` — Vercel configuration
- `references/api-routes.md` — API documentation
