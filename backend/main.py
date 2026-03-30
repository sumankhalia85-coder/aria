from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pain Point Mapper API",
    description="Customer Pain Point Collection Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Pain Point Mapper v2"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        from core.database import init_db
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}", exc_info=True)

# Load and register API routes
try:
    logger.info("Loading API routes...")
    from api.routes import router
    app.include_router(router, prefix="/api/v1")
    logger.info("API routes loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load API routes: {str(e)}", exc_info=True)
    raise

logger.info("Application initialized and ready")
