from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.routes import auth, game, user
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Balance Game API",
        description="API for the Balance Game educational application",
        version="1.0.0"
    )

    # Security middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update with specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Update in production

    # Add rate limiting
    app.state.limiter = limiter

    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(game.router, prefix="/game", tags=["Game"])
    app.include_router(user.router, prefix="/user", tags=["Users"])

    @app.on_event("startup")
    async def startup_event():
        try:
            from app.database import db
            # Create default game configuration if it doesn't exist
            config_ref = db.collection('GameConfigurations').document('default')
            if not config_ref.get().exists:
                from app.config import default_game_config
                config_ref.set(default_game_config)
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app