#!/usr/bin/env python3
"""
Check due follow-ups for Thoven prospects.
Scans prospects with stage=Contacted and identifies who needs follow-up based on Day 3/7/14 cadence.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def calculate_followup_days(contact_date: str, today: datetime = None) -> dict:
    """
    Calculate days since contact and determine if follow-up is due.
    
    Returns dict with:
        - days_since_contact: int
        - followup_due: bool
        - followup_day: int (3, 7, 14, or None)
        - days_overdue: int
    """
    if today is None:
        today = datetime.now()
    
    contact = datetime.strptime(contact_date, "%Y-%m-%d")
    days_since = (today - contact).days
    
    # Define follow-up schedule
    followup_days = [3, 7, 14]
    
    # Find which follow-up should have been sent
    due_day = None
    for day in followup_days:
        if days_since >= day:
            due_day = day
    
    return {
        "days_since_contact": days_since,
        "followup_due": due_day is not None,
        "followup_day": due_day,
        "days_overdue": days_since - due_day if due_day else 0
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


def filter_due_followups(prospects: list, today: datetime = None) -> list:
    """
    Filter prospects that need follow-up today.
    
    Criteria:
    - stage == "Contacted"
    - next_followup_date <= today (or missing, calculate from contact_date)
    - followup_count < 3 (max 3 follow-ups)
    """
    if today is None:
        today = datetime.now()
    
    due_prospects = []
    
    for prospect in prospects:
        # Only check prospects in "Contacted" stage
        if prospect.get('stage') != 'Contacted':
            continue
        
        # Skip if already sent 3 follow-ups
        followup_count = int(prospect.get('followup_count', 0))
        if followup_count >= 3:
            continue
        
        # Check if next_followup_date is due
        next_followup = prospect.get('next_followup_date')
        if next_followup:
            next_date = datetime.strptime(next_followup, "%Y-%m-%d")
            if next_date > today:
                continue  # Not due yet
        
        # Calculate days since contact and determine follow-up day
        contact_date = prospect.get('contact_date')
        if not contact_date:
            continue
        
        calc = calculate_followup_days(contact_date, today)
        
        # Skip if less than 3 days since first contact
        if calc['days_since_contact'] < 3:
            continue
        
        # Determine which follow-up number this should be
        expected_followup = followup_count + 1
        followup_day_map = {1: 3, 2: 7, 3: 14}
        expected_day = followup_day_map.get(expected_followup)
        
        # Only include if we've passed the expected day for this follow-up
        if calc['days_since_contact'] >= expected_day:
            prospect_with_calc = {
                **prospect,
                'days_since_contact': calc['days_since_contact'],
                'followup_due_day': expected_day,
                'followup_number': expected_followup,
                'days_overdue': calc['days_since_contact'] - expected_day
            }
            due_prospects.append(prospect_with_calc)
    
    return due_prospects


def format_output(prospects: list, format_type: str = 'table') -> str:
    """Format output as table, json, or csv."""
    if format_type == 'json':
        return json.dumps(prospects, indent=2)
    
    if format_type == 'csv':
        if not prospects:
            return "No prospects due for follow-up"
        output = []
        writer = csv.DictWriter(sys.stdout, fieldnames=prospects[0].keys())
        writer.writeheader()
        writer.writerows(prospects)
        return ""
    
    # Default table format
    if not prospects:
        return "No prospects due for follow-up today."
    
    lines = [
        "\n=== Prospects Due for Follow-Up ===\n",
        f"{'Name':<30} {'Day':<5} {'Since':<6} {'Overdue':<8} {'Thread ID':<20} Notes",
        "-" * 100
    ]
    
    for p in prospects:
        name = p.get('name', 'Unknown')[:28]
        day = f"D{p.get('followup_due_day', '?')}"
        since = f"{p.get('days_since_contact', 0)}d"
        overdue = f"{p.get('days_overdue', 0)}d" if p.get('days_overdue', 0) > 0 else "-"
        thread = p.get('thread_id', 'N/A')[:18]
        notes = p.get('notes', '')[:30]
        
        lines.append(f"{name:<30} {day:<5} {since:<6} {overdue:<8} {thread:<20} {notes}")
    
    lines.append(f"\nTotal: {len(prospects)} prospect(s) need follow-up")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check which Thoven prospects need follow-up today"
    )
    parser.add_argument(
        '--prospects', '-p',
        required=True,
        help='Path to prospects file (CSV or JSON)'
    )
    parser.add_argument(
        '--date', '-d',
        help='Check date (YYYY-MM-DD), defaults to today'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'json', 'csv'],
        default='table',
        help='Output format'
    )
    parser.add_argument(
        '--stage',
        default='Contacted',
        help='Filter by stage (default: Contacted)'
    )
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        today = datetime.now()
    
    try:
        # Load prospects
        prospects = load_prospects(args.prospects)
        
        # Filter for due follow-ups
        due_prospects = filter_due_followups(prospects, today)
        
        # Output results
        print(format_output(due_prospects, args.format))
        
        # Exit with count for scripting
        sys.exit(len(due_prospects))
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
