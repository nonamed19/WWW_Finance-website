"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app import config
from app.accounts import router as accounts_router
from app.bankings import router as bankings_router
from app.chats import router as chats_router
from app.currencies import router as currencies_router
from app.database import database_is_available, dispose_database, initialize_database
from app.economics import router as economics_router
from app.markets import router as markets_router
from app.recommendations import router as recommendations_router
from app.stocks import router as stocks_router
from app.subscriptions import router as subscriptions_router
from app.surveys import router as surveys_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the database without making it a server startup requirement."""
    try:
        initialize_database()
    except OperationalError as error:
        # The API remains available while MySQL is stopped. DB-backed routes
        # return 503 through the get_db dependency.
        logger.warning("MySQL is unavailable; starting without it: %s", error)

    try:
        yield
    finally:
        dispose_database()


app = FastAPI(
    title="Financial Recommendation API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=config.MEDIA_ROOT), name="media")

for router in (
    accounts_router,
    bankings_router,
    currencies_router,
    stocks_router,
    economics_router,
    markets_router,
    surveys_router,
    recommendations_router,
    subscriptions_router,
    chats_router,
):
    app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Send the default server URL to the interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health/", tags=["health"])
def health():
    return {
        "status": "ok",
        "database": "available" if database_is_available() else "unavailable",
    }
