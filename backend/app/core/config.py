"""
config.py
---------
Centralized environment configuration.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application Settings loaded from environment."""

    # App Info
    PROJECT_NAME: str = "PharmaSafe-KG API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # PostgreSQL / Relational DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT Secrets
    JWT_SECRET: str = os.getenv("JWT_SECRET", "pharmasafe-kg-secure-academic-jwt-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    COOKIE_NAME: str = "pharmasafe_refresh_token"

    # Neo4j Graph Database
    NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+s://dd205fee.databases.neo4j.io")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "dd205fee")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # CORS
    @property
    def CORS_ORIGINS(self) -> List[str]:
        cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:8501")
        origins = [o.strip() for o in cors_env.split(",") if o.strip()]
        if not origins:
            return ["*"]
        return origins


settings = Settings()
