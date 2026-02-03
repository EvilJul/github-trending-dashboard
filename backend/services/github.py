"""
GitHub 数据获取服务
"""

import logging
import os
import httpx
import json
import asyncio
import unicodedata
from datetime import datetime, timedelta
from typing import List, Optional
from models.schemas import ProjectCreate

logger = logging.getLogger(__name__)


def safe_str(s: str) -> str:
    """安全字符串处理"""
    if s is None:
        return ""
    cleaned = ''.join(c for c in s if unicodedata.category(c)[0] != 'C' or c in '\n\t')
    return cleaned


class GitHubService:
    """GitHub Trending 数据获取服务"""

    BASE_URL = "https://api.github.com"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Trending-Dashboard/1.0"
    }

    def __init__(self, token: Optional[str] = None):
        if token is None:
            token = self._load_token_from_config()
        
        self.token = token
        if token:
            self.headers = {**self.HEADERS, "Authorization": f"token {token}"}
            logger.info("使用 GitHub Token 认证")
        else:
            self.headers = self.HEADERS
            logger.warning("未配置 GitHub Token，使用公共请求限制")

    def _load_token_from_config(self) -> Optional[str]:
        try:
            # 优先从 config.local.json 加载（不提交到 git）
            local_config = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "config.local.json"
            )
            
            config_file = local_config
            if not os.path.exists(config_file):
                # 回退到 config.json
                config_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "config.json"
                )
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("github", {}).get("token")
        except Exception as e:
            logger.error(f"加载 GitHub Token 失败: {e}")
        return None

    async def fetch_trending_projects(self, days: int = 7, per_page: int = 10) -> List[ProjectCreate]:
        """获取热门项目"""
        all_projects = []
        
        logger.info("获取 GitHub Trending 项目")

        queries = [
            "sort:stars stars:>1000",
        ]

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for i, query in enumerate(queries):
                try:
                    params = {"q": query, "per_page": 50, "sort": "stars"}
                    response = await client.get(
                        f"{self.BASE_URL}/search/repositories",
                        params=params,
                        headers=self.headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])[:30]
                        for item in items:
                            project = self._parse_repository(item)
                            if project:
                                all_projects.append(project)
                        logger.info(f"查询成功，获取 {len(items)} 个项目")
                    elif response.status_code == 403:
                        logger.warning("GitHub API rate limit hit")
                        break
                    else:
                        logger.warning(f"查询失败 ({query}): {response.status_code}")
                    
                    if i < len(queries) - 1:
                        await asyncio.sleep(1.0)
                        
                except Exception as e:
                    logger.error(f"获取项目失败: {e}")
                    continue

        unique_projects = self._deduplicate(all_projects)
        sorted_projects = sorted(unique_projects, key=lambda x: x.stars, reverse=True)
        
        logger.info(f"共获取 {len(sorted_projects)} 个项目")
        return sorted_projects[:30]

    def _parse_repository(self, repo: dict) -> Optional[ProjectCreate]:
        try:
            name = repo.get("full_name", "")
            if not name:
                return None

            description = safe_str(repo.get("description") or "暂无描述")

            return ProjectCreate(
                name=name.split("/")[-1],
                full_name=name,
                url=repo.get("html_url", ""),
                fork_url=f"{repo.get('html_url', '')}/fork",
                issues_url=f"{repo.get('html_url', '')}/issues",
                description=description,
                language=repo.get("language") or "Other",
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                issues=repo.get("open_issues_count", 0),
                category=self._categorize(repo),
                trend=self._calculate_trend(repo),
                usage_steps=self._generate_usage_steps(name, repo)
            )
        except Exception as e:
            logger.error(f"解析仓库失败: {e}")
            return None

    def _categorize(self, repo: dict) -> str:
        topics = repo.get("topics", []) or []
        description = (repo.get("description", "") or "").lower()
        name = (repo.get("name", "") or "").lower()
        language = repo.get("language", "") or ""

        ai_keywords = ["ai", "ml", "deep-learning", "neural", "llm", "gpt", "transformer"]
        if any(kw in topics for kw in ai_keywords) or any(kw in description for kw in ai_keywords):
            return "AI/机器学习"

        ds_keywords = ["data-science", "data-analysis", "analytics", "statistics", "pandas"]
        if any(kw in topics for kw in ds_keywords) or any(kw in description for kw in ds_keywords):
            return "数据分析"

        web_keywords = ["web", "frontend", "backend", "http", "api", "server"]
        if any(kw in topics for kw in web_keywords) or any(kw in description for kw in web_keywords):
            return "Web开发"

        mobile_keywords = ["mobile", "android", "ios", "app"]
        if any(kw in topics for kw in mobile_keywords) or any(kw in description for kw in mobile_keywords):
            return "移动开发"

        devops_keywords = ["devops", "docker", "kubernetes", "ci-cd", "deployment"]
        if any(kw in topics for kw in devops_keywords) or any(kw in description for kw in devops_keywords):
            return "DevOps"

        if language == "Python":
            return "Python生态"
        elif language == "Java":
            return "Java生态"
        elif language == "JavaScript" or language == "TypeScript":
            return "前端技术"
        elif language == "Go":
            return "Go生态"

        return "通用工具"

    def _calculate_trend(self, repo: dict) -> str:
        stars = repo.get("stargazers_count", 0)
        recent_stars = repo.get("stargazers_since_last_analytic", 0)

        if recent_stars > 1000:
            return "rising"
        elif recent_stars < 100:
            return "falling"
        else:
            return "stable"

    def _generate_usage_steps(self, full_name: str, repo: dict) -> List[str]:
        steps = [
            f"克隆项目: git clone https://github.com/{full_name}",
            "进入项目目录"
        ]

        language = repo.get("language", "") or ""

        if language == "Python":
            steps.extend([
                "创建虚拟环境: python -m venv venv",
                "安装依赖: pip install -r requirements.txt",
                "运行项目: python main.py"
            ])
        elif language == "Java":
            steps.extend([
                "使用 Maven 构建: mvn clean install",
                "运行项目: java -jar target/*.jar"
            ])
        elif language == "JavaScript" or language == "TypeScript":
            steps.extend([
                "安装依赖: npm install",
                "运行开发服务器: npm run dev"
            ])
        elif language == "Go":
            steps.extend([
                "下载依赖: go mod download",
                "运行项目: go run main.go"
            ])
        else:
            steps.extend([
                "按照 README.md 说明安装依赖",
                "启动项目"
            ])

        return steps

    def _deduplicate(self, projects: List[ProjectCreate]) -> List[ProjectCreate]:
        seen = set()
        unique = []
        for p in projects:
            if p.full_name not in seen:
                seen.add(p.full_name)
                unique.append(p)
        return unique

    async def fetch_readme(self, full_name: str) -> Optional[str]:
        """
        获取项目 README 内容 - 尝试多种方法
        """
        logger.info(f"获取 README: {full_name}")
        
        # 移除可能的前缀
        if full_name.startswith('github.com/'):
            full_name = full_name.replace('github.com/', '')
        
        if full_name.startswith('http://github.com/'):
            full_name = full_name.replace('http://github.com/', '')
        if full_name.startswith('https://github.com/'):
            full_name = full_name.replace('https://github.com/', '')
        
        parts = full_name.split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1]
        else:
            logger.error(f"无效的仓库名称: {full_name}")
            return None
        
        # 尝试方法1: 使用 GitHub API 获取 README
        readme_content = await self._fetch_readme_api(owner, repo)
        if readme_content:
            return readme_content
        
        # 尝试方法2: 直接获取默认分支的内容
        readme_content = await self._fetch_readme_content(owner, repo)
        if readme_content:
            return readme_content
        
        logger.warning(f"无法获取 README: {full_name}")
        return None

    async def _fetch_readme_api(self, owner: str, repo: str) -> Optional[str]:
        """方法1: 使用 GitHub READMEs API"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # 先获取仓库信息，找到默认分支
                repo_url = f"{self.BASE_URL}/repos/{owner}/{repo}"
                repo_response = await client.get(repo_url, headers=self.headers)
                
                if repo_response.status_code == 200:
                    repo_info = repo_response.json()
                    default_branch = repo_info.get("default_branch", "main")
                    
                    # 使用 readme API
                    readme_url = f"{self.BASE_URL}/repos/{owner}/{repo}/readme"
                    readme_headers = {
                        **self.headers,
                        "Accept": "application/vnd.github.raw"
                    }
                    
                    readme_response = await client.get(
                        readme_url,
                        headers=readme_headers
                    )
                    
                    if readme_response.status_code == 200:
                        content = readme_response.content.decode('utf-8', errors='ignore')
                        logger.info(f"README API 获取成功: {owner}/{repo}")
                        return content
                    else:
                        logger.debug(f"README API 返回: {readme_response.status_code}")
                        
        except Exception as e:
            logger.debug(f"README API 方法失败: {e}")
        
        return None

    async def _fetch_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """方法2: 直接获取 README.md 文件内容"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # 获取仓库信息
                repo_url = f"{self.BASE_URL}/repos/{owner}/{repo}"
                repo_response = await client.get(repo_url, headers=self.headers)
                
                if repo_response.status_code != 200:
                    return None
                
                repo_info = repo_response.json()
                default_branch = repo_info.get("default_branch", "main")
                
                # 尝试多个 README 文件名
                readme_names = ["README.md", "readme.md", "README.rst", "README.txt", "README", "readme"]
                
                for readme_name in readme_names:
                    try:
                        content_url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{readme_name}"
                        content_headers = {
                            **self.headers,
                            "Accept": "application/vnd.github.raw"
                        }
                        
                        content_response = await client.get(
                            content_url,
                            params={"ref": default_branch},
                            headers=content_headers
                        )
                        
                        if content_response.status_code == 200:
                            content = content_response.content.decode('utf-8', errors='ignore')
                            logger.info(f"通过内容 API 获取 README 成功: {readme_name}")
                            return content
                            
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.debug(f"内容 API 方法失败: {e}")
        
        return None
