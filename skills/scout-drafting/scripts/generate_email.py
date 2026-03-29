#!/usr/bin/env python3
"""
Generate personalized email draft from prospect data and template.
Uses Thoven voice (Keri's warm, direct tone).
"""

import argparse
import json
import sys
import re
from datetime import datetime


# Load template from references
TEMPLATES = {
    "mom-influencer": """Subject: Quick question about %CONTENT_TOPIC%

Hi %NAME%,

I just saw your post about %CONTENT_TOPIC% — %CONTENT_HOOK_REF%

I'm Keri from Thoven, a music education platform designed for busy parents like you. We've built something that helps kids learn music without the scheduling nightmares or expensive private lessons.

%PERSONALIZATION_BLOCK%

Would you be open to a quick chat about how this might resonate with your audience? No pitch, just curious if it solves a problem you're already hearing about.

Best,
Keri
Thoven | keri@thoven.co
""",

    "homeschool-influencer": """Subject: Music curriculum that actually works for homeschoolers

Hi %NAME%,

I've been following your homeschool journey — %CONTENT_HOOK_REF%

I'm Keri from Thoven. We built a music education platform specifically with homeschool families in mind: self-paced, parent-guided, and designed to fit into your rhythm (not fight against it).

%PERSONALIZATION_BLOCK%

Many homeschool parents tell us music is the one subject they feel least equipped to teach. We've solved that with bite-sized lessons kids can do independently.

Worth a conversation?

Keri
Thoven | keri@thoven.co
""",

    "music-teacher": """Subject: Partnership opportunity for independent teachers

Hi %NAME%,

%CONTENT_HOOK_REF%

I'm Keri from Thoven, a marketplace connecting music teachers with families looking for quality instruction. We're building something different — not a race-to-the-bottom gig platform, but a place where teachers set their rates and keep their autonomy.

%PERSONALIZATION_BLOCK%

I'd love to show you what we're building and see if there's a fit for someone with your background.

Available for a brief call this week?

Keri
Thoven | keri@thoven.co
""",

    "content-creator": """Subject: Collaboration idea

Hi %NAME%,

%CONTENT_HOOK_REF% — loved the authenticity.

I'm Keri from Thoven, a music education platform for families. We're looking to partner with creators who genuinely care about kids' development (not just content metrics).

%PERSONALIZATION_BLOCK%

Would you be open to exploring what a partnership might look like? We're flexible on structure.

Keri
Thoven | keri@thoven.co
"""
}


def load_template(template_name: str) -> str:
    """Load email template by name."""
    if template_name not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
    return TEMPLATES[template_name]


def generate_personalization_block(prospect: dict, research: dict) -> str:
    """Generate the dynamic personalization paragraph."""
    angles = research.get("personalization", {})
    
    # Build personalized content
    lines = []
    
    # Reference their location if available
    location = angles.get("family_details", {}).get("location")
    if location:
        lines.append(f"I noticed you're based in {location} — we're seeing great engagement from families in your area.")
    
    # Reference their values
    values = angles.get("values_alignment", [])
    if "education" in values and "creativity" in values:
        lines.append("Your focus on balancing structure with creative expression really resonates with how we approach music education.")
    elif "education" in values:
        lines.append("Your commitment to your children's education really comes through in your content.")
    elif "creativity" in values:
        lines.append("I love how you prioritize creative development — that's exactly what we're trying to nurture.")
    
    # Reference pain points
    pain_points = angles.get("pain_points", [])
    if "busy_schedule" in pain_points:
        lines.append("We designed Thoven specifically for busy families — lessons that fit into 15-minute windows, not hour-long commitments.")
    if "screen_time_concerns" in pain_points:
        lines.append("And unlike most 'educational' apps, our approach minimizes screen time while maximizing actual music-making.")
    
    if not lines:
        lines.append("I think what we're building could be a genuine resource for your community.")
    
    return "\n\n".join(lines)


def fill_template(template: str, prospect: dict, research: dict) -> str:
    """Fill template variables with prospect data."""
    result = template
    
    # Basic replacements
    result = result.replace("%NAME%", prospect.get("name", "").split()[0])
    result = result.replace("%FULL_NAME%", prospect.get("name", ""))
    
    # Content references
    content_refs = research.get("personalization", {}).get("content_references", [])
    if content_refs:
        top_content = content_refs[0]
        result = result.replace("%CONTENT_TOPIC%", top_content.get("topic", "your recent post"))
        hook = top_content.get("hook", "it really resonated")
        result = result.replace("%CONTENT_HOOK_REF%", hook)
    else:
        result = result.replace("%CONTENT_TOPIC%", "your content")
        result = result.replace("%CONTENT_HOOK_REF%", "it's clear you care deeply about your audience")
    
    # Personalization block
    pers_block = generate_personalization_block(prospect, research)
    result = result.replace("%PERSONALIZATION_BLOCK%", pers_block)
    
    # Location
    location = research.get("personalization", {}).get("family_details", {}).get("location")
    result = result.replace("%CITY%", location.split(",")[0] if location else "your area")
    result = result.replace("%LOCATION%", location or "your area")
    
    # Platform-specific
    result = result.replace("%PLATFORM%", prospect.get("platform", ""))
    result = result.replace("%HANDLE%", prospect.get("handle", ""))
    
    return result


def generate_email(prospect: dict, template_name: str, custom_notes: str = "") -> dict:
    """Generate complete email draft."""
    # Load or generate research
    research = prospect.get("research_notes", {})
    if not research:
        # Import and call research function
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "research_prospect", 
            "/root/.openclaw/workspace/skills/scout-drafting/scripts/research_prospect.py"
        )
        research_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(research_module)
        research = research_module.generate_research_notes(prospect)
    
    # Load and fill template
    template = load_template(template_name)
    body = fill_template(template, prospect, research)
    
    # Extract subject line
    subject_match = re.search(r'^Subject: (.+)$', body, re.MULTILINE)
    subject = subject_match.group(1) if subject_match else "Quick question"
    body = re.sub(r'^Subject: .+\n+', '', body, count=1)
    
    draft = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "template_used": template_name,
            "prospect_handle": prospect.get("handle", ""),
            "fit_score": research.get("fit_score", 0),
        },
        "email": {
            "to": prospect.get("email", f"{prospect.get('handle', '')}@{prospect.get('platform', 'email.com')}"),
            "from": "keri@thoven.co",
            "subject": subject,
            "body": body.strip(),
        },
        "research_summary": {
            "fit_score": research.get("fit_score", 0),
            "fit_reasons": research.get("fit_reasons", []),
            "recommendations": research.get("recommendations", []),
        },
        "flags": []
    }
    
    # Add flags based on fit score
    if draft["meta"]["fit_score"] < 50:
        draft["flags"].append("LOW_FIT: Prospect may not be ideal target")
    if not prospect.get("email"):
        draft["flags"].append("NO_EMAIL: Need to find contact method")
    if len(body) > 2000:
        draft["flags"].append("LONG_EMAIL: Consider trimming for readability")
    
    if custom_notes:
        draft["custom_notes"] = custom_notes
    
    return draft


def main():
    parser = argparse.ArgumentParser(description="Generate personalized email draft")
    parser.add_argument("--prospect", required=True, help="Path to prospect JSON file")
    parser.add_argument("--template", required=True, 
                       choices=["mom-influencer", "homeschool-influencer", "music-teacher", "content-creator"],
                       help="Email template to use")
    parser.add_argument("--notes", help="Custom notes to include")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    args = parser.parse_args()
    
    # Load prospect
    try:
        with open(args.prospect, 'r') as f:
            prospect = json.load(f)
    except FileNotFoundError:
        print(f"Error: Prospect file not found: {args.prospect}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate email
    try:
        draft = generate_email(prospect, args.template, args.notes or "")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output
    output = json.dumps(draft, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Draft written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
