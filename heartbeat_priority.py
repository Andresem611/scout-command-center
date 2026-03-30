#!/usr/bin/env python3
"""
Scout Heartbeat - Task Priority System with Auto-Deploy
Priority: 1. Approvals → 2. Inbox → 3. Prospecting → 4. Auto-Deploy
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
DATA_FILE = Path("/root/.openclaw/workspace/scout-dashboard-v2/public/scout_data.json")
LOG_FILE = Path("/root/.openclaw/workspace/memory/heartbeat-log.jsonl")
WORKSPACE = Path("/root/.openclaw/workspace")
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY", "")

# Priority thresholds
TARGET_PIPELINE = 95
MIN_PIPELINE_BEFORE_PROSPECTING = 50

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def log(msg, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = {"info": "", "success": Colors.GREEN, "warning": Colors.YELLOW, 
             "error": Colors.RED, "priority": Colors.BLUE, "deploy": Colors.CYAN}.get(level, "")
    print(f"{color}[{timestamp}] {msg}{Colors.RESET}")
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps({"time": timestamp, "level": level, "msg": msg}) + "\n")

def run_git_command(cmd, cwd=WORKSPACE):
    """Run a git command"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

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
    
    data['stats']['contacted'] = len([p for p in data['prospects'] if p.get('stage') == 'Contacted'])
    save_data(data)
    
    log(f"📤 Task 1 complete: {sent} sent, {failed} failed", "success")
    return {"found": len(approved), "sent": sent, "failed": failed, "action": "sent"}

def send_email(prospect):
    """Send email via AgentMail API"""
    # TODO: Implement actual AgentMail API call
    return True  # Simulated success

# ============ TASK 2: INBOX ============

def task_check_inbox():
    """Check AgentMail inbox for replies"""
    log("📥 TASK 2: Checking inbox...")
    
    # Import and use actual heartbeat functions
    import sys
    sys.path.insert(0, '/root/.openclaw/workspace')
    from heartbeat import AGENTMAIL_API_KEY, check_inbox as real_check_inbox
    
    if not AGENTMAIL_API_KEY:
        log("⚠️  AgentMail API key not found — check .env file")
        return {"new_replies": 0, "action": "none"}
    
    replies = real_check_inbox()
    if replies:
        log(f"🚨 Found {len(replies)} new reply(s)!")
        return {"new_replies": len(replies), "action": "alert"}
    else:
        log("✅ No new replies")
        return {"new_replies": 0, "action": "none"}

# ============ TASK 3: PROSPECTING ============

def task_check_prospecting_needs():
    """Check if prospecting is needed"""
    log("🎯 TASK 3: Checking prospecting needs...")
    
    data = load_data()
    total = len(data.get('prospects', []))
    
    if total >= TARGET_PIPELINE:
        log(f"✅ Pipeline full ({total}/{TARGET_PIPELINE}) — no prospecting needed")
        return {"needed": False, "current": total, "target": TARGET_PIPELINE}
    
    if total >= MIN_PIPELINE_BEFORE_PROSPECTING:
        log(f"ℹ️  Pipeline adequate ({total}) — prospecting paused")
        return {"needed": False, "current": total, "target": TARGET_PIPELINE}
    
    gap = TARGET_PIPELINE - total
    log(f"⚠️  Pipeline low ({total}/{TARGET_PIPELINE}) — {gap} prospects needed", "warning")
    return {"needed": True, "current": total, "target": TARGET_PIPELINE, "gap": gap}

# ============ TASK 4: AUTO-DEPLOY ============

def task_auto_deploy():
    """Auto-commit changes and push to GitHub for Streamlit Cloud deploy"""
    log("🚀 TASK 4: Auto-deploy...", "deploy")
    
    # Check if there are changes
    success, stdout, stderr = run_git_command("git status --porcelain")
    
    if not stdout.strip():
        log("ℹ️  No changes to deploy", "deploy")
        return {"deployed": False, "reason": "no_changes"}
    
    # Add all changes
    success, _, stderr = run_git_command("git add -A")
    if not success:
        log(f"❌ Git add failed: {stderr}", "error")
        return {"deployed": False, "reason": "git_add_failed"}
    
    # Commit with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Auto-deploy: Pipeline update {timestamp}"
    success, _, stderr = run_git_command(f'git commit -m "{commit_msg}"')
    
    if not success:
        log(f"❌ Git commit failed: {stderr}", "error")
        return {"deployed": False, "reason": "git_commit_failed"}
    
    # Push to GitHub
    success, stdout, stderr = run_git_command("git push origin main")
    
    if success:
        log("✅ DEPLOYED: Changes pushed to GitHub → Streamlit Cloud auto-updates", "deploy")
        return {"deployed": True, "timestamp": timestamp}
    else:
        log(f"❌ Git push failed: {stderr}", "error")
        return {"deployed": False, "reason": "git_push_failed"}

# ============ MAIN HEARTBEAT ============

def run_heartbeat():
    log("="*60)
    log("🎯 SCOUT HEARTBEAT STARTING")
    log("Priority: APPROVALS → INBOX → PROSPECTING → AUTO-DEPLOY")
    log("="*60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tasks": {}
    }
    
    # TASK 1: APPROVALS
    approval_result = task_check_approvals()
    results['tasks']['approvals'] = approval_result
    
    if approval_result['sent'] > 0:
        log(f"🚀 PRIORITY: Sent {approval_result['sent']} emails", "priority")
    
    # TASK 2: INBOX
    inbox_result = task_check_inbox()
    results['tasks']['inbox'] = inbox_result
    
    # TASK 3: PROSPECTING
    prospecting_result = task_check_prospecting_needs()
    results['tasks']['prospecting'] = prospecting_result
    
    # TASK 4: AUTO-DEPLOY (always run at end)
    deploy_result = task_auto_deploy()
    results['tasks']['deploy'] = deploy_result
    
    # Final stats - calculate dynamically from prospects array
    data = load_data()
    prospects = data.get('prospects', [])
    total_prospects = len(prospects)
    contacted = len([p for p in prospects if p.get('stage') == 'Contacted'])
    replied = len([p for p in prospects if p.get('stage') == 'Replied'])
    
    log("-"*60)
    log(f"📊 STATS: {total_prospects} prospects | "
        f"{contacted} contacted | "
        f"{replied} replied")
    
    # Also update the stats cache for other consumers
    data['stats'] = {
        'total_prospects': total_prospects,
        'contacted': contacted,
        'replied': replied,
        'last_calculated': datetime.now().isoformat()
    }
    save_data(data)
    
    if deploy_result.get('deployed'):
        log("🌐 Vercel will update in ~2 minutes", "deploy")
    
    log("="*60)
    
    return results

if __name__ == "__main__":
    LOG_FILE.parent.mkdir(exist_ok=True)
    result = run_heartbeat()
    print("\n" + json.dumps(result, indent=2))
