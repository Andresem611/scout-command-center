# Error Types Reference

Classification rules for the Scout Error Handler system.

## Error Types

### API_ERROR

**Description:** External API failures, typically server-side issues

**Indicators:**
- HTTP 5xx status codes (500, 502, 503, 504)
- "Internal Server Error"
- "Service Unavailable"
- "Bad Gateway"
- "Gateway Timeout"
- API provider outage messages

**Severity:** High

**Retryable:** ✅ Yes

**Examples:**
```
500 Internal Server Error
503 Service Unavailable - The server is temporarily unable to handle the request
API returned error: upstream connect error
```

---

### NETWORK_ERROR

**Description:** Connection and network layer failures

**Indicators:**
- Connection timeouts
- Connection refused
- DNS resolution failures
- SSL/TLS errors
- Socket errors
- "No route to host"

**Severity:** Medium

**Retryable:** ✅ Yes

**Examples:**
```
Connection timeout after 30 seconds
Connection refused: api.example.com:443
Name or service not known (DNS failure)
SSL: certificate verify failed
```

---

### RATE_LIMIT

**Description:** Request throttling from external services

**Indicators:**
- HTTP 429 status code
- "Rate limit exceeded"
- "Too Many Requests"
- "Quota exceeded"
- "Throttled"
- Retry-After headers

**Severity:** Medium

**Retryable:** ✅ Yes (with appropriate backoff)

**Examples:**
```
429 Too Many Requests
Rate limit exceeded: 1000 requests per hour
You have exceeded your quota
```

**Note:** Always honor Retry-After headers when present.

---

### AUTH_ERROR

**Description:** Authentication and authorization failures

**Indicators:**
- HTTP 401 (Unauthorized)
- HTTP 403 (Forbidden)
- "Authentication failed"
- "Invalid credentials"
- "Token expired"
- "Access denied"
- Permission errors

**Severity:** Critical

**Retryable:** ❌ No

**Examples:**
```
401 Unauthorized: Invalid API key
403 Forbidden: Insufficient permissions
Token has expired
Access denied for resource
```

**Why not retryable:** Authentication errors require human intervention to update credentials. Retrying wastes resources and may trigger security alerts.

---

### DATA_ERROR

**Description:** Data validation and format errors

**Indicators:**
- HTTP 400 (Bad Request)
- "Validation error"
- "Invalid format"
- Schema mismatches
- Required field missing
- Parse errors
- Type errors

**Severity:** Medium

**Retryable:** ❌ No

**Examples:**
```
400 Bad Request: Invalid JSON
Validation failed: email is required
Schema error: expected string, got number
Failed to parse response
```

**Why not retryable:** Data errors indicate a bug or incorrect usage. The request must be fixed before retrying.

---

### UNKNOWN

**Description:** Errors that don't match known patterns

**Indicators:**
- Unrecognized error messages
- New error formats
- Generic errors without context

**Severity:** High

**Retryable:** ❌ No (default)

**Action:** Log and escalate for analysis

---

## Decision Matrix

| Error Type | Retry? | Max Retries | Backoff Strategy | Escalate After |
|:---|:---:|:---:|:---|:---:|
| API_ERROR | ✅ | 3 | Exponential 2s→4s→8s | Yes |
| NETWORK_ERROR | ✅ | 3 | Exponential 2s→4s→8s | Yes |
| RATE_LIMIT | ✅ | 5 | Honor Retry-After or 60s | No |
| AUTH_ERROR | ❌ | 0 | N/A | Immediately |
| DATA_ERROR | ❌ | 0 | N/A | Immediately |
| UNKNOWN | ❌ | 0 | N/A | Immediately |

---

## Pattern Matching Rules

The classifier uses regex patterns (case-insensitive) to identify error types:

### NETWORK_ERROR Patterns
```regex
connection.*(timeout|refused|reset)
network.*(unreachable|error|failure)
dns.*(error|failure|not found)
ssl.*error
certificate.*(verify|error)
unable.*connect
host.*unreachable
no route to host
temporary failure
```

### API_ERROR Patterns
```regex
5\d{2}.*error
internal server error
service unavailable
gateway timeout
bad gateway
server.*error
api.*(failure|error|down)
```

### RATE_LIMIT Patterns
```regex
rate.*limit
too many requests
429
quota exceeded
throttled
limit exceeded
retry-after
```

### AUTH_ERROR Patterns
```regex
unauthorized
authentication.*(failed|error|required)
403
401
forbidden
access.*denied
invalid.*(token|credential|key)
expired.*token
permission.*denied
```

### DATA_ERROR Patterns
```regex
validation.*error
invalid.*(data|format|input)
required.*field
schema.*error
parse.*error
malformed
bad request
400
json.*error
type.*error
```

---

## Adding New Error Types

To add a new error type:

1. Update `scripts/classify_error.py`:
   - Add new `ErrorType` enum value
   - Define patterns, severity, and retryability

2. Update this documentation with classification rules

3. Update `references/retry-policy.md` if retry behavior differs

4. Test with sample error messages
