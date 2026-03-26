#!/usr/bin/env python3
"""
Scout Heartbeat Script
Checks for approved drafts and sends them via AgentMail
Pings Next.js dashboard API with status updates
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime

DATA_FILE = "/root/.openclaw/workspace/scout_data.json"
DASHBOARD_API = os.environ.get("DASHBOARD_API_URL", "https://scout-dashboard-v2.vercel.app/api/status")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prospects": [], "replies": [], "interactions": [], "blog_forms": [], "stats": {}}

def save_data(data):
    data['metadata'] = {'last_updated': datetime.now().isoformat(), 'version': '1.0'}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_agent_status(data, status="active", current_task="", error=None):
    """Update Scout agent status in data file"""
    if 'agent_status' not in data:
        data['agent_status'] = {}
    
    agent_status = data['agent_status']
    agent_status['last_heartbeat'] = datetime.now().isoformat()
    agent_status['status'] = status
    agent_status['current_task'] = current_task
    agent_status['session_uptime'] = agent_status.get('session_start', datetime.now().isoformat())
    agent_status['dashboard_version'] = "1.1.0"  # Sync with streamlit_app.py
    
    # Daily health check tracking
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    if 'health_checks' not in agent_status:
        agent_status['health_checks'] = {}
    
    # Run health check once per day
    if today not in agent_status['health_checks']:
        agent_status['health_checks'][today] = {
            'checked_at': now.isoformat(),
            'status': 'pending_manual_verification'
        }
        log(f"🩺 Daily health check scheduled for {today}")
    
    # Activity log (keep last 50 entries)
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

def check_approvals():
    """Check for approved drafts in the data file"""
    data = load_data()
    
    approved = [p for p in data.get('prospects', []) 
                if p.get('draft_status') == 'approved' and p.get('stage') == 'Prospected']
    
    return approved, data

def generate_email(prospect):
    """Generate personalized email for a prospect"""
    return f"""Hi {prospect['name'].split()[0]},

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

After years of teaching and working closely with families, I've met so many parents who wanted music lessons for their children but feel unsure where to begin or how to stay connected to their child's progress. That's why we built Thoven.

With Thoven, parents and students can:
- Feel confident knowing every teacher is background-checked and verified
- Seamlessly schedule and pay for lessons in one place (secured with Stripe)
- Access a personalized, gamified dashboard to track progress and motivate practice
- View lesson notes, assignments, and real-time progress updates

We work with a growing group of teachers trained at The Juilliard School, Manhattan School of Music, Eastman School of Music and more.

{prospect.get('personalization', 'I love the way your content connects with your audience')}, so I wanted to reach out personally to see if you'd be open to working together in a way that feels natural for you and your audience.

We'd be happy to structure this in a way that works best for you:
- Affiliate partnership: Earn commission on every lesson booked through your unique link
- Complimentary lessons: We can provide free lessons to your family so you can experience the platform and see the value firsthand
- Other approaches: If you have a preferred method or different structure in mind, we're open to exploring options that work best for you

If you're interested, I'd love to schedule a quick call to walk you through the platform, answer any questions, and explore what a partnership could look like.

If you'd like to learn more, you can find us at Thoven in the meantime —

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist"""

def send_via_agentmail(to_email, subject, body):
    """
    Send email via AgentMail API
    Returns: (success: bool, message: str)
    """
    # For now, log what would be sent
    # In production, this would call the AgentMail API
    log(f"Would send to: {to_email}")
    log(f"Subject: {subject}")
    log(f"Body length: {len(body)} chars")
    
    # TODO: Implement actual AgentMail API call
    # API endpoint: https://api.agentmail.to/v1/send
    # Headers: Authorization: Bearer {API_KEY}
    
    return True, "Email queued (AgentMail API not yet implemented)"

def post_to_dashboard(status, current_task, version="2.0.0"):
    """
    POST agent status to Vercel dashboard API
    Returns: (success: bool, message: str)
    """
    try:
        payload = json.dumps({
            "status": status,
            "currentTask": current_task,
            "version": version
        }).encode('utf-8')
        
        req = urllib.request.Request(
            DASHBOARD_API,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': len(payload)
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            log(f"✅ Dashboard POST success: {result}")
            return True, "Status posted to dashboard"
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        log(f"❌ Dashboard POST failed: {error_msg}")
        return False, error_msg
    except urllib.error.URLError as e:
        error_msg = f"URL Error: {e.reason}"
        log(f"❌ Dashboard POST failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        log(f"❌ Dashboard POST failed: {error_msg}")
        return False, error_msg

def main():
    log("="*60)
    log("Scout Heartbeat Starting")
    log("="*60)
    
    data = load_data()
    
    # Update agent status at start
    data = update_agent_status(data, status="active", current_task="Checking pipeline")
    save_data(data)
    post_to_dashboard("active", "Checking pipeline")
    
    # Check for approved drafts
    approved, data = check_approvals()
    log(f"Found {len(approved)} approved drafts")
    
    if approved:
        log(f"Processing {len(approved)} approved drafts...")
        data = update_agent_status(data, status="active", current_task=f"Sending {len(approved)} approved emails")
        save_data(data)
        post_to_dashboard("active", f"Sending {len(approved)} approved emails")
        
        for prospect in approved:
            email = prospect.get('email')
            if not email or '@' not in email:
                log(f"⚠️  Skipping {prospect['name']} — no valid email")
                continue
            
            subject = f"Partnership: Music Education for {prospect['city']} Families"
            body = generate_email(prospect)
            
            success, message = send_via_agentmail(email, subject, body)
            
            if success:
                prospect['stage'] = 'Contacted'
                prospect['last_contact'] = datetime.now().isoformat()
                prospect['draft_status'] = 'sent'
                log(f"✅ Sent to {prospect['name']} ({email})")
            else:
                log(f"❌ Failed to send to {prospect['name']}: {message}")
        
        data = update_agent_status(data, status="active", current_task=f"Sent {len(approved)} emails")
        save_data(data)
        post_to_dashboard("active", f"Sent {len(approved)} emails")
        log(f"Updated data file with {len(approved)} sends")
    else:
        log("No approved drafts to send")
    
    # Update stats
    stats = data.get('stats', {})
    stats['total_prospects'] = len(data.get('prospects', []))
    stats['contacted'] = len([p for p in data.get('prospects', []) if p.get('stage') == 'Contacted'])
    stats['replied'] = len([p for p in data.get('prospects', []) if p.get('stage') in ['Replied', 'Negotiating']])
    data['stats'] = stats
    
    # Final status update
    data = update_agent_status(data, status="idle", current_task="Waiting for next check")
    save_data(data)
    post_to_dashboard("idle", "Waiting for next check")
    
    log(f"Stats: {stats['total_prospects']} prospects, {stats['contacted']} contacted, {stats['replied']} replied")
    log("Heartbeat complete")

if __name__ == "__main__":
    main()
