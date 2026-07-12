"""
utils/http_client.py
--------------------
Manages the shared httpx.AsyncClient instance.
"""

import httpx

_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create a shared httpx async client with connection pooling."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            timeout=5.0,
        )
    return _client


async def close_http_client():
    """Close the shared httpx client (call on app shutdown)."""
    global _client
    if _client:
        await _client.aclose()
        _client = None
