#!/usr/bin/env python3
"""
Generate follow-up messages for Thoven prospects.
Supports Day 3 (gentle bump), Day 7 (value-add), and Day 14 (soft close) messages.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# Message templates by day
TEMPLATES = {
    3: {
        "name": "Gentle Bump",
        "goal": "Get a response without being pushy",
        "tone": "Light, assumptive",
        "subject": "Quick follow-up",
        "template": """Hi {contact_name},

Just bumping this to the top of your inbox — know things get busy on the studio side.

Worth a 10-minute chat to see if Thoven could bring you a few extra students per month?

{signature}"""
    },
    7: {
        "name": "Value-Add",
        "goal": "Provide new angle/value proposition",
        "tone": "Helpful, different insight",
        "subject": "A different angle on student acquisition",
        "template": """Hi {contact_name},

Quick thought: instead of competing with online lesson platforms, Thoven partners with them to fill your local slots.

We're already working with {example_school} in {example_city} — they've seen {result} since joining.

Worth a brief call to explore if it fits {studio_name}?

{signature}"""
    },
    14: {
        "name": "Soft Close",
        "goal": "Final attempt, direct but respectful",
        "tone": "Direct, respectful",
        "subject": "Should I close the loop?",
        "template": """Hi {contact_name},

I'll be direct: I've reached out a couple times and don't want to clutter your inbox if now's not the right time.

If Thoven's student-matching model isn't a priority for {studio_name} currently, totally get it — just say the word and I'll close the loop.

If it *is* interesting, I'm here: {calendar_link}

{signature}"""
    }
}


# Thoven signature block
DEFAULT_SIGNATURE = """Best,
Andres Martinez
CEO, Thoven (thoven.com)
—
Music education marketplace connecting teachers with motivated students"""


def get_template(day: int) -> dict:
    """Get template for specific follow-up day."""
    if day not in TEMPLATES:
        raise ValueError(f"Invalid follow-up day: {day}. Must be 3, 7, or 14.")
    return TEMPLATES[day]


def generate_message(day: int, prospect: dict, custom_vars: dict = None) -> dict:
    """
    Generate follow-up message for a prospect.
    
    Args:
        day: Follow-up day (3, 7, or 14)
        prospect: Dict with prospect details
        custom_vars: Optional custom variables for template
    
    Returns:
        Dict with message components
    """
    template = get_template(day)
    
    # Build variable substitution map
    vars_map = {
        "contact_name": prospect.get("contact_name", "there").split()[0] if prospect.get("contact_name") else "there",
        "studio_name": prospect.get("name", "your studio"),
        "signature": DEFAULT_SIGNATURE,
        # For Day 7 template
        "example_school": custom_vars.get("example_school", "a local music school") if custom_vars else "a local music school",
        "example_city": custom_vars.get("example_city", "your area") if custom_vars else "your area",
        "result": custom_vars.get("result", "solid enrollment growth") if custom_vars else "solid enrollment growth",
        # For Day 14 template
        "calendar_link": custom_vars.get("calendar_link", "reply here and we'll find a time") if custom_vars else "reply here and we'll find a time"
    }
    
    # Generate message body
    body = template["template"].format(**vars_map)
    
    return {
        "day": day,
        "type": template["name"],
        "goal": template["goal"],
        "tone": template["tone"],
        "to": prospect.get("email", ""),
        "subject": template["subject"],
        "body": body,
        "thread_id": prospect.get("thread_id", ""),
        "prospect_id": prospect.get("id", ""),
        "prospect_name": prospect.get("name", ""),
        "generated_at": datetime.now().isoformat()
    }


def generate_preview(day: int) -> dict:
    """Generate a preview/example message without specific prospect data."""
    example_prospect = {
        "contact_name": "Sarah",
        "name": "Harmony Music Academy",
        "email": "sarah@harmonymusic.com",
        "id": "example-id",
        "thread_id": "thread-123"
    }
    
    example_vars = {
        "example_school": "Melody Lane Studios",
        "example_city": "Austin",
        "result": "3 new students in their first month",
        "calendar_link": "calendly.com/andres-thoven"
    }
    
    return generate_message(day, example_prospect, example_vars)


def format_output(message: dict, format_type: str = 'text') -> str:
    """Format message for output."""
    if format_type == 'json':
        return json.dumps(message, indent=2)
    
    if format_type == 'email':
        # Format as ready-to-send email
        return f"""To: {message['to']}
Subject: {message['subject']}
Thread-ID: {message['thread_id']}

{message['body']}"""
    
    # Default text format
    lines = [
        f"\n=== {message['type']} (Day {message['day']}) ===",
        f"Goal: {message['goal']}",
        f"Tone: {message['tone']}",
        f"Prospect: {message['prospect_name']}",
        f"Thread ID: {message['thread_id']}",
        "",
        f"Subject: {message['subject']}",
        "",
        "--- Message Body ---",
        message['body'],
        "--- End ---"
    ]
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate follow-up messages for Thoven prospects"
    )
    parser.add_argument(
        '--day', '-d',
        type=int,
        required=True,
        choices=[3, 7, 14],
        help='Follow-up day (3, 7, or 14)'
    )
    parser.add_argument(
        '--prospect', '-p',
        help='Prospect name (for context)'
    )
    parser.add_argument(
        '--contact-name',
        help='Contact person name'
    )
    parser.add_argument(
        '--email',
        help='Contact email'
    )
    parser.add_argument(
        '--thread-id', '-t',
        help='Thread reference ID for continuity'
    )
    parser.add_argument(
        '--prospect-file',
        help='Path to prospect JSON file'
    )
    parser.add_argument(
        '--vars', '-v',
        help='JSON string of custom template variables'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'email'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Show example message without specific prospect'
    )
    
    args = parser.parse_args()
    
    try:
        if args.preview:
            # Generate preview/example
            message = generate_preview(args.day)
            print(format_output(message, args.format))
            return
        
        # Build prospect dict from args or file
        if args.prospect_file:
            with open(args.prospect_file, 'r') as f:
                prospect = json.load(f)
        else:
            prospect = {
                "id": "manual",
                "name": args.prospect or "Unknown Studio",
                "contact_name": args.contact_name or "there",
                "email": args.email or "",
                "thread_id": args.thread_id or ""
            }
        
        # Parse custom variables
        custom_vars = None
        if args.vars:
            custom_vars = json.loads(args.vars)
        
        # Generate message
        message = generate_message(args.day, prospect, custom_vars)
        
        # Output
        print(format_output(message, args.format))
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
