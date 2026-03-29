#!/usr/bin/env python3
"""
Retry with Exponential Backoff for Scout Error Handler

Retries transient errors (network, rate limit) with exponential backoff.
Max 3 retries by default. Logs each attempt.

Usage:
    python3 retry_with_backoff.py --command "<shell_command>" [--max-retries 3] [--backoff-base 2]

Environment:
    SCOUT_MAX_RETRIES - Override max retries (default: 3)
    SCOUT_BACKOFF_BASE - Override backoff base seconds (default: 2)

Returns:
    Exit code 0 on success, 1 on failure after all retries
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path


# Configuration
DEFAULT_MAX_RETRIES = int(os.environ.get("SCOUT_MAX_RETRIES", 3))
DEFAULT_BACKOFF_BASE = int(os.environ.get("SCOUT_BACKOFF_BASE", 2))
LOG_FILE = Path("/root/.openclaw/workspace/skills/scout-error-handler/error_log.json")


def log_attempt(attempt: int, max_retries: int, command: str, success: bool, error_msg: str = ""):
    """Log retry attempt to error_log.json."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "error_type": "RETRY_ATTEMPT",
        "severity": "medium" if not success else "low",
        "message": f"Attempt {attempt}/{max_retries}: {'SUCCESS' if success else 'FAILED'}",
        "action": "retry",
        "attempts": attempt,
        "resolution": "success" if success else "pending",
        "context": command[:100],
        "details": {
            "max_retries": max_retries,
            "error": error_msg[:500] if error_msg else None,
        }
    }
    
    # Append to log file
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
    
    # Ensure directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def retry_with_backoff(command: str, max_retries: int = DEFAULT_MAX_RETRIES, backoff_base: int = DEFAULT_BACKOFF_BASE):
    """Execute command with exponential backoff retry logic."""
    
    for attempt in range(1, max_retries + 1):
        print(f"[Attempt {attempt}/{max_retries}] Executing: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per attempt
            )
            
            if result.returncode == 0:
                print(f"✓ Success on attempt {attempt}")
                log_attempt(attempt, max_retries, command, True)
                return 0
            
            error_msg = result.stderr or result.stdout or "Unknown error"
            print(f"✗ Failed: {error_msg[:200]}")
            
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out after 300 seconds"
            print(f"✗ {error_msg}")
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Exception: {error_msg}")
        
        log_attempt(attempt, max_retries, command, False, error_msg)
        
        if attempt < max_retries:
            backoff_seconds = backoff_base ** attempt
            print(f"  → Retrying in {backoff_seconds}s...")
            time.sleep(backoff_seconds)
        else:
            print(f"✗ All {max_retries} attempts exhausted")
    
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Retry command with exponential backoff"
    )
    parser.add_argument(
        "--command",
        required=True,
        help="Shell command to execute and retry if it fails"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Maximum retry attempts (default: {DEFAULT_MAX_RETRIES})"
    )
    parser.add_argument(
        "--backoff-base",
        type=int,
        default=DEFAULT_BACKOFF_BASE,
        help=f"Base seconds for exponential backoff (default: {DEFAULT_BACKOFF_BASE})"
    )
    
    args = parser.parse_args()
    
    exit_code = retry_with_backoff(args.command, args.max_retries, args.backoff_base)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
