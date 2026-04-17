"""
Dynamic proxy routes based on Consul service discovery
"""

from fastapi import APIRouter, Request, HTTPException, status

from ..config import get_config
from ..consul import ConsulClient
from ..client import get_http_client
from ..proxy import proxy_request


router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def catch_all_proxy(
    path: str,
    request: Request,
):
    """
    Catch-all proxy endpoint.
    Matches path prefix against configured routes, discovers backend via Consul,
    and forwards the request.
    """
    config = get_config()
    full_path = "/" + path

    # Match route
    matched_route = None
    for route in config.routes:
        prefix = route.prefix.rstrip("/")
        if full_path.startswith(prefix) or full_path == prefix:
            matched_route = route
            break

    if not matched_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到匹配的路由: {full_path}",
        )

    # Discover backend via Consul
    consul: ConsulClient = request.app.state.consul
    target_url = await consul.discover(matched_route.service)

    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"无可用的后端服务实例: {matched_route.service}",
        )

    # Forward request
    client = get_http_client()
    return await proxy_request(
        client=client,
        target_base_url=target_url,
        request=request,
        path=path,
        strip_prefix=matched_route.prefix if matched_route.strip_prefix else None,
    )
