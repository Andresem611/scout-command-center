#!/usr/bin/env python3
"""
Build the Scout dashboard.
Runs npm run build and reports success/failure.
"""
import subprocess
import sys
from pathlib import Path

DASHBOARD_DIR = Path("/root/.openclaw/workspace/scout-dashboard-v2")

def main():
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        sys.exit(1)
    
    print("🔨 Building Scout dashboard...")
    print(f"   Directory: {DASHBOARD_DIR}")
    
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=DASHBOARD_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Build successful")
            # Check for .next output
            next_dir = DASHBOARD_DIR / ".next"
            if next_dir.exists():
                print(f"   Output: {next_dir}")
            return 0
        else:
            print("❌ Build failed")
            print("\n--- STDOUT ---")
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            print("\n--- STDERR ---")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            return 1
            
    except FileNotFoundError:
        print("❌ npm not found. Install Node.js first.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
