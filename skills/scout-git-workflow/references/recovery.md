# Git Recovery Commands

Quick reference for fixing common git mistakes.

## Undo Last Commit

### Keep changes (unstage)

```bash
# Undo commit, keep changes in working directory
git reset HEAD~1

# Or explicitly
git reset --soft HEAD~1
```

### Discard changes entirely

```bash
# ⚠️ DANGER: This deletes your changes
git reset --hard HEAD~1
```

### Amend last commit (change message or add files)

```bash
# Edit commit message
git commit --amend -m "new message"

# Add forgotten files to last commit
git add forgotten-file.js
git commit --amend --no-edit
```

## Reset to Remote

```bash
# Fetch latest from remote
git fetch origin

# Reset local branch to match remote (⚠️ loses local commits)
git reset --hard origin/main

# Or for current branch
git reset --hard @{u}
```

## Stash and Restore

### Stash changes

```bash
# Stash all changes (staged and unstaged)
git stash

# Stash with a message
git stash push -m "half-done feature"

# Stash only unstaged changes
git stash push --keep-index

# Stash untracked files too
git stash push -u
```

### View stashes

```bash
# List all stashes
git stash list

# Show stash contents
git stash show -p stash@{0}
```

### Restore stashes

```bash
# Apply most recent stash (keeps it in stash list)
git stash apply

# Apply specific stash
git stash apply stash@{1}

# Apply and remove from stash list
git stash pop

# Apply to specific stash and remove
git stash pop stash@{0}
```

### Delete stashes

```bash
# Drop most recent stash
git stash drop

# Drop specific stash
git stash drop stash@{1}

# Clear all stashes (⚠️ destructive)
git stash clear
```

## Fix Common Problems

### Unstage files

```bash
# Unstage specific file
git reset HEAD filename.js

# Unstage everything
git reset HEAD .
```

### Discard local changes

```bash
# Discard changes in one file
git checkout -- filename.js

# Discard all unstaged changes (⚠️ destructive)
git checkout -- .
```

### Recover deleted branch

```bash
# View reflog to find commit
git reflog

# Create branch from that commit
git checkout -b recovered-branch abc1234
```

### Merge conflicts during pull

```bash
# Abort merge, keep pre-merge state
git merge --abort

# Or reset hard (⚠️ loses local changes)
git reset --hard HEAD
```

### Force pull (overwrite local)

```bash
# ⚠️ DANGER: Destroys local changes
git fetch origin
git reset --hard origin/main
```

## Emergency Reference

| Situation | Command |
|-----------|---------|
| Undo last commit, keep changes | `git reset HEAD~1` |
| Undo last commit, discard changes | `git reset --hard HEAD~1` |
| Fix commit message | `git commit --amend -m "new"` |
| Save changes temporarily | `git stash` |
| Get stashed changes back | `git stash pop` |
| Abandon everything, match remote | `git reset --hard origin/main` |
| Unstage file | `git reset HEAD <file>` |
| Unstage all | `git reset HEAD .` |
| Restore deleted file | `git checkout -- <file>` |
