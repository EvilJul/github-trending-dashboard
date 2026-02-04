"""
数据模型定义
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProjectBase(BaseModel):
    """项目基础信息"""
    name: str
    full_name: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    issues: int = 0


class ProjectCreate(ProjectBase):
    """创建项目"""
    fork_url: Optional[str] = None
    issues_url: Optional[str] = None
    category: Optional[str] = None
    trend: str = "stable"
    usage_steps: List[str] = []


class ProjectResponse(ProjectBase):
    """项目响应"""
    fork_url: Optional[str] = None
    issues_url: Optional[str] = None
    category: Optional[str] = None
    trend: str = "stable"
    usage_steps: List[str] = []

    class Config:
        from_attributes = True


class ProjectsResponse(BaseModel):
    """项目列表响应"""
    last_updated: Optional[str] = None  # 改为字符串，避免 datetime 解析问题
    projects: List[ProjectResponse]
    total_count: int


class HistoryRecord(BaseModel):
    """历史记录"""
    id: str
    week: str
    date: str
    total_projects: int
    projects: List  # 可以是字符串列表（项目名）或对象列表（完整项目详情）


class HistoryResponse(BaseModel):
    """历史记录响应"""
    history: List[HistoryRecord]


class RefreshResponse(BaseModel):
    """刷新响应"""
    success: bool
    message: str
    last_updated: Optional[str] = None
    projects_count: int


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
