#!/usr/bin/env python3
"""
Check deployment status and test API endpoints.
Returns health status of the dashboard.
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

DASHBOARD_DIR = Path("/root/.openclaw/workspace/scout-dashboard-v2")
DATA_FILE = DASHBOARD_DIR / "public" / "scout_data.json"

def get_deployment_url():
    """Get URL from Vercel project."""
    try:
        result = subprocess.run(
            ["vercel", "ls", "--json"],
            cwd=DASHBOARD_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            deployments = json.loads(result.stdout)
            if deployments:
                return deployments[0].get("url")
    except Exception:
        pass
    return None

def test_local_data():
    """Check local scout_data.json."""
    if not DATA_FILE.exists():
        return {"ok": False, "error": "scout_data.json not found"}
    
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
        
        prospects = data.get("prospects", [])
        return {
            "ok": True,
            "prospects": len(prospects),
            "last_updated": data.get("metadata", {}).get("last_updated", "unknown")
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def test_endpoint(base_url, path):
    """Test an API endpoint."""
    try:
        url = f"{base_url}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"ok": True, "status": resp.status}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    print("🏥 Checking dashboard health...\n")
    
    # Check local data
    print("📁 Local data:")
    data_status = test_local_data()
    if data_status["ok"]:
        print(f"   ✅ scout_data.json: {data_status['prospects']} prospects")
        print(f"   🕐 Last updated: {data_status['last_updated']}")
    else:
        print(f"   ❌ {data_status['error']}")
    
    # Check build output
    print("\n🔨 Build status:")
    next_dir = DASHBOARD_DIR / ".next"
    if next_dir.exists():
        print("   ✅ .next/ directory exists")
    else:
        print("   ⚠️  .next/ not found — run build.py first")
    
    # Check Vercel deployment
    print("\n🌐 Vercel deployment:")
    url = get_deployment_url()
    if url:
        full_url = f"https://{url}"
        print(f"   URL: {full_url}")
        
        # Test endpoints
        print("\n   Testing endpoints:")
        for endpoint in ["/api/status", "/api/prospects"]:
            result = test_endpoint(full_url, endpoint)
            status = "✅" if result["ok"] else "❌"
            print(f"   {status} {endpoint}", end="")
            if result["ok"]:
                print(f" (HTTP {result['status']})")
            else:
                print(f" - {result['error']}")
    else:
        print("   ⚠️  No Vercel deployment found")
    
    print("\n✨ Check complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
