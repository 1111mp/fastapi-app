# FastAPI App

一个生产可用的 FastAPI 后端模板，内置认证、数据库、缓存、异步任务与可观测性能力。

## 功能特性

- 基于 `fastapi-users` 的完整认证体系（JWT / 注册 / 找回密码 / 邮箱验证）
- GitHub OAuth 登录
- 用户资料接口（`/users/me`）
- Post 示例业务接口（鉴权后可访问）
- PostgreSQL + SQLAlchemy（异步）
- Redis 缓存/连接管理
- Alembic 数据库迁移
- Taskiq 异步任务（worker + scheduler）
- APScheduler 应用内定时任务
- Prometheus 指标 + 健康检查（`/healthz` / `/readyz`）
- OpenTelemetry 链路追踪（可选）
- Correlation ID 与结构化日志

---

## 技术栈

- Python 3.14+
- FastAPI
- SQLAlchemy + Psycopg
- PostgreSQL
- Redis
- FastAPI Users
- Alembic
- Taskiq / taskiq-redis / taskiq-fastapi
- APScheduler
- Prometheus FastAPI Instrumentator
- OpenTelemetry
- Structlog
- uv

---

## 项目结构

```text
app/
├── api/               # 路由与 API 入口
├── auth/              # 认证相关（backend / manager / deps）
├── core/              # 配置、日志、数据库、Redis、可观测性
├── db/                # 数据访问层（CRUD）
├── models/            # ORM 模型
├── schemas/           # Pydantic 模型
├── scheduler/         # APScheduler 任务定义与生命周期
└── workers/           # Taskiq broker、任务与调度器
tests/
├── integration/       # 集成测试
└── unit/              # 单元测试
alembic/               # 数据库迁移
```

---

## 快速开始（本地开发）

### 1) 安装依赖

```bash
uv sync
```

### 2) 配置环境变量

配置通过 `pydantic-settings` 加载，支持以下文件（后者覆盖前者）：

1. `.env`
2. `.env.local`
3. `.env.prod`

最小示例：

```env
PROJECT_NAME=fastapi-app
ENVIRONMENT=local
PORT=8000
FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SECRET_KEY=change-me
LOGGER_LEVEL=INFO

POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redispass
# 或直接使用 REDIS_URL 覆盖上面四项
# REDIS_URL=redis://:redispass@127.0.0.1:6379/0

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

SLOW_QUERY_THRESHOLD_MS=1000
METRICS_ENABLED=true

OTEL_ENABLED=false
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_INSECURE=true

FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=password
```

### 3) 启动基础依赖

```bash
docker compose up -d db redis
```

### 4) 执行迁移

```bash
uv run alembic upgrade head
```

### 5) 启动 API

```bash
uv run fastapi run app/main.py --reload --port 8000
```

访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`

---

## Docker Compose 启动（完整栈）

一键启动 API + PostgreSQL + Redis + Taskiq Worker + Taskiq Scheduler：

```bash
docker compose up --build
```

默认端口：

- API: `http://127.0.0.1:80`
- PostgreSQL: `127.0.0.1:5432`
- Redis: `127.0.0.1:6379`

---

## 常用命令

### 数据库迁移

```bash
# 生成迁移
uv run alembic revision --autogenerate -m "your message"

# 应用迁移
uv run alembic upgrade head

# 回滚一步
uv run alembic downgrade -1
```

### 运行单元测试

```bash
# 首次安装（包含 dev 依赖）
uv sync --group dev

# 执行全部测试（默认附带 coverage）
uv run pytest

# 生成覆盖率报告（终端 + coverage.xml）
uv run pytest --cov=app --cov-report=term-missing --cov-report=xml
```

### 集成测试数据回滚（避免脏数据）

项目提供了 `tests/integration/conftest.py` 的 `db_transaction` 夹具：

- 每个测试独立创建 `AsyncSession`。
- 覆盖 `get_async_session`，确保接口走测试会话。
- 测试期间把 `session.commit()` 临时替换为 `session.flush()`，结束后统一 `rollback()`。
- 默认 `uv run pytest` 不执行集成测试（只跑 `not integration`）。

```bash
# 显式执行集成测试
uv run pytest -m integration
```

`integration` 标记用法示例（如 `tests/integration/api/post_test.py`）：

```python
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]
```

运行方式：

- 只跑集成测试：`uv run pytest -m integration`
- 排除集成测试：`uv run pytest -m "not integration"`
- 跑某个集成测试文件：`uv run pytest tests/integration/api/post_test.py -m integration`

### 启动 Taskiq Worker / Scheduler（本地）

```bash
# Worker
uv run taskiq worker app.workers.provider:broker

# Scheduler
uv run taskiq scheduler app.workers.scheduler:scheduler --fs-discover --tasks-pattern "app/**/tasks.py"
```

---

## API 概览

默认前缀：`/api/v1`

### 认证与用户

- `POST /auth/jwt/login`
- `POST /auth/jwt/logout`
- `POST /auth/register`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /auth/verify`
- `POST /auth/request-verify-token`
- `GET /auth/github/authorize`
- `GET /auth/github/callback`
- `GET /users/me`
- `PATCH /users/me`

### Posts

- `POST /posts/`（需登录）
- `GET /posts/{id}`（需登录）

### 运维接口

- `GET /healthz`（存活检查）
- `GET /readyz`（就绪检查，含 DB/Redis）
- `GET /metrics`（Prometheus 指标，`METRICS_ENABLED=true` 时启用）


---

## CORS 配置说明

`BACKEND_CORS_ORIGINS` 支持两种格式：

- 逗号分隔字符串：`http://a.com,http://b.com`
- JSON 数组：`["http://a.com", "http://b.com"]`

系统会自动把 `FRONTEND_HOST` 追加到允许列表中。

---

## 定时任务说明

本项目有两类定时能力：

1. **应用内 APScheduler**（`app/scheduler`）
2. **Taskiq Scheduler**（`app/workers/tasks.py` 中使用 `schedule=[{"cron": "* * * * *"}]`）

如果你只需要一种调度方式，建议在实际项目中保留一种以降低复杂度。

---

## 可观测性与稳定性

本项目已提供基础可观测能力：

- `/healthz` + `/readyz`：容器探针与依赖可用性检查
- `/metrics`：Prometheus 文本格式指标
  - 由 `prometheus-fastapi-instrumentator` 自动采集 HTTP 指标
- OpenTelemetry tracing（可选开启）
  - `OTEL_ENABLED=true` 后自动启用 FastAPI / SQLAlchemy / Redis tracing
  - 设置 `OTEL_EXPORTER_OTLP_ENDPOINT` 可上报到 OTLP Collector
  - gRPC 本地示例：`OTEL_EXPORTER_OTLP_ENDPOINT=localhost:4319` + `OTEL_EXPORTER_OTLP_INSECURE=true`

---

## 生产环境建议

- 使用强随机 `SECRET_KEY`
- 为 PostgreSQL 与 Redis 设置强密码
- 将 `ENVIRONMENT` 设为 `production`
- 正确配置 `BACKEND_CORS_ORIGINS`
- 通过反向代理（Nginx / Traefik）暴露 API
- 配置日志采集与告警

---

## License

[MIT](./LICENSE)
