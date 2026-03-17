import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core import models  # noqa: F401  # 保证所有 model 已被载入
from app.core.base_model import Base
from app.core.config import settings

# 从 settings 读取数据库连接 URL
database_url = settings.database_url

# 这是 Alembic 的 Config 对象，用于访问正在使用的 .ini 文件中的配置值。
config = context.config

config.set_main_option("sqlalchemy.url", database_url)
# 解析配置文件以设置 Python 日志。
# 这一行基本上是配置记录器。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 在此添加模型的 MetaData 对象
# 以支持“自动生成”迁移
# 来自 myapp 导入模型示例：
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# env.py 所需的其他配置值也可以获取：
# my_important_option = config.get_main_option("my_important_option")
# ...等等。


def run_migrations_offline() -> None:
    """在"离线"模式下运行迁移

    这仅使用 URL 配置上下文，而不创建 Engine
    虽然这里也可以使用 Engine。通过跳过 Engine 的
    创建，我们甚至不需要可用的 DBAPI

    对 context.execute() 的调用会将给定的字符串
    输出到脚本

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在这种情况下，我们需要创建一个 Engine
    并将连接与上下文关联

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """以"在线"模式运行迁移"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
