"""
Fast Task Gateway - Entry point
"""

import uvicorn
from fastapi import FastAPI

from .lifecycle import lifespan
from .routes import router
from .config import get_config


def create_app() -> FastAPI:
    app = FastAPI(
        title="Fast Task Gateway",
        description="API Gateway with Consul service discovery and unified auth",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": get_config().gateway.name}


def main():
    config = get_config()
    uvicorn.run(
        "fast_task_gateway.main:app",
        host=config.gateway.host,
        port=config.gateway.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
