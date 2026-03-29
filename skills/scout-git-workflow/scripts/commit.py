#!/usr/bin/env python3
"""
commit.py - Stage, commit with conventional message, and optionally push

Usage:
    python3 commit.py --message "feat: add login"
    python3 commit.py -m "fix: resolve auth bug" --push
    python3 commit.py -m "docs: update README" --auto-stage
    python3 commit.py -m "feat: api changes" --auto-stage --push
"""

import argparse
import re
import subprocess
import sys


VALID_TYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]


def run_git(args: list[str], check: bool = True) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"❌ Git command failed: {' '.join(args)}")
        if result.stderr:
            print(f"   {result.stderr.strip()}")
        sys.exit(1)
    return result.returncode, result.stdout, result.stderr


def validate_message(message: str) -> tuple[bool, str]:
    """
    Validate conventional commit format.
    Returns (is_valid, error_message)
    """
    # Pattern: type(scope): description or type: description
    pattern = r"^(\w+)(?:\([^)]+\))?!?: .+"
    match = re.match(pattern, message)
    
    if not match:
        return False, "Message must follow format: type[(scope)]: description"
    
    commit_type = match.group(1)
    
    if commit_type not in VALID_TYPES:
        return False, f"Invalid type '{commit_type}'. Use: {', '.join(VALID_TYPES)}"
    
    # Check description length
    desc = message.split(":", 1)[1].strip()
    if len(desc) < 3:
        return False, "Description too short (min 3 chars)"
    
    if len(desc) > 72:
        return False, "Description too long (max 72 chars)"
    
    return True, ""


def check_status() -> tuple[bool, bool, bool]:
    """Check if there are changes to commit. Returns (has_staged, has_unstaged, has_untracked)."""
    _, stdout, _ = run_git(["status", "--porcelain"])
    
    lines = stdout.strip().split("\n") if stdout.strip() else []
    
    has_staged = False
    has_unstaged = False
    has_untracked = False
    
    for line in lines:
        if not line:
            continue
        status = line[:2]
        if status[0] in "MADRC":
            has_staged = True
        if status[1] in "MD":
            has_unstaged = True
        if status == "??":
            has_untracked = True
    
    return has_staged, has_unstaged, has_untracked


def stage_files(auto_stage: bool) -> bool:
    """Stage files. Returns True if something was staged."""
    has_staged, has_unstaged, has_untracked = check_status()
    
    if not has_staged and not has_unstaged and not has_untracked:
        print("⚠️  Nothing to commit (working tree clean)")
        return False
    
    if has_unstaged or has_untracked:
        if auto_stage:
            print("📦 Auto-staging all changes...")
            run_git(["add", "."])
        else:
            print("⚠️  Unstaged changes present. Use --auto-stage to stage all.")
            print("    Or run: git add <files>")
            
            # Show what's unstaged
            _, stdout, _ = run_git(["status", "--short"])
            print("\nCurrent status:")
            print(stdout)
            sys.exit(1)
    
    return True


def commit(message: str) -> bool:
    """Create the commit."""
    print(f"📝 Committing: {message}")
    code, stdout, stderr = run_git(["commit", "-m", message], check=False)
    
    if code != 0:
        if "nothing to commit" in stderr.lower():
            print("⚠️  Nothing to commit")
            return False
        print(f"❌ Commit failed: {stderr}")
        return False
    
    # Extract commit hash from output
    if stdout:
        # Output like: [main abc1234] message
        match = re.search(r"\[\w+ ([a-f0-9]+)\]", stdout)
        if match:
            print(f"✅ Committed: {match.group(1)[:7]}")
        else:
            print("✅ Committed")
    
    return True


def push() -> bool:
    """Push to remote."""
    # Check if we have a remote
    code, stdout, _ = run_git(["remote"], check=False)
    
    if code != 0 or not stdout.strip():
        print("⚠️  No remote configured, skipping push")
        return True
    
    # Get current branch
    _, branch, _ = run_git(["branch", "--show-current"])
    branch = branch.strip()
    
    print(f"📤 Pushing to origin/{branch}...")
    code, stdout, stderr = run_git(["push", "origin", branch], check=False)
    
    if code != 0:
        if "rejected" in stderr.lower():
            print("❌ Push rejected - pull first to merge remote changes")
        else:
            print(f"❌ Push failed: {stderr}")
        return False
    
    print("✅ Pushed successfully")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Commit changes with conventional commit format"
    )
    parser.add_argument(
        "-m", "--message",
        required=True,
        help="Commit message (conventional format: type[(scope)]: description)"
    )
    parser.add_argument(
        "--auto-stage",
        action="store_true",
        help="Automatically stage all unstaged changes"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push to remote after committing"
    )
    
    args = parser.parse_args()
    
    # Validate message format
    is_valid, error = validate_message(args.message)
    if not is_valid:
        print(f"❌ Invalid commit message: {error}")
        print(f"\nMessage: {args.message}")
        print(f"\nValid types: {', '.join(VALID_TYPES)}")
        print("\nExamples:")
        print('  "feat: add user authentication"')
        print('  "fix(api): resolve timeout issue"')
        print('  "docs: update installation guide"')
        sys.exit(1)
    
    # Check we're in a git repo
    code, _, _ = run_git(["rev-parse", "--git-dir"], check=False)
    if code != 0:
        print("❌ Not a git repository")
        sys.exit(1)
    
    # Stage files
    if not stage_files(args.auto_stage):
        sys.exit(0)
    
    # Commit
    if not commit(args.message):
        sys.exit(1)
    
    # Push if requested
    if args.push:
        if not push():
            sys.exit(1)
    
    print("\n🎯 Done!")


if __name__ == "__main__":
    main()
