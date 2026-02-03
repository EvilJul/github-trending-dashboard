"""
数据存储服务
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from models.schemas import ProjectCreate, HistoryRecord


class StorageService:
    """数据存储服务"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.projects_file = os.path.join(data_dir, "projects.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def save_projects(self, projects: List[ProjectCreate]) -> dict:
        """保存项目数据"""
        data = {
            "last_updated": datetime.utcnow().isoformat(),
            "projects": [p.model_dump() for p in projects],
            "total_projects": len(projects)
        }

        with open(self.projects_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    def load_projects(self) -> dict:
        """加载项目数据"""
        if not os.path.exists(self.projects_file):
            return self._get_default_data()

        try:
            with open(self.projects_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading projects: {e}")
            return self._get_default_data()

    def get_projects(self) -> List[ProjectCreate]:
        """获取项目列表"""
        data = self.load_projects()
        projects = []
        for item in data.get("projects", []):
            projects.append(ProjectCreate(**item))
        return projects

    def save_history(self, records: List[HistoryRecord]) -> None:
        """保存历史记录"""
        data = {"history": [r.model_dump() for r in records]}

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_history(self) -> List[HistoryRecord]:
        """加载历史记录"""
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [HistoryRecord(**item) for item in data.get("history", [])]
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def add_history_record(self, record: HistoryRecord) -> None:
        """添加历史记录"""
        history = self.load_history()

        # 检查是否已存在该周的记录
        existing = [i for i, h in enumerate(history) if h.id == record.id]
        for i in existing:
            history.pop(i)

        # 添加新记录到开头
        history.insert(0, record)

        # 只保留最近12周
        history = history[:12]

        self.save_history(history)

    def get_last_updated(self) -> Optional[datetime]:
        """获取最后更新时间"""
        data = self.load_projects()
        last_updated = data.get("last_updated")
        if last_updated:
            return datetime.fromisoformat(last_updated)
        return None

    def _get_default_data(self) -> dict:
        """获取默认数据"""
        return {
            "last_updated": datetime.utcnow().isoformat(),
            "projects": [],
            "total_projects": 0
        }
