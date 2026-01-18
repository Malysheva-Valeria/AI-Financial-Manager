# Git Workflow Guide - AI Financial Manager

**Professional Git workflow for backend (Python/FastAPI) development**

---

## Overview

This project follows **Git Flow** with feature branches and Pull Requests. We use **Conventional Commits** for automatic versioning and changelog generation.

### Branch Structure

```
main (production)
  ↑
develop (staging)
  ↑
feature/issue-N-description
```

- `main` - Production-ready code, tagged releases
- `develop` - Integration branch, always deployable
- `feature/issue-N-*` - Feature branches from GitHub Issues

---

## Quick Reference

### Start Working on Issue

```bash
# 1. Update develop
git checkout develop
git pull origin develop

# 2. Create feature branch from issue
git checkout -b feature/issue-7-user-model

# Branch naming convention:
# feature/issue-N-short-description
# bugfix/issue-N-short-description
# hotfix/critical-bug-description
```

### Commit Your Work

```bash
# Check status
git status
git diff  # Review changes before committing

# Stage changes
git add .                    # All changes
git add backend/app/models/  # Specific directory
git add -p                   # Interactive staging

# Commit with conventional format
git commit -m "feat(models): add User model with Pydantic validators

- Implemented UserModel with EmailStr validation
- Added TrackingMode enum
- Created domain entity with business logic

Closes #7"

# Push to GitHub
git push -u origin feature/issue-7-user-model  # First time
git push                                        # Subsequent pushes
```

### Create Pull Request

```bash
# 1. Ensure all changes are committed and pushed
git status  # Should show "nothing to commit, working tree clean"
git push

# 2. Go to GitHub → Pull Requests → New Pull Request
# 3. Set base: develop ← compare: feature/issue-N-...
# 4. Fill PR template, review changes, and create PR
# 5. Wait for CI checks to pass
# 6. Merge when approved (use "Squash and merge")
```

---

## Conventional Commits

Use **Conventional Commits** format for automatic GitHub Project integration and clear history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add JWT authentication` |
| `fix` | Bug fix | `fix(models): correct email validation` |
| `docs` | Documentation | `docs(api): update endpoint examples` |
| `style` | Code style (formatting) | `style(app): apply black formatter` |
| `refactor` | Code refactoring | `refactor(repos): extract common query logic` |
| `test` | Add/update tests | `test(models): add UserModel integration tests` |
| `chore` | Maintenance | `chore(deps): update FastAPI to 0.110.0` |
| `perf` | Performance improvement | `perf(db): add index on user email` |
| `ci` | CI/CD changes | `ci(docker): optimize build caching` |

### Scopes (for this project)

- `models` - Database models
- `api` - API endpoints
- `auth` - Authentication/authorization
- `repos` - Repositories
- `services` - Business logic services
- `tests` - Testing infrastructure
- `db` - Database/migrations
- `docker` - Docker configuration

### Examples

#### Feature Commit
```bash
git commit -m "feat(models): implement Transaction model

- Add TransactionModel with SQLModel
- Include amount, category, and datetime fields
- Add validators for positive amounts
- Link to UserModel via foreign key

Closes #8"
```

#### Bug Fix
```bash
git commit -m "fix(validators): correct email lowercase normalization

Email validator was not applying lowercase transformation.
Added mode='before' to Pydantic field_validator.

Fixes #15"
```

#### Documentation
```bash
git commit -m "docs(git): add professional workflow guide

Created comprehensive Git workflow documentation
with conventional commits and GitHub integration.

Related to #7"
```

---

## GitHub Integration

### Automatic Issue Movement

Use keywords in commits and PR descriptions to auto-move issues:

| Keyword | Effect |
|---------|--------|
| `Closes #N` | Closes issue when PR is merged |
| `Fixes #N` | Same as Closes |
| `Resolves #N` | Same as Closes |
| `Related to #N` | Links to issue (doesn't close) |
| `Refs #N` | References issue |

**Example:**
```bash
git commit -m "feat(budget): implement 50/30/20 rule calculation

Closes #9
Related to #8"
```

When this PR is merged to `develop`, Issue #9 will automatically close and move to "Done" column in GitHub Project.

---

## Workflow Steps (Detailed)

### 1. Starting New Work

```bash
# Always start from latest develop
git checkout develop
git pull origin develop

# Verify you're on develop
git branch -v

# Create feature branch
git checkout -b feature/issue-N-description

# Example:
git checkout -b feature/issue-8-transaction-model
```

### 2. During Development

#### Make Small, Focused Commits

```bash
# Work on feature...

# Review what changed
git status
git diff

# Stage changes (be selective!)
git add backend/app/models/transaction.py
git add backend/tests/models/test_transaction.py

# Commit with good message
git commit -m "feat(models): add Transaction model structure

- Define TransactionModel with SQLModel
- Add amount, category, type fields
- Include created_at timestamp

Part of #8"

# Continue working...
git add backend/app/models/transaction.py
git commit -m "feat(models): add Transaction validators

- Validate positive amounts
- Ensure category is from allowed list
- Add tests for validation

Part of #8"
```

#### Push Regularly

```bash
# Push to backup your work
git push -u origin feature/issue-8-transaction-model  # First time
git push  # After that
```

### 3. Keeping Branch Updated

If `develop` gets updated while you're working:

```bash
# From your feature branch
git fetch origin develop

# Option A: Rebase (cleaner history)
git rebase origin/develop
# Resolve conflicts if any, then:
git rebase --continue
git push --force-with-lease  # Safe force push

# Option B: Merge (preserves history)
git merge origin/develop
# Resolve conflicts, then:
git push
```

**Recommendation:** Use rebase for cleaner history.

### 4. Before Creating PR

#### Self-Review Checklist

```bash
# 1. All tests pass
docker exec finance_api pytest tests/ -v

# 2. Code is formatted
docker exec finance_api black app/
docker exec finance_api isort app/

# 3. No debug code left
git diff develop  # Review all changes

# 4. All changes committed
git status  # Should be clean

# 5. Push latest changes
git push
```

### 5. Creating Pull Request

#### On GitHub:

1. Navigate to repository
2. Click **"Pull requests"** → **"New pull request"**
3. Set:
   - Base: `develop`
   - Compare: `feature/issue-N-description`
4. Fill out PR template:

```markdown
## Description
Implemented Transaction model with full validation suite.

## Changes
- Added `TransactionModel` with SQLModel ORM
- Created domain entity `Transaction`
- Implemented validators for amount and category
- Added 15 unit tests and 8 integration tests

## Testing
- ✅ All 23 tests passing
- ✅ Manual testing with test data
- ✅ Database migrations work correctly

## Related Issues
Closes #8
Related to #7 (depends on User model)

## Screenshots (if applicable)
N/A - Backend only

## Checklist
- [x] Tests pass locally
- [x] Code follows project conventions
- [x] Documentation updated
- [x] No breaking changes
```

5. **Assign yourself**
6. **Add labels**: `backend`, `database`, `enhancement`
7. **Link to Project**: Auto-linked via issue number
8. Click **"Create pull request"**

### 6. After PR Created

#### Wait for CI Checks

- GitHub Actions will run tests
- Check "Checks" tab for results
- Fix any failures and push again

#### Review Your Own PR

1. Go to **"Files changed"** tab
2. Review every line
3. Add inline comments if needed
4. Look for:
   - Leftover debug code
   - Commented code
   - TODO comments
   - Sensitive data

#### Merging

When ready:
1. Click **"Squash and merge"** (preferred)
   - Keeps develop history clean
   - All commits squashed into one
2. Edit final commit message if needed
3. Click **"Confirm squash and merge"**
4. Delete branch

```bash
# Locally, clean up and get updated develop
git checkout develop
git pull origin develop
git branch -d feature/issue-8-transaction-model  # Delete local branch
```

---

## Best Practices

### ✅ Do's

- **Commit often** - Small, focused commits
- **Write good messages** - Use conventional commits
- **Test before pushing** - Run tests locally first
- **Keep branches short-lived** - Merge within 1-2 days
- **Rebase on develop** - Stay up-to-date
- **Review your own PR** - Catch mistakes before others see them

### ❌ Don'ts

- **Don't commit to develop directly** - Always use feature branches
- **Don't push broken code** - Test first
- **Don't commit secrets** - Use .env (already in .gitignore)
- **Don't leave WIP commits** - Squash before PR
- **Don't ignore conflicts** - Resolve immediately
- **Don't commit generated files** - Check .gitignore

---

## Useful Commands

### Inspecting Changes

```bash
# See what changed
git status
git diff
git diff --staged  # Changes staged for commit
git log --oneline -10  # Last 10 commits

# See changes in specific file
git diff backend/app/models/user.py
git log backend/app/models/user.py  # History of file
```

### Undoing Mistakes

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo changes in file (before staging)
git checkout -- backend/app/models/user.py

# Unstage file
git reset backend/app/models/user.py

# Amend last commit message
git commit --amend -m "new message"

# Amend last commit with new changes
git add forgotten_file.py
git commit --amend --no-edit
```

### Stashing Work

```bash
# Save work in progress
git stash save "WIP: working on validators"

# List stashes
git stash list

# Apply stash
git stash pop  # Apply and remove
git stash apply  # Apply but keep stash

# Drop stash
git stash drop stash@{0}
```

### Cherry-Picking Commits

Cherry-pick дозволяє перенести конкретні коміти з однієї гілки в іншу.

#### Use Case 1: Перенести коміт з однієї feature гілки в іншу

```bash
# Ситуація: Зробила коміт в feature/issue-8, 
# але він потрібен також в feature/issue-9

# 1. Знайди hash потрібного коміту
git log --oneline feature/issue-8
# Наприклад: a1b2c3d feat(validators): add email validation helper

# 2. Перейди на цільову гілку
git checkout feature/issue-9

# 3. Перенеси коміт
git cherry-pick a1b2c3d

# 4. Якщо є конфлікти - розв'яжи їх
# Відредагуй файли, потім:
git add .
git cherry-pick --continue

# 5. Запуш зміни
git push
```

#### Use Case 2: Випадково закомітила в develop

```bash
# Помилка: закомітила feature в develop замість feature гілки

# 1. Подивись коміт який треба перенести
git log -1  # Запам'ятай hash, наприклад b4c5d6e

# 2. Видали коміт з develop (але НЕ видаляй зміни)
git reset --hard HEAD~1

# 3. Створи/перейди на правильну гілку
git checkout -b feature/issue-10-correct-branch

# 4. Перенеси коміт
git cherry-pick b4c5d6e

# 5. Запуш
git push -u origin feature/issue-10-correct-branch
```

#### Use Case 3: Hotfix в production потрібен в develop

```bash
# Зробила hotfix в main, треба також в develop

# 1. З main дізнайся hash hotfix коміту
git log --oneline main -5
# Наприклад: e7f8g9h fix(auth): prevent token expiration bug

# 2. Перейди на develop
git checkout develop
git pull origin develop

# 3. Перенеси hotfix
git cherry-pick e7f8g9h

# 4. Запуш
git push origin develop
```

#### Use Case 4: Вибірково перенести кілька комітів

```bash
# Хочу перенести коміти A, C, E але не B і D

# 1. Знайди хеші потрібних комітів
git log --oneline feature/issue-11

# 2. Перейди на цільову гілку
git checkout feature/issue-12

# 3. Перенеси коміти по черзі
git cherry-pick commit-A-hash
git cherry-pick commit-C-hash
git cherry-pick commit-E-hash

# АБО одною командою
git cherry-pick commit-A-hash commit-C-hash commit-E-hash
```

#### Cherry-Pick з Конфліктами

```bash
# Під час cherry-pick виникли конфлікти

# 1. Git покаже які файли мають конфлікти
git status

# 2. Відкрий файли і розв'яжи конфлікти
# Видали <<<<<<, =====, >>>>>> маркери

# 3. Додай розв'язані файли
git add resolved-file.py

# 4. Продовжи cherry-pick
git cherry-pick --continue

# 5. АБО скасуй cherry-pick якщо передумала
git cherry-pick --abort
```

#### Cherry-Pick Range (діапазон комітів)

```bash
# Перенести всі коміти від старого до нового

# 1. Знайди початковий і кінцевий hash
git log --oneline feature/issue-13

# 2. Cherry-pick range (виключає start-hash)
git cherry-pick start-hash..end-hash

# 3. Cherry-pick range (включає start-hash)
git cherry-pick start-hash^..end-hash
```

#### Корисні опції cherry-pick

```bash
# Не комітити автоматично (щоб переглянути зміни)
git cherry-pick -n commit-hash  # або --no-commit
git status
git diff --staged
git commit -m "Custom message"

# Зберегти оригінальний commit message
git cherry-pick -x commit-hash  # Додає "(cherry picked from commit ...)"

# Підписати коміт
git cherry-pick -s commit-hash  # Додає Signed-off-by
```

---

## CI/CD Integration (Future)

When CI/CD is set up:

```yaml
# .github/workflows/backend-tests.yml
name: Backend Tests

on:
  pull_request:
    branches: [develop, main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: docker-compose run api pytest tests/
```

**Benefits:**
- Auto-run tests on every PR
- Prevent merging broken code
- Run linters automatically
- Deploy to staging on merge to develop

---

## Troubleshooting

### Merge Conflicts

```bash
# When you see conflict
git status  # Shows conflicted files

# Open file, look for:
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> develop

# Edit file to resolve, then:
git add resolved_file.py
git rebase --continue  # or git merge --continue
```

### Accidentally Committed to Wrong Branch

```bash
# You're on develop but wanted feature branch
git log -1  # Note commit hash

git reset --hard HEAD~1  # Undo commit on develop
git checkout -b feature/issue-N-description
git cherry-pick <commit-hash>  # Apply commit to feature branch
```

### Pushed Sensitive Data

```bash
# Remove from history (DANGER!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (be careful!)
git push origin --force --all
```

**Better:** Contact admin to rotate secrets immediately.

---

## Quick Command Reference

```bash
# Setup
git checkout develop && git pull origin develop
git checkout -b feature/issue-N-description

# Work
git status
git add <files>
git commit -m "type(scope): message"
git push

# Update
git fetch origin develop
git rebase origin/develop

# Finish
git push
# Create PR on GitHub
# Merge → Delete branch
git checkout develop && git pull origin develop
```

---

## Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Semantic Versioning](https://semver.org/)

---

**Last Updated:** 2026-01-18  
**Project:** AI Financial Manager  
**Team:** Solo (Backend only - Swift/iOS separate)
