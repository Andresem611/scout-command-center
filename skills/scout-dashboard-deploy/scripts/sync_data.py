#!/usr/bin/env python3
"""
Sync scout_data.json to dashboard public folder.
Updates API data source and verifies consistency.
"""
import json
import shutil
import sys
from pathlib import Path

# Source data (workspace root data folder)
SOURCE_FILE = Path("/root/.openclaw/workspace/data/scout_data.json")
# Dashboard public folder (served statically)
DEST_FILE = Path("/root/.openclaw/workspace/scout-dashboard-v2/public/scout_data.json")

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def verify_data(data):
    """Basic data consistency checks."""
    issues = []
    
    if not isinstance(data, dict):
        issues.append("Root is not an object")
        return issues
    
    if "prospects" not in data:
        issues.append("Missing 'prospects' array")
    elif not isinstance(data["prospects"], list):
        issues.append("'prospects' is not an array")
    
    if "metadata" not in data:
        issues.append("Missing 'metadata' object")
    
    return issues

def main():
    print("🔄 Syncing scout_data.json...")
    
    # Check source exists
    if not SOURCE_FILE.exists():
        print(f"❌ Source not found: {SOURCE_FILE}")
        sys.exit(1)
    
    # Ensure destination directory exists
    DEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load and verify
        data = load_json(SOURCE_FILE)
        issues = verify_data(data)
        
        if issues:
            print("⚠️  Data issues found:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Copy file
        shutil.copy2(SOURCE_FILE, DEST_FILE)
        
        # Verify copy
        dest_data = load_json(DEST_FILE)
        
        source_count = len(data.get("prospects", []))
        dest_count = len(dest_data.get("prospects", []))
        
        if source_count == dest_count:
            print(f"✅ Sync complete: {dest_count} prospects")
            print(f"   Source: {SOURCE_FILE}")
            print(f"   Dest: {DEST_FILE}")
            return 0
        else:
            print(f"❌ Count mismatch: source={source_count}, dest={dest_count}")
            return 1
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
