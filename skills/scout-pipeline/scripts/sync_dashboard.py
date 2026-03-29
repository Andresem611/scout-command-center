#!/usr/bin/env python3
"""
Sync dashboard data — validate records and ensure consistency.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_FIELDS = ["id", "name", "stage", "city", "branch"]
VALID_STAGES = ["Prospected", "Contacted", "Replied", "Negotiating", "Partner", "Declined"]


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


def validate_prospect(prospect: dict, index: int) -> list[str]:
    """Validate a prospect record. Returns list of errors."""
    errors = []
    prospect_id = prospect.get("id", f"<index:{index}>")
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in prospect or prospect[field] is None:
            errors.append(f"{prospect_id}: Missing required field '{field}'")
    
    # Validate stage
    stage = prospect.get("stage")
    if stage and stage not in VALID_STAGES:
        errors.append(f"{prospect_id}: Invalid stage '{stage}'")
    
    # Validate ID format (alphanumeric, hyphens, underscores)
    pid = prospect.get("id")
    if pid and not all(c.isalnum() or c in "-_" for c in str(pid)):
        errors.append(f"{prospect_id}: Invalid ID format")
    
    return errors


def ensure_computed_fields(prospect: dict) -> bool:
    """Ensure computed fields exist. Returns True if modified."""
    modified = False
    
    # Ensure timestamps exist
    if "created_at" not in prospect:
        prospect["created_at"] = datetime.now(timezone.utc).isoformat()
        modified = True
    
    if "updated_at" not in prospect:
        prospect["updated_at"] = prospect["created_at"]
        modified = True
    
    # Ensure days_in_stage exists
    if "days_in_stage" not in prospect:
        prospect["days_in_stage"] = 0
        modified = True
    
    return modified


def check_duplicate_ids(prospects: list) -> list[str]:
    """Check for duplicate prospect IDs."""
    errors = []
    seen = {}
    
    for p in prospects:
        pid = p.get("id")
        if pid:
            if pid in seen:
                errors.append(f"Duplicate ID '{pid}' at indices {seen[pid]} and {prospects.index(p)}")
            else:
                seen[pid] = prospects.index(p)
    
    return errors


def main():
    parser = argparse.ArgumentParser(description="Sync dashboard data")
    parser.add_argument("--data-path", type=Path, default=Path("data/scout_data.json"),
                        help="Path to scout_data.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate without saving changes")
    
    args = parser.parse_args()
    
    data = load_data(args.data_path)
    prospects = data.get("prospects", [])
    
    all_errors = []
    modified_count = 0
    
    print(f"Validating {len(prospects)} prospects...\n")
    
    # Check duplicates
    dup_errors = check_duplicate_ids(prospects)
    all_errors.extend(dup_errors)
    
    # Validate each prospect
    for i, prospect in enumerate(prospects):
        errors = validate_prospect(prospect, i)
        all_errors.extend(errors)
        
        if ensure_computed_fields(prospect):
            modified_count += 1
    
    # Report results
    if all_errors:
        print("ERRORS FOUND:")
        for err in all_errors:
            print(f"  ✗ {err}")
        print()
    
    if modified_count:
        print(f"Fixed {modified_count} records (added missing computed fields)")
    
    if not all_errors and modified_count == 0:
        print("✓ All records valid. No changes needed.")
    elif not all_errors:
        print(f"✓ Validation passed with {modified_count} auto-fixes")
        if not args.dry_run:
            save_data(args.data_path, data)
            print(f"✓ Saved changes to {args.data_path}")
        else:
            print("(Dry run — no changes saved)")
    else:
        print(f"✗ Validation failed with {len(all_errors)} error(s)")
        sys.exit(1)
    
    # Summary stats
    print(f"\n--- Summary ---")
    print(f"Total prospects: {len(prospects)}")
    stages = {}
    for p in prospects:
        stage = p.get("stage", "Unknown")
        stages[stage] = stages.get(stage, 0) + 1
    for stage, count in sorted(stages.items()):
        print(f"  {stage}: {count}")


if __name__ == "__main__":
    main()
