#!/usr/bin/env python3
"""
Update a prospect's stage with validation and logging.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Stage transition rules: current_stage -> [allowed_next_stages]
TRANSITIONS = {
    "Prospected": ["Contacted"],
    "Contacted": ["Replied", "Declined"],
    "Replied": ["Negotiating", "Declined"],
    "Negotiating": ["Partner", "Declined"],
    "Partner": [],
    "Declined": [],
}

ALL_STAGES = set(TRANSITIONS.keys())


def load_data(data_path: Path) -> dict:
    """Load scout_data.json."""
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)
    
    with open(data_path, "r") as f:
        return json.load(f)


def save_data(data_path: Path, data: dict) -> None:
    """Save scout_data.json."""
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)


def log_transition(log_path: Path, prospect_id: str, old_stage: str, new_stage: str) -> None:
    """Append transition to log file."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_entry = f"{timestamp} | {prospect_id}: {old_stage} -> {new_stage}\n"
    
    with open(log_path, "a") as f:
        f.write(log_entry)


def validate_transition(current_stage: str, new_stage: str) -> tuple[bool, str]:
    """Check if transition is allowed. Returns (is_valid, error_message)."""
    if current_stage not in ALL_STAGES:
        return False, f"Invalid current stage: {current_stage}"
    
    if new_stage not in ALL_STAGES:
        return False, f"Invalid target stage: {new_stage}. Valid stages: {', '.join(ALL_STAGES)}"
    
    allowed = TRANSITIONS.get(current_stage, [])
    if new_stage not in allowed:
        return False, f"Invalid transition: {current_stage} -> {new_stage}. Allowed: {', '.join(allowed) or 'none'}"
    
    return True, ""


def find_prospect(data: dict, prospect_id: str) -> dict | None:
    """Find prospect by ID in data."""
    for prospect in data.get("prospects", []):
        if prospect.get("id") == prospect_id:
            return prospect
    return None


def main():
    parser = argparse.ArgumentParser(description="Update prospect stage")
    parser.add_argument("prospect_id", help="Prospect ID")
    parser.add_argument("new_stage", help="New stage name")
    parser.add_argument("--data-path", type=Path, default=Path("data/scout_data.json"),
                        help="Path to scout_data.json")
    
    args = parser.parse_args()
    
    # Determine log path (same directory as data file)
    log_path = args.data_path.parent / "transitions.log"
    
    # Load data
    data = load_data(args.data_path)
    
    # Find prospect
    prospect = find_prospect(data, args.prospect_id)
    if not prospect:
        print(f"Error: Prospect '{args.prospect_id}' not found")
        sys.exit(1)
    
    current_stage = prospect.get("stage", "Prospected")
    
    # Skip if no change
    if current_stage == args.new_stage:
        print(f"No change needed: {args.prospect_id} already at {current_stage}")
        sys.exit(0)
    
    # Validate transition
    is_valid, error = validate_transition(current_stage, args.new_stage)
    if not is_valid:
        print(f"Error: {error}")
        sys.exit(1)
    
    # Update stage
    prospect["stage"] = args.new_stage
    prospect["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Save data
    save_data(args.data_path, data)
    
    # Log transition
    log_transition(log_path, args.prospect_id, current_stage, args.new_stage)
    
    print(f"✓ Updated {args.prospect_id}: {current_stage} -> {args.new_stage}")


if __name__ == "__main__":
    main()
