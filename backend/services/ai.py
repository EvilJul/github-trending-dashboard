"""
AI 服务 - 使用大模型增强项目数据
"""

import httpx
import json
import logging
from typing import Optional
from models.schemas import ProjectCreate

logger = logging.getLogger(__name__)


class AIService:
    """AI 增强服务"""

    def __init__(self, provider: str = "qwen", model: str = "", api_key: str = "", endpoint: str = ""):
        self.provider = provider
        self.api_key = api_key
        
        # 配置不同 provider 的默认端点和模型
        provider_configs = {
            "qwen": {
                "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "default_model": "qwen-plus"
            },
            "minimax": {
                "endpoint": "https://api.minimax.chat/v1",
                "default_model": "MiniMax-M2.1"
            },
            "openai": {
                "endpoint": "https://api.openai.com/v1",
                "default_model": "gpt-4"
            },
            "anthropic": {
                "endpoint": "https://api.anthropic.com/v1",
                "default_model": "claude-3-sonnet-20241022"
            },
            "siliconflow": {
                "endpoint": "https://api.siliconflow.cn/v1",
                "default_model": "deepseek-ai/DeepSeek-V2.5"
            }
        }
        
        if provider in provider_configs:
            config = provider_configs[provider]
            self.endpoint = endpoint or config["endpoint"]
            self.model = model or config["default_model"]
        else:
            self.endpoint = endpoint or ""
            self.model = model or "default"

    async def enhance_project(self, project: ProjectCreate) -> ProjectCreate:
        """使用 AI 增强项目数据"""
        try:
            prompt = self._build_prompt(project)
            response = await self._call_ai(prompt)
            
            if response:
                enhanced = self._parse_response(response, project)
                return enhanced
            
        except Exception as e:
            logger.error(f"AI 增强失败 for {project.full_name}: {e}")
        
        return project

    def _build_prompt(self, project: ProjectCreate) -> str:
        """构建 AI prompt"""
        return '''Please analyze this GitHub project and generate enhanced description in Chinese:

Project: {name}
Description: {desc}
Language: {lang}
Stars: {stars}

Return JSON format:
{{"enhanced_description": "...", "usage_steps": ["step1", "step2"], "category": "..."}}
'''.format(
            name=project.full_name,
            desc=project.description or '暂无描述',
            lang=project.language,
            stars=project.stars
        )

    async def _call_ai(self, prompt: str) -> Optional[str]:
        """调用 AI API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # 使用纯 ASCII 或确保 UTF-8
                data = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Reply in Chinese."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                url = f"{self.endpoint}/chat/completions"
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    # 确保返回的是 UTF-8 字符串
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    return content
                else:
                    logger.error(f"AI API 错误: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"AI 调用异常: {e}")
            return None

    def _parse_response(self, response: str, original: ProjectCreate) -> ProjectCreate:
        """解析 AI 响应"""
        try:
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
            logger.error(f"解析 AI 响应失败: {e}")
        
        return original
