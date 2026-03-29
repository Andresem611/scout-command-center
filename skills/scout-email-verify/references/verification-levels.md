# Verification Levels

Email verification in Thoven's outreach pipeline happens at three levels:

## Level 1: Syntax Validation

**What it checks:**
- Email format compliance (RFC 5322)
- Valid characters in local part
- Proper domain structure
- Common typos (gmial→gmail, etc.)

**When to use:**
- First line of defense during prospecting
- Real-time validation in forms
- Quick filtering of garbage input

**Output:**
- ✅ **Valid** - Format looks correct
- ❌ **Invalid** - Format errors detected
- ⚠️ **Valid with suggestion** - Format valid but possible typo detected

**Examples:**

| Input | Result | Notes |
|-------|--------|-------|
| `john@gmail.com` | ✅ Valid | Standard format |
| `john@gmial.com` | ⚠️ Typo | Suggests `gmail.com` |
| `john@gmail` | ❌ Invalid | Missing TLD |
| `john..doe@gmail.com` | ❌ Invalid | Consecutive dots |

---

## Level 2: Domain Verification

**What it checks:**
- MX record existence
- Domain not in disposable list
- Domain not blacklisted
- Optional: Spamhaus DBL check

**When to use:**
- Before adding to outreach list
- Pre-send validation
- Cleaning existing lists

**Output:**
- ✅ **Valid** - Domain accepts mail
- ❌ **Invalid** - Domain issues detected
- ⚠️ **Unknown** - DNS lookup failed (retry later)

**Checks performed:**

| Check | Purpose |
|-------|---------|
| MX Lookup | Verifies mail server exists |
| A Record Fallback | Some domains use A instead of MX |
| Disposable Detection | Rejects throwaway emails |
| Blacklist Check | Known bad domains |
| Spamhaus DBL | Domain reputation (optional) |

**Exit codes:**
- `0` - Domain valid, MX found
- `1` - Domain invalid (no MX, disposable, blacklisted)
- `2` - Unknown (DNS timeout, etc.)

---

## Level 3: Mailbox Verification

**What it checks:**
- SMTP handshake
- Mailbox existence
- Catch-all detection
- Greylisting handling

**When to use:**
- High-value prospects only
- Before major campaigns
- When accuracy > speed

**⚠️ Warning:**
This level involves connecting to recipient mail servers. Use sparingly to avoid:
- IP reputation damage
- Rate limiting
- Being marked as spam probe

**Implementation notes:**

Not included in current scripts because:
1. Requires careful rate limiting
2. IP warmup considerations
3. Legal/compliance factors vary by jurisdiction

**For Thoven's use case:**
- Syntax + Domain verification is sufficient for initial outreach
- Monitor bounce rates to catch invalid mailboxes
- Use mailbox verification only for $1K+ LTV prospects

---

## Recommended Workflow

```
┌─────────────────┐
│ Extract Email   │ ← From bio, website, etc.
└────────┬────────┘
         ▼
┌─────────────────┐
│ Syntax Check    │ ← Reject obvious garbage
│ (Level 1)       │
└────────┬────────┘
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Has Suggestion? │────►│ Log for Review  │
└────────┬────────┘     └─────────────────┘
         │ No
         ▼
┌─────────────────┐
│ Domain Check    │ ← Verify MX, not disposable
│ (Level 2)       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Store with      │ ← Include verification level
│ Verification    │    in prospect record
└────────┬────────┘
         ▼
┌─────────────────┐
│ Pre-send:       │ ← Re-check domain blacklist
│ Re-validate     │    (domains can go bad)
└─────────────────┘
```

---

## Verification Confidence

| Level | Speed | Accuracy | Use For |
|-------|-------|----------|---------|
| Syntax | Instant | 70% | Initial filtering |
| Domain | ~100ms | 90% | Pre-send validation |
| Mailbox | 1-5s | 95%+ | High-value targets only |

---

## Storage Recommendations

Store verification data with prospects:

```json
{
  "email": "prospect@example.com",
  "verification": {
    "syntax_valid": true,
    "syntax_checked": "2024-01-15T10:30:00Z",
    "domain_valid": true,
    "mx_records": ["mail.example.com"],
    "disposable": false,
    "domain_checked": "2024-01-15T10:30:01Z",
    "level": "domain"
  }
}
```

Re-check domain validity before sending if >30 days old.
