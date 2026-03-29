# Disposable Email Domains

This list contains known disposable/temporary email providers that should be rejected in Thoven's outreach pipeline.

## Why Block Disposable Emails?

- **Low engagement** - Users don't check these inboxes
- **High bounce rates** - Domains get shut down frequently
- **Fake prospects** - Indicates low intent
- **Wasted sends** - Costs money, hurts sender reputation

---

## Full Block List

### Major Temporary Mail Services

```
tempmail.com
temp-mail.org
fakeemail.com
throwaway.com
mailinator.com
guerrillamail.com
sharklasers.com
spam4.me
trashmail.com
yopmail.com
yopmail.fr
yopmail.net
jetable.org
mailnesia.com
tempinbox.com
mailcatch.com
tempmailaddress.com
burnermail.io
tempmail.ninja
temp-mail.io
fakemail.net
mail-temp.com
disposable-email.com
mailforspam.com
tempail.com
tempmailbox.com
getairmail.com
```

### 10-Minute Email Services

```
10minutemail.com
10minutemail.net
10minemail.com
tempmailo.com
tempmails.com
temp-mail.ru
```

### Throwaway Variants

```
discard.email
discardmail.com
throwawaymail.com
tempm.com
tmpmail.org
mailtemp.com
```

### High-Risk Free Providers

These providers are frequently used for fake signups:

```
mail.ru
inbox.ru
list.ru
bk.ru
```

---

## Detection Patterns

Beyond exact matches, flag emails matching these patterns:

| Pattern | Example | Action |
|---------|---------|--------|
| `temp*` prefix | temp-john@gmail.com | Review |
| `*mail*` + numbers | johnmail123@yahoo.com | Accept (common legit pattern) |
| Domain with `temp`, `fake`, `trash` | john@tempmail.com | Block |
| Subdomain on disposable | john@sub.mailinator.com | Block |

---

## Adding New Domains

When you encounter new disposable domains:

1. **Verify it's disposable:**
   - Visit the domain
   - Check if it generates temporary addresses
   - Look for "temporary", "disposable", "10 minute" language

2. **Add to this list:**
   - Add to `DISPOSABLE_DOMAINS` in `scripts/verify_domain.py`
   - Document the source/date in comments

3. **Update prospect records:**
   - Re-scan existing prospects with the new domain
   - Flag or remove matches

---

## False Positives

Some legitimate domains may look disposable. Review before blocking:

| Domain | Status | Notes |
|--------|--------|-------|
| `protonmail.com` | ✅ Legit | Privacy-focused, not disposable |
| `tutanota.com` | ✅ Legit | Secure email, not disposable |
| `hey.com` | ✅ Legit | Paid service |
| `fastmail.com` | ✅ Legit | Paid service |

---

## Automation

The `verify_domain.py` script checks against this list automatically:

```python
# Direct domain match
if domain in DISPOSABLE_DOMAINS:
    return True, f"Known disposable: {domain}"

# Subdomain match
if parent_domain in DISPOSABLE_DOMAINS:
    return True, f"Disposable subdomain of {parent_domain}"
```

---

## Related Files

- `scripts/verify_domain.py` - Disposable checking implementation
- `references/blacklist.json` - Runtime blacklist (auto-generated)
- `scripts/update_blacklist.py` - Bounce tracking

---

*Last updated: 2024-01*
*Source: Aggregated from public disposable email lists + Thoven bounce data*
