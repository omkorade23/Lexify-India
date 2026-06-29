"""
Lexify-India FastAPI application entry point.

Responsibilities:
  - Instantiate the FastAPI application with metadata.
  - Register CORS middleware (permissive for development).
  - Mount API routers (documents, chat).
  - Register the global exception handler for LexifyException subclasses.
  - Expose the /health liveness endpoint.
  - Configure structured JSON logging.
  - Provide startup / shutdown lifecycle hooks for future service init.
"""

from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat, documents, legal_chat
from app.core.config import settings
from app.core.exceptions import LexifyException

# ---------------------------------------------------------------------------
# Logging — JSON-structured, INFO level
# ---------------------------------------------------------------------------

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": (
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """
    Manage application lifecycle events.

    Startup:
        - Ensure required directories exist (UPLOAD_DIR, etc.).
        - TODO (OCR Agent): Initialise PaddleOCR model on startup.
        - TODO (Vector DB Agent): Connect to / create ChromaDB collection.
        - TODO (RAG Agent): Load embedding model into memory.

    Shutdown:
        - TODO: Flush pending tasks, close connections, release GPU memory.
    """
    # --- Startup ---
    logger.info(
        "Starting %s v%s [env=%s]",
        settings.API_TITLE,
        settings.API_VERSION,
        settings.ENVIRONMENT,
    )

    # Ensure upload directory exists so the OCR Agent can write files immediately.
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Upload directory ready: %s", settings.UPLOAD_DIR)

    # TODO (OCR Agent): warm up OCR model here.
    # TODO (Vector DB Agent): connect to ChromaDB here.
    # TODO (RAG Agent): load embedding model here.

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Shutting down %s", settings.API_TITLE)
    # TODO: release resources (GPU memory, DB connections, thread pools).


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "**Lexify-India** — AI-powered legal document understanding platform.\n\n"
        "Upload scanned or digital legal documents (contracts, court orders, "
        "affidavits) and ask natural language questions. The platform uses "
        "OCR extraction, semantic chunking, vector search, and Gemini LLM to "
        "deliver grounded, citation-backed answers.\n\n"
        "### Phase 1 (current)\n"
        "- API scaffold with stub endpoints\n"
        "- Pydantic models aligned to PRD specifications\n\n"
        "### Phase 2 (in progress)\n"
        "- OCR extraction via PaddleOCR\n"
        "- Vector indexing via ChromaDB\n"
        "- RAG pipeline via Gemini + LangChain\n"
    ),
    contact={
        "name": "Lexify-India Team",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    # Docs available in development only; disable in production if desired.
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------


@app.exception_handler(LexifyException)
async def lexify_exception_handler(
    request: Request,  # noqa: ARG001
    exc: LexifyException,
) -> JSONResponse:
    """
    Convert any LexifyException subclass into a structured JSON error response.

    Response shape:
        {
            "error": {
                "code": "document_not_found",
                "message": "No document with id '...' exists.",
                "details": "document_id=abc123"   // optional
            }
        }
    """
    # Map known exception types to HTTP status codes.
    from app.core.exceptions import (
        DocumentNotFoundException,
        FileSizeExceededException,
        InvalidFileTypeException,
        OCRExtractionFailedException,
        RAGPipelineException,
        RateLimitExceededException,
        VectorStoreException,
    )

    status_map: dict[type[LexifyException], int] = {
        DocumentNotFoundException: status.HTTP_404_NOT_FOUND,
        InvalidFileTypeException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        FileSizeExceededException: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        OCRExtractionFailedException: status.HTTP_500_INTERNAL_SERVER_ERROR,
        RAGPipelineException: status.HTTP_500_INTERNAL_SERVER_ERROR,
        RateLimitExceededException: status.HTTP_429_TOO_MANY_REQUESTS,
        VectorStoreException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    http_status = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.warning(
        "LexifyException [%s] %s — details: %s",
        exc.code,
        exc.message,
        exc.details,
    )

    error_body: dict = {"code": exc.code, "message": exc.message}
    if exc.details:
        error_body["details"] = exc.details

    return JSONResponse(
        status_code=http_status,
        content={"error": error_body},
    )


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------


@app.get(
    "/health",
    tags=["Health"],
    summary="API liveness check",
    description="Returns `{\"status\": \"healthy\"}` when the service is running.",
)
async def health_check() -> dict[str, str]:
    """Liveness probe used by load balancers and orchestration platforms."""
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# API routers
# ---------------------------------------------------------------------------

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(legal_chat.router)

logger.info("Registered routers: /api/documents, /api/chat, /api/legal-chat")
