"""
配置管理 API 路由
"""

import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/config", tags=["config"])

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
CONFIG_DIR = os.path.dirname(CONFIG_FILE)


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
    has_api_key: bool  # 只返回是否配置，不返回实际 key


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


def save_config(config: dict) -> None:
    """保存配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # 保留非 ai 字段
    current_config = load_config()
    current_config.update(config)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_config, f, ensure_ascii=False, indent=2)


@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config():
    """
    获取 AI 配置（不返回 api_key）
    """
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
    """
    测试 AI 配置是否有效
    """
    from services.ai import AIService
    
    try:
        # 创建 AI 服务
        ai_service = AIService(
            provider=config.provider,
            api_key=config.api_key,
            endpoint=config.endpoint
        )
        
        # 简单测试：调用模型获取响应
        test_prompt = "你好，请回复 '测试成功'"
        
        response = await ai_service._call_ai(test_prompt)
        
        if response:
            return {
                "success": True,
                "message": "API 配置测试成功！",
                "provider": config.provider,
                "model": config.model or ai_service.model
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
    """
    保存 AI 配置（持久化）
    如果 api_key 为空，保留原有配置
    """
    try:
        # 如果没有提供 api_key，保留原有的
        if not config.api_key:
            current_config = load_config()
            existing_ai = current_config.get("ai", {})
            config.api_key = existing_ai.get("api_key", "")
            
            # 如果还是没有，说明没有配置过
            if not config.api_key:
                raise HTTPException(status_code=400, detail="API Key 不能为空")
        
        # 确定模型
        from services.ai import AIService
        ai_service = AIService(
            provider=config.provider,
            api_key=config.api_key,
            endpoint=config.endpoint
        )
        
        model = config.model or ai_service.model
        
        # 保存配置
        save_config({
            "ai": {
                "provider": config.provider,
                "model": model,
                "endpoint": config.endpoint,
                "api_key": config.api_key  # 持久化保存
            }
        })
        
        return {
            "success": True,
            "message": "配置已保存",
            "provider": config.provider,
            "model": model,
            "api_key": config.api_key  # 返回给前端缓存
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ai")
async def delete_ai_config():
    """
    删除 AI 配置
    """
    config = load_config()
    if "ai" in config:
        del config["ai"]
        save_config(config)
    
    return {"success": True, "message": "配置已删除"}
