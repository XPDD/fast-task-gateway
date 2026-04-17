"""
Gateway unified authentication
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from fast_task_base.api.auth import verify_token
from fast_task_base.api.dependencies import NOAUTH_MARK


security = HTTPBearer(auto_error=False)


async def gateway_auth(request: Request) -> dict:
    """
    Gateway-level unified JWT authentication.
    Validates token and attaches user payload to request.state.user.
    """
    endpoint = request.scope.get("endpoint")
    if endpoint and hasattr(endpoint, NOAUTH_MARK):
        return None

    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
        )

    token = authorization[7:]
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
        )

    request.state.user = payload
    return payload


async def optional_auth(request: Request) -> dict | None:
    """Optional authentication - returns payload if valid, None otherwise"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]
    payload = verify_token(token, "access")
    if payload:
        request.state.user = payload
    return payload
