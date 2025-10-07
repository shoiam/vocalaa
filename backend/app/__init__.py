from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_allowed_origins
from app.core.logging import setup_logging
from app.api.routes import auth, profile, account, mcp

setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Vocalaa API",
        description="Interactive professional information server",
        version="0.1.0"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods including OPTIONS
        allow_headers=["*"],  # Allow all headers including Authorization
    )

    @app.get("/health")
    async def health():
        """Detailed health check."""
        from loguru import logger
        logger.info("Health check requested")
        return {
            "status": "healthy",
            "service": "Vocalaa API"
        }

    app.include_router(auth.router)
    app.include_router(profile.router)
    app.include_router(account.router)
    app.include_router(mcp.router)

    return app

app = create_app()