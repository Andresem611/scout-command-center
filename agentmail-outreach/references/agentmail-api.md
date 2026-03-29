# AgentMail API Reference

Base URL: `https://api.agentmail.to`

Authentication: Bearer token in Authorization header
```
Authorization: Bearer am_us_...
```

---

## Endpoints

### List Inboxes
```
GET /inboxes
```
**Response:**
```json
{
  "count": 1,
  "inboxes": [
    {
      "inbox_id": "keri@agentmail.to",
      "email": "keri@agentmail.to",
      "display_name": "Keri",
      "created_at": "2026-03-20T22:46:35.200Z"
    }
  ]
}
```

### List Messages
```
GET /inboxes/{inbox_id}/messages
```
**Query params:**
- `limit`: Max messages to return (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "messages": [
    {
      "message_id": "...",
      "thread_id": "...",
      "from": [{"email": "prospect@example.com", "name": "Jane"}],
      "to": [{"email": "keri@agentmail.to"}],
      "subject": "Re: Partnership",
      "body": "Hi Keri, I'm interested...",
      "created_at": "2026-03-29T10:30:00Z",
      "read": false
    }
  ]
}
```

### Send Message
```
POST /inboxes/{inbox_id}/messages/send
```
**Body:**
```json
{
  "to": ["prospect@example.com"],
  "subject": "Partnership opportunity",
  "body": "Hi...",
  "reply_to": "keri@agentmail.to"
}
```

**Response:**
```json
{
  "message_id": "...",
  "thread_id": "..."
}
```

### Reply to Message
```
POST /inboxes/{inbox_id}/messages/{message_id}/reply
```
**Body:**
```json
{
  "body": "Thanks for your reply..."
}
```

---

## Rate Limits

| Operation | Limit |
|:---|:---|
| Send email | 100 per minute |
| List messages | 100 per minute |
| Other operations | 100 per minute |

**Headers returned:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711800000
```

---

## Error Codes

| Code | Meaning | Resolution |
|:---|:---|:---|
| 400 | Bad Request | Check request body format |
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Inbox/message doesn't exist |
| 429 | Rate Limited | Wait and retry with backoff |
| 500 | Server Error | Retry, alert if persists |

---

## Python Usage Example

```python
import urllib.request
import json

API_KEY = "am_us_..."
INBOX = "keri@agentmail.to"

def send_email(to, subject, body):
    url = f"https://api.agentmail.to/inboxes/{INBOX}/messages/send"
    
    payload = json.dumps({
        "to": [to],
        "subject": subject,
        "body": body
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

---

## Webhooks (Optional)

For real-time notifications instead of polling:

```
POST /webhooks
```
**Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["message.received", "message.sent"]
}
```

Events:
- `message.received` — New email arrived
- `message.sent` — Email sent successfully
- `message.delivered` — Email delivered to recipient
- `message.bounced` — Email bounced

---

## Testing

Test inbox check:
```bash
curl -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  https://api.agentmail.to/inboxes/keri@agentmail.to/messages
```

Test send:
```bash
curl -X POST \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"to":["keri@agentmail.to"],"subject":"Test","body":"Hello"}' \
  https://api.agentmail.to/inboxes/keri@agentmail.to/messages/send
```
