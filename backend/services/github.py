"""
GitHub 数据获取服务
"""

import httpx
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from models.schemas import ProjectCreate


class GitHubService:
    """GitHub Trending 数据获取服务"""

    BASE_URL = "https://api.github.com"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Trending-Dashboard/1.0"
    }

    def __init__(self, token: Optional[str] = None):
        # 如果没有提供 token，尝试从配置文件读取
        if token is None:
            token = self._load_token_from_config()
        
        self.token = token
        if token:
            self.headers = {**self.HEADERS, "Authorization": f"token {token}"}
        else:
            self.headers = self.HEADERS

    def _load_token_from_config(self) -> Optional[str]:
        """从配置文件加载 GitHub Token"""
        try:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "config.json"
            )
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("github", {}).get("token")
        except Exception as e:
            print(f"加载 GitHub Token 失败: {e}")
        return None

    async def _rate_limit_wait(self, client: httpx.AsyncClient) -> None:
        """处理速率限制"""
        # 简单处理：每次请求后等待 500ms
        await asyncio.sleep(0.5)

    async def fetch_trending_projects(self, days: int = 7, per_page: int = 10) -> List[ProjectCreate]:
        """获取热门项目"""
        all_projects = []

        # 计算日期
        date_since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 查询策略：减少 API 调用次数，每个请求获取更多结果
        queries = [
            # 综合热门 - 一次性获取足够多的项目
            f"created:>{date_since} sort:stars",
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, query in enumerate(queries):
                try:
                    params = {"q": query, "per_page": 30}  # 每次获取更多项目
                    response = await client.get(
                        f"{self.BASE_URL}/search/repositories",
                        params=params,
                        headers=self.headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("items", [])[:20]:  # 取前20个
                            project = self._parse_repository(item)
                            if project:
                                all_projects.append(project)
                    elif response.status_code == 403:
                        print("GitHub API rate limit hit, using cached data")
                        break
                    else:
                        print(f"Query failed ({query}): {response.status_code}")
                    
                    # 避免触发速率限制
                    if i < len(queries) - 1:
                        await asyncio.sleep(1.0)
                        
                except Exception as e:
                    print(f"Error fetching query {query}: {e}")
                    continue

        # 去重并排序
        unique_projects = self._deduplicate(all_projects)
        sorted_projects = sorted(unique_projects, key=lambda x: x.stars, reverse=True)

        return sorted_projects[:20]  # 返回前20个

    def _parse_repository(self, repo: dict) -> Optional[ProjectCreate]:
        """解析 GitHub 仓库数据"""
        try:
            name = repo.get("full_name", "")
            if not name:
                return None

            return ProjectCreate(
                name=name.split("/")[-1],
                full_name=name,
                url=repo.get("html_url", ""),
                fork_url=f"{repo.get('html_url', '')}/fork",
                issues_url=f"{repo.get('html_url', '')}/issues",
                description=repo.get("description") or "暂无描述",
                language=repo.get("language") or "Other",
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                issues=repo.get("open_issues_count", 0),
                category=self._categorize(repo),
                trend=self._calculate_trend(repo),
                usage_steps=self._generate_usage_steps(name, repo)
            )
        except Exception as e:
            print(f"Error parsing repository: {e}")
            return None

    def _categorize(self, repo: dict) -> str:
        """分类项目"""
        topics = repo.get("topics", []) or []
        description = (repo.get("description", "") or "").lower()
        name = (repo.get("name", "") or "").lower()
        language = repo.get("language", "") or ""

        # AI/机器学习
        ai_keywords = ["ai", "ml", "deep-learning", "neural", "llm", "gpt", "transformer"]
        if any(kw in topics for kw in ai_keywords) or \
           any(kw in description for kw in ai_keywords):
            return "AI/机器学习"

        # 数据科学
        ds_keywords = ["data-science", "data-analysis", "analytics", "statistics", "pandas"]
        if any(kw in topics for kw in ds_keywords) or \
           any(kw in description for kw in ds_keywords) or \
           any(kw in name for kw in ds_keywords):
            return "数据分析"

        # Web开发
        web_keywords = ["web", "frontend", "backend", "http", "api", "server"]
        if any(kw in topics for kw in web_keywords) or \
           any(kw in description for kw in web_keywords):
            return "Web开发"

        # 移动开发
        mobile_keywords = ["mobile", "android", "ios", "app"]
        if any(kw in topics for kw in mobile_keywords) or \
           any(kw in description for kw in mobile_keywords):
            return "移动开发"

        # DevOps
        devops_keywords = ["devops", "docker", "kubernetes", "ci-cd", "deployment"]
        if any(kw in topics for kw in devops_keywords) or \
           any(kw in description for kw in devops_keywords):
            return "DevOps"

        # 按语言分类
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
        """计算趋势"""
        stars = repo.get("stargazers_count", 0)
        recent_stars = repo.get("stargazers_since_last_analytic", 0)

        if recent_stars > 1000:
            return "rising"
        elif recent_stars < 100:
            return "falling"
        else:
            return "stable"

    def _generate_usage_steps(self, full_name: str, repo: dict) -> List[str]:
        """生成使用步骤"""
        steps = [
            f"克隆项目: git clone https://github.com/{full_name}",
            "进入项目目录"
        ]

        language = repo.get("language", "") or ""

        # 根据语言添加特定步骤
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
        """去重"""
        seen = set()
        unique = []
        for p in projects:
            if p.full_name not in seen:
                seen.add(p.full_name)
                unique.append(p)
        return unique

    async def fetch_readme(self, full_name: str) -> Optional[str]:
        """获取项目 README 内容"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # README API 需要正确的 Accept header
                readme_headers = {
                    **self.headers,
                    "Accept": "application/vnd.github.raw"
                }
                
                response = await client.get(
                    f"{self.BASE_URL}/repos/{full_name}/readme",
                    headers=readme_headers
                )
                
                if response.status_code == 200:
                    # 直接返回原始内容
                    return response.text
                elif response.status_code == 404:
                    print(f"README not found for {full_name}")
                    return None
                else:
                    print(f"Failed to fetch README for {full_name}: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error fetching README for {full_name}: {e}")
                return None
