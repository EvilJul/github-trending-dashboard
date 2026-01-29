# GitHub Trending Projects Dashboard

一个简约大气、富含科技感的GitHub热门项目展示系统，每周自动更新最新的热门开源项目信息。

## 项目简介

GitHub Trending Projects Dashboard 是一个自动化项目，旨在帮助开发者快速了解每周GitHub上最热门的开源项目。通过定期抓取GitHub Trending数据，系统会自动生成精美的报告，并提供直观的网页界面展示项目详情。

该项目特别适合：
- 关注技术趋势的开发者
- 寻找开源项目的用户
- 需要技术选型参考的团队
- 对新兴技术感兴趣的个人

## 项目结构

```
github_trending_projects/
├── scripts/                 # 脚本文件
│   ├── github_report_generator.js    # 报告生成脚本
│   ├── github-trending-fetcher.js    # 数据获取脚本
│   └── github-weekly-report.sh       # 报告生成脚本
├── data/                   # 数据文件
│   └── projects.json       # GitHub项目数据
├── web/                    # 网页界面
│   ├── index.html          # 主页面
│   ├── dashboard.js        # 交互逻辑
│   └── (样式和图片等)
└── README.md               # 项目说明
```

## 功能特点

- 🚀 **自动更新**：每周五上午10点自动获取最新的GitHub热门项目
- 📊 **数据展示**：清晰展示项目Stars、Forks、Issues等关键指标
- 🎨 **科技美感**：简约大气的设计风格，富含现代科技感
- 📱 **响应式布局**：适配各种屏幕尺寸
- 🔧 **使用指南**：提供每个项目的简单使用步骤

## 使用方法

### 本地查看网页界面

1. 直接在浏览器中打开 `web/index.html` 文件
2. 或者使用简单的HTTP服务器（推荐）：
   ```bash
   cd github_trending_projects/web
   python3 -m http.server 8000
   ```
   然后访问 `http://localhost:8000`

### 数据更新

系统会根据设定的cron任务每周自动更新数据，也可以手动触发更新：

```
生成一份最新的 GitHub 热门项目报告
```

## 技术栈

- HTML5/CSS3
- JavaScript (ES6+)
- 响应式设计
- JSON数据格式

## 自定义配置

如需修改更新频率或其他设置，可以编辑cron任务：

```bash
clawdbot cron list  # 查看现有任务
clawdbot cron edit <job-id>  # 编辑任务
```

## 维护

- 数据文件位于 `data/projects.json`
- 网页界面文件位于 `web/` 目录
- 脚本文件位于 `scripts/` 目录

## 扩展功能

系统支持以下扩展功能：

### 添加更多编程语言
可以修改脚本以获取不同编程语言的热门项目：
- 当前主要关注Java项目
- 可扩展至JavaScript、Python、Go等语言

### 自定义展示字段
可以在 `projects.json` 中添加更多字段：
- 项目许可证信息
- 最近提交活动
- 贡献者统计

### 高级过滤功能
- 按项目大小过滤
- 按活跃度排序
- 按特定标签筛选

---

🤖 由 Clawdbot 自动维护 | 📅 每周五自动更新