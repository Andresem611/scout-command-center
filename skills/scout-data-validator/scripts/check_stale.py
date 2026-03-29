#!/usr/bin/env python3
"""
Check for stale prospect data.
Flags: prospects >30 days no update, >14 days no contact with no reply.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

# Thresholds (in days)
NO_UPDATE_THRESHOLD = 30
NO_CONTACT_NO_REPLY_THRESHOLD = 14

STAGE_EXPECTS_CONTACT = [
    "contacted", "responded", "interested", "meeting_scheduled"
]


class StaleChecker:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.stale_records: List[Dict[str, Any]] = []
        self.now = datetime.now(timezone.utc)

    def load_data(self) -> List[Dict]:
        """Load prospect data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Data must be a list of prospects")
        
        return data

    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO 8601 date string to datetime."""
        if not date_str:
            return None
        
        try:
            # Handle 'Z' suffix
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    def days_since(self, date: Optional[datetime]) -> Optional[int]:
        """Calculate days since a date."""
        if not date:
            return None
        delta = self.now - date
        return delta.days

    def check_no_update(self, prospect: Dict) -> Optional[Dict[str, Any]]:
        """Check if prospect hasn't been updated in >30 days."""
        updated_at = self.parse_date(prospect.get('updated_at'))
        if not updated_at:
            return None

        days = self.days_since(updated_at)
        if days is None or days <= NO_UPDATE_THRESHOLD:
            return None

        return {
            "type": "no_update",
            "prospect_id": prospect.get('id'),
            "name": prospect.get('name'),
            "email": prospect.get('email'),
            "stage": prospect.get('stage'),
            "days_since_update": days,
            "severity": "warning" if days < 60 else "error",
            "recommendation": f"Review and update prospect data (last updated {days} days ago)"
        }

    def check_no_contact_no_reply(self, prospect: Dict) -> Optional[Dict[str, Any]]:
        """Check if contacted prospect hasn't had contact/reply in >14 days."""
        stage = prospect.get('stage', '')
        
        # Only check stages that expect follow-up
        if stage not in STAGE_EXPECTS_CONTACT:
            return None

        last_contact = self.parse_date(prospect.get('last_contact_at'))
        last_reply = self.parse_date(prospect.get('last_reply_at'))

        # If they replied recently, not stale
        if last_reply:
            reply_days = self.days_since(last_reply)
            if reply_days is not None and reply_days <= NO_CONTACT_NO_REPLY_THRESHOLD:
                return None

        # Check if contacted but no reply for too long
        if last_contact:
            contact_days = self.days_since(last_contact)
            if contact_days is None:
                return None

            if contact_days > NO_CONTACT_NO_REPLY_THRESHOLD and not last_reply:
                # Contacted but no reply for >14 days
                return {
                    "type": "no_contact_no_reply",
                    "prospect_id": prospect.get('id'),
                    "name": prospect.get('name'),
                    "email": prospect.get('email'),
                    "stage": stage,
                    "days_since_contact": contact_days,
                    "severity": "warning",
                    "recommendation": f"Follow up or move to 'no_response' (contacted {contact_days} days ago, no reply)"
                }

        return None

    def check_stalled_response(self, prospect: Dict) -> Optional[Dict[str, Any]]:
        """Check for prospects who responded but no recent activity."""
        last_reply = self.parse_date(prospect.get('last_reply_at'))
        if not last_reply:
            return None

        days = self.days_since(last_reply)
        if days is None or days <= NO_CONTACT_NO_REPLY_THRESHOLD:
            return None

        stage = prospect.get('stage', '')
        
        # If they responded but we've gone silent
        if stage in ["responded", "interested"]:
            return {
                "type": "stalled_conversation",
                "prospect_id": prospect.get('id'),
                "name": prospect.get('name'),
                "email": prospect.get('email'),
                "stage": stage,
                "days_since_reply": days,
                "severity": "warning",
                "recommendation": f"Re-engage prospect (they replied {days} days ago, no follow-up)"
            }

        return None

    def check_new_never_contacted(self, prospect: Dict) -> Optional[Dict[str, Any]]:
        """Check for 'new' prospects that have been sitting untouched."""
        stage = prospect.get('stage', '')
        if stage != 'new':
            return None

        created_at = self.parse_date(prospect.get('created_at'))
        if not created_at:
            return None

        days = self.days_since(created_at)
        if days is None or days <= NO_CONTACT_NO_REPLY_THRESHOLD:
            return None

        return {
            "type": "new_never_contacted",
            "prospect_id": prospect.get('id'),
            "name": prospect.get('name'),
            "email": prospect.get('email'),
            "days_since_created": days,
            "severity": "warning",
            "recommendation": f"Contact new prospect (added {days} days ago, never contacted)"
        }

    def check(self) -> Dict[str, Any]:
        """Run all stale data checks."""
        try:
            prospects = self.load_data()
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "stale_records": [],
                "count": 0,
                "exit_code": 4
            }
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}",
                "stale_records": [],
                "count": 0,
                "exit_code": 4
            }

        stale_records = []

        for prospect in prospects:
            # Run all checks
            checks = [
                self.check_no_update(prospect),
                self.check_no_contact_no_reply(prospect),
                self.check_stalled_response(prospect),
                self.check_new_never_contacted(prospect)
            ]

            for issue in checks:
                if issue:
                    stale_records.append(issue)

        # Categorize by severity
        errors = [r for r in stale_records if r.get('severity') == 'error']
        warnings = [r for r in stale_records if r.get('severity') == 'warning']

        # Determine status
        if errors:
            status = "error"
            exit_code = 3
        elif warnings:
            status = "warning"
            exit_code = 0
        else:
            status = "success"
            exit_code = 0

        # Build summary by type
        type_counts = {}
        for record in stale_records:
            t = record.get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1

        # Build message
        message_parts = [f"Checked {len(prospects)} prospects"]
        if errors:
            message_parts.append(f"{len(errors)} stale (critical)")
        if warnings:
            message_parts.append(f"{len(warnings)} stale (warning)")
        
        message = ", ".join(message_parts)
        if len(stale_records) == 0:
            message += ": No stale records found"

        return {
            "status": status,
            "message": message,
            "stale_records": stale_records,
            "summary": {
                "errors": len(errors),
                "warnings": len(warnings),
                "total": len(stale_records),
                "by_type": type_counts
            },
            "thresholds": {
                "no_update_days": NO_UPDATE_THRESHOLD,
                "no_contact_no_reply_days": NO_CONTACT_NO_REPLY_THRESHOLD
            },
            "count": len(stale_records),
            "exit_code": exit_code
        }


def main():
    # Default path
    data_path = Path.home() / ".openclaw" / "workspace" / "scout_data.json"
    
    # Allow custom path via argument
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])

    checker = StaleChecker(str(data_path))
    result = checker.check()

    print(json.dumps(result, indent=2))
    sys.exit(result.get("exit_code", 0))


if __name__ == "__main__":
    main()
