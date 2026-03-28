# PAWCARE

PAWCARE 是一个基于 FastAPI、SQLAlchemy、PostgreSQL 的宠物管理后端服务，支持身份认证、档案管理、体重、提醒、食品与营养等功能。项目遵循分层架构，适合云原生部署与快速迭代。

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
│  ├── router.py
│  ├── schema.py
│  └── service.py
└─ main.py               # FastAPI 应用入口 + 路由挂载

tests/                   # 测试
alembic/                 # 数据库迁移脚本
``` 

---

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

> 安全提示：`JWT_SECRET` 不得使用默认值 `example_jwt_secret`，建议长度不低于 32 字符。

---

## 快速启动（本地开发）

推荐使用 `uv` 作为包和虚拟环境管理工具：

```bash
# 安装 uv（如果尚未安装）
python -m pip install -U uv

# 使用 uv 创建环境并安装依赖
uv install

# 等同于 uv 环境激活 + 应用启动
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果你仍希望使用传统 venv：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

2. 准备 `.env`（参考 `.env.example`）

3. 初始化数据库 (仅开发环境)

```bash
alembic upgrade head
```

5. 打开浏览器访问 Swagger

`http://127.0.0.1:8000/docs`

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

- 每个模块保留 `model.py/schema.py/repository.py/service.py/router.py`。
- 数据库 CRUD 仅由 repository 负责，service 处理业务异常。
- Router 依赖注入 `get_session` + service，接口返回 `response_model`。
- 使用 `app/core/exception.py` 中异常映射 HTTP 状态码（`NotFoundException`/`AlreadyExistsException` 等）。

---

## 常见问题

- 生产 `DEBUG` 必须为 `false`。
- `JWT_SECRET` 生产环境强制校验，不可省略。
- 迁移后若表结构不一，先备份再重新初始化。

---

## 贡献

欢迎提交 issue/PR，分支命名建议 `feature/xxx`/`fix/xxx`，提交信息遵循项目规范（如 `✨ 新增 ...`、`🐛 修复 ...`）。

