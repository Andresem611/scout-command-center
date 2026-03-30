#!/usr/bin/env python3
"""
Scout Heartbeat Script - AgentMail Integration
Checks for approved drafts, sends via AgentMail, checks inbox for replies
Pings dashboard API with status updates
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# Configuration
DATA_FILE = "/root/.openclaw/workspace/scout-dashboard-v2/public/scout_data.json"
DRAFT_QUEUE_FILE = "/root/.openclaw/workspace/draft_queue.json"
DASHBOARD_API = os.environ.get("DASHBOARD_API_URL", "https://scout-dashboard-tau.vercel.app/api/status")
AGENTMAIL_BASE_URL = "https://api.agentmail.to"

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

# Load .env file
load_env()

AGENTMAIL_API_KEY = os.environ.get("AGENTMAIL_API_KEY", "")
AGENTMAIL_INBOX_ID = os.environ.get("AGENTMAIL_INBOX_ID", "keri@agentmail.to")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prospects": [], "replies": [], "interactions": [], "blog_forms": [], "stats": {}}

def save_data(data):
    data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'version': '1.1',
        'updated_by': 'scout-heartbeat'
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_draft_queue():
    if os.path.exists(DRAFT_QUEUE_FILE):
        with open(DRAFT_QUEUE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_draft_queue(queue):
    with open(DRAFT_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def update_agent_status(data, status="active", current_task="", error=None):
    """Update Scout agent status in data file"""
    if 'agent_status' not in data:
        data['agent_status'] = {}
    
    agent_status = data['agent_status']
    agent_status['last_heartbeat'] = datetime.now().isoformat()
    agent_status['status'] = status
    agent_status['current_task'] = current_task
    agent_status['session_uptime'] = agent_status.get('session_start', datetime.now().isoformat())
    agent_status['dashboard_version'] = "1.1.0"
    
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    if 'health_checks' not in agent_status:
        agent_status['health_checks'] = {}
    
    if today not in agent_status['health_checks']:
        agent_status['health_checks'][today] = {
            'checked_at': now.isoformat(),
            'status': 'healthy'
        }
    
    if 'activity_log' not in agent_status:
        agent_status['activity_log'] = []
    
    if current_task:
        agent_status['activity_log'].insert(0, {
            'time': datetime.now().isoformat(),
            'task': current_task
        })
        agent_status['activity_log'] = agent_status['activity_log'][:50]
    
    if error:
        agent_status['last_error'] = {
            'time': datetime.now().isoformat(),
            'message': str(error)
        }

    data['agent_status'] = agent_status
    return data

def commit_and_push():
    """Auto-commit data changes and push to GitHub for Vercel deployment"""
    try:
        import subprocess
        import os
        
        workspace = "/root/.openclaw/workspace"
        os.chdir(workspace)
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=workspace
        )
        
        if not result.stdout.strip():
            return  # No changes to commit
        
        # Stage data file changes
        subprocess.run(
            ["git", "add", "scout-dashboard-v2/public/scout_data.json", "data/scout_data.json"],
            capture_output=True,
            cwd=workspace
        )
        
        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ["git", "commit", "-m", f"Auto: Heartbeat data update {timestamp}"],
            capture_output=True,
            cwd=workspace
        )
        
        # Push to GitHub
        subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            cwd=workspace
        )
        
        log("🚀 Data synced to GitHub → Vercel will update")
    except Exception as e:
        log(f"⚠️  Git push failed: {e}")

# ==================== AGENTMAIL API FUNCTIONS ====================

def agentmail_request(endpoint, method="GET", data=None):
    """Make authenticated request to AgentMail API"""
    if not AGENTMAIL_API_KEY:
        return None, "AGENTMAIL_API_KEY not configured"
    
    url = f"{AGENTMAIL_BASE_URL}{endpoint}"
    headers = {
        'Authorization': f'Bearer {AGENTMAIL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        payload = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method=method
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result, None
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return None, f"HTTP {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return None, f"URL Error: {e.reason}"
    except Exception as e:
        return None, f"Exception: {str(e)}"

def check_inbox():
    """Check AgentMail inbox for new replies"""
    log("📧 Checking AgentMail inbox...")
    
    if not AGENTMAIL_API_KEY:
        log("⚠️  AgentMail API key not configured — inbox check skipped")
        return []
    
    # Get inbox ID (using the email as inbox_id)
    inbox_id = AGENTMAIL_INBOX_ID
    
    # Get recent messages
    result, error = agentmail_request(f"/inboxes/{inbox_id}/messages")
    
    if error:
        log(f"❌ Inbox check failed: {error}")
        return []
    
    messages = result.get('messages', []) if isinstance(result, dict) else result
    log(f"✅ Found {len(messages)} email(s) in inbox")
    
    # Filter for unread replies (not from Scout/Keri)
    replies = []
    for msg in messages:
        sender = msg.get('from', [{}])[0].get('email', '').lower() if isinstance(msg.get('from'), list) else str(msg.get('from', '')).lower()
        is_read = msg.get('read', False)
        
        if 'keri' not in sender and 'thoven' not in sender and not is_read:
            replies.append({
                'id': msg.get('message_id'),
                'from': sender,
                'subject': msg.get('subject'),
                'body': msg.get('body', '')[:500] + '...' if len(msg.get('body', '')) > 500 else msg.get('body', ''),
                'received_at': msg.get('created_at'),
                'thread_id': msg.get('thread_id')
            })
    
    if replies:
        log(f"🔔 {len(replies)} new reply(s) from prospects!")
        for r in replies:
            log(f"   → From: {r['from']} | Subject: {r['subject']}")
    else:
        log("📭 No new prospect replies")
    
    return replies

def send_via_agentmail(to_email, subject, body, reply_to=None):
    """
    Send email via AgentMail API
    Returns: (success: bool, message: str, email_id: str or None)
    """
    if not AGENTMAIL_API_KEY:
        log(f"⚠️  AgentMail API key not configured — email to {to_email} not sent")
        return False, "AGENTMAIL_API_KEY not configured", None
    
    inbox_id = AGENTMAIL_INBOX_ID
    
    payload = {
        'to': [to_email],
        'subject': subject,
        'body': body
    }
    
    log(f"📤 Sending via AgentMail to: {to_email}")
    log(f"   Subject: {subject[:60]}...")
    
    result, error = agentmail_request(f"/inboxes/{inbox_id}/messages/send", method="POST", data=payload)
    
    if error:
        log(f"❌ AgentMail send failed: {error}")
        return False, error, None
    
    email_id = result.get('message_id') or result.get('id')
    log(f"✅ Email sent successfully (ID: {email_id[:30]}...)")
    return True, "Sent", email_id

# ==================== CORE FUNCTIONS ====================

def check_approvals_queue():
    """Check draft_queue.json for approved drafts ready to send"""
    queue = load_draft_queue()
    approved = [d for d in queue if d.get('status') == 'approved']
    return approved, queue

def classify_reply(email_body, subject):
    """Classify prospect reply type"""
    body_lower = (email_body or '').lower()
    subject_lower = (subject or '').lower()
    
    # Interested / positive signals
    if any(word in body_lower for word in ['interested', 'yes', 'sounds good', 'tell me more', 'schedule', 'call', 'zoom']):
        return 'INTERESTED'
    
    # Questions
    if any(word in body_lower for word in ['question', 'how much', 'what is', 'can you', 'do you', 'price', 'cost']):
        return 'QUESTIONS'
    
    # Declined / negative
    if any(word in body_lower for word in ['not interested', 'pass', 'no thanks', 'not right now', 'busy', 'not a fit']):
        return 'DECLINED'
    
    # Rates/negotiation
    if any(word in body_lower for word in ['rate', 'payment', 'compensation', 'fee', 'budget', 'afford']):
        return 'RATES'
    
    # Out of office
    if any(word in subject_lower for word in ['ooo', 'out of office', 'vacation', 'autoreply']):
        return 'OOO'
    
    return 'OTHER'

def main():
    log("="*60)
    log("🤖 Scout Heartbeat Starting")
    log("="*60)
    
    data = load_data()
    
    # Check AgentMail configuration
    agentmail_ready = bool(AGENTMAIL_API_KEY)
    if agentmail_ready:
        log(f"✅ AgentMail active: {AGENTMAIL_INBOX_ID}")
    else:
        log(f"⚠️  AgentMail API key not found — check .env file")
    
    # Update agent status
    data = update_agent_status(data, status="active", current_task="Starting heartbeat cycle")
    save_data(data)
    
    # ==================== TASK 1: INBOX CHECK ====================
    log("\n📋 TASK 1: Inbox Check")
    replies = check_inbox()
    
    if replies:
        data = update_agent_status(data, status="alert", current_task=f"Processing {len(replies)} new replies")
        save_data(data)
        
        # Store replies in data file
        if 'replies' not in data:
            data['replies'] = []
        
        for reply in replies:
            classification = classify_reply(reply['body'], reply['subject'])
            reply['classification'] = classification
            reply['processed_at'] = datetime.now().isoformat()
            data['replies'].insert(0, reply)
            
            log(f"\n🔔 NEW REPLY [{classification}]")
            log(f"   From: {reply['from']}")
            log(f"   Subject: {reply['subject']}")
            log(f"   Preview: {reply['body'][:100]}...")
            
            # Alert for hot leads
            if classification in ['INTERESTED', 'QUESTIONS', 'RATES']:
                log(f"   🚨 HOT LEAD — needs Andres attention!")
        
        data['replies'] = data['replies'][:100]  # Keep last 100
        save_data(data)
    else:
        log("✅ Inbox clean")
    
    # ==================== TASK 2: APPROVALS QUEUE ====================
    log("\n📋 TASK 2: Approvals Queue")
    approved, queue = check_approvals_queue()
    log(f"Found {len(approved)} approved drafts ready to send")
    
    if approved and agentmail_ready:
        data = update_agent_status(data, status="active", current_task=f"Sending {len(approved)} approved emails")
        save_data(data)
        
        for draft in approved:
            email = draft.get('email')
            if not email or '@' not in email:
                log(f"⚠️  Skipping {draft.get('prospect', 'Unknown')} — no valid email")
                continue
            
            subject = draft.get('subject', 'Partnership opportunity')
            body = draft.get('body', '')
            
            success, message, email_id = send_via_agentmail(email, subject, body)
            
            if success:
                draft['status'] = 'sent'
                draft['sent_at'] = datetime.now().isoformat()
                draft['email_id'] = email_id
                log(f"✅ Sent to {draft.get('prospect')} ({email})")
                
                # Update prospect stage in main data
                for p in data.get('prospects', []):
                    if p.get('email') == email:
                        p['stage'] = 'Contacted'
                        p['last_contact'] = datetime.now().isoformat()
                        break
            else:
                log(f"❌ Failed to send to {draft.get('prospect')}: {message}")
                draft['status'] = 'failed'
                draft['error'] = message
        
        save_draft_queue(queue)
        log(f"✅ Updated draft queue with send results")
        
    elif approved and not agentmail_ready:
        log(f"⏸️  {len(approved)} drafts approved but API key missing — cannot send")
    else:
        log("✅ No approved drafts waiting")
    
    # ==================== TASK 3: PROSPECTING CHECK ====================
    log("\n📋 TASK 3: Prospecting Check")
    total_prospects = len(data.get('prospects', []))
    target = 95
    
    if total_prospects >= target:
        log(f"✅ Pipeline full: {total_prospects}/{target} prospects — no prospecting needed")
    else:
        gap = target - total_prospects
        log(f"📉 Pipeline gap: {gap} prospects needed")
        log(f"   Next action: Identify weakest branch and prospect")
    
    # ==================== TASK 4: UPDATE STATS ====================
    log("\n📋 TASK 4: Update Stats")
    stats = data.get('stats', {})
    stats['total_prospects'] = len(data.get('prospects', []))
    stats['contacted'] = len([p for p in data.get('prospects', []) if p.get('stage') == 'Contacted'])
    stats['replied'] = len([p for p in data.get('prospects', []) if p.get('stage') in ['Replied', 'Negotiating']])
    stats['inbox_configured'] = agentmail_ready
    stats['last_heartbeat'] = datetime.now().isoformat()
    data['stats'] = stats
    
    # Final status
    data = update_agent_status(data, status="idle", current_task="Waiting for next check")
    save_data(data)
    
    # Auto-commit and push data changes to GitHub for Vercel deployment
    commit_and_push()
    
    # ==================== SUMMARY ====================
    log("\n" + "="*60)
    log("📊 HEARTBEAT SUMMARY")
    log("="*60)
    log(f"Pipeline: {stats['total_prospects']} prospects | {stats['contacted']} contacted | {stats['replied']} replied")
    log(f"Inbox: {len(replies)} new replies" if replies else "Inbox: Clean")
    log(f"Sent: {len([d for d in queue if d.get('status') == 'sent'])} emails this cycle")
    log(f"AgentMail: {'✅ Connected' if agentmail_ready else '⚠️  Not configured'}")
    log("Heartbeat complete ✅")

if __name__ == "__main__":
    main()
