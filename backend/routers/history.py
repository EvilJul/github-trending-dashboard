"""
历史记录 API 路由
"""

from fastapi import APIRouter, HTTPException
from models.schemas import HistoryResponse, HistoryRecord
from services.storage import StorageService

router = APIRouter(prefix="/api/history", tags=["history"])

# 初始化服务
storage = StorageService()


@router.get("/", response_model=HistoryResponse)
async def get_history():
    """
    获取所有历史记录
    """
    try:
        history = storage.load_history()
        return HistoryResponse(history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{record_id}", response_model=HistoryRecord)
async def get_history_record(record_id: str):
    """
    获取单条历史记录
    """
    try:
        history = storage.load_history()
        for record in history:
            if record.id == record_id:
                return record
        raise HTTPException(status_code=404, detail=f"History record {record_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{record_id}")
async def delete_history_record(record_id: str):
    """
    删除历史记录
    """
    try:
        history = storage.load_history()
        new_history = [h for h in history if h.id != record_id]

        if len(new_history) == len(history):
            raise HTTPException(status_code=404, detail=f"Record {record_id} not found")

        storage.save_history(new_history)
        return {"message": f"Record {record_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
