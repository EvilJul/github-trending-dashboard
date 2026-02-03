"""
FastAPI 主应用
"""

import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from routers import projects, history, config

# ==================== 日志配置 ====================
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 强制 UTF-8 编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
            encoding='utf-8',
            errors='replace'
        )
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    logger.info("GitHub Trending API Server Started")
    yield
    logger.info("Server Shutdown")


app = FastAPI(
    title="GitHub Trending Projects API",
    description="GitHub 热门项目数据 API 服务",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = os.path.join(os.path.dirname(__file__), "../web")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "github-trending-api"}


app.include_router(projects.router)
app.include_router(history.router)
app.include_router(config.router)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/{path:path}")
async def serve_spa(request: Request, path: str):
    if path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "API endpoint not found", "path": f"/{path}"}
        )

    file_path = os.path.join(WEB_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

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
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower()
    )
