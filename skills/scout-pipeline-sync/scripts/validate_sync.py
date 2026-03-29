#!/usr/bin/env python3
"""
Validate the sync between markdown source and JSON output.
"""

import json
import os
import glob
from typing import Dict, List, Any, Tuple


def count_prospects_in_markdown(pipeline_dir: str) -> Tuple[int, Dict[str, int]]:
    """
    Count prospect rows in all markdown files.
    Uses same logic as parse_markdown.py for consistency.
    """
    total = 0
    file_counts = {}
    
    # Import here to use actual parser logic
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from parse_markdown import parse_markdown_file
    
    pattern = os.path.join(pipeline_dir, 'PROSPECTS_*.md')
    
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)
        prospects = parse_markdown_file(filepath)
        count = len(prospects)
        file_counts[filename] = count
        total += count
    
    return total, file_counts


def count_prospects_in_json(json_path: str) -> int:
    """
    Count prospects in JSON file.
    """
    if not os.path.exists(json_path):
        return 0
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return len(data.get('prospects', []))


def validate_sync(
    pipeline_dir: str = None,
    dashboard_json_path: str = None,
    data_json_path: str = None
) -> Dict[str, Any]:
    """
    Validate sync by comparing markdown count to JSON counts.
    """
    # Determine paths - we're in skills/scout-pipeline-sync/scripts/, workspace is 3 levels up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    if pipeline_dir is None:
        pipeline_dir = os.path.join(workspace_root, 'pipeline')
    
    if dashboard_json_path is None:
        dashboard_json_path = os.path.join(workspace_root, 'scout-dashboard-v2', 'public', 'scout_data.json')
    
    if data_json_path is None:
        data_json_path = os.path.join(workspace_root, 'data', 'scout_data.json')
    
    print("=" * 60)
    print("SCOUT PIPELINE SYNC VALIDATION")
    print("=" * 60)
    
    # Count in markdown
    print("\n--- Source (Markdown) ---")
    md_total, md_files = count_prospects_in_markdown(pipeline_dir)
    print(f"Markdown files found: {len(md_files)}")
    for filename, count in sorted(md_files.items()):
        print(f"  {filename}: {count} prospects")
    print(f"Total in markdown: {md_total}")
    
    # Count in JSON files
    print("\n--- Targets (JSON) ---")
    dashboard_count = count_prospects_in_json(dashboard_json_path)
    data_count = count_prospects_in_json(data_json_path)
    
    print(f"Dashboard JSON ({dashboard_json_path}):")
    print(f"  Count: {dashboard_count}")
    print(f"  Exists: {os.path.exists(dashboard_json_path)}")
    
    print(f"\nData JSON ({data_json_path}):")
    print(f"  Count: {data_count}")
    print(f"  Exists: {os.path.exists(data_json_path)}")
    
    # Validation
    print("\n--- Validation Results ---")
    issues = []
    
    if dashboard_count != md_total:
        diff = dashboard_count - md_total
        issues.append(f"Dashboard mismatch: expected {md_total}, got {dashboard_count} (diff: {diff:+d})")
    
    if data_count != md_total:
        diff = data_count - md_total
        issues.append(f"Data JSON mismatch: expected {md_total}, got {data_count} (diff: {diff:+d})")
    
    if dashboard_count != data_count:
        issues.append(f"JSON files mismatch: dashboard={dashboard_count}, data={data_count}")
    
    # Check JSON structure
    if os.path.exists(dashboard_json_path):
        with open(dashboard_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_keys = ['prospects', 'metadata', 'stats']
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            issues.append(f"Missing keys in JSON: {missing_keys}")
        
        # Validate prospect structure
        if data.get('prospects'):
            sample = data['prospects'][0]
            required_prospect_keys = ['id', 'name', 'stage', 'city', 'branch']
            missing_prospect_keys = [k for k in required_prospect_keys if k not in sample]
            if missing_prospect_keys:
                issues.append(f"Missing prospect keys: {missing_prospect_keys}")
    
    # Report
    if issues:
        print("❌ VALIDATION FAILED")
        for issue in issues:
            print(f"  - {issue}")
        status = "FAILED"
    else:
        print("✅ VALIDATION PASSED")
        print(f"  All {md_total} prospects synced correctly")
        status = "PASSED"
    
    print("\n" + "=" * 60)
    
    return {
        "status": status,
        "markdown_total": md_total,
        "dashboard_count": dashboard_count,
        "data_count": data_count,
        "issues": issues,
        "file_breakdown": md_files
    }


if __name__ == '__main__':
    result = validate_sync()
    
    # Exit with appropriate code
    exit(0 if result['status'] == 'PASSED' else 1)
