"""
Application lifespan events: Consul registration / deregistration
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fast_task_base.service import ConsulService

from .config import get_config
from .client import close_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan: register to Consul on startup, deregister on shutdown.
    """
    config = get_config()
    consul = ConsulService(
        host=config.consul.host,
        port=config.consul.port,
        scheme=config.consul.scheme,
    )
    app.state.consul = consul

    health_url = f"http://{config.gateway.host}:{config.gateway.port}{config.gateway.health_path}"
    await consul.register(
        service_id=config.gateway.service_id,
        name=config.gateway.name,
        host=config.gateway.host,
        port=config.gateway.port,
        health_url=health_url,
    )

    yield

    await consul.deregister(config.gateway.service_id)
    await consul.close()
    await close_http_client()
