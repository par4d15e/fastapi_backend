from datetime import datetime
from typing import Annotated

from sqlalchemy import Column, DateTime, MetaData, func
from sqlmodel import Field, SQLModel

# 保持原有的命名约定 (用于 Alembic / metadata.create_all)
database_naming_convention = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

# 将命名约定应用到 sqlmodel 的全局 metadata
SQLModel.metadata = MetaData(naming_convention=database_naming_convention)


class DateTimeMixin(SQLModel):
    """
    PostgreSQL 专用的 created_at / updated_at 实现 (使用数据库端 now())
    """

    created_at: Annotated[
        datetime,
        Field(
            sa_column=Column(
                DateTime(timezone=True),
                server_default=func.now(),  # PostgreSQL 原生 now() 函数
                nullable=False,
                index=True,
            ),
            description="创建时间（数据库自动生成）",
        ),
    ]

    updated_at: Annotated[
        datetime,
        Field(
            sa_column=Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),  # 更新时自动刷新
                nullable=False,
            ),
            description="更新时间（数据库自动生成/刷新）",
        ),
    ]
