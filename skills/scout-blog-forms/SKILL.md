---
name: scout-blog-forms
description: |
  Auto-fill blog contact forms for mom/homeschool blogs.
  Use when: Submitting partnership inquiries via blog contact forms.
  Triggers on: "blog form", "contact form", "submit inquiry".
---

# Scout Blog Forms

Auto-fill and submit blog contact forms for partnership inquiries.

## Workflow

**Find → Fill → Submit → Track**

### Step 1: Find Pending Blogs

Query blogs with status = "pending" from `scout_data.json`.

### Step 2: Research Blog

Before submitting:
- Read 2-3 recent posts to understand content and audience
- Note author's name, topics, city/region
- Check for media kit, partnerships page, "work with me" page

### Step 3: Fill Contact Form

Fields to use:
- **Name:** Keri Erten
- **Email:** keri@agentmail.to
- **Subject:** "Partnership opportunity — music education for your readers"
- **Message:** Use template from skill-drafting, personalized with reference to specific post read

### Step 4: Submit Form

Use browser automation:
```python
# Attempt form submission
# If success → Mark "auto_submitted"
# If CAPTCHA/login wall → Mark "manual_needed"
# If fail → Retry max 2 times
```

### Step 5: Track Result

Update blog status in `scout_data.json`:

| Status | Meaning |
|:---|:---|
| `auto_submitted` | Form submitted automatically |
| `manual_needed` | CAPTCHA/login wall — needs human |
| `failed` | Submission failed after retries |

## Retry Logic

```
Attempt 1: Standard form fill
  ↓ Success? → Mark auto_submitted
  ↓ CAPTCHA? → Mark manual_needed
  ↓ Error? → Retry

Attempt 2: Alternative approach (different fields, slower timing)
  ↓ Success? → Mark auto_submitted
  ↓ CAPTCHA? → Mark manual_needed
  ↓ Error? → Retry

Attempt 3: Last attempt
  ↓ Success? → Mark auto_submitted
  ↓ Any issue → Mark manual_needed (don't escalate further)
```

## Manual Form Queue

Blogs marked `manual_needed` appear in Morning Batch:
```
📝 MANUAL FORM: [Blog name] | [URL] | [Pre-written message]
```

Andres fills manually in 30 seconds, clicks submit.

## Follow-Up

If no reply in 7 days:
1. Search for alternate contact (email or social)
2. Try different channel
3. Log result to playbook

## KEY LEARNINGS (max 5)

1. **CAPTCHA detection** — Stop immediately, don't waste retries
2. **Field mapping** — Most forms use standard names: name, email, subject, message
3. **Timing matters** — Don't submit too fast (looks like bot)
4. **Personalization** — Reference specific post increases response rate
5. **7-day follow-up** — Blogs respond slower than influencers
