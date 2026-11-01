import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    PROJECT_NAME: str = "PocketUni"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Primary DB_* configuration (as requested in Part B)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "pocketuni"
    
    # Backward-compatible POSTGRES_* aliases
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    DATABASE_URL: str = ""
    
    # Explicit isolated test override flag (never enabled by default)
    USE_SQLITE_TEST_DB: bool = False
    
    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production-mits-pocketuni-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for dev convenience
    
    # Local Dev Auth
    LOCAL_DEV_AUTH_ENABLED: bool = True
    
    # Super Admin Allowlist
    SUPER_ADMIN_ALLOWLIST: List[str] = [
        "utsavkumawat05@gmail.com",
        "guptamahi0207@gmail.com"
    ]
    
    # Institutional Domains
    STUDENT_EMAIL_DOMAINS: List[str] = ["mitsgwl.ac.in", "example.invalid"]
    FACULTY_EMAIL_DOMAINS: List[str] = ["mitsgwalior.in", "example.invalid"]
    
    # Storage
    STORAGE_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../storage")
    )

    # Gemini AI Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 2048
    GEMINI_TIMEOUT: int = 30
    GEMINI_MAX_RETRIES: int = 3
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    model_config = SettingsConfigDict(
        env_file=[".env", "backend/.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_url_object(self) -> URL:
        """
        Construct database URL using SQLAlchemy URL.create() with psycopg 3.
        Never concatenates raw passwords to avoid character escaping issues (e.g. trailing '#').
        """
        # Explicit test isolation only
        if self.USE_SQLITE_TEST_DB:
            return URL.create("sqlite", database="./test_pocketuni.db")
        
        # If full DATABASE_URL string provided (e.g. from cloud or CI)
        if self.DATABASE_URL:
            from sqlalchemy.engine import make_url
            return make_url(self.DATABASE_URL)
        
        user = self.DB_USER or self.POSTGRES_USER or "postgres"
        pwd = self.DB_PASSWORD or self.POSTGRES_PASSWORD or ""
        host = self.DB_HOST or self.POSTGRES_SERVER or "localhost"
        port = self.DB_PORT or self.POSTGRES_PORT or 5432
        db_name = self.DB_NAME or self.POSTGRES_DB or "pocketuni"
        
        if not pwd and self.ENVIRONMENT != "test":
            raise ValueError(
                "PostgreSQL password is not configured. Please set DB_PASSWORD in your .env file. "
                "SQLite fallback is strictly prohibited."
            )
        
        return URL.create(
            drivername="postgresql+psycopg",
            username=user,
            password=pwd,
            host=host,
            port=int(port),
            database=db_name,
        )

    def get_database_url(self) -> str:
        """
        Returns connection URL as string.
        """
        return self.get_database_url_object().render_as_string(hide_password=False)

    def get_safe_database_url(self) -> str:
        """
        Returns connection URL with password masked (***). Safe for logs and reports.
        """
        return self.get_database_url_object().render_as_string(hide_password=True)


settings = Settings()
