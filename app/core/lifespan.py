import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的 lifespan 上下文管理器（抽离到单独模块以便复用与测试）。

    行为：
    - 仅在 `settings.debug` 为 True 时自动创建 DB 表（开发/测试场景）。
    - 在关闭时释放数据库引擎资源。生产环境应使用 Alembic 进行迁移。
    """

    logger.info("应用启动中, 开始初始化资源...")
    if settings.debug:
        logger.info("当前为调试模式, 自动创建数据库表 (生产环境请使用Alembic)")
        try:
            await db.create_tables()
            logger.success("数据库表创建成功 (调试模式)")
        except Exception as e:
            logger.error(f"调试模式下创建数据库表失败: {str(e)}")
            raise  # 启动失败，避免应用带错运行

    # 注册信号处理器（捕获终止信号，确保优雅退出）
    def register_shutdown_signals():
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(_shutdown_handler())
            )
        logger.info("退出信号处理器已注册")

    async def _shutdown_handler():
        """信号触发的关闭逻辑 (和finally逻辑一致)"""
        logger.info("收到终止信号, 开始清理数据库资源...")
        await db.dispose()
        logger.success("数据库引擎已销毁, 连接池资源释放完成")

    register_shutdown_signals()

    try:
        yield

    # 应用关闭阶段（无论是否异常，必执行）
    finally:
        logger.info("应用开始关闭, 清理数据库引擎资源...")
        await db.dispose()
        logger.success("数据库引擎已销毁, 连接池资源释放完成")
