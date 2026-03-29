# API Routes Reference

## Endpoints

### GET /api/status

Returns pipeline stats and agent heartbeat.

**Response:**
```json
{
  "status": {
    "id": "scout",
    "status": "working",
    "currentTask": "Processing prospects",
    "version": "2.0.0",
    "lastHeartbeat": "2026-03-30T03:14:20.995Z"
  },
  "activity": [
    {
      "task": "Processed 5 prospects",
      "createdAt": "2026-03-30T03:14:20.995Z"
    }
  ]
}
```

### POST /api/status

Update agent status (heartbeat).

**Request:**
```json
{
  "status": "working",
  "currentTask": "Processing prospects",
  "version": "2.0.0"
}
```

**Response:**
```json
{ "success": true }
```

### GET /api/prospects

Returns prospect list with optional filters.

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `stage` | string | Filter by stage (e.g., `Prospected`, `Emailed`) |
| `city` | string | Filter by city |
| `branch` | string | Filter by branch (e.g., `Mom Blogs`) |

**Response:**
```json
{
  "prospects": [
    {
      "name": "Alicia (Making Time For Mommy)",
      "handle": "makingtimeformommy",
      "followers": 24700,
      "city": "Chicago",
      "email": "makingtimeformommy@gmail.com",
      "stage": "Prospected",
      "type": "Nano",
      "branch": "Mom Blogs",
      "score": 5,
      "scoreReason": "...",
      "draft_ready": true
    }
  ],
  "count": 1
}
```

## Data Schema

The API reads from `public/scout_data.json`:

```json
{
  "metadata": {
    "last_updated": "ISO timestamp",
    "version": "1.0"
  },
  "prospects": [...],
  "stats": {...},
  "agent_status": {...}
}
```

## Error Responses

All endpoints return standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 500 | Server error (check logs) |
