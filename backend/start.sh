#!/bin/bash
# GitHub Trending API Server 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# 检查依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 自动查找可用端口 (10000-11000)
find_available_port() {
    for port in $(seq 10000 11000); do
        if ! nc -z localhost $port 2>/dev/null; then
            echo $port
            return 0
        fi
    done
    echo "10000"  # 默认返回范围起始端口
    return 1
}

PORT=$(find_available_port)

# 启动服务
echo "🚀 启动 GitHub Trending API Server..."
echo "   访问地址: http://localhost:$PORT"
echo "   API 文档: http://localhost:$PORT/docs"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port $PORT --reload
