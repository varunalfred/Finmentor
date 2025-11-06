# PGVector Setup Guide for Windows

PGVector enables efficient vector similarity search in PostgreSQL, essential for semantic search and AI embeddings.

---

## Installation Methods

### Method 1: Docker (Recommended) ⭐
**Pros:** Quick, pre-configured, isolated environment  
**Cons:** Requires Docker Desktop  
**Time:** ~5-10 minutes

```powershell
# Pull PGVector-enabled PostgreSQL image
docker pull pgvector/pgvector:0.8.0-pg17

# Run container
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=finmentor \
  -p 5432:5432 \
  pgvector/pgvector:0.8.0-pg17

# Connect and verify
docker exec -it postgres-pgvector psql -U postgres -d finmentor
```

In psql:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

---

### Method 2: Native Installation (Advanced) 🔧
**Pros:** No Docker needed, uses existing PostgreSQL  
**Cons:** Complex compilation on Windows, more time-consuming  
**Time:** ~30-45 minutes

#### Prerequisites
- PostgreSQL 17.5 installed
- Admin rights on Windows
- Internet connection

#### Step 1: Install Visual Studio Build Tools

Open PowerShell as **Administrator**:

```powershell
winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"
```

⏱️ Wait 5-10 minutes for installation to complete.

#### Step 2: Open Developer Command Prompt

1. Press **Win** key
2. Search for **"x64 Native Tools Command Prompt for VS 2022"**
3. Right-click → **Run as Administrator**

#### Step 3: Set PostgreSQL Path

In the Developer Command Prompt:

```cmd
set "PGROOT=C:\Program Files\PostgreSQL\17"
```

> ⚠️ **Note:** Verify this path matches your PostgreSQL installation. Adjust if different.

#### Step 4: Clone pgvector Repository

```cmd
cd %TEMP%
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
```

#### Step 5: Compile and Install

```cmd
nmake /F Makefile.win
nmake /F Makefile.win install
```

✅ Expected output: Compilation messages, then "Installation successful" or similar.

#### Step 6: Verify Installation Files

```cmd
dir "C:\Program Files\PostgreSQL\17\share\extension\vector*"
```

✅ Should show: `vector.control` and `vector--0.8.0.sql`

#### Step 7: Enable Extension in PostgreSQL

Open psql:

```bash
psql -U postgres
```

In psql:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

✅ Expected output:

```
 extname | extversion
---------+------------
 vector  | 0.8.0
```

---

## Python Package Installation

After PostgreSQL extension is enabled, install the Python package:

```powershell
# Activate your virtual environment first
.\venv\Scripts\Activate.ps1

# Install pgvector Python package
pip install pgvector==0.4.1
```

Verify installation:

```powershell
python -c "from pgvector.sqlalchemy import Vector; print('✅ PGVector Python package installed')"
```

---

## Enable in Your Database

Run the setup script to enable PGVector in your FinMentor database:

```powershell
python scripts/enable_pgvector.py
```

✅ Expected output:
```
INFO:__main__:Enabling PGVector extension...
INFO:__main__:✅ PGVector extension already enabled
INFO:__main__:✅ PGVector version: 0.8.0

🎉 PGVector is now enabled! Restart your server to use vector embeddings.
```

---

## Verification

### 1. Check Database Extension

```sql
-- Connect to your database
psql -U postgres -d finmentor

-- List all extensions
\dx

-- Should show 'vector' in the list
```

### 2. Test Vector Operations

```sql
-- Create test table
CREATE TABLE test_vectors (
    id serial PRIMARY KEY,
    embedding vector(3)
);

-- Insert sample vectors
INSERT INTO test_vectors (embedding) VALUES 
    ('[1,2,3]'),
    ('[4,5,6]'),
    ('[7,8,9]');

-- Query by similarity (L2 distance)
SELECT id, embedding <-> '[3,3,3]' AS distance
FROM test_vectors
ORDER BY distance
LIMIT 3;

-- Clean up
DROP TABLE test_vectors;
```

### 3. Restart Your Server

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ The warning should be **gone**:
```
# Before:
⚠️  PGVector not available - using JSON for embeddings (limited semantic search)

# After:
✅ PGVector enabled - using optimized vector operations
```

---

## Troubleshooting

### Error: "could not access file "$libdir/vector""

**Cause:** Extension files not in PostgreSQL lib directory  
**Solution:**
```cmd
# Re-run installation in Developer Command Prompt
cd %TEMP%\pgvector
nmake /F Makefile.win install
```

### Error: "permission denied for database"

**Cause:** Insufficient privileges  
**Solution:**
```sql
-- Grant superuser temporarily
ALTER USER your_user WITH SUPERUSER;

-- Enable extension
CREATE EXTENSION vector;

-- Revoke superuser
ALTER USER your_user WITH NOSUPERUSER;
```

### Warning persists after installation

**Cause:** Python package not installed or wrong environment  
**Solution:**
```powershell
# Ensure venv is active
.\venv\Scripts\Activate.ps1

# Reinstall package
pip uninstall pgvector -y
pip install pgvector==0.4.1

# Restart server
```

---

## Benefits of PGVector

### Without PGVector (JSON storage)
- ❌ Slow similarity search (full table scans)
- ❌ No indexing for embeddings
- ❌ Limited to small datasets
- ❌ High memory usage

### With PGVector (Vector storage)
- ✅ Fast similarity search (IVFFlat/HNSW indexes)
- ✅ Optimized distance calculations (L2, cosine, inner product)
- ✅ Scales to millions of vectors
- ✅ Low memory footprint

---

## Usage in FinMentor

PGVector is used for:

1. **Semantic Search**: Find similar financial queries in conversation history
2. **Educational Content**: Match user questions to relevant learning materials
3. **Portfolio Analysis**: Compare investment strategies using embeddings
4. **User Profiling**: Find similar user behavior patterns

### Example: Semantic Message Search

```python
from sqlalchemy import select
from models.database import Message

# Find messages similar to a query
query_embedding = [0.1, 0.2, 0.3, ...]  # 1536 dims from OpenAI/Gemini

similar_messages = await session.execute(
    select(Message)
    .order_by(Message.embedding.l2_distance(query_embedding))
    .limit(5)
)
```

---

## Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| PostgreSQL | 17.5 | Required for PGVector 0.8.0 |
| PGVector Extension | 0.8.0 | Latest stable |
| Python pgvector | 0.4.1 | SQLAlchemy integration |
| Embedding Dims | 1536 | OpenAI/Gemini standard |

---

## Additional Resources

- [PGVector GitHub](https://github.com/pgvector/pgvector)
- [PGVector Documentation](https://github.com/pgvector/pgvector#pgvector)
- [Python Package Docs](https://github.com/pgvector/pgvector-python)
- [FinMentor Database Schema](./DATABASE_MANAGEMENT.md)

---

**Last Updated:** November 5, 2025  
**Maintained By:** Development Team
