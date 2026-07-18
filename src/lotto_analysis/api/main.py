"""FastAPI application assembly and public error handling."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator, Optional, Sequence

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from lotto_analysis.api.routers.analysis import router as analysis_router
from lotto_analysis.api.routers.advanced_analysis import router as advanced_router
from lotto_analysis.api.routers.draws import router as draws_router
from lotto_analysis.api.routers.health import router as health_router
from lotto_analysis.api.routers.generation import router as generation_router
from lotto_analysis.api.routers.backtests import router as backtests_router
from lotto_analysis.api.dependencies import dispose_engine, get_settings


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Release the shared SQLAlchemy pool when the API process stops."""
    try:
        yield
    finally:
        dispose_engine()


def create_app(cors_origins: Optional[Sequence[str]] = None) -> FastAPI:
    """Build the API app without embedding domain calculations."""
    application = FastAPI(
        title="Lotto Analysis API",
        version="0.1.0",
        description="Prediction-neutral Korean Lotto 6/45 data and analysis API.",
        lifespan=lifespan,
    )
    origins = (
        tuple(cors_origins)
        if cors_origins is not None
        else get_settings().cors_origins
    )
    if origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type"],
        )
    application.include_router(health_router, prefix="/api")
    application.include_router(draws_router, prefix="/api")
    application.include_router(analysis_router, prefix="/api")
    application.include_router(advanced_router, prefix="/api")
    application.include_router(generation_router, prefix="/api")
    application.include_router(backtests_router, prefix="/api")

    @application.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Map domain input failures to a stable client error."""
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Log database failures while hiding connection details from clients."""
        logger.exception("Database request failed", exc_info=exc)
        return JSONResponse(
            status_code=503, content={"detail": "database service unavailable"}
        )

    return application


app = create_app()
