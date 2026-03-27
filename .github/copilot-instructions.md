# GitHub Copilot Instructions


## 全局核心规则

1. **响应语言强制**：所有思考过程和回答、代码注释、文档字符串、字段描述必须使用**简体中文**；代码标识符（变量、函数、类名、表名）保持英文规范（蛇形/驼峰命名）。
2. **规范优先级**：本文件所有规则为最高优先级，生成代码时必须严格遵循后续技术栈、目录结构、分层架构等所有规范。


## 项目概述

**PAWCARE** 是一个基于 FastAPI + SQLModel + PostgreSQL + asyncio 构建的宠物管理后端服务。
项目采用严格的分层架构，所有新功能模块均须遵循以下规范。

---

## 技术栈

| 层次         | 技术                                            |
| ------------ | ----------------------------------------------- |
| Web 框架     | FastAPI (with standard extras)                  |
| ORM / Schema | SQLModel (SQLAlchemy 2.x asyncio + Pydantic v2) |
| 数据库驱动   | asyncpg (PostgreSQL)                            |
| 密码哈希     | pwdlib (推荐 argon2 或 bcrypt)                  |
| JWT          | python-jose                                     |
| 配置管理     | pydantic-settings (.env 文件)                   |
| 日志         | loguru                                          |
| 包管理       | uv + pyproject.toml                             |
| 测试         | pytest + pytest-asyncio + httpx                 |

---

## 目录结构规范

每个业务模块放在 `app/<module_name>/` 目录下，必须包含以下文件：

```
app/
  <module_name>/
    __init__.py       # 按需导出 router 等
    model.py          # SQLModel 数据表定义
    schema.py         # Pydantic/SQLModel 请求与响应 Schema
    repository.py     # 数据库 CRUD 操作（仅操作 DB，不含业务逻辑）
    service.py        # 业务逻辑层（调用 repository，抛出业务异常）
    router.py         # FastAPI 路由层（依赖注入 service）
```

公共基础设施放在 `app/core/` 下：

- `base_model.py` — `DateTimeMixin`、`database_naming_convention`
- `config.py` — `Settings`（pydantic-settings）& `settings` 单例
- `database.py` — `Database` 类 & `db` 单例 & `get_session`
- `exception.py` — 业务异常类 & 全局异常注册
- `lifespan.py` — FastAPI `lifespan` 上下文管理器
- `security.py` — 密码哈希 & JWT 工具函数

---

## 数据模型规范（model.py）

- 所有 ORM 表模型继承 `SQLModel`，并通过 `mixins=[DateTimeMixin]` 附加时间戳字段。
- 优先使用 SQLModel 内建的属性和 `Field` 参数实现约束、索引、关系等；只有在确实需要 PostgreSQL 特性或复杂表达式时才导入并使用 `sqlalchemy`（例如自定义列类型、函数调用等）。
- 始终显式声明 `__tablename__`（复数形式，snake_case），并加 `# type: ignore[assignment]`。
- 字段使用 `name: type = Field(...)` 风格，并在 `Field` 中填写 `description`。
- 主键统一用 `id: int | None = Field(default=None, primary_key=True)`。
- 常用查询字段加 `index=True`。
- 关联关系用 `TYPE_CHECKING` 保护导入，避免循环依赖。

```python
# 示例
from app.core.base_model import DateTimeMixin

class MyModel(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "my_models"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True, description="ID")
    name: str = Field(..., max_length=100, unique=True, description="名称")
```

---

## Schema 规范（schema.py）

每个模块至少提供三个 Schema，均继承 `SQLModel`（不声明 `table=True`）：

| Schema 类         | 用途                                                      |
| ----------------- | --------------------------------------------------------- |
| `<Model>Create`   | 创建请求体，所有必填字段                                  |
| `<Model>Update`   | 更新请求体，所有字段设为 `Optional`（`Field(None, ...)`） |
| `<Model>Response` | 接口响应，包含 `id` 及所有暴露字段                        |

- 字段同样使用 `name: type = Field(...)` 风格。
- `Update` Schema 所有字段必须可选（`field | None = None`），服务层调用 `model_dump(exclude_unset=True, exclude_none=True)`。

---

## Repository 规范（repository.py）

- 类名为 `<Model>Repository`，构造函数接收 `session: AsyncSession`。
- 仅负责数据库操作，**禁止**包含业务判断或异常抛出（`IntegrityError` 直接上抛）。
- 必须提供的标准方法：

```python
async def get_by_id(self, id: int) -> Model | None
async def get_all(self, *, search, order_by, direction, limit, offset) -> list[Model]
async def create(self, data: Mapping[str, Any]) -> Model
async def update(self, id: int, data: Mapping[str, Any]) -> Model | None
async def delete(self, id: int) -> bool
```

- 查询使用 `select(Model)` + `session.exec()`，更新前先 `get_by_id`。
- `create` / `update` 后调用 `session.commit()` 和 `session.refresh()`。
- `delete` 后调用 `session.commit()`，不需要 refresh。
- `get_all` 中排序字段需用白名单校验，分页 `limit` 上限 500，`offset` 下限 0。

---

## Service 规范（service.py）

- 类名为 `<Model>Service`，构造函数接收 `repository: <Model>Repository`。
- 所有业务逻辑（存在性检查、唯一性错误转换等）放在此层。
- **不允许**在 service 中直接操作 `session`。
- 资源不存在时抛出 `NotFoundException`，唯一性冲突时将 `IntegrityError` 转换为 `AlreadyExistsException`。
- 方法返回值统一使用 `<Model>Response`（调用 `Model.model_validate()`）。

```python
from app.core.exception import AlreadyExistsException, NotFoundException

class MyService:
    def __init__(self, repository: MyRepository) -> None:
        self.repository = repository

    async def get_by_id(self, id: int) -> MyResponse:
        obj = await self.repository.get_by_id(id)
        if not obj:
            raise NotFoundException("MyModel not found")
        return MyResponse.model_validate(obj)
```

---

## Router 规范（router.py）

- 路由器用 `APIRouter(prefix="/<resources>", tags=["<tag>"])` 定义。
- 通过局部依赖函数（`async def get_<model>_service(...) -> <Model>Service`）注入 service：

```python
async def get_my_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MyService:
    return MyService(MyRepository(session))
```

- 路由函数参数使用 `Annotated[..., Depends(...)]` 注解。
- 路径参数使用 `Annotated[int, Path(..., description="...")]`。
- 响应类型始终声明 `response_model=<Schema>Response`。
- 创建操作返回 `status_code=201`；删除操作返回 `status_code=204`，函数体 `return None`。

---

## 异常处理规范

使用 `app/core/exception.py` 中的业务异常，**禁止**直接在 router/service 中抛出裸 `HTTPException`：

| 异常类                   | HTTP 状态码 | 使用场景   |
| ------------------------ | ----------- | ---------- |
| `NotFoundException`      | 404         | 资源不存在 |
| `AlreadyExistsException` | 409         | 唯一性冲突 |
| `UnauthorizedException`  | 401         | 未认证     |
| `ForbiddenException`     | 403         | 无权限     |

全局未处理异常由 `global_exception_handler` 兜底，返回 500。

---

## 数据库与配置规范

- 数据库连接参数必须通过 `settings`（`app/core/config.py`）读取，**禁止**硬编码。
- 敏感配置（`db_password`、`jwt_secret`）必须放在 `.env` 文件或环境变量中，不得提交真实值。
- 生产环境使用 Alembic 进行 Schema 迁移，`settings.debug=True` 时才允许 `create_tables()`。
- 连接池参数（`pool_size`、`max_overflow` 等）统一通过 `settings.engine_options` 传入。

---

## 安全规范

- 密码哈希使用 `app/core/security.get_password_hash()`，验证使用 `verify_password()`。
- JWT 签发使用 `create_access_token(subject)`，解码使用 `decode_access_token(token)`。
- `jwt_secret` 生产环境必须为随机高强度字符串，绝不可使用默认值。
- 刷新令牌存入 `refresh_tokens` 表，支持按设备管理、撤销与过期校验（`RefreshToken.is_valid()`）。

---

## 测试规范

- 测试文件置于 `tests/` 目录，文件名以 `test_` 开头。
- 异步测试使用 `pytest-asyncio`，fixture 作用域：`engine` 为 `session`，`session_factory` / `app` / `client` 为函数级。
- 通过 `app.dependency_overrides[real_get_session]` 替换数据库会话为测试专用 session。
- HTTP 集成测试使用 `httpx.AsyncClient` + `ASGITransport(app=app)`。
- 测试数据库 URL 从环境变量 `TEST_DATABASE_URL` 读取，默认指向本地 `test_db`。
- **禁止**在测试中直接操作生产数据库。

---

## 代码风格

- Python 版本：`>= 3.14`，充分使用新语法（`X | Y` 联合类型、`match` 语句等）。
- 所有函数和方法参数须声明类型注解。
- 异步函数统一使用 `async def`，数据库操作必须用 `await`。
- 日志使用 `loguru`（`from loguru import logger`），禁止使用 `print()`。
- 导入顺序：标准库 → 第三方库 → 本地模块，各组之间空一行。
- `TYPE_CHECKING` 保护块仅用于解决循环导入，不用于非类型注解目的。

---

## 提交信息规范

为了保持历史整洁、快速定位变更，每次 `git commit` 请遵循以下中文格式：

1. **前缀使用 emoji + 简短类别**，如 `✨ 新功能`、`🐛 修复`、`🛠️ 重构`、`📄 文档` 等。
2. 主体描述使用简洁中文，首字母不大写，不带句号。
3. 必要时在描述后面添加更详细的解释或关联 issue/PR 编号。

示例风格（参考 FastAPI 仓库）：
```
✨ 新增用户注册和登录接口 (#123)
🐛 修复令牌过期时间计算错误
🛠️ 重构 profile 模块以支持多用户
📄 更新 README 文档，添加部署说明
🚀 发布 1.2.0 版本
```

> 推荐在提交时使用 emoji 来快速区分类型，同时保持消息尽量简洁、中文说明明确。

