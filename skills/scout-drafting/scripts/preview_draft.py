#!/usr/bin/env python3
"""
Preview email draft in a nicely formatted way for approval.
Highlights key info, flags, and research context.
"""

import argparse
import json
import sys


def format_draft_for_preview(draft: dict) -> str:
    """Format draft for human review."""
    lines = []
    
    # Header
    lines.append("=" * 70)
    lines.append("📧 EMAIL DRAFT PREVIEW")
    lines.append("=" * 70)
    lines.append("")
    
    # Meta info
    meta = draft.get("meta", {})
    lines.append(f"Template: {meta.get('template_used', 'unknown')}")
    lines.append(f"Generated: {meta.get('generated_at', 'unknown')}")
    lines.append(f"Prospect: {meta.get('prospect_handle', 'unknown')}")
    lines.append("")
    
    # Fit score
    fit_score = draft.get("research_summary", {}).get("fit_score", 0)
    score_emoji = "🟢" if fit_score >= 70 else "🟡" if fit_score >= 50 else "🔴"
    lines.append(f"{score_emoji} Fit Score: {fit_score}/100")
    lines.append("")
    
    # Flags (prominent if any)
    flags = draft.get("flags", [])
    if flags:
        lines.append("⚠️  FLAGS:")
        for flag in flags:
            lines.append(f"   • {flag}")
        lines.append("")
    
    # Divider
    lines.append("-" * 70)
    lines.append("")
    
    # Email content
    email = draft.get("email", {})
    lines.append(f"To:      {email.get('to', 'N/A')}")
    lines.append(f"From:    {email.get('from', 'keri@thoven.co')}")
    lines.append(f"Subject: {email.get('subject', 'N/A')}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append(email.get("body", "[No body generated]"))
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    
    # Research summary
    research = draft.get("research_summary", {})
    reasons = research.get("fit_reasons", [])
    if reasons:
        lines.append("📊 Fit Reasons:")
        for reason in reasons:
            lines.append(f"   ✓ {reason}")
        lines.append("")
    
    recommendations = research.get("recommendations", [])
    if recommendations:
        lines.append("💡 Recommendations:")
        for rec in recommendations:
            lines.append(f"   • {rec}")
        lines.append("")
    
    # Action options
    lines.append("=" * 70)
    lines.append("ACTIONS:")
    lines.append("=" * 70)
    lines.append("")
    lines.append("  [1] Approve — Queue for sending")
    lines.append("  [2] Edit — Request changes (describe below)")
    lines.append("  [3] Reject — Do not send")
    lines.append("")
    lines.append("Custom notes:")
    if draft.get("custom_notes"):
        lines.append(f"  {draft['custom_notes']}")
    lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Preview email draft for approval")
    parser.add_argument("--draft", required=True, help="Path to draft JSON file")
    parser.add_argument("--export", help="Export formatted preview to text file")
    args = parser.parse_args()
    
    # Load draft
    try:
        with open(args.draft, 'r') as f:
            draft = json.load(f)
    except FileNotFoundError:
        print(f"Error: Draft file not found: {args.draft}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format preview
    preview = format_draft_for_preview(draft)
    
    # Export if requested
    if args.export:
        with open(args.export, 'w') as f:
            f.write(preview)
        print(f"Preview exported to: {args.export}")
    
    # Always print to stdout
    print(preview)


if __name__ == "__main__":
    main()
