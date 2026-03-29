#!/usr/bin/env python3
"""
update_blacklist.py - Bounced email tracking and blacklist management

Tracks bounced emails and maintains a blacklist to prevent future sends
to invalid addresses.
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional

# Path to store blacklist (relative to skill directory)
SKILL_DIR = Path(__file__).parent.parent
BLACKLIST_FILE = SKILL_DIR / 'references' / 'blacklist.json'
BOUNCES_FILE = SKILL_DIR / 'references' / 'bounces.log'

# Bounce types that indicate permanent failure
HARD_BOUNCE_TYPES = {
    'bounce',           # General bounce
    'permanent_bounce', # Permanent failure
    'invalid_email',    # Email doesn't exist
    'rejected',         # Rejected by server
    'suppress',         # Suppression list
    'spam',             # Marked as spam (domain reputation issue)
}

# Bounce types that might resolve (temporary)
SOFT_BOUNCE_TYPES = {
    'deferral',         # Temporary deferral
    'temporary_bounce', # Temporary failure
    'mailbox_full',     # Mailbox full
    'timeout',          # Connection timeout
}


def load_blacklist() -> Dict:
    """Load existing blacklist or create new one."""
    if BLACKLIST_FILE.exists():
        try:
            with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    
    return {
        'version': '1.0',
        'created': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'description': 'Thoven email blacklist - addresses that should not be contacted',
        'domains': {},      # domain -> {reason, date, count}
        'emails': {},       # email -> {reason, date, bounce_type}
        'patterns': [],     # regex patterns
        'stats': {
            'total_blacklisted': 0,
            'domain_blocks': 0,
            'email_blocks': 0
        }
    }


def save_blacklist(blacklist: Dict):
    """Save blacklist to file."""
    blacklist['last_updated'] = datetime.now().isoformat()
    
    # Update stats
    blacklist['stats']['domain_blocks'] = len(blacklist['domains'])
    blacklist['stats']['email_blocks'] = len(blacklist['emails'])
    blacklist['stats']['total_blacklisted'] = (
        blacklist['stats']['domain_blocks'] + 
        blacklist['stats']['email_blocks']
    )
    
    BLACKLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(blacklist, f, indent=2)


def log_bounce(email: str, bounce_type: str, reason: str, provider: str = None):
    """Log a bounce event to the bounces log."""
    BOUNCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'email': email,
        'bounce_type': bounce_type,
        'reason': reason,
        'provider': provider or 'unknown'
    }
    
    with open(BOUNCES_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def add_to_blacklist(
    blacklist: Dict,
    email: str,
    reason: str,
    bounce_type: str = 'bounce',
    provider: str = None
) -> Dict:
    """
    Add an email to the blacklist.
    
    Returns:
        Dict with action taken and details
    """
    result = {
        'email': email,
        'action': 'none',
        'reason': reason,
        'bounce_type': bounce_type
    }
    
    email_lower = email.lower().strip()
    
    # Check if already blacklisted
    if email_lower in blacklist['emails']:
        # Update existing entry
        blacklist['emails'][email_lower]['bounce_count'] = \
            blacklist['emails'][email_lower].get('bounce_count', 0) + 1
        blacklist['emails'][email_lower]['last_bounce'] = datetime.now().isoformat()
        result['action'] = 'updated'
        result['bounce_count'] = blacklist['emails'][email_lower]['bounce_count']
        return result
    
    # Add to blacklist
    blacklist['emails'][email_lower] = {
        'reason': reason,
        'bounce_type': bounce_type,
        'date_added': datetime.now().isoformat(),
        'bounce_count': 1,
        'provider': provider
    }
    
    result['action'] = 'added'
    
    # If hard bounce, also consider blocking domain after threshold
    if bounce_type in HARD_BOUNCE_TYPES:
        domain = email_lower.split('@')[1] if '@' in email_lower else None
        if domain:
            domain_bounces = blacklist['domains'].get(domain, {})
            domain_bounces['count'] = domain_bounces.get('count', 0) + 1
            domain_bounces['last_bounce'] = datetime.now().isoformat()
            
            # Block domain after 3 bounces
            if domain_bounces['count'] >= 3:
                domain_bounces['blocked'] = True
                domain_bounces['reason'] = f"Multiple bounces ({domain_bounces['count']})"
                result['domain_blocked'] = True
            
            blacklist['domains'][domain] = domain_bounces
    
    return result


def is_blacklisted(blacklist: Dict, email: str) -> Dict:
    """Check if an email is blacklisted."""
    email_lower = email.lower().strip()
    
    # Direct email match
    if email_lower in blacklist['emails']:
        return {
            'blacklisted': True,
            'level': 'email',
            'details': blacklist['emails'][email_lower]
        }
    
    # Domain match
    if '@' in email_lower:
        domain = email_lower.split('@')[1]
        if domain in blacklist['domains']:
            domain_info = blacklist['domains'][domain]
            if domain_info.get('blocked'):
                return {
                    'blacklisted': True,
                    'level': 'domain',
                    'details': domain_info
                }
    
    return {'blacklisted': False}


def process_bounce_file(filepath: str, provider: str = None) -> Dict:
    """
    Process a CSV file of bounced emails.
    
    Expected CSV columns: email, bounce_type, reason (optional)
    """
    results = {
        'processed': 0,
        'added': [],
        'updated': [],
        'skipped': [],
        'domains_blocked': [],
        'errors': []
    }
    
    blacklist = load_blacklist()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    email = row.get('email', '').strip()
                    bounce_type = row.get('bounce_type', 'bounce').strip()
                    reason = row.get('reason', 'Bounced email').strip()
                    
                    if not email or '@' not in email:
                        results['skipped'].append({'row': row, 'reason': 'Invalid email'})
                        continue
                    
                    # Log the bounce
                    log_bounce(email, bounce_type, reason, provider)
                    
                    # Only blacklist hard bounces
                    if bounce_type not in HARD_BOUNCE_TYPES:
                        results['skipped'].append({
                            'email': email,
                            'reason': f"Soft bounce type: {bounce_type}"
                        })
                        continue
                    
                    # Add to blacklist
                    result = add_to_blacklist(blacklist, email, reason, bounce_type, provider)
                    results['processed'] += 1
                    
                    if result['action'] == 'added':
                        results['added'].append(email)
                    elif result['action'] == 'updated':
                        results['updated'].append(email)
                    
                    if result.get('domain_blocked'):
                        domain = email.split('@')[1]
                        results['domains_blocked'].append(domain)
                        
                except Exception as e:
                    results['errors'].append({'row': row, 'error': str(e)})
    
    except FileNotFoundError:
        return {'error': f'File not found: {filepath}'}
    except Exception as e:
        return {'error': f'Failed to process file: {str(e)}'}
    
    # Save updated blacklist
    save_blacklist(blacklist)
    
    results['blacklist_stats'] = blacklist['stats']
    
    return results


def get_blacklist_stats() -> Dict:
    """Get current blacklist statistics."""
    blacklist = load_blacklist()
    return {
        'stats': blacklist['stats'],
        'last_updated': blacklist['last_updated'],
        'domains_blocked': len([d for d in blacklist['domains'].values() if d.get('blocked')]),
        'total_domains_tracked': len(blacklist['domains']),
        'total_emails': len(blacklist['emails'])
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Bounced email tracking and blacklist management'
    )
    parser.add_argument(
        'action',
        choices=['add', 'process', 'check', 'stats', 'list'],
        help='Action to perform'
    )
    parser.add_argument(
        'target',
        nargs='?',
        help='Email address or file path (depending on action)'
    )
    parser.add_argument(
        '--reason',
        default='Bounced email',
        help='Reason for blacklisting'
    )
    parser.add_argument(
        '--bounce-type',
        default='bounce',
        choices=list(HARD_BOUNCE_TYPES | SOFT_BOUNCE_TYPES),
        help='Type of bounce'
    )
    parser.add_argument(
        '--provider',
        help='Email provider (sendgrid, mailgun, etc.)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'add':
        if not args.target:
            print("Error: Email required for 'add' action", file=sys.stderr)
            sys.exit(1)
        
        blacklist = load_blacklist()
        result = add_to_blacklist(
            blacklist,
            args.target,
            args.reason,
            args.bounce_type,
            args.provider
        )
        save_blacklist(blacklist)
        print(json.dumps(result, indent=2))
        
    elif args.action == 'process':
        if not args.target:
            print("Error: File path required for 'process' action", file=sys.stderr)
            sys.exit(1)
        
        results = process_bounce_file(args.target, args.provider)
        print(json.dumps(results, indent=2))
        
    elif args.action == 'check':
        if not args.target:
            print("Error: Email required for 'check' action", file=sys.stderr)
            sys.exit(1)
        
        blacklist = load_blacklist()
        result = is_blacklisted(blacklist, args.target)
        print(json.dumps(result, indent=2))
        
    elif args.action == 'stats':
        stats = get_blacklist_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.action == 'list':
        blacklist = load_blacklist()
        sample = {
            'emails_sample': list(blacklist['emails'].keys())[:20],
            'domains_sample': [
                {k: v for k, v in d.items() if k != 'last_bounce'}
                for d in list(blacklist['domains'].values())[:10]
            ],
            'stats': blacklist['stats']
        }
        print(json.dumps(sample, indent=2))


if __name__ == '__main__':
    main()
