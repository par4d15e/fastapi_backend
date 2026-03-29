# PAWCARE

PAWCARE 是一个基于 FastAPI、SQLAlchemy、PostgreSQL 的宠物管理后端服务，支持身份认证、家庭共享、宠物档案、体重记录、提醒、食品管理与营养分析等功能。项目遵循分层架构，适合云原生部署与快速迭代。

当前版本新增了家庭模块与家庭邀请流程，并让宠物档案、食品、体重记录和提醒支持“个人 + 家庭”共享访问；同时补充了营养偏好接口，便于保存最近一次的配餐选择。

---

## 目录结构

```
app/
├─ core/                 # 全局基础设施
│  ├── __init__.py
│  ├── base_model.py      # DateTimeMixin / 数据库命名规范
│  ├── config.py         # Settings（pydantic-settings）
│  ├── database.py       # Database / db / get_session
│  ├── exception.py      # 统一业务异常与全局异常处理
│  ├── lifespan.py       # FastAPI lifespan
│  └── security.py       # 密码哈希 / JWT
├─ auth/                 # 认证与用户管理
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── router.py
│  ├── dependencies.py
│  └── user_manager.py
├─ families/             # 家庭共享、成员与邀请
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── repository.py
│  ├── service.py
│  └── router.py
├─ profiles/             # 宠物档案
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── repository.py
│  ├── service.py
│  └── router.py
├─ weights/              # 体重记录
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── repository.py
│  ├── service.py
│  └── router.py
├─ reminders/            # 事件提醒
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── repository.py
│  ├── service.py
│  └── router.py
├─ foods/                # 食品管理
│  ├── __init__.py
│  ├── model.py
│  ├── schema.py
│  ├── repository.py
│  ├── service.py
│  └── router.py
├─ nutrition/            # 营养分析
│  ├── __init__.py
│  ├── model.py
│  ├── repository.py
│  ├── router.py
│  ├── schema.py
│  └── service.py
└─ main.py               # FastAPI 应用入口 + 路由挂载

tests/                   # 测试
alembic/                 # 数据库迁移脚本
``` 

---

## 环境要求

- Python `>=3.14`（与 `pyproject.toml` 保持一致）

## 关键环境变量（开发/测试 `.env`，生产请通过 CI/CD secrets）

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `JWT_SECRET`
- `JWT_ALGORITHM`（默认 `HS256`）
- `ACCESS_TOKEN_EXPIRE_MINUTES`（默认 `60`）
- `DEBUG`（生产 `false`）

可选（启用 Redis 相关能力时配置）：

- `REDIS_HOST`
- `REDIS_PORT`
- `AUTH_REDIS_DB`
- `CACHE_REDIS_DB`

> 安全提示：`JWT_SECRET` 不得使用默认值 `example_jwt_secret`，建议长度不低于 32 字符。

---

## 功能概览

- `auth`：用户注册、登录、找回密码与认证令牌管理
- `families`：家庭创建、成员管理、邀请生成与邀请接受
- `profiles`：宠物档案管理，支持归属个人或家庭
- `foods`：食品管理，支持归属个人或家庭
- `weights`：体重记录管理，支持归属个人或家庭
- `reminders`：提醒管理，支持归属个人或家庭
- `nutrition`：营养方案计算、每日目标热量计算、营养偏好保存

---

## 核心 API

所有业务路由均挂载在 `app.main:app` 上，主要前缀如下：

- `/auth`：认证相关接口
- `/families`：家庭、成员、邀请接口
- `/profiles`：宠物档案接口
- `/foods`：食品接口
- `/weights`：体重记录接口
- `/reminders`：提醒接口
- `/nutrition`：营养分析与营养偏好接口

其中营养模块提供以下接口：

- `POST /nutrition/plans`：根据宠物、体重和候选食品生成每日喂食方案
- `POST /nutrition/daily-kcals`：只计算每日目标热量
- `GET /nutrition/preferences/{profile_id}`：获取宠物的营养偏好
- `PUT /nutrition/preferences/{profile_id}`：保存或更新宠物的营养偏好

家庭模块提供以下接口：

- `POST /families`：创建家庭
- `POST /families/{family_id}/members`：添加家庭成员
- `DELETE /families/{family_id}/members/{user_id}`：移除家庭成员
- `POST /families/{family_id}/invites`：创建家庭邀请
- `POST /families/invites/accept`：接受家庭邀请

宠物档案、食品、体重记录和提醒接口都支持家庭成员共享访问：家庭成员可以读取家庭范围内的数据，家庭拥有者可以继续管理这些资源。

---

## 快速启动（本地开发）

推荐使用 `uv` 作为包和虚拟环境管理工具：

1. 安装 `uv`（如果尚未安装）

```bash
python -m pip install -U uv
```

2. 同步项目依赖（包含开发依赖）

```bash
uv sync --extra dev
```

3. 准备环境变量文件

```bash
cp .env.example .env
```

4. 初始化数据库（仅开发环境）

```bash
uv run alembic upgrade head
```

5. 启动服务

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. 打开 Swagger

`http://127.0.0.1:8000/docs`

如果你仍希望使用传统 venv，可执行：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

---

## Docker 部署示例

`Dockerfile` 中建议注入运行时环境：

```dockerfile
ENV DB_HOST=your_db_host
ENV DB_PORT=5432
ENV DB_USER=your_db_user
ENV DB_PASSWORD=your_db_password
ENV DB_NAME=your_db_name
ENV JWT_SECRET=your_very_strong_secret
ENV DEBUG=false
```

`docker-compose.yml`/`pyproject.toml` 同样应使用以上变量。

---

## 运行测试

```bash
pytest -q
```

---

## 开发规范（重点）

- 资源型模块（如 `profiles`、`weights`、`foods`、`reminders`）遵循 `model.py/schema.py/repository.py/service.py/router.py` 分层。
- 特殊模块可按职责裁剪结构（如 `auth`、`nutrition`、`families`），但仍需保持“router -> service -> repository（或等价数据访问层）”的职责边界。
- 数据库 CRUD 仅由 repository 负责，service 处理业务异常。
- Router 依赖注入 `get_session` + service，接口返回 `response_model`。
- 使用 `app/core/exception.py` 中异常映射 HTTP 状态码（`NotFoundException`/`AlreadyExistsException` 等）。
- 共享资源需要同时考虑个人归属和家庭归属，相关 repository/service 应保持权限判断一致。

---

## 常见问题

- 生产 `DEBUG` 必须为 `false`。
- `JWT_SECRET` 生产环境强制校验，不可省略。
- 迁移后若表结构不一，先备份再重新初始化。

---

## 贡献

欢迎提交 issue/PR，分支命名建议 `feature/xxx`/`fix/xxx`，提交信息遵循项目规范（如 `✨ 新增 ...`、`🐛 修复 ...`）。
