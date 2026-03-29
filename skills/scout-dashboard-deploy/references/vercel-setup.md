# Vercel Setup Guide

## Project Configuration

The dashboard uses `vercel.json` for build settings:

```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

## Environment Variables

Set these in Vercel dashboard or via CLI:

```bash
vercel env add POSTGRES_URL
```

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_URL` | Postgres connection string | `postgresql://user:pass@host:5432/db` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_VERSION` | `2.0.0` | App version string |

## Domain Settings

Default deployment URL:
```
https://scout-dashboard-v2-[username].vercel.app
```

### Custom Domain

1. Add domain in Vercel dashboard
2. Update DNS records
3. Run: `vercel domains add your-domain.com`

## Build Settings

TypeScript and ESLint errors are ignored in production builds:

```typescript
// next.config.ts
export default {
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
}
```

## Deployment Regions

Default: `iad1` (Washington, D.C.)

To change regions, add to `vercel.json`:
```json
{
  "regions": ["iad1", "sfo1"]
}
```
