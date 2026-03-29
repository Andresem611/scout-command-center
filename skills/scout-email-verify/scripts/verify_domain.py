#!/usr/bin/env python3
"""
verify_domain.py - Domain verification for email validation

Checks:
- MX records (mail server existence)
- Domain blacklist status
- Disposable email detection
"""

import sys
import json
import socket
from typing import Dict, List, Set, Tuple

# Try to import dns.resolver, fallback to socket if not available
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

# Disposable email domains (common throwaway providers)
DISPOSABLE_DOMAINS = {
    # Temporary/throwaway services
    'tempmail.com', 'temp-mail.org', 'fakeemail.com',
    'throwaway.com', 'mailinator.com', 'guerrillamail.com',
    'sharklasers.com', 'spam4.me', 'trashmail.com',
    'yopmail.com', 'yopmail.fr', 'yopmail.net',
    'jetable.org', 'mailnesia.com', 'tempinbox.com',
    'mailcatch.com', 'tempmailaddress.com', 'burnermail.io',
    'tempmail.ninja', 'temp-mail.io', 'fakemail.net',
    'mail-temp.com', 'disposable-email.com', 'mailforspam.com',
    'tempail.com', 'tempmailbox.com', 'getairmail.com',
    '10minutemail.com', '10minutemail.net', '10minemail.com',
    'tempmailo.com', 'tempmails.com', 'temp-mail.ru',
    'discard.email', 'discardmail.com', 'throwawaymail.com',
    'tempm.com', 'tmpmail.org', 'mailtemp.com',
    
    # Known suspicious/throwaway patterns
    'mail.ru', 'inbox.ru', 'list.ru', 'bk.ru',
}

# Known problematic/bad domains (spam sources, dead domains)
BLACKLISTED_DOMAINS = {
    # Example dead/non-existent domains
    'example.com', 'test.com', 'localhost',
    'domain.com', 'email.com', 'mail.com',
}

# Domains that don't accept external mail
NO_EXTERNAL_MAIL = {
    'noreply.com', 'no-reply.com',
}


def has_mx_record(domain: str) -> Tuple[bool, List[str], str]:
    """
    Check if domain has valid MX records.
    Returns: (has_mx, mx_records_list, error_message)
    """
    if DNS_AVAILABLE:
        return _has_mx_record_dns(domain)
    else:
        return _has_mx_record_socket(domain)


def _has_mx_record_dns(domain: str) -> Tuple[bool, List[str], str]:
    """DNS-based MX lookup using dnspython."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(rdata.exchange).rstrip('.') for rdata in answers]
        mx_records.sort(key=lambda x: (answers[0].preference if hasattr(answers[0], 'preference') else 0))
        return True, mx_records, None
    except dns.resolver.NXDOMAIN:
        return False, [], f"Domain '{domain}' does not exist (NXDOMAIN)"
    except dns.resolver.NoAnswer:
        # Try A record as fallback (some domains use A record for mail)
        try:
            answers = dns.resolver.resolve(domain, 'A')
            ips = [str(rdata) for rdata in answers]
            if ips:
                return True, [domain], f"No MX record, but A record exists: {ips[0]}"
            return False, [], f"No MX or A records found for '{domain}'"
        except Exception as e:
            return False, [], f"No MX record and A record check failed: {str(e)}"
    except dns.resolver.NoNameservers:
        return False, [], f"No nameservers available for '{domain}'"
    except dns.exception.Timeout:
        return False, [], f"DNS lookup timed out for '{domain}'"
    except Exception as e:
        return False, [], f"DNS lookup failed: {str(e)}"


def _has_mx_record_socket(domain: str) -> Tuple[bool, List[str], str]:
    """Fallback MX lookup using socket (no external deps)."""
    try:
        # Check if domain resolves at all
        socket.getaddrinfo(domain, None)
        
        # Try to connect to common mail ports
        for port in [25, 587, 465]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((domain, port))
                sock.close()
                if result == 0:
                    return True, [domain], f"Port {port} open (fallback check)"
            except Exception:
                continue
        
        # Domain exists but no mail ports open - might still have external MX
        return True, [domain], "Domain resolves (MX check limited without dnspython)"
    except socket.gaierror:
        return False, [], f"Domain '{domain}' does not resolve"
    except Exception as e:
        return False, [], f"Lookup failed: {str(e)}"


def is_disposable(domain: str) -> Tuple[bool, str]:
    """Check if domain is a known disposable email provider."""
    domain_lower = domain.lower()
    
    # Direct match
    if domain_lower in DISPOSABLE_DOMAINS:
        return True, f"Known disposable email domain: {domain}"
    
    # Check subdomains
    parts = domain_lower.split('.')
    for i in range(len(parts) - 1):
        parent = '.'.join(parts[i:])
        if parent in DISPOSABLE_DOMAINS:
            return True, f"Disposable email subdomain of {parent}"
    
    return False, None


def is_blacklisted(domain: str) -> Tuple[bool, str]:
    """Check if domain is in local blacklist."""
    domain_lower = domain.lower()
    
    if domain_lower in BLACKLISTED_DOMAINS:
        return True, f"Domain '{domain}' is in local blacklist"
    
    return False, None


def check_spamhaus(domain: str) -> Tuple[bool, str]:
    """
    Check domain against Spamhaus DBL (Domain Block List).
    Note: Requires proper DNS resolver setup. Simplified check.
    """
    if not DNS_AVAILABLE:
        return False, "Spamhaus check requires dnspython"
    
    # Simplified implementation - in production, query Spamhaus DNS
    # Format: domain.dbl.spamhaus.org
    # Return codes indicate listing status
    try:
        query = f"{domain}.dbl.spamhaus.org"
        answers = dns.resolver.resolve(query, 'A')
        # If we get a response, domain is listed
        return True, f"Domain listed in Spamhaus DBL: {query}"
    except dns.resolver.NXDOMAIN:
        # NXDOMAIN means not listed (good)
        return False, None
    except Exception:
        # Any error, assume not listed
        return False, None


def verify_domain(domain: str, check_spamhaus_list: bool = False) -> Dict:
    """
    Verify a domain for email deliverability.
    
    Args:
        domain: The domain to verify (e.g., 'gmail.com')
        check_spamhaus_list: Whether to check Spamhaus DBL (slower)
    
    Returns:
        Dict with verification results
    """
    result = {
        'status': 'unknown',
        'domain': domain,
        'checks': {
            'mx': {'valid': False, 'records': [], 'message': None},
            'disposable': {'is_disposable': False, 'reason': None},
            'blacklist': {'is_blacklisted': False, 'reason': None},
            'spamhaus': {'is_listed': False, 'reason': None} if check_spamhaus_list else None,
        },
        'reason': None,
        'recommendation': None
    }
    
    # Validate domain format
    if not domain or '.' not in domain:
        result['status'] = 'invalid'
        result['reason'] = 'Invalid domain format'
        return result
    
    # Check disposable first (fast)
    is_disp, disp_reason = is_disposable(domain)
    result['checks']['disposable'] = {'is_disposable': is_disp, 'reason': disp_reason}
    
    if is_disp:
        result['status'] = 'invalid'
        result['reason'] = disp_reason
        result['recommendation'] = 'Reject - disposable email addresses have low engagement'
        return result
    
    # Check local blacklist
    is_black, black_reason = is_blacklisted(domain)
    result['checks']['blacklist'] = {'is_blacklisted': is_black, 'reason': black_reason}
    
    if is_black:
        result['status'] = 'invalid'
        result['reason'] = black_reason
        result['recommendation'] = 'Reject - blacklisted domain'
        return result
    
    # Check MX records
    has_mx, mx_list, mx_error = has_mx_record(domain)
    result['checks']['mx'] = {
        'valid': has_mx,
        'records': mx_list,
        'message': mx_error
    }
    
    if not has_mx:
        result['status'] = 'invalid'
        result['reason'] = mx_error or 'No valid MX records found'
        result['recommendation'] = 'Reject - cannot deliver to this domain'
        return result
    
    # Optional Spamhaus check
    if check_spamhaus_list:
        is_spam, spam_reason = check_spamhaus(domain)
        result['checks']['spamhaus'] = {'is_listed': is_spam, 'reason': spam_reason}
        if is_spam:
            result['status'] = 'invalid'
            result['reason'] = spam_reason
            result['recommendation'] = 'Reject - domain has poor reputation'
            return result
    
    # All checks passed
    result['status'] = 'valid'
    result['reason'] = None
    result['recommendation'] = 'Accept - domain appears deliverable'
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: verify_domain.py <domain> [--spamhaus]", file=sys.stderr)
        print("Example: verify_domain.py gmail.com", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    check_spamhaus_flag = '--spamhaus' in sys.argv
    
    result = verify_domain(domain, check_spamhaus_list=check_spamhaus_flag)
    print(json.dumps(result, indent=2))
    
    # Exit codes: 0 = valid, 1 = invalid, 2 = unknown
    if result['status'] == 'valid':
        sys.exit(0)
    elif result['status'] == 'invalid':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
