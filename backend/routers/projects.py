"""
项目相关 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.schemas import ProjectsResponse, ProjectResponse, RefreshResponse, ErrorResponse
from services.github import GitHubService
from services.storage import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

# 初始化服务
storage = StorageService()
github_service = GitHubService()

# 存储异步任务结果
_async_readme_results: dict = {}


@router.get("/", response_model=ProjectsResponse)
async def get_projects():
    """
    获取所有项目
    """
    try:
        logger.info("获取项目列表")
        data = storage.load_projects()
        projects = []

        for item in data.get("projects", []):
            projects.append(ProjectResponse(**item))

        logger.info(f"返回 {len(projects)} 个项目")
        return ProjectsResponse(
            last_updated=data.get("last_updated", ""),
            projects=projects,
            total_count=len(projects)
        )
    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_projects():
    """
    刷新项目数据（从 GitHub 获取最新趋势）
    """
    try:
        logger.info("刷新项目数据...")
        projects = await github_service.fetch_trending_projects(days=7, per_page=10)
        logger.info(f"获取到 {len(projects)} 个项目")

        saved_data = storage.save_projects(projects)

        # 添加历史记录
        from models.schemas import HistoryRecord
        from datetime import datetime

        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
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
            projects=projects_detail
        )
        storage.add_history_record(record)

        logger.info("项目数据刷新完成")
        return RefreshResponse(
            success=True,
            message=f"成功获取 {len(projects)} 个项目",
            last_updated=saved_data.get("last_updated", ""),
            projects_count=len(projects)
        )
    except Exception as e:
        logger.error(f"刷新项目数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-ai")
async def refresh_projects_ai(provider: str = "qwen", api_key: str = "", endpoint: str = ""):
    """
    使用 AI 增强刷新项目数据
    """
    try:
        logger.info(f"AI 增强刷新项目数据... provider={provider}")
        
        github_svc = GitHubService()
        projects = await github_svc.fetch_trending_projects(days=7, per_page=10)
        logger.info(f"获取到 {len(projects)} 个项目")
        
        if api_key and provider:
            try:
                from services.ai import AIService
                ai_service = AIService(provider=provider, api_key=api_key, endpoint=endpoint)
                
                enhanced_projects = []
                for p in projects:
                    enhanced = await ai_service.enhance_project(p)
                    enhanced_projects.append(enhanced)
                    logger.info(f"AI 增强项目: {p.full_name}")
                
                projects = enhanced_projects
                logger.info("AI 增强完成")
            except Exception as ai_error:
                logger.error(f"AI 增强失败: {ai_error}")

        saved_data = storage.save_projects(projects)

        from models.schemas import HistoryRecord
        from datetime import datetime

        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
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
            projects=projects_detail
        )
        storage.add_history_record(record)

        return {
            "success": True,
            "message": f"AI 增强刷新成功，获取 {len(projects)} 个项目",
            "last_updated": saved_data.get("last_updated", ""),
            "projects_count": len(projects),
            "ai_enhanced": bool(api_key)
        }
    except Exception as e:
        logger.error(f"AI 刷新失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_stats():
    """获取统计信息"""
    try:
        data = storage.load_projects()
        projects = data.get("projects", [])

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
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/readme")
async def get_project_readme(project_name: str):
    """
    获取项目 README 内容（同步方式）
    """
    try:
        # URL 解码 project_name
        from urllib.parse import unquote
        project_name = unquote(project_name)
        
        logger.info(f"获取 README: {project_name}")
        
        # 从本地数据中查找项目
        projects = storage.get_projects()
        project = None
        
        for p in projects:
            # 支持 name 和 full_name 两种格式
            if p.name == project_name or p.full_name == project_name:
                project = p
                break
        
        if not project:
            logger.warning(f"项目不存在: {project_name}")
            # 返回空内容而不是 404 错误
            return {
                "project": project_name,
                "full_name": project_name,
                "readme": None,
                "has_readme": False,
                "error": "项目不存在"
            }
        
        full_name = project.full_name
        logger.info(f"获取 README: {full_name}")
        
        readme_content = await github_service.fetch_readme(full_name)
        
        if readme_content is None:
            logger.info(f"项目无 README: {full_name}")
            return {
                "project": project_name,
                "full_name": full_name,
                "readme": None,
                "has_readme": False
            }
        
        logger.info(f"README 获取成功: {full_name} ({len(readme_content)} 字符)")
        return {
            "project": project_name,
            "full_name": full_name,
            "readme": readme_content,
            "has_readme": True
        }
    except Exception as e:
        logger.error(f"获取 README 失败: {e}")
        return {
            "project": project_name,
            "full_name": project_name,
            "readme": None,
            "has_readme": False,
            "error": str(e)
        }


@router.get("/readme/async")
async def get_project_readme_async(project_name: str):
    """
    异步获取项目 README（后台加载，前端轮询）
    返回任务 ID，前端可以轮询获取结果
    """
    import asyncio
    import uuid
    from urllib.parse import unquote
    
    try:
        project_name = unquote(project_name)
        
        # 查找项目
        projects = storage.get_projects()
        project = None
        
        for p in projects:
            if p.name == project_name or p.full_name == project_name:
                project = p
                break
        
        if not project:
            return {
                "task_id": None,
                "status": "error",
                "message": "项目不存在"
            }
        
        full_name = project.full_name
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(f"[{task_id}] 启动异步获取 README: {full_name}")
        
        # 在后台任务中获取 README
        async def fetch_readme_background():
            try:
                readme_content = await github_service.fetch_readme(full_name)
                result = {
                    "task_id": task_id,
                    "status": "success" if readme_content else "empty",
                    "readme": readme_content,
                    "has_readme": readme_content is not None
                }
                # 存储结果
                _async_readme_results[task_id] = result
                logger.info(f"[{task_id}] README 获取完成，状态: {result['status']}")
                return result
            except Exception as e:
                logger.error(f"[{task_id}] 异步获取 README 失败: {e}")
                result = {
                    "task_id": task_id,
                    "status": "error",
                    "message": str(e),
                    "readme": None,
                    "has_readme": False
                }
                _async_readme_results[task_id] = result
                return result
        
        # 启动后台任务
        asyncio.create_task(fetch_readme_background())
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "README 获取中，请稍候..."
        }
        
    except Exception as e:
        logger.error(f"启动异步获取失败: {e}")
        return {
            "task_id": None,
            "status": "error",
            "message": str(e)
        }


@router.get("/readme/result/{task_id}")
async def get_readme_result(task_id: str):
    """
    获取异步 README 获取结果
    """
    try:
        # 从内存中获取结果（如果有）
        result = _async_readme_results.get(task_id)
        
        if result:
            # 清理已完成的任务（保留错误状态稍久一点）
            if result.get("status") in ["success", "empty"]:
                del _async_readme_results[task_id]
            return result
        
        # 检查是否还在处理中
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "正在获取..."
        }
        
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}")
        return {
            "task_id": task_id,
            "status": "error",
            "message": str(e)
        }


@router.get("/{project_name}", response_model=ProjectResponse)
async def get_project(project_name: str):
    """
    获取单个项目详情
    """
    try:
        logger.info(f"获取项目详情: {project_name}")
        
        projects = storage.get_projects()
        for p in projects:
            if p.name == project_name or p.full_name == project_name:
                logger.info(f"找到项目: {p.full_name}")
                return p
        
        logger.warning(f"项目不存在: {project_name}")
        raise HTTPException(status_code=404, detail=f"Project {project_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
