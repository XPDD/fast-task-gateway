"""
Gateway configuration
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List

import yaml


@dataclass
class ConsulConfig:
    host: str = "localhost"
    port: int = 8500
    scheme: str = "http"


@dataclass
class GatewayConfig:
    name: str = "fast-task-gateway"
    service_id: str = "fast-task-gateway-1"
    host: str = "0.0.0.0"
    port: int = 8080
    health_path: str = "/health"


@dataclass
class RouteConfig:
    prefix: str
    service: str
    strip_prefix: bool = True


@dataclass
class Config:
    gateway: GatewayConfig = field(default_factory=GatewayConfig)
    consul: ConsulConfig = field(default_factory=ConsulConfig)
    routes: List[RouteConfig] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "Config":
        p = Path(path)
        if not p.exists():
            return cls()

        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        gw_data = data.get("gateway", {})
        gateway = GatewayConfig(
            name=gw_data.get("name", "fast-task-gateway"),
            service_id=gw_data.get("service_id", "fast-task-gateway-1"),
            host=gw_data.get("host", "0.0.0.0"),
            port=gw_data.get("port", 8080),
            health_path=gw_data.get("health_path", "/health"),
        )

        cs_data = data.get("consul", {})
        consul = ConsulConfig(
            host=cs_data.get("host", "localhost"),
            port=cs_data.get("port", 8500),
            scheme=cs_data.get("scheme", "http"),
        )

        routes = []
        for r in data.get("routes", []):
            routes.append(RouteConfig(
                prefix=r.get("prefix", ""),
                service=r.get("service", ""),
                strip_prefix=r.get("strip_prefix", True),
            ))

        return cls(gateway=gateway, consul=consul, routes=routes)


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_yaml()
    return _config
