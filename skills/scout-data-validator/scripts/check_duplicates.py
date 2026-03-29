#!/usr/bin/env python3
"""
Check for duplicate prospects in scout_data.json.
Detects: same email with different names, similar names with same email.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.85


class DuplicateChecker:
    def __init__(self, data_path: str, threshold: float = SIMILARITY_THRESHOLD):
        self.data_path = Path(data_path)
        self.threshold = threshold
        self.duplicates: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict]:
        """Load prospect data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Data must be a list of prospects")
        
        return data

    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        return ' '.join(name.lower().split())

    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names."""
        n1 = self.normalize_name(name1)
        n2 = self.normalize_name(name2)
        return SequenceMatcher(None, n1, n2).ratio()

    def check_same_email_different_name(self, prospects: List[Dict]) -> List[Dict[str, Any]]:
        """Find prospects with same email but different names."""
        # Group by email
        email_groups: Dict[str, List[Dict]] = {}
        for p in prospects:
            email = p.get('email', '').lower().strip()
            if email:
                if email not in email_groups:
                    email_groups[email] = []
                email_groups[email].append(p)

        issues = []
        for email, group in email_groups.items():
            if len(group) < 2:
                continue

            # Check if names are different
            names = [p.get('name', '').strip() for p in group]
            unique_names = set(self.normalize_name(n) for n in names if n)
            
            if len(unique_names) > 1:
                issue = {
                    "type": "same_email_different_name",
                    "email": email,
                    "severity": "error",
                    "prospects": [
                        {
                            "id": p.get('id'),
                            "name": p.get('name'),
                            "stage": p.get('stage'),
                            "source": p.get('source')
                        }
                        for p in group
                    ],
                    "recommendation": "Merge or deduplicate these records"
                }
                issues.append(issue)

        return issues

    def check_similar_name_same_email_domain(self, prospects: List[Dict]) -> List[Dict[str, Any]]:
        """Find prospects with similar names and same email domain (possible duplicates)."""
        # Group by email domain
        domain_groups: Dict[str, List[Dict]] = {}
        for p in prospects:
            email = p.get('email', '').lower().strip()
            if email and '@' in email:
                domain = email.split('@')[1]
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append(p)

        issues = []
        for domain, group in domain_groups.items():
            if len(group) < 2:
                continue

            # Check for similar names within domain
            checked_pairs: Set[Tuple[str, str]] = set()
            
            for i, p1 in enumerate(group):
                for p2 in group[i+1:]:
                    id1, id2 = p1.get('id'), p2.get('id')
                    if (id1, id2) in checked_pairs or (id2, id1) in checked_pairs:
                        continue
                    checked_pairs.add((id1, id2))

                    name1 = p1.get('name', '')
                    name2 = p2.get('name', '')
                    
                    if not name1 or not name2:
                        continue

                    similarity = self.name_similarity(name1, name2)
                    
                    if similarity >= self.threshold:
                        issue = {
                            "type": "similar_name_same_domain",
                            "domain": domain,
                            "similarity": round(similarity, 3),
                            "severity": "warning" if similarity < 0.95 else "error",
                            "prospects": [
                                {
                                    "id": p1.get('id'),
                                    "name": p1.get('name'),
                                    "email": p1.get('email'),
                                    "stage": p1.get('stage')
                                },
                                {
                                    "id": p2.get('id'),
                                    "name": p2.get('name'),
                                    "email": p2.get('email'),
                                    "stage": p2.get('stage')
                                }
                            ],
                            "recommendation": "Review for potential duplicate"
                        }
                        issues.append(issue)

        return issues

    def check_exact_duplicate_ids(self, prospects: List[Dict]) -> List[Dict[str, Any]]:
        """Find prospects with duplicate IDs."""
        id_counts: Dict[str, List[Dict]] = {}
        for p in prospects:
            pid = p.get('id')
            if pid:
                if pid not in id_counts:
                    id_counts[pid] = []
                id_counts[pid].append(p)

        issues = []
        for pid, group in id_counts.items():
            if len(group) > 1:
                issue = {
                    "type": "duplicate_id",
                    "id": pid,
                    "severity": "critical",
                    "count": len(group),
                    "prospects": [
                        {
                            "name": p.get('name'),
                            "email": p.get('email')
                        }
                        for p in group
                    ],
                    "recommendation": "CRITICAL: Duplicate IDs must be resolved immediately"
                }
                issues.append(issue)

        return issues

    def check(self) -> Dict[str, Any]:
        """Run all duplicate checks."""
        try:
            prospects = self.load_data()
        except FileNotFoundError as e:
            return {
                "status": "error",
                "message": str(e),
                "duplicates": [],
                "count": 0,
                "exit_code": 4
            }
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}",
                "duplicates": [],
                "count": 0,
                "exit_code": 4
            }

        # Run all checks
        all_issues = []
        
        issues = self.check_exact_duplicate_ids(prospects)
        all_issues.extend(issues)
        
        issues = self.check_same_email_different_name(prospects)
        all_issues.extend(issues)
        
        issues = self.check_similar_name_same_email_domain(prospects)
        all_issues.extend(issues)

        # Categorize by severity
        critical = [i for i in all_issues if i.get('severity') == 'critical']
        errors = [i for i in all_issues if i.get('severity') == 'error']
        warnings = [i for i in all_issues if i.get('severity') == 'warning']

        # Determine status
        if critical:
            status = "critical"
            exit_code = 2
        elif errors:
            status = "error"
            exit_code = 2
        elif warnings:
            status = "warning"
            exit_code = 0
        else:
            status = "success"
            exit_code = 0

        # Build message
        message_parts = [f"Checked {len(prospects)} prospects"]
        if critical:
            message_parts.append(f"{len(critical)} critical")
        if errors:
            message_parts.append(f"{len(errors)} errors")
        if warnings:
            message_parts.append(f"{len(warnings)} warnings")
        
        message = ", ".join(message_parts)
        if len(all_issues) == 0:
            message += ": No duplicates found"

        return {
            "status": status,
            "message": message,
            "duplicates": all_issues,
            "summary": {
                "critical": len(critical),
                "errors": len(errors),
                "warnings": len(warnings),
                "total": len(all_issues)
            },
            "count": len(all_issues),
            "exit_code": exit_code
        }


def main():
    # Default path
    data_path = Path.home() / ".openclaw" / "workspace" / "scout_data.json"
    
    # Allow custom path and threshold via arguments
    threshold = SIMILARITY_THRESHOLD
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        try:
            threshold = float(sys.argv[2])
        except ValueError:
            pass

    checker = DuplicateChecker(str(data_path), threshold)
    result = checker.check()

    print(json.dumps(result, indent=2))
    sys.exit(result.get("exit_code", 0))


if __name__ == "__main__":
    main()
