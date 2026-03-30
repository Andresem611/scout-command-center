#!/usr/bin/env python3
"""
Branch Gap Analyzer - Identifies which pipeline branches need prospecting
AGENTS.md Skill: skill-pipeline/scripts/analyze_gaps.py
"""

import json
import sys
from typing import Dict, List, Tuple

# Branch targets as defined in pipeline strategy
BRANCH_TARGETS = {
    "Mom Influencers": 95,  # Already overfilled at 342
    "Mom Blog": 15,         # Only 5 - NEEDS WORK
    "Homeschool": 35,       # Only 17 - NEEDS WORK
}

# City distribution targets (no city > 30%)
CITY_TARGETS = {
    "max_percentage": 30,
    "min_percentage": 5,
}

def analyze_branch_gaps(data_file: str = "/root/.openclaw/workspace/scout-dashboard-v2/public/scout_data.json") -> Dict:
    """Analyze pipeline and identify which branches/cities need work"""
    
    with open(data_file) as f:
        data = json.load(f)
    
    prospects = data.get("prospects", [])
    total = len(prospects)
    
    # Count by branch
    branch_counts = {}
    for p in prospects:
        b = p.get("branch", "Unknown")
        branch_counts[b] = branch_counts.get(b, 0) + 1
    
    # Count by city
    city_counts = {}
    for p in prospects:
        c = p.get("city", "Unknown")
        city_counts[c] = city_counts.get(c, 0) + 1
    
    # Calculate gaps
    branch_gaps = []
    for branch, target in BRANCH_TARGETS.items():
        current = branch_counts.get(branch, 0)
        gap = target - current
        percentage = (current / target * 100) if target > 0 else 0
        
        branch_gaps.append({
            "branch": branch,
            "current": current,
            "target": target,
            "gap": gap,
            "percentage": percentage,
            "needs_work": gap > 0,
            "priority": gap if gap > 0 else 0
        })
    
    # Sort by priority (largest gap first)
    branch_gaps.sort(key=lambda x: -x["priority"])
    
    # Check city distribution
    city_issues = []
    if total > 0:
        for city, count in city_counts.items():
            percentage = (count / total) * 100
            if percentage > CITY_TARGETS["max_percentage"]:
                city_issues.append({
                    "city": city,
                    "count": count,
                    "percentage": percentage,
                    "issue": "over_represented"
                })
            elif city != "Unknown" and percentage < CITY_TARGETS["min_percentage"]:
                city_issues.append({
                    "city": city,
                    "count": count,
                    "percentage": percentage,
                    "issue": "under_represented"
                })
    
    return {
        "total_prospects": total,
        "branch_analysis": branch_gaps,
        "city_issues": city_issues,
        "weakest_branch": branch_gaps[0] if branch_gaps and branch_gaps[0]["needs_work"] else None,
        "overall_status": "needs_rebalancing" if any(g["needs_work"] for g in branch_gaps) else "balanced"
    }

def get_next_prospecting_target(analysis: Dict) -> Dict:
    """Determine what to prospect next based on gaps (per AGENTS.md routing)"""
    
    weakest = analysis.get("weakest_branch")
    if weakest:
        return {
            "action": "prospect_branch",
            "branch": weakest["branch"],
            "target_count": weakest["gap"],
            "reason": f"{weakest['branch']} is {weakest['gap']} prospects below target"
        }
    
    # If all branches at target, check city distribution
    city_issues = analysis.get("city_issues", [])
    under_represented = [c for c in city_issues if c.get("issue") == "under_represented"]
    
    if under_represented:
        return {
            "action": "prospect_city",
            "city": under_represented[0]["city"],
            "reason": f"{under_represented[0]['city']} is under-represented ({under_represented[0]['percentage']:.1f}%)"
        }
    
    return {
        "action": "none",
        "reason": "All branches at target, no prospecting needed"
    }

def print_json_output(analysis: Dict, next_action: Dict):
    """Print machine-readable JSON output for skill dispatch"""
    print(f"ANALYSIS:{json.dumps(analysis)}")
    print(f"NEXT_ACTION:{json.dumps(next_action)}")

def main():
    # Check for --json flag
    json_mode = "--json" in sys.argv
    
    analysis = analyze_branch_gaps()
    next_action = get_next_prospecting_target(analysis)
    
    if json_mode:
        # Machine-readable output for AGENTS.md routing
        print_json_output(analysis, next_action)
    else:
        # Human-readable output
        print("=" * 60)
        print("PIPELINE BRANCH ANALYSIS")
        print("=" * 60)
        print(f"\nTotal Prospects: {analysis['total_prospects']}")
        print(f"Overall Status: {analysis['overall_status']}")
        
        print("\n--- Branch Gaps ---")
        for branch in analysis["branch_analysis"]:
            status = "🔴 NEEDS WORK" if branch["needs_work"] else "✅ OK"
            print(f"{branch['branch']}: {branch['current']}/{branch['target']} ({branch['percentage']:.0f}%) {status}")
            if branch["needs_work"]:
                print(f"   → Gap: {branch['gap']} prospects needed")
        
        if analysis["city_issues"]:
            print("\n--- City Distribution Issues ---")
            for issue in analysis["city_issues"]:
                print(f"{issue['city']}: {issue['count']} ({issue['percentage']:.1f}%) - {issue['issue']}")
        
        print("\n--- Next Action ---")
        print(f"Action: {next_action['action']}")
        print(f"Reason: {next_action['reason']}")
        if next_action['action'] != 'none':
            if 'branch' in next_action:
                print(f"Target: {next_action['branch']}")
            if 'city' in next_action:
                print(f"City: {next_action['city']}")

if __name__ == "__main__":
    main()
