# Alembic Migrations Guide

## Overview
Professional database migration management using Alembic for the AI Financial Manager project.

---

## Setup Complete ✅

Alembic has been initialized and configured for Docker environment with:
- SQLModel metadata integration
- Settings-based database URL
- All models imported (User, Transaction, Budget)
- Type and default value comparison enabled

---

## How to Create Migrations

### 1. After Merging Model Changes

Once PR #7, #8, #9 are merged to `develop`:

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Navigate to backend directory
cd backend

# Generate migration automatically
docker exec finance_api alembic revision --autogenerate -m "Add users, transactions, budgets tables"
```

This will create a file like: `alembic/versions/abc123_add_users_transactions_budgets_tables.py`

### 2. Review Generated Migration

```bash
# View the generated migration
cat alembic/versions/*_add_users_transactions_budgets_tables.py
```

Check that it includes:
- `users` table with all fields
- `transactions` table with foreign key to users
- `budgets` table with foreign key to users  
- All indexes and constraints

### 3. Apply Migration

```bash
# Apply migration to database
docker exec finance_api alembic upgrade head

# Check current version
docker exec finance_api alembic current

# View migration history
docker exec finance_api alembic history
```

### 4. Verify in Database

```bash
# Connect to PostgreSQL
docker exec -it finance_db psql -U postgres -d finance_db

# List all tables
\dt

# Should see:
# - users
# - transactions
# - budgets
# - alembic_version

# Check users table structure
\d users

# Check foreign keys
\d transactions
\d budgets

# Exit
\q
```

---

## Common Migration Commands

### Create New Migration

```bash
# Auto-generate from model changes
docker exec finance_api alembic revision --autogenerate -m "description"

# Create empty migration (for data migrations)
docker exec finance_api alembic revision -m "description"
```

### Apply Migrations

```bash
# Upgrade to latest
docker exec finance_api alembic upgrade head

# Upgrade one version
docker exec finance_api alembic upgrade +1

# Downgrade one version
docker exec finance_api alembic downgrade -1

# Downgrade to specific version
docker exec finance_api alembic downgrade <revision>
```

### View Migration Status

```bash
# Current version
docker exec finance_api alembic current

# Migration history
docker exec finance_api alembic history

# Show SQL without executing
docker exec finance_api alembic upgrade head --sql
```

---

## Migration Best Practices

### 1. Always Review Auto-Generated Migrations

Alembic `--autogenerate` is smart but not perfect. Always review:
- Column types are correct
- Indexes are created
- Foreign keys have correct ON DELETE behavior
- No unwanted table drops

### 2. Test Migrations Locally First

```bash
# Create test database
docker exec finance_api alembic upgrade head

# Verify everything works
docker exec finance_api pytest

# If issues, downgrade
docker exec finance_api alembic downgrade -1
```

### 3. Keep Migrations Small

One logical change per migration:
- ✅ Good: "Add email_verified column to users"
- ❌ Bad: "Add 5 tables and change 3 existing ones"

### 4. Never Edit Applied Migrations

If migration is already applied (`alembic upgrade`):
- Don't edit it
- Create a new migration to fix issues

### 5. Add Data Migrations When Needed

```python
# Example: Set default values
def upgrade():
    op.execute("UPDATE users SET tracking_mode = 'MANUAL' WHERE tracking_mode IS NULL")

def downgrade():
    pass
```

---

## Troubleshooting

### Issue: "Table already exists"

If tables were created manually (via `create_db_and_tables()`):

```bash
# Mark current state as migrated without running migrations
docker exec finance_api alembic stamp head
```

### Issue: Models not detected

Ensure all models are imported in `alembic/env.py`:

```python
from app.infrastructure.persistence import (
    UserModel,
    TransactionModel,
    BudgetModel
)
```

### Issue: Database URL not found

Check `.env` file has `DATABASE_URL` or all individual db variables.

---

## Production Deployment

### Initial Setup

```bash
# 1. Pull latest code
git pull origin main

# 2. Run migrations
docker exec finance_api alembic upgrade head

# 3. Verify
docker exec finance_api alembic current
```

### Rolling Back

```bash
# Downgrade one version
docker exec finance_api alembic downgrade -1

# Downgrade to specific version
docker exec finance_api alembic downgrade <revision_id>
```

---

## File Structure

```
backend/
├── alembic.ini              # Alembic configuration
├── alembic/
│   ├── env.py              # Environment setup (imports models)
│   ├── script.py.mako      # Template for new migrations
│   ├── README              # Alembic readme
│   └── versions/           # Migration files
│       └── abc123_initial.py
```

---

## Next Steps After Setup

1. ✅ Merge PR #7, #8, #9 first
2. ✅ Create initial migration
3. ✅ Apply to database
4. ✅ Verify tables created
5. ✅ Test application endpoints

---

**Status:** Alembic configured and ready ✅  
**PR:** https://github.com/Malysheva-Valeria/AI-Financial-Manager/pull/new/feature/alembic-setup
