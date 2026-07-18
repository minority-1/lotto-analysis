"""FastAPI application assembly and public error handling."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from lotto_analysis.api.routers.analysis import router as analysis_router
from lotto_analysis.api.routers.advanced_analysis import router as advanced_router
from lotto_analysis.api.routers.draws import router as draws_router
from lotto_analysis.api.routers.health import router as health_router
from lotto_analysis.api.routers.generation import router as generation_router
from lotto_analysis.api.routers.backtests import router as backtests_router


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build the API app without embedding domain calculations."""
    application = FastAPI(
        title="Lotto Analysis API",
        version="0.1.0",
        description="Prediction-neutral Korean Lotto 6/45 data and analysis API.",
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
