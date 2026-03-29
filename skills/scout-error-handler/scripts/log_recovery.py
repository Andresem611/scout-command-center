#!/usr/bin/env python3
"""
Log Recovery Script for Scout Error Handler

Logs: error type, action taken, resolution, timestamp. Appends to error_log.json

Usage:
    python3 log_recovery.py --type <error_type> --action <action> [--resolution "<msg>"] \
                            [--severity <level>] [--context <context>] [--details <json>]

Actions:
    - retry: Retrying with backoff
    - escalate: Escalated for human review
    - ignore: Ignored (expected error)
    - fix: Auto-fixed

Returns:
    Exit code 0 (log entry created)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path


# Configuration
DEFAULT_LOG_FILE = Path("/root/.openclaw/workspace/skills/scout-error-handler/error_log.json")


def log_recovery(
    error_type: str,
    action: str,
    resolution: str = "pending",
    severity: str = "medium",
    context: str = "",
    details: dict = None,
    message: str = "",
    attempts: int = 0,
    log_file: Path = DEFAULT_LOG_FILE
):
    """Append a recovery log entry to the error log file."""
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "error_type": error_type,
        "severity": severity,
        "message": message or f"Error handling action: {action}",
        "action": action,
        "attempts": attempts,
        "resolution": resolution,
        "context": context,
        "details": details or {},
    }
    
    # Load existing logs
    logs = []
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                content = f.read().strip()
                if content:
                    logs = json.loads(content)
                    if not isinstance(logs, list):
                        logs = [logs]
        except (json.JSONDecodeError, IOError):
            logs = []
    
    logs.append(log_entry)
    
    # Ensure directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write updated logs
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)
    
    return log_entry


def get_stats(log_file: Path = DEFAULT_LOG_FILE) -> dict:
    """Get statistics from the error log."""
    if not log_file.exists():
        return {"total": 0, "by_type": {}, "by_resolution": {}}
    
    try:
        with open(log_file, "r") as f:
            content = f.read().strip()
            if not content:
                return {"total": 0, "by_type": {}, "by_resolution": {}}
            logs = json.loads(content)
            if not isinstance(logs, list):
                logs = [logs]
    except (json.JSONDecodeError, IOError):
        return {"total": 0, "by_type": {}, "by_resolution": {}}
    
    stats = {
        "total": len(logs),
        "by_type": {},
        "by_resolution": {},
        "by_severity": {},
    }
    
    for log in logs:
        error_type = log.get("error_type", "UNKNOWN")
        resolution = log.get("resolution", "unknown")
        severity = log.get("severity", "unknown")
        
        stats["by_type"][error_type] = stats["by_type"].get(error_type, 0) + 1
        stats["by_resolution"][resolution] = stats["by_resolution"].get(resolution, 0) + 1
        stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Log error recovery actions"
    )
    parser.add_argument(
        "--type",
        required=True,
        help="Error type (API_ERROR, NETWORK_ERROR, etc.)"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["retry", "escalate", "ignore", "fix", "classify"],
        help="Action taken to handle the error"
    )
    parser.add_argument(
        "--resolution",
        default="pending",
        choices=["success", "failure", "escalated", "ignored", "pending"],
        help="Resolution status"
    )
    parser.add_argument(
        "--message",
        default="",
        help="Detailed error message"
    )
    parser.add_argument(
        "--severity",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Error severity level"
    )
    parser.add_argument(
        "--context",
        default="",
        help="Context where error occurred"
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=0,
        help="Number of retry attempts made"
    )
    parser.add_argument(
        "--details",
        default="{}",
        help="Additional details as JSON string"
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help=f"Path to log file (default: {DEFAULT_LOG_FILE})"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics instead of logging"
    )
    
    args = parser.parse_args()
    
    log_file = Path(args.log_file)
    
    if args.stats:
        stats = get_stats(log_file)
        print(json.dumps(stats, indent=2))
        sys.exit(0)
    
    # Parse details JSON
    try:
        details = json.loads(args.details)
    except json.JSONDecodeError:
        details = {"raw": args.details}
    
    # Log the recovery
    entry = log_recovery(
        error_type=args.type,
        action=args.action,
        resolution=args.resolution,
        severity=args.severity,
        context=args.context,
        details=details,
        message=args.message,
        attempts=args.attempts,
        log_file=log_file
    )
    
    print(f"✓ Logged recovery action")
    print(f"  Type: {args.type}")
    print(f"  Action: {args.action}")
    print(f"  Resolution: {args.resolution}")
    print(f"  Log file: {log_file}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
