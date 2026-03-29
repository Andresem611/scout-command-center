#!/usr/bin/env python3
"""
Extract email addresses from social bios, websites, and press pages.
Handles common patterns and validates format.
"""

import argparse
import json
import re
import sys
from typing import List, Dict, Set, Any
from urllib.parse import urljoin, urlparse

# Email regex pattern
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)

# Common email obfuscation patterns
OBFUSCATION_PATTERNS = [
    (r'([\w.]+)\s*\[at\]\s*([\w.]+)\s*\[dot\]\s*(\w+)', r'\1@\2.\3'),
    (r'([\w.]+)\s*@\s*([\w.]+)\s*dot\s*(\w+)', r'\1@\2.\3'),
    (r'([\w.]+)\s*\(at\)\s*([\w.]+)\s*\(dot\)\s*(\w+)', r'\1@\2.\3'),
    (r'([\w.]+)\s*AT\s*([\w.]+)\s*DOT\s*(\w+)', r'\1@\2.\3'),
]

# Common disposable/non-professional domains to filter
DISPOSABLE_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
    'icloud.com', 'protonmail.com', 'mail.com'
}

def extract_from_text(text: str) -> List[str]:
    """Extract emails from raw text, handling obfuscation."""
    if not text:
        return []
    
    # First, try to de-obfuscate common patterns
    cleaned_text = text
    for pattern, replacement in OBFUSCATION_PATTERNS:
        cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
    
    # Find all emails
    emails = EMAIL_PATTERN.findall(cleaned_text)
    
    # Normalize and dedupe
    seen: Set[str] = set()
    unique_emails = []
    for email in emails:
        email = email.lower().strip()
        if email not in seen and _is_valid_email(email):
            seen.add(email)
            unique_emails.append(email)
    
    return unique_emails

def _is_valid_email(email: str) -> bool:
    """Basic email validation."""
    if not email or '@' not in email:
        return False
    
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain:
        return False
    
    # Check for image file extensions (common false positive)
    image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
    if any(email.lower().endswith(ext) for ext in image_exts):
        return False
    
    return True

def classify_email(email: str) -> Dict[str, str]:
    """Classify email type and quality."""
    domain = email.split('@')[1].lower()
    
    if domain in DISPOSABLE_DOMAINS:
        return {"type": "personal", "quality": "medium"}
    
    if any(x in domain for x in ['press', 'media', 'pr', 'publicity']):
        return {"type": "press", "quality": "high"}
    
    if any(x in domain for x in ['hello', 'info', 'contact', 'hi', 'hey']):
        return {"type": "general", "quality": "medium"}
    
    return {"type": "professional", "quality": "high"}

def extract_from_bio(bio: str) -> Dict[str, Any]:
    """Extract emails from bio text."""
    emails = extract_from_text(bio)
    
    return {
        "emails": emails,
        "sources": ["bio"] * len(emails),
        "confidence": "high" if emails else "none",
        "classifications": [classify_email(e) for e in emails]
    }

def extract_from_url(url: str, deep: bool = False) -> Dict[str, Any]:
    """
    Extract emails from URL.
    Note: Deep crawling requires browser automation - placeholder for now.
    """
    # This is a placeholder - actual implementation would use browser
    # to fetch the page and extract emails
    return {
        "emails": [],
        "sources": [],
        "confidence": "low",
        "note": "URL extraction requires browser automation. Use --bio for direct text extraction."
    }

def main():
    parser = argparse.ArgumentParser(
        description="Extract email addresses from bios and websites"
    )
    parser.add_argument("--url", help="Social profile or website URL")
    parser.add_argument("--bio", help="Raw bio text")
    parser.add_argument(
        "--deep", 
        action="store_true", 
        help="Crawl linked websites (requires browser)"
    )
    parser.add_argument(
        "--output", 
        help="Output JSON file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    if not args.url and not args.bio:
        parser.error("Either --url or --bio must be provided")
    
    # Extract emails
    if args.bio:
        result = extract_from_bio(args.bio)
    else:
        result = extract_from_url(args.url, args.deep)
    
    # Add source info
    result["input"] = {
        "url": args.url,
        "bio_provided": bool(args.bio),
        "deep_crawl": args.deep
    }
    
    json_output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(json_output)

if __name__ == "__main__":
    main()
