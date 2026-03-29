---
name: scout-error-handler
description: |
  Error handling and recovery system for Thoven's growth outreach operations.
  Provides error classification, retry logic with exponential backoff, 
  escalation for persistent failures, and comprehensive logging.
version: 1.0.0
author: Scout (Thoven)
tags: [error-handling, retry, logging, recovery, scout]
---

# Scout Error Handler

Handles failures gracefully across Thoven's outreach pipeline.

## Error Classification

| Type | Description | Retryable | Severity |
|:---|:---|:---:|:---:|
| `API_ERROR` | External API failures (5xx, timeouts) | ✅ Yes | High |
| `NETWORK_ERROR` | Connection issues, DNS failures | ✅ Yes | Medium |
| `AUTH_ERROR` | Authentication/authorization failures | ❌ No | Critical |
| `DATA_ERROR` | Invalid data, validation failures | ❌ No | Medium |
| `RATE_LIMIT` | Rate limiting from external services | ✅ Yes | Medium |

## Scripts

### classify_error.py
Categorizes errors into types with severity levels.

```bash
python3 scripts/classify_error.py "<error_message>" [--context <context>]
```

**Returns:** JSON with `type`, `severity`, `retryable`, `context`

### retry_with_backoff.py
Retries transient errors with exponential backoff.

```bash
python3 scripts/retry_with_backoff.py --command "<shell_command>" [--max-retries 3]
```

**Backoff:** 2s → 4s → 8s (exponential)

### escalate.py
Formats and queues persistent errors for human review.

```bash
python3 scripts/escalate.py --error-file <path> --type <error_type> [--suggest "<fix>"]
```

### log_recovery.py
Logs error details and recovery actions to `error_log.json`.

```bash
python3 scripts/log_recovery.py --type <error_type> --action <action> [--resolution "<msg>"]
```

## Usage Flow

```
1. Operation fails
      ↓
2. classify_error.py → Determine type & retryability
      ↓
   ┌─────────────────┴─────────────────┐
   ↓                                   ↓
Retryable                          Non-retryable
   ↓                                   ↓
retry_with_backoff.py              escalate.py
(max 3 attempts)                   (human review)
   ↓                                   ↓
Success? ──Yes──→ log_recovery.py    log_recovery.py
   ↓
   No ──→ escalate.py
```

## Configuration

| Setting | Default | Description |
|:---|:---|:---|
| `MAX_RETRIES` | 3 | Maximum retry attempts |
| `BACKOFF_BASE` | 2 | Base seconds for exponential backoff |
| `CIRCUIT_BREAKER_THRESHOLD` | 5 | Failures before circuit opens |
| `CIRCUIT_BREAKER_TIMEOUT` | 60s | Seconds before circuit half-opens |

## Integration Example

```python
import subprocess
import json

# 1. Run operation
result = subprocess.run(["some_command"], capture_output=True, text=True)

if result.returncode != 0:
    # 2. Classify error
    classify = subprocess.run(
        ["python3", "skills/scout-error-handler/scripts/classify_error.py", result.stderr],
        capture_output=True, text=True
    )
    error_info = json.loads(classify.stdout)
    
    if error_info["retryable"]:
        # 3. Retry with backoff
        subprocess.run([
            "python3", "skills/scout-error-handler/scripts/retry_with_backoff.py",
            "--command", "some_command",
            "--max-retries", "3"
        ])
    else:
        # 4. Escalate
        subprocess.run([
            "python3", "skills/scout-error-handler/scripts/escalate.py",
            "--error-file", "/tmp/error.txt",
            "--type", error_info["type"]
        ])
```

## Log Format

`error_log.json` entries:

```json
{
  "timestamp": "2026-03-30T03:41:00Z",
  "error_type": "NETWORK_ERROR",
  "severity": "medium",
  "message": "Connection timeout",
  "action": "retry",
  "attempts": 3,
  "resolution": "success",
  "context": "email_outreach"
}
```


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Network/API/Rate = retry with backoff** — 2s → 4s → 8s
2. **Auth/Data = escalate immediately** — Never retry auth failures
3. **Log everything for patterns** — error_log.json for analysis
4. **Max 3 retries then escalate** — Don't loop forever
5. 
