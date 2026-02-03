"""
配置管理 API 路由
"""

import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/config", tags=["config"])

# 配置文件路径（项目根目录的 config.json）
CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
)


class AIConfig(BaseModel):
    """AI 配置"""
    provider: str = "qwen"
    model: str = ""
    endpoint: str = ""
    api_key: str = ""


class AIConfigResponse(BaseModel):
    """AI 配置响应"""
    provider: str
    model: str
    endpoint: str
    has_api_key: bool


class GitHubConfig(BaseModel):
    """GitHub 配置"""
    token: str = ""


class GitHubConfigResponse(BaseModel):
    """GitHub 配置响应"""
    has_token: bool


def load_config() -> dict:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败: {e}")
        return {}


def save_config(new_config: dict) -> None:
    """保存配置（深度合并，保留所有字段）"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    # 加载现有配置
    current_config = load_config()
    
    # 深度合并配置
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    merged_config = deep_merge(current_config, new_config)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_config, f, ensure_ascii=False, indent=2)


@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config():
    """获取 AI 配置（不返回 api_key）"""
    config = load_config()
    ai_config = config.get("ai", {})
    
    return AIConfigResponse(
        provider=ai_config.get("provider", "qwen"),
        model=ai_config.get("model", ""),
        endpoint=ai_config.get("endpoint", ""),
        has_api_key=bool(ai_config.get("api_key", ""))
    )


@router.post("/ai/test")
async def test_ai_config(config: AIConfig):
    """测试 AI 配置是否有效"""
    from services.ai import AIService
    
    try:
        # 创建 AI 服务
        ai_service = AIService(
            provider=config.provider,
            model=config.model,
            api_key=config.api_key,
            endpoint=config.endpoint
        )
        
        # 确定使用的模型
        used_model = config.model if config.model else ai_service.model
        
        # 测试调用
        test_prompt = "你好，请回复 '测试成功'"
        
        response = await ai_service._call_ai(test_prompt)
        
        if response:
            return {
                "success": True,
                "message": "API 配置测试成功！",
                "provider": config.provider,
                "model": used_model
            }
        else:
            return {
                "success": False,
                "message": "API 调用失败，请检查配置"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


@router.post("/ai/save")
async def save_ai_config(config: AIConfig):
    """保存 AI 配置（自动合并，保留其他配置）"""
    try:
        # 如果没有提供 api_key，保留原有的
        if not config.api_key:
            current_config = load_config()
            existing_ai = current_config.get("ai", {})
            config.api_key = existing_ai.get("api_key", "")
            
            if not config.api_key:
                raise HTTPException(status_code=400, detail="API Key 不能为空")
        
        # 确定模型
        from services.ai import AIService
        ai_service = AIService(
            provider=config.provider,
            model=config.model,
            api_key=config.api_key,
            endpoint=config.endpoint
        )
        
        model = config.model if config.model else ai_service.model
        
        # 深度合并保存（保留 project 等其他配置）
        save_config({
            "ai": {
                "provider": config.provider,
                "model": model,
                "endpoint": config.endpoint,
                "api_key": config.api_key
            }
        })
        
        return {
            "success": True,
            "message": "配置已保存",
            "provider": config.provider,
            "model": model,
            "api_key": config.api_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ai")
async def delete_ai_config():
    """删除 AI 配置"""
    config = load_config()
    if "ai" in config:
        del config["ai"]
        save_config(config)
    
    return {"success": True, "message": "配置已删除"}


# ==================== GitHub Token 配置 ====================

@router.get("/github", response_model=GitHubConfigResponse)
async def get_github_config():
    """获取 GitHub Token 配置（不返回实际 token）"""
    config = load_config()
    github_config = config.get("github", {})
    
    return GitHubConfigResponse(
        has_token=bool(github_config.get("token", ""))
    )


@router.post("/github/save")
async def save_github_config(config: GitHubConfig):
    """保存 GitHub Token（自动合并，保留其他配置）"""
    try:
        current_config = load_config()
        
        if config.token:
            # 保存 token（深度合并，保留其他配置）
            if "github" not in current_config:
                current_config["github"] = {}
            current_config["github"]["token"] = config.token
            save_config(current_config)
        else:
            # 删除 token
            if "github" in current_config:
                del current_config["github"]
                save_config(current_config)
        
        return {
            "success": True,
            "message": "GitHub 配置已保存",
            "has_token": bool(config.token)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/github")
async def delete_github_config():
    """删除 GitHub Token 配置"""
    config = load_config()
    if "github" in config:
        del config["github"]
        save_config(config)
    
    return {"success": True, "message": "GitHub 配置已删除"}
