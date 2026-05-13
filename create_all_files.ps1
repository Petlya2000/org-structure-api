# create_all_files.ps1
Write-Host "Creating project..." -ForegroundColor Green

$folders = @("app\api\routers","app\core","app\models","app\schemas","app\services","app\utils","app\tests","alembic\versions")
foreach ($folder in $folders) { New-Item -ItemType Directory -Force -Path $folder | Out-Null; Write-Host "Created: $folder" -ForegroundColor Yellow }

$files = @{
"requirements.txt" = @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
"@
"docker-compose.yml" = @"
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: org_structure
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/org_structure
    volumes:
      - .:/app
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
volumes:
  postgres_data:
"@
"Dockerfile" = @"
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"@
".env" = "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/org_structure"
"alembic.ini" = @"
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@db:5432/org_structure
"@
"app\__init__.py" = ""
"app\main.py" = @"
import logging
from fastapi import FastAPI
from app.api.routers import departments, employees
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Organizational Structure API")
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])
@app.get("/")
async def root():
    return {"message": "Organizational Structure API", "docs": "/docs"}
"@
"app\core\__init__.py" = ""
"app\core\config.py" = ""
"app\models\__init__.py" = ""
"app\models\department.py" = ""
"app\models\employee.py" = ""
"app\api\__init__.py" = ""
"app\api\dependencies.py" = ""
"app\api\routers\__init__.py" = ""
"app\api\routers\departments.py" = ""
"app\api\routers\employees.py" = ""
"app\schemas\__init__.py" = ""
"app\services\__init__.py" = ""
"app\utils\__init__.py" = ""
"app\tests\__init__.py" = ""
}
foreach ($file in $files.Keys) { $dir = Split-Path $file -Parent; if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }; Set-Content -Path $file -Value $files[$file] -Encoding UTF8; Write-Host "Created: $file" -ForegroundColor Cyan }
Write-Host "`nDone! Run: docker-compose up --build" -ForegroundColor Green
