# fast-task-gateway

Fast Task API Gateway — 基于 FastAPI + httpx + Consul 的轻量聚合网关。

## 特性

- **Consul 服务自发现**：自动从 Consul 查询健康后端实例
- **动态路由转发**：按路径前缀匹配并转发到对应微服务
- **自动注册/注销**：启动时向 Consul 注册，关闭时优雅注销
- **无侵入鉴权**：鉴权完全交给后端微服务自身控制，网关只做透明转发
- **高性能转发**：基于 `httpx` + HTTP/2 + 连接池

## 启动

```bash
uv sync
python -m fast_task_gateway.main
```

## 配置

编辑 `config.yaml`：

```yaml
gateway:
  name: fast-task-gateway
  service_id: fast-task-gateway-1
  host: 0.0.0.0
  port: 8080

consul:
  host: localhost
  port: 8500

routes:
  - prefix: /api/server
    service: fast-task-server
    strip_prefix: true
```

## Docker

```bash
docker build -t fast-task-gateway .
docker run -p 8080:8080 fast-task-gateway
```
