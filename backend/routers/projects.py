"""
项目相关 API 路由
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import ProjectsResponse, ProjectResponse, RefreshResponse, ErrorResponse
from services.github import GitHubService
from services.storage import StorageService

router = APIRouter(prefix="/api/projects", tags=["projects"])

# 初始化服务
storage = StorageService()
github_service = GitHubService()


@router.get("/", response_model=ProjectsResponse)
async def get_projects():
    """
    获取所有项目
    """
    try:
        data = storage.load_projects()
        projects = []

        for item in data.get("projects", []):
            projects.append(ProjectResponse(**item))

        return ProjectsResponse(
            last_updated=data.get("last_updated", ""),
            projects=projects,
            total_count=len(projects)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}", response_model=ProjectResponse)
async def get_project(project_name: str):
    """
    获取单个项目详情
    """
    try:
        projects = storage.get_projects()
        for p in projects:
            if p.name == project_name or p.full_name == project_name:
                return p
        raise HTTPException(status_code=404, detail=f"Project {project_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_projects():
    """
    刷新项目数据（从 GitHub 获取最新趋势）
    """
    try:
        # 从 GitHub 获取数据
        projects = await github_service.fetch_trending_projects(days=7, per_page=10)

        # 保存到文件
        saved_data = storage.save_projects(projects)

        # 添加历史记录 - 保存完整的项目详情
        from models.schemas import HistoryRecord
        from datetime import datetime

        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
        # 构建完整的项目详情列表
        projects_detail = []
        for p in projects:
            projects_detail.append({
                "name": p.name,
                "full_name": p.full_name,
                "url": p.url,
                "description": p.description,
                "language": p.language,
                "stars": p.stars,
                "forks": p.forks,
                "issues": p.issues,
                "fork_url": p.fork_url,
                "issues_url": p.issues_url,
                "category": p.category,
                "trend": p.trend,
                "usage_steps": p.usage_steps
            })
        
        record = HistoryRecord(
            id=f"{year}-W{week_num}",
            week=f"{year}年{week_num}月第{week_num}周",
            date=datetime.now().strftime("%Y-%m-%d"),
            total_projects=len(projects),
            projects=projects_detail  # 保存完整项目详情
        )
        storage.add_history_record(record)

        return RefreshResponse(
            success=True,
            message=f"成功获取 {len(projects)} 个项目",
            last_updated=saved_data.get("last_updated", ""),
            projects_count=len(projects)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats():
    """
    获取项目统计信息
    """
    try:
        data = storage.load_projects()
        projects = data.get("projects", [])

        # 统计语言分布
        languages = {}
        categories = {}
        total_stars = 0
        total_forks = 0

        for p in projects:
            lang = p.get("language", "Unknown")
            category = p.get("category", "Other")
            languages[lang] = languages.get(lang, 0) + 1
            categories[category] = categories.get(category, 0) + 1
            total_stars += p.get("stars", 0)
            total_forks += p.get("forks", 0)

        return {
            "total_projects": len(projects),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "language_distribution": languages,
            "category_distribution": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/readme")
async def get_project_readme(project_name: str):
    """
    获取项目 README 内容
    """
    try:
        # 先从本地数据中查找项目
        projects = storage.get_projects()
        project = None
        
        for p in projects:
            if p.name == project_name or p.full_name == project_name:
                project = p
                break
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_name} not found")
        
        # 从 GitHub 获取 README
        readme_content = await github_service.fetch_readme(project.full_name)
        
        return {
            "project": project_name,
            "full_name": project.full_name,
            "readme": readme_content,
            "has_readme": readme_content is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
