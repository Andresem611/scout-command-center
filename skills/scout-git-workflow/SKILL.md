---
name: scout-git-workflow
description: |
  Safe Git workflow automation for Thoven projects. Handles status checks,
  conventional commits, and safe deployments with guardrails.
author: Scout
version: 1.0.0
tags: [git, workflow, deployment, thoven]
triggers:
  - "git status"
  - "commit changes"
  - "deploy safely"
  - "check git"
  - "safe deploy"
---

# scout-git-workflow

Safe Git operations for Thoven projects. Prevents messy deploys and enforces conventions.

## Quick Start

```bash
# Check repository status
python3 ~/.openclaw/workspace/skills/scout-git-workflow/scripts/check_status.py

# Commit with conventional message
python3 ~/.openclaw/workspace/skills/scout-git-workflow/scripts/commit.py --message "feat: add user auth" --push

# Full safe deploy workflow
python3 ~/.openclaw/workspace/skills/scout-git-workflow/scripts/safe_deploy.py
```

## Scripts

| Script | Purpose |
|--------|---------|
| `check_status.py` | Check uncommitted changes, untracked files, sync status |
| `commit.py` | Stage, commit with conventional message, optional push |
| `safe_deploy.py` | Full workflow: check → commit → push → verify |

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[(scope)]: <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

See [references/commit-conventions.md](references/commit-conventions.md) for full guide.

## Recovery

See [references/recovery.md](references/recovery.md) for:
- Undo last commit
- Reset to remote
- Stash/restore changes

## Branch Workflow

1. **main**: Production-ready code only
2. **feature/***: New features (e.g., `feature/user-auth`)
3. **fix/***: Bug fixes (e.g., `fix/login-redirect`)
4. **hotfix/***: Urgent production fixes

### Typical Flow

```bash
# Start feature
git checkout -b feature/new-thing

# Work...

# Commit & push
python3 scripts/commit.py -m "feat: implement new thing" --push

# Create PR, merge via GitHub

# Deploy main
python3 scripts/safe_deploy.py
```


---

## 🔑 KEY LEARNINGS (Max 5)

1. **Dry-run first, then execute** — Never auto-stage without --auto-stage flag
2. **Conventional commits: type(scope): description** — Enforced format
3. **Check status before any operation** — Know state before changing it
4. **Recovery docs for mistakes** — Undo last commit, reset to remote
5. 
