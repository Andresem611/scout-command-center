#!/usr/bin/env python3
"""
check_format.py - Email syntax validation with typo detection

Validates email format and suggests fixes for common typos.
"""

import re
import sys
import json
from typing import Dict, List, Tuple

# Common domain typos and their corrections
DOMAIN_TYPOS = {
    # Gmail variants
    'gmial.com': 'gmail.com',
    'gmal.com': 'gmail.com',
    'gmail.co': 'gmail.com',
    'gmail.cm': 'gmail.com',
    'gmail.con': 'gmail.com',
    'gmail.co.uk': 'gmail.com',
    'gnail.com': 'gmail.com',
    'gmaill.com': 'gmail.com',
    'gamil.com': 'gmail.com',
    
    # Yahoo variants
    'yahooo.com': 'yahoo.com',
    'yaho.com': 'yahoo.com',
    'yahoo.co': 'yahoo.com',
    'yhaoo.com': 'yahoo.com',
    
    # Hotmail/Outlook variants
    'hotmal.com': 'hotmail.com',
    'hotmial.com': 'hotmail.com',
    'hotmail.co': 'hotmail.com',
    'hotail.com': 'hotmail.com',
    'outlok.com': 'outlook.com',
    'outlook.co': 'outlook.com',
    'outook.com': 'outlook.com',
    
    # AOL variants
    'aol.com.com': 'aol.com',
    'aol.co': 'aol.com',
    
    # iCloud variants
    'icloud.co': 'icloud.com',
    'icould.com': 'icloud.com',
    'me.co': 'me.com',
    'mac.co': 'me.com',
    
    # Common TLD typos
    '.con': '.com',
    '.coom': '.com',
    '.comm': '.com',
    '.ne': '.net',
    '.nat': '.net',
    '.ogr': '.org',
    '.or': '.org',
}

# RFC 5322 compliant regex (simplified but robust)
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"  # Local part
    r"@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"  # Domain start
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"  # Subdomains
    r"\.[a-zA-Z]{2,}$"  # TLD
)

# Forbidden characters in local part
INVALID_LOCAL_CHARS = re.compile(r'[<>()\[\]\\,;: ]')

# Consecutive dots check
CONSECUTIVE_DOTS = re.compile(r'\.\.{2,}')


def check_typo_suggestions(domain: str) -> List[Dict]:
    """Check domain for common typos and return suggestions."""
    suggestions = []
    domain_lower = domain.lower()
    
    # Direct match - user entered a known typo domain
    if domain_lower in DOMAIN_TYPOS:
        suggestions.append({
            'type': 'typo',
            'found': domain,
            'suggested': DOMAIN_TYPOS[domain_lower],
            'confidence': 'high'
        })
        return suggestions  # Return early if direct typo found
    
    # TLD typo check
    for typo, fix in DOMAIN_TYPOS.items():
        if typo.startswith('.') and domain_lower.endswith(typo):
            suggestions.append({
                'type': 'tld_typo',
                'found': domain,
                'suggested': domain_lower[:-len(typo)] + fix,
                'confidence': 'medium'
            })
    
    # Character swap detection - only check against VALID domains (the values)
    # to suggest corrections, not against typo entries
    valid_domains = set(DOMAIN_TYPOS.values())
    for valid_domain in valid_domains:
        if valid_domain != domain_lower and edit_distance(domain_lower, valid_domain) <= 2:
            suggestions.append({
                'type': 'possible_typo',
                'found': domain,
                'suggested': valid_domain,
                'confidence': 'low'
            })
    
    return suggestions


def edit_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def validate_email(email: str) -> Dict:
    """Validate email format and check for typos."""
    result = {
        'status': 'unknown',
        'email': email,
        'checks': {
            'syntax': {'valid': False, 'errors': [], 'typos': []},
        },
        'reason': None
    }
    
    # Basic null/empty check
    if not email or not isinstance(email, str):
        result['status'] = 'invalid'
        result['reason'] = 'Email is empty or not a string'
        result['checks']['syntax']['errors'].append('empty_or_null')
        return result
    
    email = email.strip()
    
    if len(email) == 0:
        result['status'] = 'invalid'
        result['reason'] = 'Email is empty'
        result['checks']['syntax']['errors'].append('empty')
        return result
    
    if len(email) > 254:
        result['status'] = 'invalid'
        result['reason'] = 'Email exceeds maximum length (254 chars)'
        result['checks']['syntax']['errors'].append('too_long')
        return result
    
    # Check for @ symbol
    if '@' not in email:
        result['status'] = 'invalid'
        result['reason'] = 'Missing @ symbol'
        result['checks']['syntax']['errors'].append('missing_at')
        return result
    
    # Split local and domain
    parts = email.rsplit('@', 1)
    if len(parts) != 2:
        result['status'] = 'invalid'
        result['reason'] = 'Multiple @ symbols found'
        result['checks']['syntax']['errors'].append('multiple_at')
        return result
    
    local_part, domain = parts
    
    # Local part validation
    if len(local_part) == 0:
        result['status'] = 'invalid'
        result['reason'] = 'Local part (before @) is empty'
        result['checks']['syntax']['errors'].append('empty_local')
        return result
    
    if len(local_part) > 64:
        result['status'] = 'invalid'
        result['reason'] = 'Local part exceeds 64 characters'
        result['checks']['syntax']['errors'].append('local_too_long')
        return result
    
    if local_part.startswith('.') or local_part.endswith('.'):
        result['status'] = 'invalid'
        result['reason'] = 'Local part cannot start or end with a dot'
        result['checks']['syntax']['errors'].append('dot_at_edges')
        return result
    
    if CONSECUTIVE_DOTS.search(local_part):
        result['status'] = 'invalid'
        result['reason'] = 'Local part contains consecutive dots'
        result['checks']['syntax']['errors'].append('consecutive_dots')
        return result
    
    if INVALID_LOCAL_CHARS.search(local_part):
        result['status'] = 'invalid'
        result['reason'] = 'Local part contains invalid characters'
        result['checks']['syntax']['errors'].append('invalid_chars')
        return result
    
    # Domain validation
    if len(domain) == 0:
        result['status'] = 'invalid'
        result['reason'] = 'Domain part (after @) is empty'
        result['checks']['syntax']['errors'].append('empty_domain')
        return result
    
    if domain.startswith('.') or domain.endswith('.'):
        result['status'] = 'invalid'
        result['reason'] = 'Domain cannot start or end with a dot'
        result['checks']['syntax']['errors'].append('domain_dot_edges')
        return result
    
    # Check for consecutive dots in domain
    if '..' in domain:
        result['status'] = 'invalid'
        result['reason'] = 'Domain contains consecutive dots'
        result['checks']['syntax']['errors'].append('domain_consecutive_dots')
        return result
    
    # Check for uppercase in domain (should be lowercase)
    if domain != domain.lower():
        result['checks']['syntax']['warnings'] = result['checks']['syntax'].get('warnings', [])
        result['checks']['syntax']['warnings'].append('domain_has_uppercase')
    
    # Regex validation
    if not EMAIL_REGEX.match(email):
        result['status'] = 'invalid'
        result['reason'] = 'Email format does not match RFC 5322'
        result['checks']['syntax']['errors'].append('regex_failed')
        return result
    
    # Check for typos
    typo_suggestions = check_typo_suggestions(domain)
    if typo_suggestions:
        result['checks']['syntax']['typos'] = typo_suggestions
        # If high confidence typo found, mark for review
        high_confidence = [t for t in typo_suggestions if t['confidence'] == 'high']
        if high_confidence:
            result['checks']['syntax']['suggested_fix'] = high_confidence[0]['suggested']
    
    # All checks passed
    result['status'] = 'valid'
    result['checks']['syntax']['valid'] = True
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: check_format.py <email>", file=sys.stderr)
        print("Example: check_format.py 'prospect@example.com'", file=sys.stderr)
        sys.exit(1)
    
    email = sys.argv[1]
    result = validate_email(email)
    print(json.dumps(result, indent=2))
    
    # Exit code: 0 = valid, 1 = invalid, 2 = unknown/needs review
    if result['status'] == 'valid':
        if result['checks']['syntax'].get('typos'):
            sys.exit(2)  # Valid but has typo suggestions
        sys.exit(0)
    elif result['status'] == 'invalid':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
