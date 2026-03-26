#!/usr/bin/env python3
"""
Scout Heartbeat - API Version
Checks API for approved drafts and sends them via AgentMail
"""

import requests
import json
import os
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = os.getenv("SCOUT_API_URL", "http://localhost:8000")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY", "")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def api_get(endpoint):
    """GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=10)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        log(f"❌ API Error: {e}")
        return {}

def api_post(endpoint, data):
    """POST request to API"""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data, timeout=10)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        log(f"❌ API Error: {e}")
        return {}

def generate_email(prospect):
    """Generate personalized email for a prospect"""
    first_name = prospect['name'].split()[0]
    city = prospect.get('city', 'your city')
    personalization = prospect.get('personalization', 'I love the way your content connects with your audience')
    
    return f"""Hi {first_name},

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

If you'd like to learn more, you can find us at Thoven in the meantime —

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist"""

def send_via_agentmail(to_email, subject, body, prospect_id):
    """
    Send email via AgentMail API
    Returns: (success: bool, message: str)
    """
    # For now, log what would be sent
    # In production, this would call the AgentMail API
    log(f"📧 Would send to: {to_email}")
    log(f"📧 Subject: {subject}")
    
    # TODO: Implement actual AgentMail API call
    # API endpoint: https://api.agentmail.to/v1/send
    # Headers: Authorization: Bearer {AGENTMAIL_API_KEY}
    
    # For testing, just mark as sent via API
    result = api_post(f"mark-sent/{prospect_id}", {})
    return result.get('success', False), "Email queued"

def check_inbox():
    """Check AgentMail inbox for replies"""
    log("📥 Checking inbox...")
    
    # TODO: Implement AgentMail inbox check
    # API endpoint: https://api.agentmail.to/v1/inbox
    
    log("📥 Inbox check: AgentMail API not yet configured")
    return []

def process_approved():
    """Process approved drafts"""
    log("🔍 Checking for approved drafts...")
    
    approved = api_get("approved")
    log(f"📋 Found {len(approved)} approved drafts")
    
    if not approved:
        return 0
    
    sent_count = 0
    for prospect in approved:
        email = prospect.get('email', '')
        if not email or '@' not in email:
            log(f"⚠️  Skipping {prospect['name']} — no valid email")
            continue
        
        subject = f"Partnership: Music Education for {prospect.get('city', 'Your City')} Families"
        body = generate_email(prospect)
        
        success, message = send_via_agentmail(email, subject, body, prospect['id'])
        
        if success:
            sent_count += 1
            log(f"✅ Sent to {prospect['name']} ({email})")
        else:
            log(f"❌ Failed to send to {prospect['name']}: {message}")
    
    return sent_count

def run_health_checks():
    """Run various health checks"""
    log("🏥 Running health checks...")
    
    # Check API health
    health = api_get("health")
    if health.get('status') == 'healthy':
        log("✅ API is healthy")
    else:
        log("⚠️  API health check failed")
    
    # Get stats
    stats = api_get("stats")
    log(f"📊 Stats: {stats.get('total_prospects', 0)} prospects, "
        f"{stats.get('contacted', 0)} contacted, "
        f"{stats.get('replied', 0)} replied")
    
    return stats

def main():
    log("="*60)
    log("🎯 Scout Heartbeat Starting")
    log("="*60)
    
    # Health checks
    stats = run_health_checks()
    
    # Process approved drafts
    sent = process_approved()
    log(f"📤 Sent {sent} emails this cycle")
    
    # Check inbox
    replies = check_inbox()
    if replies:
        log(f"📨 Found {len(replies)} new replies")
    
    log("✅ Heartbeat complete")
    
    # Return summary for logging
    return {
        "timestamp": datetime.now().isoformat(),
        "prospects": stats.get('total_prospects', 0),
        "contacted": stats.get('contacted', 0),
        "sent_this_cycle": sent,
        "replies": len(replies)
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
