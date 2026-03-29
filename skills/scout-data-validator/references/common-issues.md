# Common Data Issues and Fixes

Frequent problems encountered in Thoven prospect data and their solutions.

## Issue Categories

### 1. Data Entry Errors

#### Trailing Whitespace
**Problem**: Names and emails with leading/trailing spaces
```json
{ "name": "  Sarah Johnson  ", "email": "sarah@example.com " }
```
**Fix**: Auto-trim all string fields
**Script**: `fix_common.py --trim-whitespace`

#### Email Case Issues
**Problem**: Mixed-case emails
```json
{ "email": "Sarah@Example.COM" }
```
**Fix**: Lowercase all emails
**Script**: `fix_common.py --lowercase-emails`

#### Name Capitalization
**Problem**: All lowercase or uppercase names
```json
{ "name": "sarah johnson" }
{ "name": "SARAH JOHNSON" }
```
**Fix**: Manual review - too risky to auto-capitalize
**Action**: Flag for human review

---

### 2. Stage Name Issues

#### Non-Standard Stages
**Problem**: Typos or variations in stage names
```json
{ "stage": "contact" }
{ "stage": "reached out" }
{ "stage": "Replied" }
{ "stage": "INTERESTED" }
```
**Fix**: Map to canonical stage names
**Script**: `fix_common.py` (built-in mappings)

#### Common Mappings
| Incorrect | Correct |
|-----------|---------|
| `contact` | `contacted` |
| `reached out` | `contacted` |
| `emailed` | `contacted` |
| `reply` | `responded` |
| `replied` | `responded` |
| `interest` | `interested` |
| `meeting` | `meeting_scheduled` |
| `signed up` | `onboarded` |
| `pass` | `declined` |
| `no response` | `no_response` |
| `ghosted` | `no_response` |

---

### 3. Duplicate Records

#### Same Email, Different Names
**Problem**: One person entered multiple times with name variations
```json
[
  { "email": "sarah@example.com", "name": "Sarah Johnson" },
  { "email": "sarah@example.com", "name": "Sarah J." }
]
```
**Fix**: Merge records or mark as duplicate
**Script**: `check_duplicates.py`
**Action**: Manual merge required

#### Similar Names, Same Domain
**Problem**: Possible duplicates with slightly different emails
```json
[
  { "email": "sarah@example.com", "name": "Sarah Johnson" },
  { "email": "s.johnson@example.com", "name": "Sarah Johnson" }
]
```
**Fix**: Review for same person
**Script**: `check_duplicates.py` (similarity > 0.85)
**Action**: Flag for review

---

### 4. Stale Data

#### No Updates > 30 Days
**Problem**: Record hasn't been touched in over a month
**Criteria**: `updated_at` > 30 days ago
**Fix**: Review and update or archive
**Script**: `check_stale.py`

#### Contacted, No Reply > 14 Days
**Problem**: Outreach sent but no response
**Criteria**: 
- `stage` in `[contacted, responded, interested]`
- `last_contact_at` > 14 days ago
- `last_reply_at` is null
**Fix**: Send follow-up or move to `no_response`
**Script**: `check_stale.py`

#### New, Never Contacted > 14 Days
**Problem**: Prospect sitting untouched
**Criteria**:
- `stage` = `new`
- `created_at` > 14 days ago
**Fix**: Contact or remove
**Script**: `check_stale.py`

---

### 5. Missing Data

#### Required Fields Missing
**Problem**: Missing `id`, `name`, `email`, `stage`, `source`, `created_at`, or `updated_at`
**Fix**: Cannot auto-fix - requires data entry
**Script**: `validate_schema.py`
**Action**: Add missing data or delete record

#### Optional Defaults Applied
**Problem**: Optional fields missing
**Fix**: Auto-fill defaults
| Field | Default |
|-------|---------|
| `country` | `"US"` |
| `tags` | `[]` |
| `notes` | `""` |
| `followers` | `0` |

**Script**: `fix_common.py`

---

### 6. Format Issues

#### Instagram Handle
**Problem**: Various formats for Instagram handle
```json
{ "instagram": "@sarah.teaches" }
{ "instagram": "https://instagram.com/sarah.teaches" }
{ "instagram": "sarah.teaches/" }
```
**Fix**: Extract username only
**Result**: `"sarah.teaches"`
**Script**: `fix_common.py`

#### Website URL
**Problem**: Missing protocol
```json
{ "website": "sarahjohnson.com" }
```
**Fix**: Add `https://` prefix
**Result**: `"https://sarahjohnson.com"`
**Script**: `fix_common.py`

#### Phone Numbers
**Problem**: Various phone formats
```json
{ "phone": "(512) 555-1234" }
{ "phone": "512.555.1234" }
{ "phone": "+1 512-555-1234" }
```
**Fix**: Store digits only
**Result**: `"5125551234"` or `"+15125551234"`
**Script**: `fix_common.py`

#### Follower Count
**Problem**: String with suffix
```json
{ "followers": "12.5k" }
{ "followers": "1.2M" }
{ "followers": "12,500" }
```
**Fix**: Parse to number
**Result**: `12500`, `1200000`, `12500`
**Script**: `fix_common.py`

---

### 7. Data Integrity Issues

#### Invalid Email
**Problem**: Malformed email addresses
```json
{ "email": "sarah@example" }
{ "email": "sarah@.com" }
{ "email": "not an email" }
```
**Fix**: Cannot auto-fix - flag for review
**Script**: `validate_schema.py`

#### Invalid Stage
**Problem**: Stage not in valid enum
```json
{ "stage": "thinking about it" }
```
**Fix**: Map to closest valid stage or flag
**Script**: `validate_schema.py`

#### Invalid Source
**Problem**: Source not in valid enum
```json
{ "source": "linkedin" }
```
**Fix**: Map to `other` or flag
**Script**: `validate_schema.py`

#### Invalid Dates
**Problem**: Non-ISO 8601 dates
```json
{ "created_at": "01/15/2024" }
{ "created_at": "Jan 15, 2024" }
```
**Fix**: Parse and reformat
**Script**: Manual conversion required

---

## Quick Fix Commands

### Run All Fixes
```bash
python3 scripts/fix_common.py
```

### Dry Run (Preview Changes)
```bash
python3 scripts/fix_common.py --dry-run
```

### Full Validation Pipeline
```bash
# 1. Fix common issues
python3 scripts/fix_common.py

# 2. Validate schema
python3 scripts/validate_schema.py

# 3. Check for duplicates
python3 scripts/check_duplicates.py

# 4. Find stale records
python3 scripts/check_stale.py
```

## Exit Codes Reference

| Code | Meaning |
|------|---------|
| 0 | Success / No issues |
| 1 | Schema validation errors |
| 2 | Duplicates found |
| 3 | Stale records found |
| 4 | File not found |
| 5 | Schema definition missing |
