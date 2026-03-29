#!/usr/bin/env python3
"""
Schedule next follow-up for Thoven prospects.
Updates prospect record with next_followup_date and increments followup_count.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Follow-up schedule mapping
FOLLOWUP_SCHEDULE = {
    0: {"next_day": 3, "label": "first"},
    1: {"next_day": 7, "label": "second"},
    2: {"next_day": 14, "label": "third"},
    3: {"next_day": None, "label": None}  # Max reached
}


def calculate_next_followup(current_count: int, from_date: datetime = None) -> dict:
    """
    Calculate next follow-up date based on current count.
    
    Args:
        current_count: Number of follow-ups already sent (0-3)
        from_date: Date to calculate from (defaults to today)
    
    Returns:
        Dict with next_followup_date, days_until, followup_number
    """
    if from_date is None:
        from_date = datetime.now()
    
    schedule = FOLLOWUP_SCHEDULE.get(current_count, FOLLOWUP_SCHEDULE[3])
    next_day = schedule["next_day"]
    label = schedule["label"]
    
    if next_day is None:
        return {
            "next_followup_date": None,
            "days_until": None,
            "followup_number": 3,
            "is_final": True,
            "message": "Maximum follow-ups reached (3). Consider moving to 'Declined' or manual follow-up."
        }
    
    next_date = from_date + timedelta(days=next_day)
    
    return {
        "next_followup_date": next_date.strftime("%Y-%m-%d"),
        "days_until": next_day,
        "followup_number": current_count + 1,
        "is_final": current_count + 1 >= 3,
        "label": label,
        "message": f"{label.capitalize()} follow-up scheduled for {next_date.strftime('%Y-%m-%d')}"
    }


def load_prospects(filepath: str) -> list:
    """Load prospects from CSV or JSON file."""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Prospects file not found: {filepath}")
    
    if path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get('prospects', [])
    
    elif path.suffix.lower() == '.csv':
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .json")


def save_prospects(prospects: list, filepath: str):
    """Save prospects back to file."""
    path = Path(filepath)
    
    if path.suffix.lower() == '.json':
        with open(path, 'w') as f:
            json.dump(prospects, f, indent=2)
    
    elif path.suffix.lower() == '.csv':
        if not prospects:
            return
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=prospects[0].keys())
            writer.writeheader()
            writer.writerows(prospects)


def find_prospect(prospects: list, prospect_id: str = None, email: str = None, name: str = None) -> tuple:
    """
    Find prospect by ID, email, or name.
    Returns (index, prospect) tuple or (None, None) if not found.
    """
    for i, prospect in enumerate(prospects):
        if prospect_id and prospect.get('id') == prospect_id:
            return i, prospect
        if email and prospect.get('email') == email:
            return i, prospect
        if name and prospect.get('name') == name:
            return i, prospect
    return None, None


def update_prospect(prospect: dict, current_day: int = None, custom_date: str = None, dry_run: bool = False) -> dict:
    """
    Update prospect with next follow-up date.
    
    Args:
        prospect: Prospect dict to update
        current_day: Current follow-up day (3, 7, 14) to determine next
        custom_date: Custom next follow-up date (YYYY-MM-DD)
        dry_run: If True, don't actually modify
    
    Returns:
        Dict with update result
    """
    current_count = int(prospect.get('followup_count', 0))
    
    # If custom date provided, use it
    if custom_date:
        next_date = custom_date
        new_count = current_count + 1
        result = {
            "next_followup_date": next_date,
            "days_until": None,
            "followup_number": new_count,
            "is_final": new_count >= 3,
            "label": "custom",
            "message": f"Custom follow-up scheduled for {next_date}"
        }
    else:
        # Calculate based on schedule
        result = calculate_next_followup(current_count)
    
    # Apply updates
    if not dry_run:
        prospect['followup_count'] = str(result['followup_number'])
        prospect['next_followup_date'] = result['next_followup_date']
        prospect['last_followup_date'] = datetime.now().strftime("%Y-%m-%d")
    
    return result


def format_output(result: dict, prospect: dict, dry_run: bool = False) -> str:
    """Format schedule result for output."""
    status = "[DRY RUN] " if dry_run else ""
    
    lines = [
        f"\n{status}Follow-up Scheduled",
        f"Prospect: {prospect.get('name', 'Unknown')}",
        f"Contact: {prospect.get('contact_name', 'N/A')}",
        "",
        f"Previous count: {int(prospect.get('followup_count', 0)) - 1 if not dry_run else prospect.get('followup_count', 0)}",
        f"New count: {result['followup_number']}",
        f"Next follow-up: {result['next_followup_date']}",
    ]
    
    if result['days_until']:
        lines.append(f"Days until: {result['days_until']}")
    
    lines.extend([
        f"Final follow-up: {'Yes' if result['is_final'] else 'No'}",
        "",
        f"Status: {result['message']}"
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Schedule next follow-up for Thoven prospects"
    )
    parser.add_argument(
        '--prospects', '-p',
        required=True,
        help='Path to prospects file (CSV or JSON)'
    )
    parser.add_argument(
        '--prospect-id', '-i',
        help='Prospect ID to update'
    )
    parser.add_argument(
        '--email', '-e',
        help='Prospect email to find and update'
    )
    parser.add_argument(
        '--name', '-n',
        help='Prospect name to find and update'
    )
    parser.add_argument(
        '--current-day', '-d',
        type=int,
        choices=[3, 7, 14],
        help='Current follow-up day (to determine next)'
    )
    parser.add_argument(
        '--custom-date', '-c',
        help='Custom next follow-up date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying file'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Validate args
    if not any([args.prospect_id, args.email, args.name]):
        print("Error: Must provide --prospect-id, --email, or --name", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load prospects
        prospects = load_prospects(args.prospects)
        
        # Find prospect
        idx, prospect = find_prospect(prospects, args.prospect_id, args.email, args.name)
        
        if idx is None:
            print(f"Error: Prospect not found", file=sys.stderr)
            sys.exit(1)
        
        # Update prospect
        result = update_prospect(prospect, args.current_day, args.custom_date, args.dry_run)
        
        # Save if not dry run
        if not args.dry_run:
            save_prospects(prospects, args.prospects)
        
        # Output result
        if args.format == 'json':
            output = {
                "prospect": prospect,
                "schedule": result,
                "dry_run": args.dry_run
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_output(result, prospect, args.dry_run))
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
