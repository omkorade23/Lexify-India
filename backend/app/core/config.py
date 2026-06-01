"""
Application configuration management using Pydantic BaseSettings.

Settings are loaded from environment variables and/or a .env file.
Phase 2 (RAG Pipeline) settings are now fully activated.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings — loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Ignore extra keys so future agents can append to .env without breaking this
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application identity
    # ------------------------------------------------------------------
    API_TITLE: str = "Lexify-India API"
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")

    # ------------------------------------------------------------------
    # CORS — stored as str in env, parsed to list by validator below
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"

    # ------------------------------------------------------------------
    # File upload
    # ------------------------------------------------------------------
    UPLOAD_DIR: Path = Path("data/uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: str = ".pdf,.jpg,.jpeg,.png"  # parsed to set by validator

    # ------------------------------------------------------------------
    # OCR Agent (Phase 2) — ACTIVE
    # ------------------------------------------------------------------
    OCR_CONFIDENCE_THRESHOLD: float = 0.6  # Minimum acceptable OCR confidence score

    # ------------------------------------------------------------------
    # Vector Database (ChromaDB) — ACTIVE
    # ------------------------------------------------------------------
    DATABASE_PATH: str = "data/chroma_db"
    # Legacy single-collection name (kept for backwards compatibility)
    COLLECTION_NAME: str = "legal_documents"
    SIMILARITY_THRESHOLD: float = 0.7

    # Dual-collection names for RAG pipeline
    DOCUMENT_COLLECTION_NAME: str = "document_chunks"   # Per-document embeddings
    LEGAL_COLLECTION_NAME: str = "legal_knowledge"      # Pre-seeded legal knowledge

    # Similarity search thresholds
    DOCUMENT_SIMILARITY_THRESHOLD: float = 0.40
    LEGAL_SIMILARITY_THRESHOLD: float = 0.35
    DOCUMENT_TOP_K: int = 5
    LEGAL_TOP_K: int = 3

    # ------------------------------------------------------------------
    # Gemini AI — ACTIVE (Phase 2 RAG Pipeline)
    # ------------------------------------------------------------------
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_MAX_TOKENS: int = 1500

    # ------------------------------------------------------------------
    # Chunking — ACTIVE (Phase 2 RAG Pipeline)
    # ------------------------------------------------------------------
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # ------------------------------------------------------------------
    # Data paths
    # ------------------------------------------------------------------
    LEGAL_KNOWLEDGE_PATH: str = "data/legal_knowledge_base.json"
    DOCUMENT_REGISTRY_PATH: str = "data/document_registry.json"

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> str:
        """Accept list or str, store as comma-separated string."""
        if isinstance(value, (list, tuple)):
            return ",".join(str(v) for v in value)
        return str(value)

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, value: object) -> str:
        """Accept str or set, store as comma-separated string."""
        if isinstance(value, (set, list)):
            return ",".join(str(v) for v in value)
        return str(value)

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS_ORIGINS parsed as a list of URLs."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions_set(self) -> Set[str]:
        """ALLOWED_EXTENSIONS parsed as a set."""
        return {e.strip() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()}

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


# ---------------------------------------------------------------------------
# Module-level singleton — import this in application code.
# ---------------------------------------------------------------------------
settings = Settings()
