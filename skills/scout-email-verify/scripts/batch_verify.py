#!/usr/bin/env python3
"""
batch_verify.py - Batch email verification processor

Processes a list of emails and categorizes them as valid/invalid/unknown
with detailed reasons for each.
"""

import sys
import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import sibling scripts
sys.path.insert(0, str(Path(__file__).parent))
from check_format import validate_email as check_syntax
from verify_domain import verify_domain as check_domain


def verify_single_email(email: str, check_domain_flag: bool = True) -> Dict:
    """
    Run full verification on a single email.
    
    Levels:
    1. Syntax validation
    2. Domain verification (if syntax passes)
    """
    email = email.strip()
    
    result = {
        'email': email,
        'status': 'unknown',
        'level': None,
        'syntax_check': None,
        'domain_check': None,
        'reason': None,
        'suggested_fix': None
    }
    
    # Level 1: Syntax check
    syntax_result = check_syntax(email)
    result['syntax_check'] = syntax_result['checks']['syntax']
    
    if syntax_result['status'] == 'invalid':
        result['status'] = 'invalid'
        result['level'] = 'syntax'
        result['reason'] = syntax_result['reason']
        if syntax_result['checks']['syntax'].get('suggested_fix'):
            result['suggested_fix'] = syntax_result['checks']['syntax']['suggested_fix']
        return result
    
    # Check for high-confidence typo suggestions even if valid
    if syntax_result['checks']['syntax'].get('suggested_fix'):
        result['suggested_fix'] = syntax_result['checks']['syntax']['suggested_fix']
    
    # Level 2: Domain check (if requested)
    if check_domain_flag:
        try:
            domain = email.split('@')[1]
            domain_result = check_domain(domain, check_spamhaus=False)
            result['domain_check'] = {
                'mx_valid': domain_result['checks']['mx']['valid'],
                'is_disposable': domain_result['checks']['disposable']['is_disposable'],
                'is_blacklisted': domain_result['checks']['blacklist']['is_blacklisted'],
                'mx_records': domain_result['checks']['mx']['records'][:3]  # Limit records
            }
            
            if domain_result['status'] == 'invalid':
                result['status'] = 'invalid'
                result['level'] = 'domain'
                result['reason'] = domain_result['reason']
                return result
            
            result['status'] = 'valid'
            result['level'] = 'domain'
            result['reason'] = None
            
        except Exception as e:
            result['status'] = 'unknown'
            result['level'] = 'domain'
            result['reason'] = f"Domain check failed: {str(e)}"
    else:
        result['status'] = 'valid'
        result['level'] = 'syntax'
        result['reason'] = None
    
    return result


def read_email_list(source: str) -> List[str]:
    """Read emails from file or comma-separated string."""
    emails = []
    
    # Check if it's a file
    if Path(source).exists():
        with open(source, 'r', encoding='utf-8') as f:
            # Try CSV first
            content = f.read()
            f.seek(0)
            
            # Detect if CSV
            if ',' in content and '\n' in content:
                try:
                    reader = csv.reader(f)
                    for row in reader:
                        for cell in row:
                            if '@' in cell:
                                emails.append(cell.strip())
                except Exception:
                    pass
            
            # Plain text, one per line
            if not emails:
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if line and '@' in line:
                        emails.append(line)
    else:
        # Treat as comma-separated list
        emails = [e.strip() for e in source.split(',') if '@' in e]
    
    # Deduplicate while preserving order
    seen = set()
    unique_emails = []
    for e in emails:
        e_lower = e.lower()
        if e_lower not in seen:
            seen.add(e_lower)
            unique_emails.append(e)
    
    return unique_emails


def batch_verify(
    source: str,
    output: Optional[str] = None,
    skip_domain: bool = False,
    max_workers: int = 5,
    delay: float = 0.1
) -> Dict:
    """
    Process batch of emails for verification.
    
    Args:
        source: File path or comma-separated email list
        output: Optional output file path
        skip_domain: Skip domain/MX checks (syntax only)
        max_workers: Concurrent verification threads
        delay: Delay between domain checks (rate limiting)
    """
    emails = read_email_list(source)
    
    results = {
        'total': len(emails),
        'valid': [],
        'invalid': [],
        'unknown': [],
        'with_suggestions': [],
        'summary': {},
        'details': []
    }
    
    if not emails:
        results['summary'] = {'error': 'No valid emails found in source'}
        return results
    
    # Process emails
    check_domain_flag = not skip_domain
    
    if max_workers > 1 and len(emails) > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_email = {
                executor.submit(verify_single_email, email, check_domain_flag): email
                for email in emails
            }
            
            for future in as_completed(future_to_email):
                result = future.result()
                results['details'].append(result)
                
                if result['status'] == 'valid':
                    results['valid'].append(result)
                elif result['status'] == 'invalid':
                    results['invalid'].append(result)
                else:
                    results['unknown'].append(result)
                
                if result.get('suggested_fix'):
                    results['with_suggestions'].append(result)
                
                time.sleep(delay)  # Rate limiting
    else:
        # Sequential processing
        for email in emails:
            result = verify_single_email(email, check_domain_flag)
            results['details'].append(result)
            
            if result['status'] == 'valid':
                results['valid'].append(result)
            elif result['status'] == 'invalid':
                results['invalid'].append(result)
            else:
                results['unknown'].append(result)
            
            if result.get('suggested_fix'):
                results['with_suggestions'].append(result)
            
            if check_domain_flag:
                time.sleep(delay)
    
    # Build summary
    results['summary'] = {
        'total': len(emails),
        'valid_count': len(results['valid']),
        'invalid_count': len(results['invalid']),
        'unknown_count': len(results['unknown']),
        'suggestions_count': len(results['with_suggestions']),
        'valid_rate': round(len(results['valid']) / len(emails) * 100, 1) if emails else 0,
        'invalid_rate': round(len(results['invalid']) / len(emails) * 100, 1) if emails else 0
    }
    
    # Remove full lists from main output (too verbose)
    # Keep only counts in summary
    output_results = {
        'summary': results['summary'],
        'valid_sample': [r['email'] for r in results['valid'][:5]],
        'invalid_sample': [
            {'email': r['email'], 'reason': r['reason']}
            for r in results['invalid'][:5]
        ],
        'suggestions': [
            {'email': r['email'], 'suggested': r['suggested_fix']}
            for r in results['with_suggestions'][:10]
        ]
    }
    
    # Write full results to file if requested
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        output_results['full_results_saved_to'] = output
    
    return output_results


def main():
    parser = argparse.ArgumentParser(
        description='Batch email verification for Thoven outreach'
    )
    parser.add_argument(
        'source',
        help='Email list file or comma-separated emails'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file for full results'
    )
    parser.add_argument(
        '--syntax-only',
        action='store_true',
        help='Skip domain verification (syntax checks only)'
    )
    parser.add_argument(
        '-j', '--workers',
        type=int,
        default=5,
        help='Number of concurrent workers (default: 5)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between domain checks in seconds (default: 0.1)'
    )
    
    args = parser.parse_args()
    
    results = batch_verify(
        source=args.source,
        output=args.output,
        skip_domain=args.syntax_only,
        max_workers=args.workers,
        delay=args.delay
    )
    
    print(json.dumps(results, indent=2))
    
    # Exit code based on results
    summary = results.get('summary', {})
    if summary.get('valid_rate', 0) >= 80:
        sys.exit(0)  # Mostly valid
    elif summary.get('invalid_rate', 0) >= 50:
        sys.exit(1)  # Mostly invalid
    else:
        sys.exit(2)  # Mixed results


if __name__ == '__main__':
    main()
