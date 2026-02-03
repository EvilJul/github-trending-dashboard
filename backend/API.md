# GitHub Trending Projects API 文档

## 概述

GitHub Trending Projects Dashboard 的后端 API 服务，提供 GitHub 热门项目数据的查询和管理功能。

## 基础信息

| 项目 | 值 |
|------|-----|
| 服务地址 | `http://localhost:8000` |
| API 文档 | `http://localhost:8000/docs` (Swagger UI) |
| 健康检查 | `http://localhost:8000/health` |

## API 列表

### 健康检查

```http
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "service": "github-trending-api"
}
```

---

### 获取项目列表

```http
GET /api/projects/
```

**响应示例:**
```json
{
  "last_updated": "2026-02-02T16:41:55.123456",
  "projects": [
    {
      "name": "beautiful-mermaid",
      "full_name": "lukilabs/beautiful-mermaid",
      "url": "https://github.com/lukilabs/beautiful-mermaid",
      "description": "项目描述",
      "language": "TypeScript",
      "stars": 5391,
      "forks": 149,
      "issues": 18,
      "category": "前端技术",
      "trend": "falling",
      "usage_steps": [
        "克隆项目: git clone https://github.com/...",
        "进入项目目录",
        "安装依赖: npm install",
        "运行开发服务器: npm run dev"
      ]
    }
  ],
  "total_count": 20
}
```

---

### 刷新项目数据

```http
POST /api/projects/refresh
```

从 GitHub API 获取最新的热门项目数据。

**响应示例:**
```json
{
  "success": true,
  "message": "成功获取 20 个项目",
  "last_updated": "2026-02-02T16:41:55.123456",
  "projects_count": 20
}
```

---

### 获取单个项目

```http
GET /api/projects/{project_name}
```

**参数:**
- `project_name`: 项目名称 (如 `beautiful-mermaid`)

**响应示例:**
```json
{
  "name": "beautiful-mermaid",
  "full_name": "lukilabs/beautiful-mermaid",
  ...
}
```

---

### 获取统计信息

```http
GET /api/projects/stats/summary
```

**响应示例:**
```json
{
  "total_projects": 20,
  "total_stars": 18825,
  "total_forks": 1234,
  "language_distribution": {
    "TypeScript": 8,
    "Python": 7,
    "JavaScript": 3,
    "Other": 2
  },
  "category_distribution": {
    "前端技术": 5,
    "AI/机器学习": 8,
    "Python生态": 4,
    "通用工具": 3
  }
}
```

---

### 获取历史记录

```http
GET /api/history/
```

**响应示例:**
```json
{
  "history": [
    {
      "id": "2026-W6",
      "week": "2026年6月第6周",
      "date": "2026-02-03",
      "total_projects": 20,
      "projects": [
        "lukilabs/beautiful-mermaid",
        "antfu/skills",
        ...
      ]
    }
  ]
}
```

---

### 获取单条历史记录

```http
GET /api/history/{record_id}
```

**参数:**
- `record_id`: 记录 ID (如 `2026-W6`)

---

## 启动服务

```bash
cd backend

# 使用虚拟环境
source venv/bin/activate

# 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

或使用启动脚本:

```bash
./start.sh
```

## 技术栈

- **FastAPI**: 现代高性能 Web 框架
- **httpx**: 异步 HTTP 客户端
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI 服务器

## 项目结构

```
backend/
├── main.py           # FastAPI 应用入口
├── routers/          # API 路由
│   ├── projects.py   # 项目相关 API
│   └── history.py    # 历史记录 API
├── services/         # 业务逻辑
│   ├── github.py     # GitHub 数据获取
│   └── storage.py    # 数据存储
└── models/           # 数据模型
    └── schemas.py    # Pydantic 模型
```
