#!/usr/bin/env python3
"""
check_status.py - Check Git repository status safely

Checks for:
- Uncommitted changes (staged/unstaged)
- Untracked files
- Sync status with remote (ahead/behind/diverged)
- Current branch
"""

import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitStatus:
    branch: str
    is_clean: bool
    has_staged: bool
    has_unstaged: bool
    has_untracked: bool
    ahead: int
    behind: int
    diverged: bool
    files_staged: list[str]
    files_unstaged: list[str]
    files_untracked: list[str]


def run_git(args: list[str]) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_current_branch() -> str:
    """Get the current branch name."""
    code, stdout, _ = run_git(["branch", "--show-current"])
    if code == 0:
        return stdout.strip()
    return "unknown"


def get_status() -> GitStatus:
    """Parse git status into structured data."""
    code, stdout, _ = run_git(["status", "--porcelain", "--branch"])
    
    if code != 0:
        print("❌ Failed to get git status")
        sys.exit(1)
    
    lines = stdout.strip().split("\n") if stdout.strip() else []
    
    # Parse branch line (## main...origin/main [ahead 2, behind 1])
    branch = "unknown"
    ahead = 0
    behind = 0
    diverged = False
    
    if lines and lines[0].startswith("##"):
        branch_line = lines[0][3:]  # Remove "## "
        
        # Handle diverged state
        if "..." in branch_line:
            branch = branch_line.split("...")[0]
            rest = branch_line.split("...")[1]
            
            if " [ahead " in rest:
                ahead_str = rest.split(" [ahead ")[1].split(",")[0].split("]")[0]
                ahead = int(ahead_str)
            if " behind " in rest:
                behind_str = rest.split(" behind ")[1].split("]")[0].split(",")[0]
                behind = int(behind_str)
            if "diverged" in rest:
                diverged = True
        else:
            branch = branch_line
        
        lines = lines[1:]  # Remove branch line from file list
    
    files_staged = []
    files_unstaged = []
    files_untracked = []
    
    for line in lines:
        if not line:
            continue
        
        status_code = line[:2]
        filename = line[3:]
        
        # Staged changes (first column)
        if status_code[0] in "MADRC":
            files_staged.append(filename)
        
        # Unstaged changes (second column)
        if status_code[1] in "MD":
            files_unstaged.append(filename)
        
        # Untracked
        if status_code == "??":
            files_untracked.append(filename)
    
    has_staged = len(files_staged) > 0
    has_unstaged = len(files_unstaged) > 0
    has_untracked = len(files_untracked) > 0
    is_clean = not (has_staged or has_unstaged or has_untracked)
    
    return GitStatus(
        branch=branch,
        is_clean=is_clean,
        has_staged=has_staged,
        has_unstaged=has_unstaged,
        has_untracked=has_untracked,
        ahead=ahead,
        behind=behind,
        diverged=diverged,
        files_staged=files_staged,
        files_unstaged=files_unstaged,
        files_untracked=files_untracked
    )


def print_status(status: GitStatus) -> None:
    """Print formatted status output."""
    print(f"📍 Branch: {status.branch}")
    print()
    
    # Working tree status
    if status.is_clean:
        print("✅ Working tree clean")
    else:
        if status.has_staged:
            print(f"🟡 Staged ({len(status.files_staged)}):")
            for f in status.files_staged[:10]:
                print(f"   • {f}")
            if len(status.files_staged) > 10:
                print(f"   ... and {len(status.files_staged) - 10} more")
            print()
        
        if status.has_unstaged:
            print(f"🔴 Unstaged ({len(status.files_unstaged)}):")
            for f in status.files_unstaged[:10]:
                print(f"   • {f}")
            if len(status.files_unstaged) > 10:
                print(f"   ... and {len(status.files_unstaged) - 10} more")
            print()
        
        if status.has_untracked:
            print(f"⚪ Untracked ({len(status.files_untracked)}):")
            for f in status.files_untracked[:10]:
                print(f"   • {f}")
            if len(status.files_untracked) > 10:
                print(f"   ... and {len(status.files_untracked) - 10} more")
            print()
    
    # Remote sync status
    if status.diverged:
        print("⚠️  DIVERGED from remote - needs manual resolution")
    elif status.ahead > 0 and status.behind > 0:
        print(f"⚠️  Local is {status.ahead} ahead, {status.behind} behind remote")
    elif status.ahead > 0:
        print(f"📤 {status.ahead} commit(s) ahead of remote (needs push)")
    elif status.behind > 0:
        print(f"📥 {status.behind} commit(s) behind remote (needs pull)")
    else:
        print("🔄 In sync with remote")


def main():
    """Main entry point."""
    # Check if we're in a git repo
    code, _, _ = run_git(["rev-parse", "--git-dir"])
    if code != 0:
        print("❌ Not a git repository")
        sys.exit(1)
    
    status = get_status()
    print_status(status)
    
    # Exit code indicates if repo is clean
    sys.exit(0 if status.is_clean else 1)


if __name__ == "__main__":
    main()
