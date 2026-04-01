"""
业务单元管理 API 路由
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list", response_model=Dict[str, Any])
async def list_business_units():
    """获取所有业务单元列表（含成本计算基础数据）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                unit_id, unit_name, description,
                policy_count, avg_premium, pure_risk_cost,
                expected_loss_ratio, expected_profit_margin,
                is_active, created_at, updated_at
            FROM business_unit
            WHERE is_active = 1
            ORDER BY unit_id
        """)
        
        units = []
        for row in cursor.fetchall():
            units.append({
                'unit_id': row['unit_id'],
                'unit_name': row['unit_name'],
                'description': row['description'] or '',
                'policy_count': row['policy_count'] or 0,
                'avg_premium': float(row['avg_premium']) if row['avg_premium'] else 0,
                'pure_risk_cost': float(row['pure_risk_cost']) if row['pure_risk_cost'] else 0,
                'expected_loss_ratio': float(row['expected_loss_ratio']) if row['expected_loss_ratio'] else 0,
                'expected_profit_margin': float(row['expected_profit_margin']) if row['expected_profit_margin'] else 0,
                'is_active': bool(row['is_active']),
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            })
        
        return {
            'business_units': units,
            'total': len(units)
        }
    except Exception as e:
        logger.error(f"获取业务单元列表失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取业务单元列表失败')
    finally:
        conn.close()


@router.get("/{unit_id}", response_model=Dict[str, Any])
async def get_business_unit(unit_id: str):
    """获取单个业务单元详情"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                unit_id, unit_name, description,
                policy_count, avg_premium, pure_risk_cost,
                expected_loss_ratio, expected_profit_margin,
                is_active, created_at, updated_at
            FROM business_unit
            WHERE unit_id = %s
        """, (unit_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"业务单元 {unit_id} 不存在")
        
        return {
            'unit_id': row['unit_id'],
            'unit_name': row['unit_name'],
            'description': row['description'] or '',
            'policy_count': row['policy_count'] or 0,
            'avg_premium': float(row['avg_premium']) if row['avg_premium'] else 0,
            'pure_risk_cost': float(row['pure_risk_cost']) if row['pure_risk_cost'] else 0,
            'expected_loss_ratio': float(row['expected_loss_ratio']) if row['expected_loss_ratio'] else 0,
            'expected_profit_margin': float(row['expected_profit_margin']) if row['expected_profit_margin'] else 0,
            'is_active': bool(row['is_active']),
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取业务单元详情失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取业务单元详情失败')
    finally:
        conn.close()
