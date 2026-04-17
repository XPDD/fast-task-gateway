"""
Shared HTTP client for backend requests
"""

import httpx

_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create shared httpx AsyncClient"""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            http2=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=httpx.Timeout(30.0, connect=5.0),
        )
    return _http_client


async def close_http_client() -> None:
    """Close shared HTTP client"""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None
