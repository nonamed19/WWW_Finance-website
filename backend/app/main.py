"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .accounts import router as accounts_router
from .bankings import router as bankings_router
from .chats import router as chats_router
from .currencies import router as currencies_router
from .database import Base, engine
from .economics import router as economics_router
from .markets import router as markets_router
from .recommendations import router as recommendations_router
from .stocks import router as stocks_router
from .subscriptions import router as subscriptions_router
from .surveys import router as surveys_router


app = FastAPI(title="Financial Recommendation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    # `create_all` does not add indexes to tables created by an older version of
    # the application.  Create the declared indexes idempotently on startup.
    for table in Base.metadata.tables.values():
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)


@app.get("/health/", tags=["health"])
def health():
    return {"status": "ok"}
