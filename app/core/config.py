import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/org_structure")
    MAX_DEPTH: int = 5
    DEFAULT_DEPTH: int = 1

settings = Settings()
