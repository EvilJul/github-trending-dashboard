# API 文档

GitHub Trending Projects Backend API

## 基础信息

- **Base URL**: `http://localhost:8000`
- **文档**: `/api/docs` (Swagger UI) | `/api/redoc` (ReDoc)

## 端点列表

### 健康检查

**GET** `/api/health`

检查服务是否正常运行。

**响应示例**:
```json
{
  "status": "ok",
  "timestamp": "2026-02-03T00:30:00.000Z"
}
```

---

### 获取项目列表

**GET** `/api/projects`

获取GitHub热门项目列表。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | string | 否 | 按编程语言筛选 (Java, Python, JavaScript等) |

**响应示例**:
```json
{
  "lastUpdated": "2026-02-03T00:30:00.000Z",
  "projects": [
    {
      "name": "huggingface/transformers",
      "fullName": "huggingface/transformers",
      "url": "https://github.com/huggingface/transformers",
      "forkUrl": "https://github.com/huggingface/transformers/fork",
      "issuesUrl": "https://github.com/huggingface/transformers/issues",
      "description": "Hugging Face Transformers 是 NLP 领域最流行的预训练模型库",
      "language": "Python",
      "stars": 156000,
      "forks": 38500,
      "issues": 1234,
      "usageSteps": [
        "加载模型: from transformers import AutoModelForCausalLM, AutoTokenizer",
        "文本生成: 使用 pipeline('text-generation') 快速体验"
      ],
      "trend": "stable",
      "category": "NLP"
    }
  ],
  "totalProjects": 10
}
```

---

### 刷新数据

**POST** `/api/refresh`

从GitHub API获取最新的热门项目数据。

**响应示例**:
```json
{
  "success": true,
  "message": "成功获取 10 个热门项目",
  "projectsCount": 10,
  "lastUpdated": "2026-02-03T00:35:00.000Z"
}
```

**错误响应**:
```json
{
  "detail": "刷新失败: Error message here"
}
```

---

### 获取历史记录

**GET** `/api/history`

获取历史记录列表。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回记录数量，默认10条 |

**响应示例**:
```json
[
  {
    "id": "20260124",
    "date": "2026-01-24",
    "displayDate": "2026年1月24日",
    "summary": {
      "totalProjects": 10,
      "totalStars": 245600,
      "topLanguage": "Python",
      "highlights": ["AI/机器学习项目热度持续上升"]
    },
    "projects": [
      {
        "name": "huggingface/transformers",
        "stars": 156000,
        "language": "Python",
        "trend": "stable"
      }
    ],
    "reportUrl": "/reports/github-weekly-report-2026-01-24.md"
  }
]
```

---

### 获取统计信息

**GET** `/api/stats`

获取项目统计数据。

**响应示例**:
```json
{
  "totalProjects": 10,
  "totalStars": 245600,
  "topLanguages": {
    "Python": 5,
    "Java": 3,
    "JavaScript": 2
  },
  "topCategories": {
    "AI/机器学习": 4,
    "NLP": 2,
    "深度学习": 2,
    "Web开发": 1,
    "通用工具": 1
  },
  "lastUpdated": "2026-02-03T00:30:00.000Z"
}
```

---

## 静态页面

| 路由 | 说明 |
|------|------|
| `/` | 主页面 (index.html) |
| `/history` | 历史记录页面 |
| `/history.html` | 历史记录页面 (兼容) |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |
