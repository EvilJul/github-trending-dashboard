# GitHub Trending Projects API 文档

## 概述

GitHub Trending Projects Dashboard 的后端 API 服务，提供 GitHub 热门项目数据的查询和管理功能。

## 基础信息

| 项目 | 值 |
|------|-----|
| 服务地址 | `http://localhost:8001` |
| API 文档 | `http://localhost:8001/docs` (Swagger UI) |
| 健康检查 | `http://localhost:8001/health` |

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
  "last_updated": "2026-02-03T04:30:44.061772",
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
      "fork_url": "https://github.com/lukilabs/beautiful-mermaid/fork",
      "issues_url": "https://github.com/lukilabs/beautiful-mermaid/issues",
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
  "last_updated": "2026-02-03T04:30:44.061772",
  "projects_count": 20
}
```

---

### AI 增强刷新

```http
POST /api/projects/refresh-ai?provider=qwen&api_key=xxx
```

使用 AI 模型增强项目数据，生成更丰富的描述和使用指南。

**参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| provider | string | AI 服务提供商 (qwen/minimax/openai/anthropic) |
| api_key | string | API Key |
| endpoint | string | API 端点 (可选) |

**响应示例:**
```json
{
  "success": true,
  "message": "AI 增强刷新成功，获取 20 个项目",
  "last_updated": "2026-02-03T04:30:44.061772",
  "projects_count": 20,
  "ai_enhanced": true
}
```

---

### 获取单个项目

```http
GET /api/projects/{project_name}
```

**参数:**
- `project_name`: 项目名称 (如 `beautiful-mermaid` 或 `lukilabs/beautiful-mermaid`)

**响应示例:**
```json
{
  "name": "beautiful-mermaid",
  "full_name": "lukilabs/beautiful-mermaid",
  "url": "https://github.com/lukilabs/beautiful-mermaid",
  "description": "项目描述",
  "language": "TypeScript",
  "stars": 5391,
  "forks": 149,
  "issues": 18,
  "fork_url": "https://github.com/lukilabs/beautiful-mermaid/fork",
  "issues_url": "https://github.com/lukilabs/beautiful-mermaid/issues",
  "category": "前端技术",
  "trend": "falling",
  "usage_steps": [...]
}
```

---

### 获取项目 README

```http
GET /api/projects/{project_name}/readme
```

获取项目的 README.md 文件内容（Markdown 格式）。

**参数:**
- `project_name`: 项目名称

**响应示例:**
```json
{
  "project": "skills",
  "full_name": "antfu/skills",
  "readme": "# Anthony Fu's Skills\n\nA curated collection...",
  "has_readme": true
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
        {
          "name": "beautiful-mermaid",
          "full_name": "lukilabs/beautiful-mermaid",
          "description": "...",
          "language": "TypeScript",
          "stars": 5391,
          "category": "前端技术"
        },
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

### 删除历史记录

```http
DELETE /api/history/{record_id}
```

---

## 启动服务

```bash
cd backend

# 使用虚拟环境
source venv/bin/activate

# 启动服务
python main.py --port 8001
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
│   ├── projects.py   # 项目相关 API (20+ 端点)
│   └── history.py    # 历史记录 API
├── services/         # 业务逻辑
│   ├── github.py     # GitHub 数据获取、README 抓取
│   ├── storage.py    # 数据存储
│   └── ai.py         # AI 增强服务
├── models/           # 数据模型
│   └── schemas.py    # Pydantic 模型
└── data/             # 数据文件存储
    ├── projects.json
    └── history.json
```

## AI 服务配置

支持多种 AI 服务提供商：

| 提供商 | 模型 | 端点 |
|--------|------|------|
| 通义千问 (qwen) | qwen-plus | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| MiniMax | MiniMax-M2.1 | https://api.minimax.chat/v1 |
| OpenAI | gpt-4 | https://api.openai.com/v1 |
| Anthropic | claude-3-sonnet | https://api.anthropic.com/v1 |

### AI 增强示例

```bash
# 使用通义千问增强数据
curl -X POST "http://localhost:8001/api/projects/refresh-ai?provider=qwen&api_key=YOUR_API_KEY"
```
