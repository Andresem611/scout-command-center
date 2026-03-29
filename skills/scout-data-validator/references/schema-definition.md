# Prospect Schema Definition

Complete schema for Thoven prospect data stored in `scout_data.json`.

## File Format

- **Format**: JSON array of objects
- **Encoding**: UTF-8
- **Location**: `~/.openclaw/workspace/scout_data.json`

## Field Reference

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier (UUID or slug) | `"p_001"` |
| `name` | string | Full name of prospect | `"Sarah Johnson"` |
| `email` | string | Valid email address | `"sarah@example.com"` |
| `stage` | enum | Current pipeline stage | `"contacted"` |
| `source` | enum | Where the prospect was found | `"instagram"` |
| `created_at` | string (ISO 8601) | When record was created | `"2024-01-15T10:30:00Z"` |
| `updated_at` | string (ISO 8601) | When record was last updated | `"2024-01-20T14:22:00Z"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `email_domain` | string | Domain extracted from email | `"example.com"` |
| `phone` | string | Phone number (digits only) | `"5551234567"` |
| `city` | string | City name | `"Austin"` |
| `state` | string | State/Province code | `"TX"` |
| `country` | string | Country code (default: "US") | `"US"` |
| `tags` | array[string] | Tags/categories | `["mom-blogger", "piano"]` |
| `notes` | string | Free-form notes | `"Interested in group classes"` |
| `website` | string | Personal website URL | `"https://sarahjohnson.com"` |
| `instagram` | string | Instagram handle (no @) | `"sarah teaches"` |
| `followers` | number | Social media follower count | `12500` |
| `last_contact_at` | string (ISO 8601) or null | Last outreach sent | `"2024-01-18T09:00:00Z"` |
| `last_reply_at` | string (ISO 8601) or null | Last reply received | `"2024-01-18T15:30:00Z"` |

## Enum Values

### Source

Valid values for the `source` field:

| Value | Description |
|-------|-------------|
| `instagram` | Found via Instagram |
| `facebook` | Found via Facebook |
| `twitter` | Found via Twitter/X |
| `youtube` | Found via YouTube |
| `tiktok` | Found via TikTok |
| `referral` | Referred by existing teacher |
| `manual` | Added manually |
| `imported` | Bulk imported |
| `other` | Other source |

### Stage

Valid values for the `stage` field:

| Value | Description |
|-------|-------------|
| `new` | New prospect, no contact yet |
| `contacted` | Initial outreach sent |
| `responded` | Prospect replied |
| `interested` | Expressed interest |
| `meeting_scheduled` | Call/meeting scheduled |
| `onboarded` | Successfully onboarded as teacher |
| `declined` | Explicitly declined |
| `no_response` | No response after follow-up |
| `disqualified` | Not a good fit |

## Validation Rules

### Email Validation

- Must match pattern: `^[^\s@]+@[^\s@]+\.[^\s@]+$`
- Automatically lowercased
- Common typos flagged (e.g., `gmial.com` → `gmail.com`)

### Date Validation

- Must be valid ISO 8601 format
- Examples: `2024-01-15T10:30:00Z`, `2024-01-15T10:30:00-05:00`
- Timezone offset optional (Z = UTC)

### Phone Validation

- Stored as digits only (normalized)
- Keep country code if present: `+15551234567`
- Remove all non-numeric characters except `+`

### String Validation

- Trim leading/trailing whitespace
- Collapse multiple spaces to single space
- Empty strings allowed for optional fields

## Example Record

```json
{
  "id": "p_001",
  "name": "Sarah Johnson",
  "email": "sarah@example.com",
  "email_domain": "example.com",
  "phone": "5125551234",
  "city": "Austin",
  "state": "TX",
  "country": "US",
  "source": "instagram",
  "stage": "contacted",
  "tags": ["mom-blogger", "piano", "homeschool"],
  "notes": "Teaches piano to homeschool kids. Interested in expanding to group classes.",
  "website": "https://sarahjohnson.com",
  "instagram": "sarah.teaches",
  "followers": 12500,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:22:00Z",
  "last_contact_at": "2024-01-18T09:00:00Z",
  "last_reply_at": null
}
```

## Schema Version

- **Version**: 1.0.0
- **Last Updated**: 2024-03-30
