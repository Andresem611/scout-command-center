#!/usr/bin/env python3
"""
safe_deploy.py - Full safe deployment workflow

Steps:
1. Check repository status
2. Commit any pending changes (optional, with message)
3. Pull from remote to ensure sync
4. Push to remote
5. Verify clean state

Usage:
    python3 safe_deploy.py                    # Check, prompt for commit, push
    python3 safe_deploy.py --auto-commit "deploy: update site"  # Auto-commit if needed
    python3 safe_deploy.py --dry-run          # Show what would happen
"""

import argparse
import subprocess
import sys


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
    return result.returncode, result.stdout, result.stderr


def check_status() -> dict:
    """Get detailed status."""
    code, stdout, _ = run_git(["status", "--porcelain", "--branch"], check=False)
    
    if code != 0:
        return {"error": "Not a git repository"}
    
    lines = stdout.strip().split("\n") if stdout.strip() else []
    
    status = {
        "clean": True,
        "has_staged": False,
        "has_unstaged": False,
        "has_untracked": False,
        "ahead": 0,
        "behind": 0,
        "diverged": False,
        "branch": "unknown"
    }
    
    if lines and lines[0].startswith("##"):
        branch_line = lines[0][3:]
        
        if "..." in branch_line:
            status["branch"] = branch_line.split("...")[0]
            rest = branch_line.split("...")[1]
            
            if " [ahead " in rest:
                ahead_str = rest.split(" [ahead ")[1].split(",")[0].split("]")[0]
                status["ahead"] = int(ahead_str)
            if " behind " in rest:
                behind_str = rest.split(" behind ")[1].split("]")[0].split(",")[0]
                status["behind"] = int(behind_str)
            if "diverged" in rest:
                status["diverged"] = True
        else:
            status["branch"] = branch_line
        
        lines = lines[1:]
    
    for line in lines:
        if not line:
            continue
        code = line[:2]
        if code[0] in "MADRC":
            status["has_staged"] = True
            status["clean"] = False
        if code[1] in "MD":
            status["has_unstaged"] = True
            status["clean"] = False
        if code == "??":
            status["has_untracked"] = True
            status["clean"] = False
    
    return status


def has_remote() -> bool:
    """Check if remote exists."""
    code, stdout, _ = run_git(["remote"], check=False)
    return code == 0 and bool(stdout.strip())


def step_check(status: dict) -> bool:
    """Step 1: Check status and report."""
    print("=" * 50)
    print("🔍 STEP 1: Check Repository Status")
    print("=" * 50)
    
    if "error" in status:
        print(f"❌ {status['error']}")
        return False
    
    print(f"📍 Branch: {status['branch']}")
    
    if status["clean"]:
        print("✅ Working tree clean - no local changes")
    else:
        print("⚠️  Local changes detected:")
        if status["has_staged"]:
            print("   • Staged changes")
        if status["has_unstaged"]:
            print("   • Unstaged changes")
        if status["has_untracked"]:
            print("   • Untracked files")
    
    if status["diverged"]:
        print("🚨 WARNING: Branch has diverged from remote!")
        print("   Manual resolution required.")
        return False
    
    if status["behind"] > 0:
        print(f"📥 Behind remote by {status['behind']} commit(s)")
    
    if status["ahead"] > 0:
        print(f"📤 Ahead of remote by {status['ahead']} commit(s)")
    
    if not has_remote():
        print("⚠️  No remote configured - push will be skipped")
    
    print()
    return True


def step_commit(status: dict, auto_commit: str = None, dry_run: bool = False) -> bool:
    """Step 2: Handle committing if needed."""
    print("=" * 50)
    print("📝 STEP 2: Commit Changes")
    print("=" * 50)
    
    if status["clean"]:
        print("✅ Nothing to commit")
        print()
        return True
    
    if dry_run:
        print("[DRY RUN] Would commit changes")
        if auto_commit:
            print(f"[DRY RUN] Commit message: {auto_commit}")
        print()
        return True
    
    if not auto_commit:
        print("❌ Uncommitted changes present but no --auto-commit message provided")
        print("   Options:")
        print('   1. Run with --auto-commit "message here"')
        print('   2. Commit manually first: git add . && git commit -m "..."')
        print()
        return False
    
    # Stage and commit
    print("📦 Staging all changes...")
    run_git(["add", "."])
    
    print(f"📝 Committing: {auto_commit}")
    code, stdout, stderr = run_git(["commit", "-m", auto_commit], check=False)
    
    if code != 0:
        print(f"❌ Commit failed: {stderr}")
        return False
    
    print("✅ Committed successfully")
    print()
    return True


def step_pull(status: dict, dry_run: bool = False) -> bool:
    """Step 3: Pull from remote if behind."""
    print("=" * 50)
    print("📥 STEP 3: Sync with Remote")
    print("=" * 50)
    
    if not has_remote():
        print("ℹ️  No remote configured, skipping sync")
        print()
        return True
    
    if status["behind"] == 0 and not status["diverged"]:
        print("✅ Already up to date with remote")
        print()
        return True
    
    if dry_run:
        print(f"[DRY RUN] Would pull {status['behind']} commit(s) from remote")
        print()
        return True
    
    print(f"📥 Pulling {status['behind']} commit(s) from remote...")
    code, stdout, stderr = run_git(["pull", "--ff-only"], check=False)
    
    if code != 0:
        if "merge" in stderr.lower() or "conflict" in stderr.lower():
            print("❌ Pull failed - merge conflicts detected")
            print("   Resolve conflicts manually, then retry")
        else:
            print(f"❌ Pull failed: {stderr}")
        return False
    
    print("✅ Pulled successfully")
    print()
    return True


def step_push(status: dict, dry_run: bool = False) -> bool:
    """Step 4: Push to remote."""
    print("=" * 50)
    print("📤 STEP 4: Push to Remote")
    print("=" * 50)
    
    if not has_remote():
        print("ℹ️  No remote configured, skipping push")
        print()
        return True
    
    # Re-check status after potential pull
    fresh_status = check_status()
    
    if fresh_status["ahead"] == 0:
        print("✅ Nothing to push")
        print()
        return True
    
    if dry_run:
        print(f"[DRY RUN] Would push {fresh_status['ahead']} commit(s) to remote")
        print()
        return True
    
    print(f"📤 Pushing {fresh_status['ahead']} commit(s) to origin/{fresh_status['branch']}...")
    code, stdout, stderr = run_git(["push", "origin", fresh_status["branch"]], check=False)
    
    if code != 0:
        print(f"❌ Push failed: {stderr}")
        return False
    
    print("✅ Pushed successfully")
    print()
    return True


def step_verify(dry_run: bool = False) -> bool:
    """Step 5: Verify clean state."""
    print("=" * 50)
    print("✅ STEP 5: Verify Clean State")
    print("=" * 50)
    
    if dry_run:
        print("[DRY RUN] Would verify repository is clean and in sync")
        print()
        return True
    
    status = check_status()
    
    if not status["clean"]:
        print("❌ Verification failed - working tree not clean")
        return False
    
    if status["ahead"] > 0:
        print("❌ Verification failed - still ahead of remote")
        return False
    
    if status["behind"] > 0:
        print("❌ Verification failed - still behind remote")
        return False
    
    print("✅ Repository clean and in sync with remote")
    print()
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Safe deployment workflow with git"
    )
    parser.add_argument(
        "--auto-commit",
        metavar="MESSAGE",
        help="Automatically commit pending changes with this message"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes"
    )
    
    args = parser.parse_args()
    
    print("🚀 SAFE DEPLOY WORKFLOW")
    print()
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No changes will be made")
        print()
    
    # Initial status check
    status = check_status()
    
    # Execute steps
    success = True
    
    success = step_check(status) and success
    if not success:
        print("❌ Workflow aborted at step 1")
        sys.exit(1)
    
    success = step_commit(status, args.auto_commit, args.dry_run) and success
    if not success:
        print("❌ Workflow aborted at step 2")
        sys.exit(1)
    
    success = step_pull(status, args.dry_run) and success
    if not success:
        print("❌ Workflow aborted at step 3")
        sys.exit(1)
    
    success = step_push(status, args.dry_run) and success
    if not success:
        print("❌ Workflow aborted at step 4")
        sys.exit(1)
    
    success = step_verify(args.dry_run) and success
    if not success:
        print("❌ Workflow aborted at step 5")
        sys.exit(1)
    
    print("=" * 50)
    if args.dry_run:
        print("🧪 DRY RUN COMPLETE")
    else:
        print("🎉 DEPLOYMENT SUCCESSFUL")
    print("=" * 50)


if __name__ == "__main__":
    main()
