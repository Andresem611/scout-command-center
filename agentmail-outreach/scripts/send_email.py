#!/usr/bin/env python3
"""
Send email via AgentMail API
Usage: python3 send_email.py --to prospect@example.com --subject "..." --body "..."
"""

import os
import sys
import json
import urllib.request
import urllib.error
import argparse

def load_env():
    """Load environment variables from .env file"""
    env_path = "/root/.openclaw/workspace/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def send_email(to, subject, body, from_inbox=None, api_key=None):
    """
    Send email via AgentMail API
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_inbox: Sender inbox ID (default: keri@agentmail.to)
        api_key: AgentMail API key (loaded from env if not provided)
    
    Returns:
        (success: bool, message_id: str or None, error: str or None)
    """
    load_env()
    
    api_key = api_key or os.environ.get('AGENTMAIL_API_KEY')
    from_inbox = from_inbox or os.environ.get('AGENTMAIL_INBOX_ID', 'keri@agentmail.to')
    
    if not api_key:
        return False, None, "AGENTMAIL_API_KEY not configured"
    
    url = f"https://api.agentmail.to/inboxes/{from_inbox}/messages/send"
    
    payload = json.dumps({
        'to': [to],
        'subject': subject,
        'body': body
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            message_id = result.get('message_id')
            return True, message_id, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return False, None, f"HTTP {e.code}: {error_body}"
    except Exception as e:
        return False, None, f"Exception: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Send email via AgentMail')
    parser.add_argument('--to', required=True, help='Recipient email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body')
    parser.add_argument('--from', dest='from_inbox', default=None, help='Sender inbox')
    
    args = parser.parse_args()
    
    print(f"Sending to: {args.to}")
    print(f"Subject: {args.subject[:50]}...")
    
    success, msg_id, error = send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        from_inbox=args.from_inbox
    )
    
    if success:
        print(f"✅ Sent successfully!")
        print(f"   Message ID: {msg_id}")
    else:
        print(f"❌ Failed: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
