#!/usr/bin/env python3
"""
Escalation Script for Scout Error Handler

For persistent/non-transient errors: formats error details, suggests fix, queues for human review.

Usage:
    python3 escalate.py --error-file <path> --type <error_type> [--suggest "<fix>"] [--context <context>]

Outputs:
    - Formatted error report to stdout
    - Escalation queue entry to escalate_queue.json
    - Logs escalation to error_log.json

Returns:
    Exit code 0 (escalation logged)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


# Configuration
ESCALATION_QUEUE = Path("/root/.openclaw/workspace/skills/scout-error-handler/escalate_queue.json")
LOG_FILE = Path("/root/.openclaw/workspace/skills/scout-error-handler/error_log.json")


# Fix suggestions by error type
FIX_SUGGESTIONS = {
    "AUTH_ERROR": [
        "Check API credentials/token expiration",
        "Verify permissions for the requested resource",
        "Regenerate API keys if expired",
        "Check for IP whitelisting requirements",
    ],
    "DATA_ERROR": [
        "Validate input data format against schema",
        "Check required fields are populated",
        "Review data type conversions",
        "Verify JSON/XML syntax",
    ],
    "API_ERROR": [
        "Check service status page for outages",
        "Review API documentation for changes",
        "Contact API provider support",
        "Implement fallback service if available",
    ],
    "NETWORK_ERROR": [
        "Check network connectivity",
        "Verify DNS resolution",
        "Review firewall/proxy settings",
        "Try alternative network path",
    ],
    "UNKNOWN": [
        "Review full error logs for context",
        "Check recent system changes",
        "Contact technical support",
        "Document error pattern for future handling",
    ],
}


def format_escalation_report(error_type: str, error_content: str, suggestion: str = "", context: str = "") -> str:
    """Format a human-readable escalation report."""
    
    report_lines = [
        "=" * 60,
        "🚨 ERROR ESCALATION REPORT",
        "=" * 60,
        f"",
        f"Timestamp:    {datetime.now(timezone.utc).isoformat()}Z",
        f"Error Type:   {error_type}",
        f"Context:      {context or 'Not specified'}",
        f"",
        "-" * 40,
        "ERROR DETAILS:",
        "-" * 40,
    ]
    
    # Truncate long error content
    max_length = 2000
    if len(error_content) > max_length:
        error_content = error_content[:max_length] + f"\n... [{len(error_content) - max_length} more chars]"
    
    report_lines.append(error_content)
    report_lines.append("")
    
    # Add suggestions
    if suggestion:
        report_lines.extend([
            "-" * 40,
            "SUGGESTED FIX:",
            "-" * 40,
            suggestion,
            "",
        ])
    else:
        suggestions = FIX_SUGGESTIONS.get(error_type, FIX_SUGGESTIONS["UNKNOWN"])
        report_lines.extend([
            "-" * 40,
            "SUGGESTED ACTIONS:",
            "-" * 40,
        ])
        for i, s in enumerate(suggestions, 1):
            report_lines.append(f"  {i}. {s}")
        report_lines.append("")
    
    report_lines.extend([
        "-" * 40,
        "STATUS: Queued for human review",
        "=" * 60,
    ])
    
    return "\n".join(report_lines)


def queue_escalation(error_type: str, error_content: str, suggestion: str, context: str):
    """Add escalation to the queue file."""
    escalation = {
        "id": f"ESC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "error_type": error_type,
        "context": context,
        "error_preview": error_content[:500],
        "suggested_fix": suggestion,
        "status": "pending_review",
        "assigned_to": None,
        "resolved_at": None,
    }
    
    # Load existing queue
    queue = []
    if ESCALATION_QUEUE.exists():
        try:
            with open(ESCALATION_QUEUE, "r") as f:
                content = f.read().strip()
                if content:
                    queue = json.loads(content)
                    if not isinstance(queue, list):
                        queue = [queue]
        except (json.JSONDecodeError, IOError):
            queue = []
    
    queue.append(escalation)
    
    # Ensure directory exists
    ESCALATION_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ESCALATION_QUEUE, "w") as f:
        json.dump(queue, f, indent=2)
    
    return escalation["id"]


def log_escalation(error_type: str, context: str, escalation_id: str):
    """Log escalation to error_log.json."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "error_type": error_type,
        "severity": "high",
        "message": f"Error escalated for human review",
        "action": "escalate",
        "attempts": 0,
        "resolution": "escalated",
        "context": context,
        "details": {
            "escalation_id": escalation_id,
            "queue_file": str(ESCALATION_QUEUE),
        }
    }
    
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    logs = json.loads(content)
                    if not isinstance(logs, list):
                        logs = [logs]
        except (json.JSONDecodeError, IOError):
            logs = []
    
    logs.append(log_entry)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Escalate persistent errors for human review"
    )
    parser.add_argument(
        "--error-file",
        required=True,
        help="Path to file containing error details"
    )
    parser.add_argument(
        "--type",
        required=True,
        help="Error type (API_ERROR, AUTH_ERROR, DATA_ERROR, etc.)"
    )
    parser.add_argument(
        "--suggest",
        default="",
        help="Suggested fix for the error"
    )
    parser.add_argument(
        "--context",
        default="",
        help="Context where error occurred"
    )
    parser.add_argument(
        "--error-content",
        default="",
        help="Error message content (alternative to --error-file)"
    )
    
    args = parser.parse_args()
    
    # Read error content
    error_content = args.error_content
    if not error_content and args.error_file:
        try:
            with open(args.error_file, "r") as f:
                error_content = f.read()
        except FileNotFoundError:
            error_content = f"[Error file not found: {args.error_file}]"
        except IOError as e:
            error_content = f"[Could not read error file: {e}]"
    
    # Generate report
    report = format_escalation_report(args.type, error_content, args.suggest, args.context)
    print(report)
    
    # Queue for review
    escalation_id = queue_escalation(args.type, error_content, args.suggest, args.context)
    print(f"\n📋 Escalation ID: {escalation_id}")
    print(f"📁 Queue file: {ESCALATION_QUEUE}")
    
    # Log the escalation
    log_escalation(args.type, args.context, escalation_id)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
