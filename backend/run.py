"""Local development entry point for the FastAPI application.

Run from the ``backend`` directory with ``python run.py``.
"""

import webbrowser

import uvicorn


if __name__ == "__main__":
    webbrowser.open_new_tab("http://127.0.0.1:8000/docs")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
