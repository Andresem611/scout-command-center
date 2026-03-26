# Scout Dashboard v2

Next.js agent command center for Thoven.

## Setup

```bash
npm install
npx prisma generate
npx prisma db push
```

## Environment Variables

Create `.env.local`:
```
POSTGRES_URL=your_vercel_postgres_url
```

## Run Dev

```bash
npm run dev
```

## Deploy

```bash
vercel
```
