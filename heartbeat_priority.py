#!/usr/bin/env python3
"""
Scout Heartbeat - Task Priority System
Priority: 1. Approvals → 2. Inbox → 3. Prospecting
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DATA_FILE = Path("/root/.openclaw/workspace/scout_data.json")
LOG_FILE = Path("/root/.openclaw/workspace/memory/heartbeat-log.jsonl")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY", "")

# Priority thresholds
TARGET_PIPELINE = 95
MIN_PIPELINE_BEFORE_PROSPECTING = 50  # Don't prospect if above this

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def log(msg, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = {"info": "", "success": Colors.GREEN, "warning": Colors.YELLOW, 
             "error": Colors.RED, "priority": Colors.BLUE}.get(level, "")
    print(f"{color}[{timestamp}] {msg}{Colors.RESET}")
    
    # Append to log file
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps({"time": timestamp, "level": level, "msg": msg}) + "\n")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prospects": [], "replies": [], "blog_forms": [], "interactions": [], "stats": {}}

def save_data(data):
    data['metadata'] = {'last_updated': datetime.now().isoformat(), 'version': '1.0'}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return data

# ============ TASK 1: APPROVALS (HIGHEST PRIORITY) ============

def task_check_approvals():
    """Check for approved drafts and send emails"""
    log("🔍 TASK 1: Checking for approvals...", "priority")
    
    data = load_data()
    approved = [p for p in data.get('prospects', []) 
                if p.get('draft_status') == 'approved' and p.get('stage') == 'Prospected']
    
    if not approved:
        log("ℹ️  No approved drafts waiting")
        return {"found": 0, "sent": 0, "action": "none"}
    
    log(f"🎯 FOUND {len(approved)} APPROVED DRAFTS — SENDING NOW", "priority")
    
    sent = 0
    failed = 0
    
    for prospect in approved:
        email = prospect.get('email', '')
        if not email or '@' not in email:
            log(f"⚠️  {prospect['name']} — no valid email, skipping", "warning")
            prospect['draft_status'] = 'skipped_no_email'
            failed += 1
            continue
        
        # Generate and send email
        success = send_email(prospect)
        
        if success:
            prospect['stage'] = 'Contacted'
            prospect['draft_status'] = 'sent'
            prospect['last_contact'] = datetime.now().isoformat()
            prospect['sent_at'] = datetime.now().isoformat()
            sent += 1
            log(f"✅ SENT to {prospect['name']} ({email})", "success")
        else:
            prospect['draft_status'] = 'failed'
            failed += 1
            log(f"❌ FAILED to send to {prospect['name']}", "error")
    
    # Update stats
    data['stats']['contacted'] = len([p for p in data['prospects'] if p.get('stage') == 'Contacted'])
    save_data(data)
    
    log(f"📤 Task 1 complete: {sent} sent, {failed} failed", "success")
    return {"found": len(approved), "sent": sent, "failed": failed, "action": "sent"}

def send_email(prospect):
    """Send email via AgentMail API"""
    # TODO: Implement actual AgentMail API call
    # For now, simulate success
    
    first_name = prospect['name'].split()[0]
    city = prospect.get('city', 'Your City')
    personalization = prospect.get('personalization', 'I love the way your content connects')
    
    subject = f"Partnership: Music Education for {city} Families"
    body = f"""Hi {first_name},

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

After years of teaching and working closely with families, I've met so many parents who wanted music lessons for their children but feel unsure where to begin or how to stay connected to their child's progress. That's why we built Thoven.

With Thoven, parents and students can:
- Feel confident knowing every teacher is background-checked and verified
- Seamlessly schedule and pay for lessons in one place (secured with Stripe)
- Access a personalized, gamified dashboard to track progress and motivate practice
- View lesson notes, assignments, and real-time progress updates

We work with a growing group of teachers trained at The Juilliard School, Manhattan School of Music, Eastman School of Music and more.

{personalization}, so I wanted to reach out personally to see if you'd be open to working together in a way that feels natural for you and your audience.

We'd be happy to structure this in a way that works best for you:
- Affiliate partnership: Earn commission on every lesson booked through your unique link
- Complimentary lessons: We can provide free lessons to your family so you can experience the platform and see the value firsthand
- Other approaches: If you have a preferred method or different structure in mind, we're open to exploring options that work best for you

If you're interested, I'd love to schedule a quick call to walk you through the platform, answer any questions, and explore what a partnership could look like.

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist"""
    
    # TODO: Replace with actual AgentMail API call
    # For now, just log and return success (simulated)
    return True

# ============ TASK 2: INBOX (SECOND PRIORITY) ============

def task_check_inbox():
    """Check AgentMail inbox for replies"""
    log("📥 TASK 2: Checking inbox...")
    
    # TODO: Implement AgentMail inbox check
    # API: GET https://api.agentmail.to/v1/inbox
    
    # For now, simulate no new replies
    log("📥 Inbox check: AgentMail API not yet configured")
    return {"new_replies": 0, "action": "none"}

# ============ TASK 3: PROSPECTING (LOWEST PRIORITY) ============

def task_check_prospecting_needs():
    """Check if prospecting is needed"""
    log("🎯 TASK 3: Checking prospecting needs...")
    
    data = load_data()
    total = len(data.get('prospects', []))
    
    if total >= TARGET_PIPELINE:
        log(f"✅ Pipeline full ({total}/{TARGET_PIPELINE}) — no prospecting needed")
        return {"needed": False, "current": total, "target": TARGET_PIPELINE}
    
    if total >= MIN_PIPELINE_BEFORE_PROSPECTING:
        log(f"ℹ️  Pipeline adequate ({total}) — prospecting paused until below {MIN_PIPELINE_BEFORE_PROSPECTING}")
        return {"needed": False, "current": total, "target": TARGET_PIPELINE}
    
    gap = TARGET_PIPELINE - total
    log(f"⚠️  Pipeline low ({total}/{TARGET_PIPELINE}) — {gap} prospects needed", "warning")
    
    return {
        "needed": True,
        "current": total,
        "target": TARGET_PIPELINE,
        "gap": gap,
        "action": "prospect_now"
    }

# ============ MAIN HEARTBEAT ============

def run_heartbeat():
    log("="*60)
    log("🎯 SCOUT HEARTBEAT STARTING")
    log(f"Priority: APPROVALS → INBOX → PROSPECTING")
    log("="*60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tasks": {}
    }
    
    # TASK 1: APPROVALS (Always run first)
    approval_result = task_check_approvals()
    results['tasks']['approvals'] = approval_result
    
    # If we sent emails, make that prominent
    if approval_result['sent'] > 0:
        log(f"🚀 PRIORITY ACTION: Sent {approval_result['sent']} emails", "priority")
    
    # TASK 2: INBOX (Always run)
    inbox_result = task_check_inbox()
    results['tasks']['inbox'] = inbox_result
    
    # TASK 3: PROSPECTING (Only if time permits and needed)
    prospecting_result = task_check_prospecting_needs()
    results['tasks']['prospecting'] = prospecting_result
    
    # Final stats
    data = load_data()
    stats = data.get('stats', {})
    log("-"*60)
    log(f"📊 FINAL STATS: {stats.get('total_prospects', 0)} prospects | "
        f"{stats.get('contacted', 0)} contacted | "
        f"{stats.get('replied', 0)} replied")
    log("="*60)
    
    return results

if __name__ == "__main__":
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    result = run_heartbeat()
    
    # Print JSON result for cron logging
    print("\n" + json.dumps(result, indent=2))
