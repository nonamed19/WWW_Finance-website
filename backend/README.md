# FastAPI backend

This directory is served by FastAPI. It retains the public routes used by the
Vue frontend, including the Django REST-compatible `Token <key>` authorization
header, so no frontend API rewiring is required.

## Run locally

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, with interactive OpenAPI
documentation at `/docs` and a health check at `/health/`.

## MySQL setup

Create the database with UTF-8 support, then enter its URL in `.env`.

```sql
CREATE DATABASE www_financial CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```dotenv
DATABASE_URL=mysql+pymysql://www_user:password@127.0.0.1:3306/www_financial?charset=utf8mb4
```

FastAPI creates the required MySQL tables automatically at startup.
