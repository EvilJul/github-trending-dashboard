# GitHub Trending Projects Dashboard

> 每周精选最热门的开源项目 | Powered by Clawdbot

![Dashboard Preview](docs/images/preview.png)

## ✨ 特性

- 🚀 **前后端分离架构** - FastAPI + 现代Web前端
- 📊 **实时数据获取** - 从GitHub API自动抓取热门项目
- 🎨 **优雅的界面** - 深色主题、流畅过渡动效
- 📱 **响应式设计** - 完美适配桌面和移动设备
- 📋 **历史记录** - 查看过往的热门项目报告
- 🔄 **自动刷新** - 每周五上午10:00自动更新
- 📚 **完整文档** - API文档、部署指南

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ index.html  │  │ history.html│  │  dashboard.js   │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP API
┌────────────────────────┴────────────────────────────────┐
│                      Backend (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  /api/projects  │  /api/refresh  │  /api/history  │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│              ┌───────────┴───────────┐                   │
│              │   GitHub Scraper      │                   │
│              └───────────────────────┘                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                       Data Storage                       │
│        data/projects.json  │  data/history.json         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用

打开浏览器访问: http://localhost:8000

## 📖 使用指南

### 获取最新项目

1. 点击右上角「刷新数据」按钮
2. 等待后端从GitHub获取数据
3. 数据自动保存并显示

### 筛选项目

使用语言筛选按钮快速找到感兴趣的项目：
- ☕ Java
- 🐍 Python
- 📜 JavaScript
- 📘 TypeScript

### 查看历史

点击顶部「历史记录」查看过往报告。

## ⚙️ 配置说明

### 定时任务 (可选)

每周五上午10:00自动刷新数据：

```bash
# 添加 cron 任务
clawdbot cron add --schedule "0 10 * * 5" --task "curl -X POST http://localhost:8000/api/refresh"
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| PORT | 服务端口 | 8000 |
| HOST | 绑定地址 | 0.0.0.0 |

## 📚 API 文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects/` | 获取项目列表 |
| POST | `/api/projects/refresh` | 刷新数据 |
| GET | `/api/projects/stats/summary` | 获取统计信息 |
| GET | `/api/history/` | 获取历史记录 |
| GET | `/api/history/{id}` | 获取单条历史记录 |
| GET | `/health` | 健康检查 |

## 📁 项目结构

```
github_trending_projects/
├── backend/
│   ├── main.py           # FastAPI 主服务
│   └── requirements.txt  # Python 依赖
├── web/
│   ├── index.html        # 主页面
│   ├── history.html      # 历史记录页
│   └── dashboard.js      # 前端逻辑
├── data/
│   ├── projects.json     # 项目数据
│   └── history.json      # 历史记录
├── docs/
│   ├── API.md            # API 文档
│   └── images/           # 图片资源
├── config.json           # 项目配置
└── README.md             # 本文件
```

## 🛠️ 开发

### 添加新功能

1. **后端**: 在 `backend/main.py` 添加新端点
2. **前端**: 在 `web/dashboard.js` 添加新方法
3. **样式**: 在 `web/index.html` 的 `<style>` 中添加

### 运行测试

```bash
# 后端测试
cd backend
python -m pytest

# API 健康检查
curl http://localhost:8000/api/health
```

## 📝 更新日志

### v1.1.0 (2026-02-03)
- ✨ 新增前后端分离架构
- 🎨 优化界面动效 (页面切换、卡片入场动画)
- 📊 新增加载状态动画
- 📚 完善API文档
- 🔄 支持实时数据刷新
- 📋 完善历史记录功能

### v1.0.0 (2026-01-29)
- 🎉 初始版本
- 📊 项目展示功能
- 🌙 深色主题

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
