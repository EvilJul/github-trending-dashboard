"""
AI 服务 - 使用大模型增强项目数据
"""

import httpx
import json
from typing import Optional
from models.schemas import ProjectCreate


class AIService:
    """AI 增强服务"""

    def __init__(self, provider: str = "qwen", api_key: str = "", endpoint: str = ""):
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        
        # 配置不同 provider 的端点
        if provider == "qwen":
            self.endpoint = endpoint or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            self.model = "qwen-plus"
        elif provider == "minimax":
            self.endpoint = endpoint or "https://api.minimax.chat/v1"
            self.model = "MiniMax-M2.1"
        elif provider == "openai":
            self.endpoint = endpoint or "https://api.openai.com/v1"
            self.model = "gpt-4"
        elif provider == "anthropic":
            self.endpoint = endpoint or "https://api.anthropic.com/v1"
            self.model = "claude-3-sonnet-20241022"
        else:
            self.endpoint = endpoint or "https://api.example.com/v1"
            self.model = "default"

    async def enhance_project(self, project: ProjectCreate) -> ProjectCreate:
        """使用 AI 增强项目数据"""
        try:
            # 构建 prompt
            prompt = self._build_prompt(project)
            
            # 调用 AI
            response = await self._call_ai(prompt)
            
            if response:
                # 解析 AI 响应
                enhanced = self._parse_response(response, project)
                return enhanced
            
        except Exception as e:
            print(f"AI 增强失败 for {project.full_name}: {e}")
        
        return project

    def _build_prompt(self, project: ProjectCreate) -> str:
        """构建 AI prompt"""
        return f"""
请分析以下 GitHub 项目，生成更丰富的描述和使用指南：

项目名称: {project.full_name}
原描述: {project.description or '暂无描述'}
语言: {project.language}
Stars: {project.stars}
Forks: {project.forks}

请返回 JSON 格式：
{{
    "enhanced_description": "更详细的描述（100-200字）",
    "usage_steps": ["步骤1", "步骤2", "步骤3"],
    "category": "分类"
}}
"""

    async def _call_ai(self, prompt: str) -> Optional[str]:
        """调用 AI API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个开源项目分析助手，请用中文回复。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            response = await client.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"AI API 错误: {response.status_code}")
                return None

    def _parse_response(self, response: str, original: ProjectCreate) -> ProjectCreate:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                
                return ProjectCreate(
                    name=original.name,
                    full_name=original.full_name,
                    url=original.url,
                    fork_url=original.fork_url,
                    issues_url=original.issues_url,
                    description=data.get("enhanced_description", original.description),
                    language=original.language,
                    stars=original.stars,
                    forks=original.forks,
                    issues=original.issues,
                    category=data.get("category", original.category),
                    trend=original.trend,
                    usage_steps=data.get("usage_steps", original.usage_steps)
                )
        except Exception as e:
            print(f"解析 AI 响应失败: {e}")
        
        return original
