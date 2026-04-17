"""
Request proxying logic
"""

from fastapi import Request, Response
import httpx


HOP_BY_HOP_HEADERS = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

RESPONSE_FILTER_HEADERS = {
    "content-encoding",
    "transfer-encoding",
    "connection",
}


async def proxy_request(
    client: httpx.AsyncClient,
    target_base_url: str,
    request: Request,
    path: str,
    strip_prefix: str | None = None,
) -> Response:
    """
    Proxy an incoming request to a backend service.
    """
    # Build target path
    target_path = "/" + path
    if strip_prefix:
        prefix = strip_prefix.rstrip("/")
        if target_path.startswith(prefix):
            target_path = target_path[len(prefix):]
            if not target_path:
                target_path = "/"

    target_url = f"{target_base_url.rstrip('/')}{target_path}"
    query = str(request.query_params)
    if query:
        target_url += "?" + query

    # Prepare headers
    headers = {}
    for k, v in request.headers.items():
        if k.lower() not in HOP_BY_HOP_HEADERS:
            headers[k] = v

    # Read body
    body = await request.body()

    # Forward request
    resp = await client.request(
        method=request.method,
        url=target_url,
        headers=headers,
        content=body,
        follow_redirects=False,
    )

    # Prepare response headers
    response_headers = {}
    for k, v in resp.headers.items():
        if k.lower() not in RESPONSE_FILTER_HEADERS:
            response_headers[k] = v

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers,
    )
