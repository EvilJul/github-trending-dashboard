"""
FastAPI 主应用
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from routers import projects, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：初始化数据目录
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    print("🚀 GitHub Trending API Server Started")
    yield
    # 关闭时
    print("👋 Server Shutdown")


# 创建 FastAPI 应用
app = FastAPI(
    title="GitHub Trending Projects API",
    description="GitHub 热门项目数据 API 服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取 web 目录路径
WEB_DIR = os.path.join(os.path.dirname(__file__), "../web")


# ==================== API 路由 ====================

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "github-trending-api"}


# 注册 API 路由
app.include_router(projects.router)
app.include_router(history.router)


# ==================== 静态文件服务 ====================

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


# ==================== SPA 路由支持 ====================

@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/{path:path}")
async def serve_spa(request: Request, path: str):
    """服务单页应用 - 只处理非 API 路径"""
    # 排除 API 路径
    if path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "API endpoint not found", "path": f"/{path}"}
        )

    # 检查静态文件
    file_path = os.path.join(WEB_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # 返回 index.html 让前端处理路由
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": f"/{path}"}
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Trending API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
