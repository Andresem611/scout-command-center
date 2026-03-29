#!/usr/bin/env python3
"""
Auto-fix common data issues in scout_data.json.
Fixes: trim whitespace, lowercase emails, standardize stage names, fill missing defaults.
"""

import json
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Stage name mappings (common typos/variants -> canonical)
STAGE_MAPPINGS = {
    # Variants
    "new prospect": "new",
    "new lead": "new",
    "lead": "new",
    
    "contact": "contacted",
    "reached out": "contacted",
    "emailed": "contacted",
    "messaged": "contacted",
    
    "reply": "responded",
    "replied": "responded",
    "response": "responded",
    "answered": "responded",
    
    "interest": "interested",
    "wants to join": "interested",
    "positive": "interested",
    
    "meeting": "meeting_scheduled",
    "call scheduled": "meeting_scheduled",
    "zoom": "meeting_scheduled",
    "demo": "meeting_scheduled",
    
    "signed up": "onboarded",
    "joined": "onboarded",
    "active": "onboarded",
    "teacher": "onboarded",
    
    "pass": "declined",
    "no": "declined",
    "not interested": "declined",
    "rejected": "declined",
    
    "no response": "no_response",
    "ghosted": "no_response",
    "unresponsive": "no_response",
    "no reply": "no_response",
    
    "bad fit": "disqualified",
    "unqualified": "disqualified",
    "spam": "disqualified",
}

# Default values for missing optional fields
DEFAULTS = {
    "country": "US",
    "tags": [],
    "notes": "",
    "followers": 0,
}

# Phone number normalization
PHONE_REGEX = re.compile(r'[^0-9+]')


class DataFixer:
    def __init__(self, data_path: str, dry_run: bool = False):
        self.data_path = Path(data_path)
        self.dry_run = dry_run
        self.changes: List[Dict[str, Any]] = []
        self.fixed_count = 0

    def load_data(self) -> List[Dict]:
        """Load prospect data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Data must be a list of prospects")
        
        return data

    def save_data(self, data: List[Dict]) -> None:
        """Save fixed data back to file."""
        if self.dry_run:
            return
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_change(self, prospect_id: str, field: str, old: Any, new: Any, fix_type: str):
        """Record a change made to a prospect."""
        self.changes.append({
            "prospect_id": prospect_id,
            "field": field,
            "old": old,
            "new": new,
            "fix_type": fix_type
        })

    def fix_whitespace(self, prospect: Dict) -> Dict:
        """Trim whitespace from string fields."""
        prospect_id = prospect.get('id', 'unknown')
        
        string_fields = ['name', 'email', 'phone', 'city', 'state', 'country', 
                        'website', 'instagram', 'notes']
        
        for field in string_fields:
            if field in prospect and isinstance(prospect[field], str):
                old = prospect[field]
                new = old.strip()
                # Also normalize internal whitespace
                new = ' '.join(new.split())
                if old != new:
                    prospect[field] = new
                    self.record_change(prospect_id, field, old, new, "trim_whitespace")
        
        # Trim tags
        if 'tags' in prospect and isinstance(prospect['tags'], list):
            old_tags = prospect['tags']
            new_tags = [tag.strip() for tag in old_tags if tag.strip()]
            if old_tags != new_tags:
                prospect['tags'] = new_tags
                self.record_change(prospect_id, 'tags', old_tags, new_tags, "trim_whitespace")
        
        return prospect

    def fix_email(self, prospect: Dict) -> Dict:
        """Lowercase and normalize emails."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'email' in prospect and isinstance(prospect['email'], str):
            old = prospect['email']
            new = old.lower().strip()
            # Remove any accidental mailto: prefix
            if new.startswith('mailto:'):
                new = new[7:]
            if old != new:
                prospect['email'] = new
                self.record_change(prospect_id, 'email', old, new, "lowercase_email")
        
        return prospect

    def fix_stage_name(self, prospect: Dict) -> Dict:
        """Standardize stage names."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'stage' in prospect:
            old = prospect['stage']
            if isinstance(old, str):
                new = old.lower().strip()
                # Check mappings
                if new in STAGE_MAPPINGS:
                    new = STAGE_MAPPINGS[new]
                
                if old != new:
                    prospect['stage'] = new
                    self.record_change(prospect_id, 'stage', old, new, "standardize_stage")
        
        return prospect

    def fix_phone(self, prospect: Dict) -> Dict:
        """Normalize phone numbers."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'phone' in prospect and isinstance(prospect['phone'], str):
            old = prospect['phone']
            # Keep only digits and +
            new = PHONE_REGEX.sub('', old)
            if old != new and new:  # Only if we still have something
                prospect['phone'] = new
                self.record_change(prospect_id, 'phone', old, new, "normalize_phone")
        
        return prospect

    def fix_missing_defaults(self, prospect: Dict) -> Dict:
        """Fill missing optional fields with defaults."""
        prospect_id = prospect.get('id', 'unknown')
        
        for field, default in DEFAULTS.items():
            if field not in prospect or prospect[field] is None:
                prospect[field] = default
                self.record_change(prospect_id, field, None, default, "fill_default")
        
        return prospect

    def fix_instagram_handle(self, prospect: Dict) -> Dict:
        """Normalize Instagram handles (remove @ if present)."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'instagram' in prospect and isinstance(prospect['instagram'], str):
            old = prospect['instagram']
            new = old.strip()
            # Remove @ prefix if present
            if new.startswith('@'):
                new = new[1:]
            # Remove instagram.com/ prefix if present
            if 'instagram.com/' in new:
                new = new.split('instagram.com/')[-1]
            # Remove trailing slash
            new = new.rstrip('/')
            
            if old != new:
                prospect['instagram'] = new
                self.record_change(prospect_id, 'instagram', old, new, "normalize_instagram")
        
        return prospect

    def fix_website(self, prospect: Dict) -> Dict:
        """Normalize website URLs."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'website' in prospect and isinstance(prospect['website'], str):
            old = prospect['website']
            new = old.strip()
            
            # Add https:// if missing and not empty
            if new and not new.startswith(('http://', 'https://')):
                new = 'https://' + new
            
            if old != new:
                prospect['website'] = new
                self.record_change(prospect_id, 'website', old, new, "normalize_website")
        
        return prospect

    def fix_followers(self, prospect: Dict) -> Dict:
        """Ensure followers is a number."""
        prospect_id = prospect.get('id', 'unknown')
        
        if 'followers' in prospect:
            old = prospect['followers']
            try:
                if isinstance(old, str):
                    # Handle "1.2k" or "1.2K"
                    old_str = old.lower().replace(',', '').strip()
                    if 'k' in old_str:
                        new = int(float(old_str.replace('k', '')) * 1000)
                    elif 'm' in old_str:
                        new = int(float(old_str.replace('m', '')) * 1000000)
                    else:
                        new = int(old_str)
                else:
                    new = int(old)
                
                if old != new:
                    prospect['followers'] = new
                    self.record_change(prospect_id, 'followers', old, new, "normalize_followers")
            except (ValueError, TypeError):
                # If can't parse, set to 0
                prospect['followers'] = 0
                self.record_change(prospect_id, 'followers', old, 0, "normalize_followers")
        
        return prospect

    def update_timestamp(self, prospect: Dict) -> Dict:
        """Update the updated_at timestamp if any changes were made."""
        prospect_id = prospect.get('id', 'unknown')
        
        # Check if this prospect had any changes
        prospect_changes = [c for c in self.changes if c['prospect_id'] == prospect_id]
        if prospect_changes:
            old = prospect.get('updated_at')
            new = datetime.now(timezone.utc).isoformat()
            prospect['updated_at'] = new
            self.record_change(prospect_id, 'updated_at', old, new, "update_timestamp")
            self.fixed_count += 1
        
        return prospect

    def fix_prospect(self, prospect: Dict) -> Dict:
        """Apply all fixes to a single prospect."""
        prospect = self.fix_whitespace(prospect)
        prospect = self.fix_email(prospect)
        prospect = self.fix_stage_name(prospect)
        prospect = self.fix_phone(prospect)
        prospect = self.fix_missing_defaults(prospect)
        prospect = self.fix_instagram_handle(prospect)
        prospect = self.fix_website(prospect)
        prospect = self.fix_followers(prospect)
        prospect = self.update_timestamp(prospect)
        return prospect

    def fix(self) -> Dict[str, Any]:
        """Run all fixes on the data."""
        try:
            data = self.load_data()
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "changes": [],
                "count": 0,
                "exit_code": 4
            }
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}",
                "changes": [],
                "count": 0,
                "exit_code": 4
            }

        # Apply fixes to all prospects
        fixed_data = [self.fix_prospect(p) for p in data]

        # Group changes by type
        changes_by_type = {}
        for change in self.changes:
            t = change['fix_type']
            changes_by_type[t] = changes_by_type.get(t, 0) + 1

        # Save if not dry run
        self.save_data(fixed_data)

        # Build result
        status = "success" if self.changes else "success"
        message = f"Fixed {self.fixed_count}/{len(data)} prospects"
        if self.changes:
            message += f", {len(self.changes)} changes made"
        else:
            message += ": No fixes needed"

        return {
            "status": status,
            "message": message,
            "dry_run": self.dry_run,
            "changes": self.changes,
            "summary": {
                "total_prospects": len(data),
                "fixed_prospects": self.fixed_count,
                "total_changes": len(self.changes),
                "by_type": changes_by_type
            },
            "count": len(self.changes),
            "exit_code": 0
        }


def main():
    # Default path
    data_path = Path.home() / ".openclaw" / "workspace" / "scout_data.json"
    
    # Parse arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    # Get path from args (skip flags)
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if args:
        data_path = Path(args[0])

    fixer = DataFixer(str(data_path), dry_run)
    result = fixer.fix()

    print(json.dumps(result, indent=2))
    sys.exit(result.get("exit_code", 0))


if __name__ == "__main__":
    main()
