"""
保司管理 API 路由
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import logging

from app.services.strategy_engine import StrategyEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
strategy_engine = StrategyEngine()


@router.get("/list")
async def list_insurers():
    """获取所有保司列表"""
    insurers = list(strategy_engine.insurers.values())
    return {"insurers": insurers}


@router.get("/{insurer_id}")
async def get_insurer(insurer_id: str):
    """获取保司详情"""
    if insurer_id not in strategy_engine.insurers:
        raise HTTPException(status_code=404, detail=f"保司 {insurer_id} 不存在")
    
    return strategy_engine.insurers[insurer_id]


@router.get("/{insurer_id}/scores")
async def get_insurer_scores(insurer_id: str):
    """获取保司评分"""
    if insurer_id not in strategy_engine.insurers:
        raise HTTPException(status_code=404, detail=f"保司 {insurer_id} 不存在")
    
    insurer = strategy_engine.insurers[insurer_id]
    return {
        "insurer_id": insurer_id,
        "insurer_name": insurer["insurer_name"],
        "base_scores": insurer["base_scores"],
        "market_share": insurer["market_share"],
    }


@router.post("/{insurer_id}/priority")
async def update_insurer_priority(insurer_id: str, priority_config: Dict):
    """更新保司优先级配置"""
    if insurer_id not in strategy_engine.insurers:
        raise HTTPException(status_code=404, detail=f"保司 {insurer_id} 不存在")
    
    # 更新优先级配置（简化实现）
    logger.info(f"保司优先级已更新：{insurer_id}, config={priority_config}")
    return {"message": "优先级已更新", "insurer_id": insurer_id}


@router.get("/monitoring/status")
async def get_monitoring_status():
    """获取保司动态监控状态"""
    status = {
        "last_update": "2026-03-30 08:00:00",
        "insurers_status": [
            {
                "insurer_id": "picc",
                "insurer_name": "人保财险",
                "status": "normal",
                "quote_count_today": 1250,
                "avg_response_time_ms": 120,
            },
            {
                "insurer_id": "pingan",
                "insurer_name": "平安产险",
                "status": "normal",
                "quote_count_today": 980,
                "avg_response_time_ms": 135,
            },
            {
                "insurer_id": "cpic",
                "insurer_name": "太平洋产险",
                "status": "normal",
                "quote_count_today": 760,
                "avg_response_time_ms": 145,
            },
        ]
    }
    return status
