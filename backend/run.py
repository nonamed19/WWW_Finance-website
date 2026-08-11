"""Local development entry point for the FastAPI application.

Run from the ``backend`` directory with ``python run.py``.
"""

import uvicorn


HOST = "127.0.0.1"
PORT = 8000
DOCS_URL = f"http://{HOST}:{PORT}/docs"


def main() -> None:
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
