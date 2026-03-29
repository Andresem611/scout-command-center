#!/usr/bin/env python3
"""
Check AgentMail inbox for replies and classify them
Usage: python3 check_inbox.py [--inbox keri@agentmail.to] [--since-hours 24]
"""

import os
import sys
import json
import urllib.request
import urllib.error
import argparse
from datetime import datetime, timedelta

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

def get_messages(inbox_id=None, api_key=None, since_hours=24):
    """
    Get messages from AgentMail inbox
    
    Args:
        inbox_id: Inbox ID (default: keri@agentmail.to)
        api_key: AgentMail API key
        since_hours: Only get messages from last N hours
    
    Returns:
        (messages: list, error: str or None)
    """
    load_env()
    
    api_key = api_key or os.environ.get('AGENTMAIL_API_KEY')
    inbox_id = inbox_id or os.environ.get('AGENTMAIL_INBOX_ID', 'keri@agentmail.to')
    
    if not api_key:
        return [], "AGENTMAIL_API_KEY not configured"
    
    url = f"https://api.agentmail.to/inboxes/{inbox_id}/messages"
    
    req = urllib.request.Request(
        url,
        headers={'Authorization': f'Bearer {api_key}'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            messages = result.get('messages', []) if isinstance(result, dict) else result
            
            # Filter by time if specified
            if since_hours:
                cutoff = datetime.now() - timedelta(hours=since_hours)
                filtered = []
                for msg in messages:
                    created_at = msg.get('created_at', '')
                    if created_at:
                        try:
                            msg_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if msg_time >= cutoff:
                                filtered.append(msg)
                        except:
                            filtered.append(msg)  # Include if parsing fails
                    else:
                        filtered.append(msg)
                messages = filtered
            
            return messages, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return [], f"HTTP {e.code}: {error_body}"
    except Exception as e:
        return [], f"Exception: {str(e)}"

def classify_reply(body, subject):
    """
    Classify prospect reply type
    
    Returns one of:
    - INTERESTED: Positive response, wants to proceed
    - QUESTIONS: Asking for more info
    - RATES: Asking about pricing/compensation
    - DECLINED: Not interested
    - OOO: Out of office auto-reply
    - OTHER: Unclassified
    """
    body_lower = (body or '').lower()
    subject_lower = (subject or '').lower()
    
    # Out of office
    if any(word in subject_lower for word in ['ooo', 'out of office', 'vacation', 'autoreply', 'auto-reply']):
        return 'OOO'
    
    # Declined / negative
    declined_phrases = ['not interested', 'pass', 'no thanks', 'not right now', 'not a fit', 'not for us', 'passing']
    if any(phrase in body_lower for phrase in declined_phrases):
        return 'DECLINED'
    
    # Rates / pricing
    rate_phrases = ['rate', 'payment', 'compensation', 'fee', 'budget', 'afford', 'pricing', 'cost', 'how much', 'pay']
    if any(phrase in body_lower for phrase in rate_phrases):
        return 'RATES'
    
    # Interested / positive
    interested_phrases = ['interested', 'yes', 'sounds good', 'tell me more', 'schedule', 'call', 'zoom', 'meeting', 'love to', 'would like']
    if any(phrase in body_lower for phrase in interested_phrases):
        return 'INTERESTED'
    
    # Questions
    question_words = ['question', 'what is', 'how do', 'can you', 'do you', 'is it', 'are you', 'how much', 'when', 'where']
    if any(word in body_lower for word in question_words) or '?' in body:
        return 'QUESTIONS'
    
    return 'OTHER'

def is_from_prospect(msg, our_emails=None):
    """
    Check if message is from a prospect (not from us)
    
    Args:
        msg: Message dict from AgentMail
        our_emails: List of our email addresses (default: ['keri@agentmail.to', 'keri@thoven.co'])
    """
    our_emails = our_emails or ['keri@agentmail.to', 'keri@thoven.co', 'andres@thoven.co']
    
    from_field = msg.get('from', [])
    if isinstance(from_field, list) and from_field:
        sender_email = from_field[0].get('email', '').lower()
    else:
        sender_email = str(from_field).lower()
    
    return not any(our in sender_email for our in our_emails)

def check_inbox(inbox_id=None, since_hours=24, api_key=None):
    """
    Check inbox and return classified prospect replies
    
    Returns:
        List of reply dicts with classification
    """
    messages, error = get_messages(inbox_id, api_key, since_hours)
    
    if error:
        print(f"❌ Error checking inbox: {error}")
        return []
    
    replies = []
    for msg in messages:
        # Skip if from us
        if not is_from_prospect(msg):
            continue
        
        # Skip if already read
        if msg.get('read', False):
            continue
        
        # Get sender
        from_field = msg.get('from', [])
        if isinstance(from_field, list) and from_field:
            sender = from_field[0].get('email', 'Unknown')
        else:
            sender = str(from_field)
        
        body = msg.get('body', '')
        subject = msg.get('subject', '')
        
        classification = classify_reply(body, subject)
        
        replies.append({
            'message_id': msg.get('message_id'),
            'thread_id': msg.get('thread_id'),
            'from': sender,
            'subject': subject,
            'body': body[:500] + '...' if len(body) > 500 else body,
            'classification': classification,
            'received_at': msg.get('created_at'),
            'is_hot_lead': classification in ['INTERESTED', 'QUESTIONS', 'RATES']
        })
    
    return replies

def main():
    parser = argparse.ArgumentParser(description='Check AgentMail inbox for replies')
    parser.add_argument('--inbox', default=None, help='Inbox ID')
    parser.add_argument('--since-hours', type=int, default=24, help='Hours to look back')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    print(f"📧 Checking inbox...")
    
    replies = check_inbox(
        inbox_id=args.inbox,
        since_hours=args.since_hours
    )
    
    if args.json:
        print(json.dumps(replies, indent=2))
    else:
        print(f"\n✅ Found {len(replies)} prospect reply(s)")
        
        hot_leads = [r for r in replies if r['is_hot_lead']]
        if hot_leads:
            print(f"🔔 {len(hot_leads)} HOT LEAD(S):")
            for r in hot_leads:
                print(f"\n  [{r['classification']}] From: {r['from']}")
                print(f"  Subject: {r['subject']}")
                print(f"  Preview: {r['body'][:100]}...")
        
        other = [r for r in replies if not r['is_hot_lead']]
        if other:
            print(f"\n📭 Other replies:")
            for r in other:
                print(f"  [{r['classification']}] {r['from']}: {r['subject']}")

if __name__ == "__main__":
    main()
