"""
策略效果分析 API

提供策略效果看板、对比分析、图表数据等功能
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/effect/dashboard")
async def get_effect_dashboard():
    """获取策略效果看板"""
    dashboard = {
        "overview": {
            "total_strategies": 5,
            "active_strategies": 3,
            "total_tests": 1580,
            "avg_pass_rate": 97.5,
            "total_quotes": 15680,
            "conversion_rate": 32.5,
        },
        "strategy_performance": [
            {
                "strategy_id": "default_v1",
                "strategy_name": "默认推荐策略",
                "test_count": 580,
                "pass_rate": 98.5,
                "avg_premium": 4368.50,
                "conversion_rate": 32.0,
                "last_updated": "2026-03-30 08:00:00",
            },
            {
                "strategy_id": "price_priority",
                "strategy_name": "价格优先策略",
                "test_count": 450,
                "pass_rate": 96.2,
                "avg_premium": 4150.00,
                "conversion_rate": 35.0,
                "last_updated": "2026-03-29 18:00:00",
            },
            {
                "strategy_id": "service_priority",
                "strategy_name": "服务优先策略",
                "test_count": 320,
                "pass_rate": 97.8,
                "avg_premium": 4580.00,
                "conversion_rate": 30.0,
                "last_updated": "2026-03-29 15:00:00",
            },
        ],
        "trend": {
            "daily_tests": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "tests": 200 + i * 10,
                 "pass_rate": 97 + i * 0.2}
                for i in range(7, -1, -1)
            ],
        },
    }
    return dashboard


@router.get("/effect/comparison")
async def get_strategy_comparison():
    """获取策略对比数据"""
    comparison = {
        "strategies": [
            {
                "strategy_id": "default_v1",
                "strategy_name": "默认推荐策略",
                "metrics": {
                    "test_count": 580,
                    "pass_rate": 98.5,
                    "avg_premium": 4368.50,
                    "conversion_rate": 32.0,
                    "avg_score": 89.5,
                    "customer_satisfaction": 4.5,
                },
            },
            {
                "strategy_id": "price_priority",
                "strategy_name": "价格优先策略",
                "metrics": {
                    "test_count": 450,
                    "pass_rate": 96.2,
                    "avg_premium": 4150.00,
                    "conversion_rate": 35.0,
                    "avg_score": 85.2,
                    "customer_satisfaction": 4.3,
                },
            },
            {
                "strategy_id": "service_priority",
                "strategy_name": "服务优先策略",
                "metrics": {
                    "test_count": 320,
                    "pass_rate": 97.8,
                    "avg_premium": 4580.00,
                    "conversion_rate": 30.0,
                    "avg_score": 92.1,
                    "customer_satisfaction": 4.7,
                },
            },
        ],
        "comparison_dimensions": [
            {"name": "测试通过率", "unit": "%", "better": "higher"},
            {"name": "平均保费", "unit": "元", "better": "lower"},
            {"name": "转化率", "unit": "%", "better": "higher"},
            {"name": "平均评分", "unit": "分", "better": "higher"},
            {"name": "客户满意度", "unit": "分", "better": "higher"},
        ],
    }
    return comparison


@router.get("/effect/charts")
async def get_effect_charts(chart_type: str = "all"):
    """获取策略效果图表数据"""
    charts = {}
    
    if chart_type in ["all", "premium_distribution"]:
        # 保费分布图
        charts["premium_distribution"] = {
            "title": "保费分布图",
            "type": "histogram",
            "data": [
                {"range": "0-3000", "count": 1250, "percentage": 8},
                {"range": "3000-4000", "count": 4680, "percentage": 30},
                {"range": "4000-5000", "count": 6272, "percentage": 40},
                {"range": "5000-6000", "count": 2354, "percentage": 15},
                {"range": "6000+", "count": 1124, "percentage": 7},
            ],
        }
    
    if chart_type in ["all", "conversion_trend"]:
        # 转化率趋势图
        charts["conversion_trend"] = {
            "title": "转化率趋势图",
            "type": "line",
            "data": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                 "conversion_rate": 30 + i * 0.5}
                for i in range(30, -1, -1)
            ],
        }
    
    if chart_type in ["all", "strategy_radar"]:
        # 策略雷达图
        charts["strategy_radar"] = {
            "title": "策略对比雷达图",
            "type": "radar",
            "dimensions": ["通过率", "保费优势", "转化率", "满意度", "稳定性"],
            "strategies": [
                {
                    "name": "默认推荐策略",
                    "data": [98.5, 85, 80, 90, 95],
                },
                {
                    "name": "价格优先策略",
                    "data": [96.2, 95, 88, 86, 90],
                },
                {
                    "name": "服务优先策略",
                    "data": [97.8, 75, 75, 94, 92],
                },
            ],
        }
    
    if chart_type in ["all", "region_heatmap"]:
        # 地区热力图
        charts["region_heatmap"] = {
            "title": "地区保费热力图",
            "type": "heatmap",
            "data": [
                {"region": "beijing", "avg_premium": 5240.00, "quote_count": 3125},
                {"region": "shanghai", "avg_premium": 5180.00, "quote_count": 2890},
                {"region": "guangzhou", "avg_premium": 4950.00, "quote_count": 2340},
                {"region": "shenzhen", "avg_premium": 4920.00, "quote_count": 2180},
                {"region": "hangzhou", "avg_premium": 4580.00, "quote_count": 1890},
                {"region": "chengdu", "avg_premium": 4120.00, "quote_count": 3255},
            ],
        }
    
    return charts


@router.get("/effect/customer-value")
async def get_customer_value_analysis():
    """获取客户价值分析"""
    analysis = {
        "distribution": {
            "high": {"count": 1568, "percentage": 10},
            "medium": {"count": 7840, "percentage": 50},
            "low": {"count": 6272, "percentage": 40},
        },
        "value_metrics": {
            "high": {
                "avg_premium": 6580.00,
                "conversion_rate": 55.0,
                "retention_rate": 92.0,
                "satisfaction": 4.8,
            },
            "medium": {
                "avg_premium": 4368.00,
                "conversion_rate": 32.0,
                "retention_rate": 78.0,
                "satisfaction": 4.3,
            },
            "low": {
                "avg_premium": 2850.00,
                "conversion_rate": 18.0,
                "retention_rate": 65.0,
                "satisfaction": 3.9,
            },
        },
        "suggestions": {
            "high": "提供 VIP 服务和专属优惠，加强关系维护",
            "medium": "提供适度优惠和增值服务，提升满意度",
            "low": "加强风险教育，提供基础保障方案",
        },
    }
    return analysis


@router.get("/effect/risk-analysis")
async def get_risk_analysis():
    """获取风险分析"""
    analysis = {
        "risk_score_distribution": [
            {"range": "0-20", "count": 1568, "percentage": 10, "label": "低风险"},
            {"range": "21-40", "count": 4704, "percentage": 30, "label": "中低风险"},
            {"range": "41-60", "count": 6272, "percentage": 40, "label": "中风险"},
            {"range": "61-80", "count": 2354, "percentage": 15, "label": "中高风险"},
            {"range": "81-100", "count": 782, "percentage": 5, "label": "高风险"},
        ],
        "risk_vs_premium": [
            {"risk_range": "0-20", "avg_premium": 3850.00, "quote_count": 1568},
            {"risk_range": "21-40", "avg_premium": 4120.00, "quote_count": 4704},
            {"risk_range": "41-60", "avg_premium": 4380.00, "quote_count": 6272},
            {"risk_range": "61-80", "avg_premium": 4750.00, "quote_count": 2354},
            {"risk_range": "81-100", "avg_premium": 5280.00, "quote_count": 782},
        ],
        "risk_factors": [
            {"factor": "车辆价值", "impact": 0.25, "description": "高价值车辆风险更高"},
            {"factor": "地区", "impact": 0.20, "description": "一线城市风险系数高"},
            {"factor": "年龄", "impact": 0.15, "description": "年轻和年老驾驶员风险高"},
            {"factor": "历史出险", "impact": 0.25, "description": "出险记录影响显著"},
            {"factor": "交通违法", "impact": 0.15, "description": "违法次数多风险高"},
        ],
    }
    return analysis
