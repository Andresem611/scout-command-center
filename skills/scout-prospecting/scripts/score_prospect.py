#!/usr/bin/env python3
"""
Score prospects 1-5 based on Thoven-specific criteria.
Evaluates followers, engagement, content fit, and other factors.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Any

# Scoring weights
WEIGHTS = {
    "followers": 0.25,
    "engagement": 0.30,
    "content_fit": 0.25,
    "has_website": 0.10,
    "activity": 0.10
}

# Follower score thresholds
FOLLOWER_TIERS = [
    (0, 1000, 1),
    (1000, 10000, 2),
    (10000, 50000, 3),
    (50000, 200000, 4),
    (200000, float('inf'), 5)
]

# Engagement benchmarks (percentage)
ENGAGEMENT_TIERS = [
    (0, 0.5, 1),
    (0.5, 1.5, 2),
    (1.5, 3.0, 3),
    (3.0, 5.0, 4),
    (5.0, float('inf'), 5)
]

CONTENT_FIT_SCORES = {
    "high": 5,
    "medium": 3,
    "low": 1
}

def parse_followers(followers_str: str) -> int:
    """Parse follower count from string like '50k' or '1.2M'."""
    if isinstance(followers_str, (int, float)):
        return int(followers_str)
    
    if not followers_str:
        return 0
    
    followers_str = str(followers_str).upper().replace(",", "").strip()
    match = re.match(r"([0-9.]+)([KM]?)", followers_str)
    if not match:
        return 0
    
    num, suffix = match.groups()
    num = float(num)
    
    if suffix == "K":
        return int(num * 1000)
    elif suffix == "M":
        return int(num * 1000000)
    return int(num)

def score_followers(count: int) -> int:
    """Score based on follower count (1-5)."""
    for min_val, max_val, score in FOLLOWER_TIERS:
        if min_val <= count < max_val:
            return score
    return 1

def score_engagement(rate: float) -> int:
    """Score based on engagement rate percentage (1-5)."""
    for min_val, max_val, score in ENGAGEMENT_TIERS:
        if min_val <= rate < max_val:
            return score
    return 1

def calculate_score(
    followers: int,
    engagement: float,
    content_fit: str,
    has_website: bool = False,
    is_active: bool = True
) -> Dict[str, Any]:
    """Calculate overall prospect score."""
    
    # Component scores
    follower_score = score_followers(followers)
    engagement_score = score_engagement(engagement)
    fit_score = CONTENT_FIT_SCORES.get(content_fit.lower(), 3)
    website_score = 5 if has_website else 2
    activity_score = 5 if is_active else 1
    
    # Weighted average
    weighted_score = (
        follower_score * WEIGHTS["followers"] +
        engagement_score * WEIGHTS["engagement"] +
        fit_score * WEIGHTS["content_fit"] +
        website_score * WEIGHTS["has_website"] +
        activity_score * WEIGHTS["activity"]
    )
    
    # Round to nearest integer (1-5)
    final_score = max(1, min(5, round(weighted_score)))
    
    # Map to tier
    tiers = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D"}
    tier = tiers.get(final_score, "C")
    
    # Generate reasoning
    reasoning = []
    
    if followers >= 200000:
        reasoning.append(f"{followers/1000:.0f}K followers (major reach)")
    elif followers >= 50000:
        reasoning.append(f"{followers/1000:.0f}K followers (strong reach)")
    elif followers >= 10000:
        reasoning.append(f"{followers/1000:.0f}K followers (good reach)")
    else:
        reasoning.append(f"{followers/1000:.0f}K followers (growing)")
    
    if engagement >= 5:
        reasoning.append(f"{engagement}% engagement (excellent)")
    elif engagement >= 3:
        reasoning.append(f"{engagement}% engagement (above avg)")
    else:
        reasoning.append(f"{engagement}% engagement (average)")
    
    if content_fit == "high":
        reasoning.append("Strong content alignment")
    elif content_fit == "medium":
        reasoning.append("Moderate content fit")
    else:
        reasoning.append("Weak content alignment")
    
    if has_website:
        reasoning.append("Has website/blog")
    
    if not is_active:
        reasoning.append("WARNING: Low activity")
    
    return {
        "score": final_score,
        "tier": tier,
        "weighted_average": round(weighted_score, 2),
        "components": {
            "followers": {"value": followers, "score": follower_score},
            "engagement": {"value": engagement, "score": engagement_score},
            "content_fit": {"value": content_fit, "score": fit_score},
            "has_website": {"value": has_website, "score": website_score},
            "activity": {"value": is_active, "score": activity_score}
        },
        "reasoning": reasoning,
        "recommendation": _get_recommendation(final_score, tier)
    }

def _get_recommendation(score: int, tier: str) -> str:
    """Get action recommendation based on score."""
    recommendations = {
        5: "PRIORITY: Reach out immediately - ideal partner",
        4: "HIGH: Strong prospect - personalized outreach",
        3: "MEDIUM: Worth testing - templated outreach",
        2: "LOW: Deprioritize - low ROI potential",
        1: "SKIP: Not a fit - save for later"
    }
    return recommendations.get(score, "Review manually")

def load_prospect_from_file(filepath: str) -> Dict[str, Any]:
    """Load prospect data from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(
        description="Score prospects based on Thoven criteria"
    )
    parser.add_argument("--followers", help="Follower count (e.g., 50k, 1M)")
    parser.add_argument(
        "--engagement", 
        type=float, 
        help="Engagement rate percentage (e.g., 4.5)"
    )
    parser.add_argument(
        "--content-fit",
        choices=["high", "medium", "low"],
        default="medium",
        help="Content alignment with Thoven"
    )
    parser.add_argument(
        "--has-website",
        action="store_true",
        help="Has blog or website"
    )
    parser.add_argument(
        "--inactive",
        action="store_true",
        help="Mark as inactive (penalizes score)"
    )
    parser.add_argument(
        "--file",
        help="JSON file with prospect data"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Load from file or use CLI args
    if args.file:
        data = load_prospect_from_file(args.file)
        followers = parse_followers(data.get("followers", 0))
        engagement = float(data.get("engagement", 0))
        content_fit = data.get("content_fit", "medium")
        has_website = data.get("has_website", False)
        is_active = data.get("is_active", True)
    else:
        if not args.followers or args.engagement is None:
            parser.error("--followers and --engagement required (or use --file)")
        
        followers = parse_followers(args.followers)
        engagement = args.engagement
        content_fit = args.content_fit
        has_website = args.has_website
        is_active = not args.inactive
    
    # Calculate score
    result = calculate_score(
        followers=followers,
        engagement=engagement,
        content_fit=content_fit,
        has_website=has_website,
        is_active=is_active
    )
    
    json_output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(json_output)

if __name__ == "__main__":
    main()
