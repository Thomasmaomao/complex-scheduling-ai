"""
分析 API 路由
"""

from fastapi import APIRouter
from typing import List, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard():
    """获取分析看板数据"""
    # 模拟数据
    dashboard = {
        "total_quotes": 15680,
        "total_premium": 68500000.00,
        "avg_premium": 4368.50,
        "conversion_rate": 0.32,
        "insurer_distribution": [
            {"insurer_id": "picc", "insurer_name": "人保财险", "count": 5174, "percentage": 33},
            {"insurer_id": "pingan", "insurer_name": "平安产险", "count": 4390, "percentage": 28},
            {"insurer_id": "cpic", "insurer_name": "太平洋产险", "count": 3136, "percentage": 20},
            {"insurer_id": "others", "insurer_name": "其他", "count": 2980, "percentage": 19},
        ],
        "daily_trend": [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
             "quotes": 2200 + i * 50, 
             "premium": 9600000 + i * 200000}
            for i in range(7, -1, -1)
        ],
    }
    return dashboard


@router.get("/strategy/comparison")
async def get_strategy_comparison():
    """获取策略对比数据"""
    comparison = {
        "strategies": [
            {
                "strategy_id": "default_v1",
                "strategy_name": "默认推荐策略",
                "total_tests": 150,
                "pass_rate": 98.5,
                "avg_premium": 4368.50,
                "conversion_rate": 0.32,
            },
            {
                "strategy_id": "price_priority",
                "strategy_name": "价格优先策略",
                "total_tests": 150,
                "pass_rate": 96.2,
                "avg_premium": 4150.00,
                "conversion_rate": 0.35,
            },
            {
                "strategy_id": "service_priority",
                "strategy_name": "服务优先策略",
                "total_tests": 150,
                "pass_rate": 97.8,
                "avg_premium": 4580.00,
                "conversion_rate": 0.30,
            },
        ]
    }
    return comparison


@router.get("/premium/analysis")
async def get_premium_analysis():
    """获取保费分析数据"""
    analysis = {
        "premium_distribution": [
            {"range": "0-3000", "count": 1250, "percentage": 8},
            {"range": "3000-4000", "count": 4680, "percentage": 30},
            {"range": "4000-5000", "count": 6272, "percentage": 40},
            {"range": "5000-6000", "count": 2354, "percentage": 15},
            {"range": "6000+", "count": 1124, "percentage": 7},
        ],
        "region_analysis": [
            {"region": "beijing", "avg_premium": 5240.00, "count": 3125},
            {"region": "shanghai", "avg_premium": 5180.00, "count": 2890},
            {"region": "guangzhou", "avg_premium": 4950.00, "count": 2340},
            {"region": "shenzhen", "avg_premium": 4920.00, "count": 2180},
            {"region": "hangzhou", "avg_premium": 4580.00, "count": 1890},
            {"region": "chengdu", "avg_premium": 4120.00, "count": 3255},
        ],
        "vehicle_type_analysis": [
            {"type": "sedan", "avg_premium": 4200.00, "count": 8920},
            {"type": "suv", "avg_premium": 4680.00, "count": 4560},
            {"type": "mpv", "avg_premium": 5120.00, "count": 1450},
            {"type": "electric", "avg_premium": 4850.00, "count": 750},
        ],
    }
    return analysis


@router.get("/risk/analysis")
async def get_risk_analysis():
    """获取风险分析数据"""
    analysis = {
        "risk_score_distribution": [
            {"range": "0-20", "count": 1568, "percentage": 10, "label": "低风险"},
            {"range": "21-40", "count": 4704, "percentage": 30, "label": "中低风险"},
            {"range": "41-60", "count": 6272, "percentage": 40, "label": "中风险"},
            {"range": "61-80", "count": 2354, "percentage": 15, "label": "中高风险"},
            {"range": "81-100", "count": 782, "percentage": 5, "label": "高风险"},
        ],
        "risk_vs_premium": [
            {"risk_range": "0-20", "avg_premium": 3850.00},
            {"risk_range": "21-40", "avg_premium": 4120.00},
            {"risk_range": "41-60", "avg_premium": 4380.00},
            {"risk_range": "61-80", "avg_premium": 4750.00},
            {"risk_range": "81-100", "avg_premium": 5280.00},
        ],
    }
    return analysis
