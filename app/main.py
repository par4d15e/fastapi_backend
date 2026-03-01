from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_routers
from app.core.exception import register_exception_handlers
from app.core.lifespan import lifespan
from app.foods import router as food_routers
from app.profiles import router as profile_routers
from app.reminders import router as reminder_routers


def create_app() -> FastAPI:
    app = FastAPI(
        title="fastapi_sqlmodel_backend",
        version="0.1.0",
        description="FastAPI + SQLModel(asynio)",
        lifespan=lifespan,  # 绑定生命周期管理器
    )

    # 中间件（按需启用）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由注册
    app.include_router(profile_routers.router, prefix="", tags=["profile"])
    app.include_router(food_routers.router, prefix="", tags=["food"])
    app.include_router(reminder_routers.router, prefix="", tags=["reminder"])
    app.include_router(auth_routers.router, prefix="", tags=["auth"])

    # 健康检查
    @app.get("/healthz", tags=["health"])
    async def healthz():
        return {"status": "ok"}

    # 注册全局异常处理
    register_exception_handlers(app)

    return app


app = create_app()
