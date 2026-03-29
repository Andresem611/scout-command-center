#!/usr/bin/env python3
"""
Validate scout_data.json against prospect schema.
Checks required fields, data types, and enum values.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

# Schema definition
REQUIRED_FIELDS = [
    "id", "name", "email", "stage", "source", "created_at", "updated_at"
]

VALID_SOURCES = [
    "instagram", "facebook", "twitter", "youtube", "tiktok",
    "referral", "manual", "imported", "other"
]

VALID_STAGES = [
    "new", "contacted", "responded", "interested", "meeting_scheduled",
    "onboarded", "declined", "no_response", "disqualified"
]

FIELD_TYPES = {
    "id": str,
    "name": str,
    "email": str,
    "email_domain": str,
    "phone": str,
    "city": str,
    "state": str,
    "country": str,
    "source": str,
    "stage": str,
    "tags": list,
    "notes": str,
    "website": str,
    "instagram": str,
    "followers": int,
    "created_at": str,
    "updated_at": str,
    "last_contact_at": (str, type(None)),
    "last_reply_at": (str, type(None)),
}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ISO8601_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$')


class SchemaValidator:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict]:
        """Load prospect data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Data must be a list of prospects")
        
        return data

    def validate_email(self, email: str, prospect_id: str) -> bool:
        """Validate email format."""
        if not email:
            self.errors.append({
                "prospect_id": prospect_id,
                "field": "email",
                "error": "Email is empty",
                "value": email
            })
            return False
        
        if not EMAIL_REGEX.match(email):
            self.errors.append({
                "prospect_id": prospect_id,
                "field": "email",
                "error": "Invalid email format",
                "value": email
            })
            return False
        
        # Check for common typos
        common_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        domain = email.split('@')[-1].lower()
        
        typos = {
            "gmial.com": "gmail.com",
            "gmal.com": "gmail.com",
            "gnail.com": "gmail.com",
            "yahooo.com": "yahoo.com",
            "yaho.com": "yahoo.com",
            "hotmal.com": "hotmail.com",
            "hotmial.com": "hotmail.com",
        }
        
        if domain in typos:
            self.warnings.append({
                "prospect_id": prospect_id,
                "field": "email",
                "warning": f"Possible typo: '{domain}' should be '{typos[domain]}'",
                "value": email
            })
        
        return True

    def validate_iso8601(self, value: str, field: str, prospect_id: str) -> bool:
        """Validate ISO 8601 date format."""
        if not value:
            return True  # Null values allowed for some date fields
        
        if not ISO8601_REGEX.match(value):
            self.errors.append({
                "prospect_id": prospect_id,
                "field": field,
                "error": "Invalid ISO 8601 date format",
                "value": value
            })
            return False
        
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError as e:
            self.errors.append({
                "prospect_id": prospect_id,
                "field": field,
                "error": f"Invalid date: {str(e)}",
                "value": value
            })
            return False

    def validate_type(self, value: Any, expected_type: type, field: str, prospect_id: str) -> bool:
        """Validate field type."""
        if expected_type == (str, type(None)):
            return value is None or isinstance(value, str)
        
        if not isinstance(value, expected_type):
            self.errors.append({
                "prospect_id": prospect_id,
                "field": field,
                "error": f"Expected {expected_type.__name__}, got {type(value).__name__}",
                "value": value
            })
            return False
        return True

    def validate_prospect(self, prospect: Dict, index: int) -> bool:
        """Validate a single prospect record."""
        prospect_id = prospect.get('id', f"[index:{index}]")
        is_valid = True

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in prospect:
                self.errors.append({
                    "prospect_id": prospect_id,
                    "field": field,
                    "error": f"Missing required field: {field}",
                    "value": None
                })
                is_valid = False

        # Check field types and values
        for field, value in prospect.items():
            if field not in FIELD_TYPES:
                self.warnings.append({
                    "prospect_id": prospect_id,
                    "field": field,
                    "warning": f"Unknown field: {field}",
                    "value": value
                })
                continue

            expected_type = FIELD_TYPES[field]
            if not self.validate_type(value, expected_type, field, prospect_id):
                is_valid = False

            # Field-specific validations
            if field == "email" and value:
                if not self.validate_email(value, prospect_id):
                    is_valid = False
            
            elif field == "source" and value:
                if value not in VALID_SOURCES:
                    self.errors.append({
                        "prospect_id": prospect_id,
                        "field": "source",
                        "error": f"Invalid source. Must be one of: {VALID_SOURCES}",
                        "value": value
                    })
                    is_valid = False
            
            elif field == "stage" and value:
                if value not in VALID_STAGES:
                    self.errors.append({
                        "prospect_id": prospect_id,
                        "field": "stage",
                        "error": f"Invalid stage. Must be one of: {VALID_STAGES}",
                        "value": value
                    })
                    is_valid = False
            
            elif field in ["created_at", "updated_at", "last_contact_at", "last_reply_at"]:
                if value and not self.validate_iso8601(value, field, prospect_id):
                    is_valid = False

        return is_valid

    def validate(self) -> Dict[str, Any]:
        """Run full validation."""
        try:
            prospects = self.load_data()
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "errors": [],
                "warnings": [],
                "count": 0,
                "exit_code": 4
            }
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}",
                "errors": [],
                "warnings": [],
                "count": 0,
                "exit_code": 4
            }

        valid_count = 0
        for i, prospect in enumerate(prospects):
            if not isinstance(prospect, dict):
                self.errors.append({
                    "prospect_id": f"[index:{i}]",
                    "error": f"Expected dict, got {type(prospect).__name__}"
                })
                continue
            
            if self.validate_prospect(prospect, i):
                valid_count += 1

        status = "error" if self.errors else ("warning" if self.warnings else "success")
        message = f"Validated {len(prospects)} prospects: {valid_count} valid"
        if self.errors:
            message += f", {len(self.errors)} errors"
        if self.warnings:
            message += f", {len(self.warnings)} warnings"

        exit_code = 1 if self.errors else (0 if not self.warnings else 0)

        return {
            "status": status,
            "message": message,
            "errors": self.errors,
            "warnings": self.warnings,
            "count": {
                "total": len(prospects),
                "valid": valid_count,
                "errors": len(self.errors),
                "warnings": len(self.warnings)
            },
            "exit_code": exit_code
        }


def main():
    # Default path
    data_path = Path.home() / ".openclaw" / "workspace" / "scout_data.json"
    
    # Allow custom path via argument
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])

    validator = SchemaValidator(str(data_path))
    result = validator.validate()

    print(json.dumps(result, indent=2))
    sys.exit(result.get("exit_code", 0))


if __name__ == "__main__":
    main()
