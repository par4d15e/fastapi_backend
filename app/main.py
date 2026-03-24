from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.auth.backend import fastapi_users
from app.auth.router import register_fastapi_users_routes
from app.core.exception import register_exception_handlers
from app.core.lifespan import lifespan
from app.foods.router import router as food_routers
from app.nutrition.router import router as nutrition_routers
from app.profiles.router import router as profile_routers
from app.reminders.router import router as reminder_routers
from app.weights.router import router as weight_routers


def create_app() -> FastAPI:
    app = FastAPI(
        title="fastapi_sqlalchemy_backend",
        version="0.1.0",
        description="FastAPI + SQLAlchemy(asyncio)",
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

    # 认证审计：记录 /auth 路径的成功/失败的登录/注册事件
    @app.middleware("http")
    async def auth_audit_middleware(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/auth"):
            if response.status_code >= 400:
                logger.warning(
                    "Auth request failed",
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                )
            elif request.url.path.endswith("/login") and response.status_code == 200:
                logger.info(
                    "Auth login succeeded",
                    path=request.url.path,
                    method=request.method,
                )
        return response

    # 路由注册
    app.include_router(profile_routers)
    app.include_router(food_routers)
    app.include_router(nutrition_routers)
    app.include_router(reminder_routers)
    app.include_router(weight_routers)
    register_fastapi_users_routes(app, fastapi_users)

    # 健康检查
    @app.get("/healthz", tags=["health"])
    async def healthz():
        return {"status": "ok"}

    # 注册全局异常处理
    register_exception_handlers(app)

    return app


app = create_app()
