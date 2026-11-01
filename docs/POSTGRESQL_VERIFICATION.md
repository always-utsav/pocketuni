# PocketUni — PostgreSQL 18 Verification Record

## 1. Environment & Database Configuration
- **DBMS:** PostgreSQL 18.6 on x86_64-pc-windows-msvc, 64-bit
- **Host:** localhost:5432
- **Database:** `pocketuni`
- **Application User:** `postgres`
- **Driver:** `psycopg` 3 (`postgresql+psycopg`)
- **SQLAlchemy URL Construction:** Constructed via `sqlalchemy.engine.URL.create()` to ensure special characters (e.g., trailing `#`) in passwords are parsed cleanly without URL escape corruption or accidental comment truncation.
- **Masked Connection String:** `postgresql+psycopg://postgres:***@localhost:5432/pocketuni`

## 2. Verification Queries & Execution Results

```sql
SELECT version();
```
**Output:**
```
PostgreSQL 18.6 on x86_64-pc-windows-msvc, compiled by Visual C++ build 1944, 64-bit
```

```sql
SELECT current_database();
```
**Output:**
```
pocketuni
```

```sql
SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';
```
**Output:**
```
51 (50 application tables + alembic_version)
```

```sql
SELECT version_num FROM alembic_version;
```
**Output:**
```
1e5131ff1c7b (Initial 50 table schema)
```

## 3. Database Health Check Verification

`GET /api/health` returns HTTP 200:
```json
{
  "status": "HEALTHY",
  "service": "PocketUni Backend",
  "module": "1 of 3 (Foundation, Auth, Super Admin, Doc Management)",
  "environment": "development",
  "database": {
    "status": "HEALTHY",
    "driver": "postgresql+psycopg",
    "database": "pocketuni",
    "version": "PostgreSQL 18.6 on x86_64-pc-windows-msvc...",
    "url": "postgresql+psycopg://postgres:***@localhost:5432/pocketuni"
  }
}
```

## 4. Connection Rules Enforced
1. **No SQLite Fallback:** SQLite fallback has been completely removed from runtime operation. If PostgreSQL is offline, the API immediately throws an `OperationalError` and refuses startup.
2. **Credential Privacy:** Password values are never logged, serialized, or returned over API endpoints.
3. **Shared Migration Engine:** `backend/alembic/env.py` directly consumes `settings.get_database_url_object()`, ensuring Alembic and FastAPI always target the exact same database.
