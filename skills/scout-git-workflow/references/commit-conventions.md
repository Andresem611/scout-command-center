# Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear, structured commit messages.

## Format

```
<type>[(optional scope)]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Use When | Example |
|------|----------|---------|
| `feat` | New feature | `feat: add user login` |
| `fix` | Bug fix | `fix: resolve auth timeout` |
| `docs` | Documentation only | `docs: update API reference` |
| `style` | Code style (formatting, semicolons) | `style: format with prettier` |
| `refactor` | Code change that neither fixes nor adds | `refactor: simplify auth logic` |
| `test` | Adding/updating tests | `test: add login unit tests` |
| `chore` | Build, tooling, dependencies | `chore: update dependencies` |

## Scopes (Optional)

Use parentheses to specify what area changed:

```
feat(auth): add password reset
fix(api): handle null responses
docs(readme): add setup instructions
```

Common scopes for Thoven projects:
- `api` - Backend API changes
- `ui` - User interface
- `db` - Database/schema changes
- `auth` - Authentication
- `config` - Configuration files

## Rules

1. **Use imperative mood**: "add" not "added" or "adds"
2. **No period at end** of description
3. **Max 72 chars** for description line
4. **Be specific**: "fix login bug" → "fix: resolve timeout on login form submit"

## Examples

```bash
# Good
feat: implement user registration
fix(auth): resolve session expiration bug
docs: add environment setup guide
chore: upgrade Next.js to 14.0.0

# Bad
feat: implemented user registration      # past tense
fix: bug fix                            # vague
docs: updated readme.                   # period, past tense
chore(deps): update stuff               # vague
```

## When to Commit

### DO Commit

- Logical unit of work is complete
- Tests pass
- Code compiles/builds
- Self-contained change

### DON'T Commit

- Broken code (doesn't compile/tests fail)
- Multiple unrelated changes together
- Debug code or console.logs
- Sensitive data (passwords, keys)

## Commit Frequency

- **Small, frequent commits** > large, rare commits
- Commit when a feature/part is working
- Don't let uncommitted work sit for days

## Branch Naming

| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Feature | `feature/<description>` | `feature/user-auth` |
| Bug fix | `fix/<description>` | `fix/login-redirect` |
| Hotfix | `hotfix/<description>` | `hotfix/payment-bug` |
| Release | `release/<version>` | `release/v1.2.0` |

### Branch Naming Rules

1. Lowercase only
2. Use hyphens, not underscores
3. Keep it descriptive but concise
4. Include issue number if applicable: `feature/123-user-auth`
