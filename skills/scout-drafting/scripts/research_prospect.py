#!/usr/bin/env python3
"""
Research prospect data to extract personalization angles.
Returns structured research notes for email generation.
"""

import argparse
import json
import sys
from typing import Any


def extract_personalization_angles(prospect: dict) -> dict:
    """Extract personalization hooks from prospect data."""
    angles = {
        "content_references": [],
        "family_details": {},
        "values_alignment": [],
        "pain_points": [],
        "opportunity_gaps": []
    }
    
    bio = prospect.get("bio", "")
    recent_content = prospect.get("recent_content", [])
    
    # Extract content references
    for content in recent_content[:3]:  # Last 3 posts
        ref = {
            "topic": content.get("topic", ""),
            "hook": content.get("hook", "")[:100] + "..." if len(content.get("hook", "")) > 100 else content.get("hook", ""),
            "date": content.get("date", ""),
            "engagement": content.get("engagement", {})
        }
        angles["content_references"].append(ref)
    
    # Extract family details for personalization
    if "kids" in bio.lower() or "children" in bio.lower() or "mom" in bio.lower():
        angles["family_details"]["is_parent"] = True
    if "homeschool" in bio.lower() or "homeschooling" in bio.lower():
        angles["family_details"]["homeschooler"] = True
    
    # Extract location if mentioned
    import re
    location_match = re.search(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),?\s*(?:TX|CA|NY|FL|WA|OR|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|UT|IA|NV|AR|MS|KS|NM|NE|WV|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\b', bio)
    if location_match:
        angles["family_details"]["location"] = location_match.group(0)
    
    # Values alignment
    value_keywords = {
        "creativity": ["creative", "imagination", "arts", "expression"],
        "education": ["learning", "education", "teaching", "growth", "development"],
        "family": ["family", "quality time", "together", "bonding"],
        "mindfulness": ["calm", "mindful", "peaceful", "present"],
        "screen_free": ["screen-free", "unplugged", "offline", "digital detox"]
    }
    
    bio_lower = bio.lower()
    for value, keywords in value_keywords.items():
        if any(kw in bio_lower for kw in keywords):
            angles["values_alignment"].append(value)
    
    # Pain points (inferred)
    pain_indicators = {
        "busy_schedule": ["busy", "overwhelmed", "no time", "juggling"],
        "screen_time_concerns": ["screen time", "tablet", "phone", "device"],
        "finding_activities": ["what to do", "activities", "bored", "entertainment"],
        "cost_concerns": ["expensive", "affordable", "budget", "cost"]
    }
    
    for pain, indicators in pain_indicators.items():
        if any(ind in bio_lower for ind in indicators):
            angles["pain_points"].append(pain)
    
    # Opportunity gaps
    if angles["family_details"].get("is_parent") and "music" not in bio_lower:
        angles["opportunity_gaps"].append("music_education_not_highlighted")
    if angles["family_details"].get("homeschooler") and "music" not in bio_lower:
        angles["opportunity_gaps"].append("curriculum_gap_music")
    
    return angles


def generate_research_notes(prospect: dict) -> dict:
    """Generate comprehensive research notes for a prospect."""
    notes = {
        "prospect": {
            "name": prospect.get("name", ""),
            "handle": prospect.get("handle", ""),
            "platform": prospect.get("platform", ""),
            "follower_count": prospect.get("follower_count", 0),
            "engagement_rate": prospect.get("engagement_rate", 0),
        },
        "personalization": extract_personalization_angles(prospect),
        "recommendations": [],
        "fit_score": 0,
        "template_suggestion": ""
    }
    
    # Calculate fit score
    score = 0
    reasons = []
    
    pers = notes["personalization"]
    
    if pers["family_details"].get("is_parent"):
        score += 30
        reasons.append("Parent audience match")
    if pers["family_details"].get("homeschooler"):
        score += 25
        reasons.append("Homeschool segment")
        notes["template_suggestion"] = "homeschool-influencer"
    if "music" in prospect.get("bio", "").lower():
        score += 20
        reasons.append("Music content alignment")
    if pers["family_details"].get("location"):
        score += 10
        reasons.append("Location data for personalization")
    if len(pers["values_alignment"]) >= 2:
        score += 15
        reasons.append("Strong values alignment")
    
    # Cap at 100
    notes["fit_score"] = min(score, 100)
    notes["fit_reasons"] = reasons
    
    # Default template if not set
    if not notes["template_suggestion"]:
        if pers["family_details"].get("is_parent"):
            notes["template_suggestion"] = "mom-influencer"
        else:
            notes["template_suggestion"] = "content-creator"
    
    # Recommendations
    if notes["fit_score"] >= 70:
        notes["recommendations"].append("HIGH PRIORITY: Strong fit, prioritize outreach")
    elif notes["fit_score"] >= 50:
        notes["recommendations"].append("MEDIUM PRIORITY: Good fit with personalized approach")
    else:
        notes["recommendations"].append("LOW PRIORITY: Consider before investing outreach effort")
    
    # Personalization recommendations
    if pers["content_references"]:
        top_content = pers["content_references"][0]
        notes["recommendations"].append(
            f"Lead with reference to: '{top_content['hook'][:60]}...'"
        )
    
    if pers["family_details"].get("location"):
        notes["recommendations"].append(
            f"Reference location: {pers['family_details']['location']}"
        )
    
    return notes


def main():
    parser = argparse.ArgumentParser(description="Research prospect for personalization")
    parser.add_argument("--prospect", required=True, help="Path to prospect JSON file")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    # Load prospect data
    try:
        with open(args.prospect, 'r') as f:
            prospect = json.load(f)
    except FileNotFoundError:
        print(f"Error: Prospect file not found: {args.prospect}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in prospect file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate research notes
    notes = generate_research_notes(prospect)
    
    # Output
    output = json.dumps(notes, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Research notes written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
