import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
# Example: mysql+pymysql://www_user:password@127.0.0.1:3306/www_financial?charset=utf8mb4
DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "3"))
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT.mkdir(exist_ok=True)

BANKINGS_KEY = os.getenv("BANKINGS_KEY", "")
CURRENCIES_KEY = os.getenv("CURRENCIES_KEY", "")
STOCKS_KEY = os.getenv("STOCKS_KEY", "")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
CHATS_KEY = os.getenv("CHATS_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Comma-separated origins make local and deployed frontend addresses explicit
# without widening credentialed CORS requests to every origin.
CORS_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
)
