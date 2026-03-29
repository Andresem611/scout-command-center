# Retry Policy Reference

Backoff timing, max attempts, and circuit breaker configuration for Scout Error Handler.

## Exponential Backoff

### Default Configuration

| Parameter | Default | Environment Variable | Description |
|:---|:---:|:---|:---|
| Base delay | 2 seconds | `SCOUT_BACKOFF_BASE` | Starting delay between retries |
| Max retries | 3 attempts | `SCOUT_MAX_RETRIES` | Maximum retry attempts |
| Backoff multiplier | 2x | (hardcoded) | Exponential growth factor |

### Backoff Sequence

For default settings (base=2, max=3):

| Attempt | Delay | Total Wait Time |
|:---:|:---:|:---:|
| 1 | 2s | 2s |
| 2 | 4s | 6s |
| 3 | 8s | 14s |

### Rate Limit Backoff

For `RATE_LIMIT` errors, the policy adapts:

| Scenario | Behavior |
|:---|:---|
| Retry-After header present | Use header value (max 300s) |
| No header, known provider | Provider-specific default |
| Unknown | 60s base, 1.5x multiplier |
| Max retries | 5 (more lenient) |

### Jitter

To prevent thundering herd problems, optional jitter can be applied:

```python
delay = base_delay ** attempt
jittered_delay = delay + random.uniform(0, delay * 0.1)  # +0-10%
```

**Note:** Jitter not implemented in base version but recommended for high-throughput scenarios.

---

## Circuit Breaker Pattern

### Concept

Prevent cascading failures by "opening the circuit" after consecutive failures, bypassing requests until the service recovers.

### States

```
CLOSED ──[failure]──┐
   ↑                │
   │                ↓
HALF-OPEN ←──[timeout]── OPEN
   │                        │
   └──[success]─────────────┘
```

| State | Description |
|:---|:---|
| **CLOSED** | Normal operation, requests pass through |
| **OPEN** | Requests fail fast without attempting |
| **HALF-OPEN** | Test request to check if service recovered |

### Configuration

| Parameter | Default | Description |
|:---|:---:|:---|
| Failure threshold | 5 consecutive | Opens circuit after N failures |
| Timeout duration | 60 seconds | Time in OPEN state before HALF-OPEN |
| Success threshold | 1 | Closes circuit after N successes in HALF-OPEN |

### Implementation Notes

Current implementation (Python scripts) uses simple retry logic. Circuit breaker would require:

1. **State storage:** Shared state across processes (file, Redis, etc.)
2. **Failure counting:** Track consecutive failures per service
3. **State transitions:** Logic for OPEN → HALF-OPEN → CLOSED

### Pseudo-Implementation

```python
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.failure_threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpen("Service temporarily unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
```

---

## Timeout Configuration

| Operation | Timeout | Rationale |
|:---|:---:|:---|
| Individual HTTP request | 30s | Prevent hanging connections |
| Command execution | 300s (5min) | Allow slow operations but cap them |
| Total retry cycle | ~15s (3 retries) | Fail fast enough to escalate |
| Rate limit wait | Max 300s | Don't wait forever |

---

## Provider-Specific Policies

### Email Services

| Provider | Rate Limit | Backoff Strategy |
|:---|:---|:---|
| Gmail API | 250 quota units/user/second | 1s base, 2 retries |
| SendGrid | 600 requests/minute | 2s base, 3 retries |
| Mailgun | Based on plan | 2s base, 3 retries |

### Social APIs

| Platform | Rate Limit | Backoff Strategy |
|:---|:---|:---|
| Twitter/X | 300 requests/15min | 60s base, 5 retries |
| LinkedIn | 500 requests/day | 120s base, 3 retries |
| Instagram | 200 requests/hour | 60s base, 5 retries |

---

## Environment Overrides

Set these environment variables to customize retry behavior:

```bash
# Increase retries for flaky network
export SCOUT_MAX_RETRIES=5

# Faster backoff for low-latency requirements
export SCOUT_BACKOFF_BASE=1

# Disable retries (fail fast mode)
export SCOUT_MAX_RETRIES=0
```

---

## Best Practices

1. **Idempotency:** Only retry idempotent operations (GET, PUT with same data)

2. **Exponential backoff:** Linear backoff causes thundering herd; exponential spreads load

3. **Maximum backoff:** Cap backoff at reasonable limit (e.g., 60s) to prevent indefinite waiting

4. **Jitter:** Add randomness to prevent synchronized retries

5. **Dead letter queue:** After max retries, queue for manual review rather than dropping

6. **Monitoring:** Track retry rates; high retry rates indicate systemic issues

---

## Retry vs Escalate Decision Tree

```
Is error retryable?
    ├── No → ESCALATE immediately
    │
    └── Yes → Are retries exhausted?
                ├── Yes → ESCALATE
                │
                └── No → Is circuit open?
                            ├── Yes → ESCALATE
                            └── No → RETRY with backoff
```
