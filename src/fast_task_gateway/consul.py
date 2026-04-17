"""
Consul service discovery and registration
"""

import random
from typing import Optional, List

import httpx

from .config import ConsulConfig


class ConsulClient:
    """Consul HTTP API client for discovery and self-registration"""

    def __init__(self, config: ConsulConfig):
        self.config = config
        self.base_url = f"{config.scheme}://{config.host}:{config.port}"
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=5.0)

    async def discover(self, service_name: str) -> Optional[str]:
        """
        Discover a healthy service instance.
        Returns a base URL like http://host:port or None if no healthy instance.
        """
        try:
            resp = await self._client.get(f"/v1/health/service/{service_name}")
            resp.raise_for_status()
            services = resp.json()

            healthy: List[str] = []
            for svc in services:
                checks = svc.get("Checks", [])
                if all(c.get("Status") == "passing" for c in checks):
                    service = svc["Service"]
                    addr = service.get("Address") or svc["Node"]["Address"]
                    port = service["Port"]
                    healthy.append(f"http://{addr}:{port}")

            return random.choice(healthy) if healthy else None
        except Exception:
            return None

    async def register(
        self,
        service_id: str,
        name: str,
        host: str,
        port: int,
        health_url: str,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Register gateway service to Consul"""
        payload = {
            "ID": service_id,
            "Name": name,
            "Tags": tags or ["gateway", "fastapi"],
            "Address": host,
            "Port": port,
            "Check": {
                "HTTP": health_url,
                "Interval": "10s",
                "Timeout": "5s",
                "DeregisterCriticalServiceAfter": "30s",
            },
        }
        resp = await self._client.put("/v1/agent/service/register", json=payload)
        resp.raise_for_status()

    async def deregister(self, service_id: str) -> None:
        """Deregister service from Consul"""
        try:
            resp = await self._client.put(f"/v1/agent/service/deregister/{service_id}")
            resp.raise_for_status()
        except Exception:
            pass

    async def close(self) -> None:
        await self._client.aclose()
