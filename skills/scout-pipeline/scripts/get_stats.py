#!/usr/bin/env python3
"""
Calculate pipeline metrics and stats.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_data(data_path: Path) -> dict:
    """Load scout_data.json."""
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)
    
    with open(data_path, "r") as f:
        return json.load(f)


def calculate_stats(data: dict) -> dict:
    """Calculate all pipeline metrics."""
    prospects = data.get("prospects", [])
    
    # Active prospects (non-declined)
    active = [p for p in prospects if p.get("stage") != "Declined"]
    
    # By stage
    by_stage = defaultdict(int)
    for p in active:
        by_stage[p.get("stage", "Unknown")] += 1
    
    # By city
    by_city = defaultdict(int)
    for p in active:
        by_city[p.get("city", "Unknown")] += 1
    
    # By branch (type of music school/business)
    by_branch = defaultdict(int)
    for p in active:
        by_branch[p.get("branch", "Unknown")] += 1
    
    # Conversion metrics
    partners = len([p for p in prospects if p.get("stage") == "Partner"])
    declined = len([p for p in prospects if p.get("stage") == "Declined"])
    conversion_rate = partners / (partners + declined) if (partners + declined) > 0 else 0
    
    return {
        "total": len(active),
        "by_stage": dict(by_stage),
        "by_city": dict(by_city),
        "by_branch": dict(by_branch),
        "conversion_rate": round(conversion_rate, 2),
        "partners": partners,
        "declined": declined,
    }


def format_table(stats: dict) -> str:
    """Format stats as readable table."""
    lines = []
    lines.append("=" * 40)
    lines.append("PIPELINE STATS")
    lines.append("=" * 40)
    lines.append(f"\nTotal Active Prospects: {stats['total']}")
    lines.append(f"Conversion Rate: {stats['conversion_rate']*100:.0f}%")
    lines.append(f"Partners: {stats['partners']} | Declined: {stats['declined']}")
    
    lines.append("\n--- By Stage ---")
    for stage, count in sorted(stats['by_stage'].items()):
        lines.append(f"  {stage:15} : {count}")
    
    lines.append("\n--- By City ---")
    for city, count in sorted(stats['by_city'].items(), key=lambda x: -x[1]):
        lines.append(f"  {city:15} : {count}")
    
    lines.append("\n--- By Branch ---")
    for branch, count in sorted(stats['by_branch'].items(), key=lambda x: -x[1]):
        lines.append(f"  {branch:15} : {count}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get pipeline stats")
    parser.add_argument("--data-path", type=Path, default=Path("data/scout_data.json"),
                        help="Path to scout_data.json")
    parser.add_argument("--format", choices=["json", "table"], default="json",
                        help="Output format")
    
    args = parser.parse_args()
    
    data = load_data(args.data_path)
    stats = calculate_stats(data)
    
    if args.format == "json":
        print(json.dumps(stats, indent=2))
    else:
        print(format_table(stats))


if __name__ == "__main__":
    main()
