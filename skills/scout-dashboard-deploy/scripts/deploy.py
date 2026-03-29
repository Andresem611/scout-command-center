#!/usr/bin/env python3
"""
Deploy Scout dashboard to Vercel.
Handles auth check and returns deployment URL.
"""
import subprocess
import sys
import re
from pathlib import Path

DASHBOARD_DIR = Path("/root/.openclaw/workspace/scout-dashboard-v2")

def check_auth():
    """Check if logged into Vercel."""
    try:
        result = subprocess.run(
            ["vercel", "whoami"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def deploy():
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        sys.exit(1)
    
    # Check authentication
    if not check_auth():
        print("❌ Not authenticated with Vercel")
        print("   Run: vercel login")
        sys.exit(1)
    
    print("🚀 Deploying to Vercel (production)...")
    print(f"   Directory: {DASHBOARD_DIR}")
    
    try:
        result = subprocess.run(
            ["vercel", "--prod"],
            cwd=DASHBOARD_DIR,
            capture_output=True,
            text=True
        )
        
        # Extract URL from output
        url_match = re.search(r'https?://[^\s]+\.vercel\.app', result.stdout)
        if url_match:
            url = url_match.group(0)
            print(f"✅ Deployed: {url}")
            return 0
        elif result.returncode == 0:
            print("✅ Deployed (no URL in output)")
            print(result.stdout[-500:])
            return 0
        else:
            print("❌ Deploy failed")
            print("\n--- STDERR ---")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            return 1
            
    except FileNotFoundError:
        print("❌ vercel CLI not found. Install with: npm i -g vercel")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    return deploy()

if __name__ == "__main__":
    sys.exit(main())
