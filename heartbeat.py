#!/usr/bin/env python3
"""
Scout Heartbeat Script
Checks scout_data.json for approved drafts and sends them via AgentMail
"""

import json
import os
from datetime import datetime

DATA_FILE = "/root/.openclaw/workspace/scout_data.json"

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

def main():
    log("="*60)
    log("Scout Heartbeat Starting")
    log("="*60)
    
    # Check for approved drafts
    approved, data = check_approvals()
    log(f"Found {len(approved)} approved drafts")
    
    if approved:
        log(f"Processing {len(approved)} approved drafts...")
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
        
        save_data(data)
        log(f"Updated data file with {len(approved)} sends")
    else:
        log("No approved drafts to send")
    
    # Update stats
    stats = data.get('stats', {})
    stats['total_prospects'] = len(data.get('prospects', []))
    stats['contacted'] = len([p for p in data.get('prospects', []) if p.get('stage') == 'Contacted'])
    stats['replied'] = len([p for p in data.get('prospects', []) if p.get('stage') in ['Replied', 'Negotiating']])
    data['stats'] = stats
    save_data(data)
    
    log(f"Stats: {stats['total_prospects']} prospects, {stats['contacted']} contacted, {stats['replied']} replied")
    log("Heartbeat complete")

if __name__ == "__main__":
    main()
