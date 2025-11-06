# Database Management Strategy

## Current Tables (11 total)

Your database schema includes:
1. **users** - User accounts and authentication
2. **conversations** - Chat conversation sessions
3. **messages** - Individual chat messages
4. **message_feedback** - User feedback on responses
5. **portfolios** - User investment portfolios
6. **holdings** - Individual asset holdings
7. **transactions** - Buy/sell transaction records
8. **learning_progress** - Educational progress tracking
9. **educational_content** - Learning resources
10. **user_activity** - User activity logs
11. **query_analytics** - Performance analytics

## Initial Setup (First Time Only)

Run once to create all tables:
```bash
cd backend
.\venv\Scripts\Activate.ps1
python scripts\init_db.py
```

This creates all tables based on `models/database.py`

## Future Changes: Use Alembic Migrations

**DO NOT modify `scripts/init_db.py` for schema changes!**

Instead, use Alembic for all future database changes:

### Why Alembic?
- ✅ Tracks database version history
- ✅ Allows rollback if something goes wrong
- ✅ Works on production databases without losing data
- ✅ Team members can sync database changes easily

### How to Make Schema Changes:

#### 1. Modify the Model
First, edit `models/database.py`:
```python
# Example: Add a new column to User table
class User(Base):
    __tablename__ = "users"
    # ... existing columns ...
    phone_number = Column(String(20))  # NEW COLUMN
```

#### 2. Create Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add phone_number to users"
```

This creates a new file in `migrations/versions/` like:
`20251105_1234-abc123_add_phone_number_to_users.py`

#### 3. Review Migration
Open the generated file and verify the changes are correct:
```python
def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(20)))

def downgrade():
    op.drop_column('users', 'phone_number')
```

#### 4. Apply Migration
```bash
# Apply the migration to database
alembic upgrade head
```

#### 5. Rollback (if needed)
```bash
# Undo the last migration
alembic downgrade -1

# Or go to specific version
alembic downgrade abc123
```

### Common Migration Scenarios:

**Add a new table:**
1. Create new class in `models/database.py`
2. `alembic revision --autogenerate -m "Add new_table"`
3. `alembic upgrade head`

**Add a column:**
1. Add column to existing class in `models/database.py`
2. `alembic revision --autogenerate -m "Add column to table"`
3. `alembic upgrade head`

**Modify a column:**
1. Change column definition in `models/database.py`
2. `alembic revision --autogenerate -m "Modify column type"`
3. Review and edit the migration file (autogenerate might not catch all changes)
4. `alembic upgrade head`

**Delete a column/table:**
1. Remove from `models/database.py`
2. `alembic revision --autogenerate -m "Remove column/table"`
3. `alembic upgrade head`

### Check Migration Status:

```bash
# See current version
alembic current

# See migration history
alembic history

# See pending migrations
alembic show head
```

### Important Notes:

- ✅ **First time setup**: Use `scripts/init_db.py` (creates all tables)
- ✅ **All future changes**: Use Alembic migrations
- ⚠️ **Never** edit database directly in production
- ⚠️ **Always** test migrations on dev database first
- 💾 **Commit** migration files to git
- 🔄 Team members run `alembic upgrade head` to sync their databases

## File Organization:

```
backend/
├── models/
│   └── database.py          # Define schema HERE
├── scripts/
│   └── init_db.py           # Initial setup only (run once)
├── migrations/
│   ├── env.py               # Alembic config (already set up)
│   └── versions/            # Migration files (auto-generated)
│       └── YYYYMMDD_HHMM-hash_description.py
└── alembic.ini              # Alembic configuration
```

## Summary:

1. **Initial setup** → Run `python scripts/init_db.py` (once)
2. **Schema changes** → Modify `models/database.py` + Alembic migration
3. **Apply changes** → `alembic upgrade head`
4. **Rollback** → `alembic downgrade -1`
