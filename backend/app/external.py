"""Reusable, resilient HTTP client for upstream data providers."""
from typing import Any

import requests
from fastapi import HTTPException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_TIMEOUT = (5, 20)  # connect, read (seconds)

_session = requests.Session()
_retry_adapter = HTTPAdapter(
    max_retries=Retry(
        total=2,
        backoff_factor=0.25,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
)
_session.mount("https://", _retry_adapter)
_session.mount("http://", _retry_adapter)


def get_json(url: str, **kwargs: Any) -> Any:
    """Fetch JSON with pooled connections and turn upstream failures into 502."""
    try:
        response = _session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise HTTPException(502, "Upstream data provider is unavailable.") from error
    except ValueError as error:
        raise HTTPException(502, "Upstream data provider returned invalid JSON.") from error


def get_content(url: str, **kwargs: Any) -> bytes:
    """Fetch a non-JSON upstream response with the same connection policy."""
    try:
        response = _session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.content
    except requests.RequestException as error:
        raise HTTPException(502, "Upstream data provider is unavailable.") from error
