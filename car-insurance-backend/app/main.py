from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.api import quote, strategy, insurer, analytics, effect_analysis, business_unit
from app.core.logging_setup import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="智能业务决策平台后端 API - 基于 UE 模型和情景仿真的智能决策系统",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境需要限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(quote.router, prefix=f"{settings.API_PREFIX}/quote", tags=["询价"])
    app.include_router(strategy.router, prefix=f"{settings.API_PREFIX}/strategy", tags=["策略"])
    app.include_router(insurer.router, prefix=f"{settings.API_PREFIX}/insurer", tags=["保司"])
    app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["分析"])
    app.include_router(effect_analysis.router, prefix=f"{settings.API_PREFIX}/effect", tags=["效果分析"])
    app.include_router(business_unit.router, prefix=f"{settings.API_PREFIX}/business-unit", tags=["业务单元"])
    
    # 健康检查
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
