#!/usr/bin/env python3
"""
Sync parsed prospect data to JSON for the dashboard.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter

# Import parse module
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_markdown import parse_all_markdown_files, prospects_to_dicts


def generate_prospect_id(prospect: Dict[str, Any], index: int) -> str:
    """
    Generate a unique ID for a prospect.
    """
    city_prefix = prospect['city'][:3].lower() if prospect['city'] else 'unk'
    handle_clean = prospect['handle'].replace('@', '').replace('.', '_')[:10]
    return f"{city_prefix}-{handle_clean}-{index:03d}"


def calculate_stats(prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate pipeline statistics.
    """
    total = len(prospects)
    
    # By stage
    stage_counts = Counter(p['status'] for p in prospects)
    
    # By city
    city_counts = Counter(p['city'] for p in prospects if p['city'])
    
    # By branch
    branch_counts = Counter(p['branch'] for p in prospects if p['branch'])
    
    # Contact info availability
    with_email = sum(1 for p in prospects if p['email'] and p['email'] not in ('N/A', '', 'DM for collabs', 'Blog contact'))
    
    return {
        "total_prospects": total,
        "by_stage": dict(stage_counts),
        "by_city": dict(city_counts),
        "by_branch": dict(branch_counts),
        "with_contactable_email": with_email,
        "dm_for_collabs": sum(1 for p in prospects if 'DM for collabs' in p['email']),
        "calculated_at": datetime.now().isoformat()
    }


def transform_prospect(prospect: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Transform parsed prospect to dashboard format.
    """
    return {
        "id": generate_prospect_id(prospect, index),
        "name": prospect['name'],
        "handle": prospect['handle'],
        "followers": prospect['followers'],
        "contact_email": prospect['email'] if prospect['email'] not in ('N/A', '', 'DM for collabs', 'Blog contact') else None,
        "stage": prospect['status'],
        "city": prospect['city'],
        "branch": prospect['branch'],
        "source": prospect['source_file'],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "days_in_stage": 0
    }


def backup_existing_json(filepath: str):
    """
    Create a backup of existing JSON file before overwriting.
    """
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{filepath}.backup.{timestamp}"
        shutil.copy2(filepath, backup_path)
        print(f"  Backed up to: {backup_path}")


def sync_to_json(
    pipeline_dir: str = None,
    dashboard_json_path: str = None,
    data_json_path: str = None
) -> Dict[str, Any]:
    """
    Main sync function: parse markdown and write to JSON targets.
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
    
    print(f"Pipeline dir: {pipeline_dir}")
    print(f"Dashboard target: {dashboard_json_path}")
    print(f"Data target: {data_json_path}")
    
    # Parse markdown files
    print("\n--- Parsing Markdown Files ---")
    prospects = parse_all_markdown_files(pipeline_dir)
    prospect_dicts = prospects_to_dicts(prospects)
    
    print(f"\nTotal prospects parsed: {len(prospect_dicts)}")
    
    # Transform to dashboard format
    print("\n--- Transforming Data ---")
    transformed_prospects = [transform_prospect(p, i) for i, p in enumerate(prospect_dicts)]
    
    # Calculate stats
    stats = calculate_stats(prospect_dicts)
    print(f"Stats: {json.dumps(stats, indent=2)}")
    
    # Build output structure
    output = {
        "prospects": transformed_prospects,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
            "source_files": list(set(p['source_file'] for p in prospect_dicts))
        },
        "stats": {
            "total_prospects": stats["total_prospects"],
            "by_stage": stats["by_stage"],
            "by_city": stats["by_city"],
            "by_branch": stats["by_branch"],
            "contacted": stats["by_stage"].get("Contacted", 0) + stats["by_stage"].get("Replied", 0) + stats["by_stage"].get("Negotiating", 0) + stats["by_stage"].get("Partner", 0),
            "replied": stats["by_stage"].get("Replied", 0) + stats["by_stage"].get("Negotiating", 0) + stats["by_stage"].get("Partner", 0),
            "last_calculated": stats["calculated_at"]
        }
    }
    
    # Ensure target directories exist
    os.makedirs(os.path.dirname(dashboard_json_path), exist_ok=True)
    os.makedirs(os.path.dirname(data_json_path), exist_ok=True)
    
    # Backup existing files
    print("\n--- Backing Up Existing Files ---")
    backup_existing_json(dashboard_json_path)
    backup_existing_json(data_json_path)
    
    # Write to targets
    print("\n--- Writing JSON Files ---")
    
    with open(dashboard_json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Written: {dashboard_json_path}")
    
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Written: {data_json_path}")
    
    print("\n--- Sync Complete ---")
    print(f"Total prospects synced: {len(transformed_prospects)}")
    
    return output


if __name__ == '__main__':
    result = sync_to_json()
    
    print("\n--- Summary ---")
    print(f"Total prospects: {result['stats']['total_prospects']}")
    print(f"By stage: {result['stats']['by_stage']}")
    print(f"By city: {result['stats']['by_city']}")
    print(f"By branch: {result['stats']['by_branch']}")
