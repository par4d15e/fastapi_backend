import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理应用启动和关闭生命周期。"""

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
        """注册进程关闭信号处理器。"""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(_shutdown_handler())
            )
        logger.info("退出信号处理器已注册")

    async def _shutdown_handler():
        """处理应用关闭信号。"""
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
