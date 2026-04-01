"""
策略管理 API
提供策略的 CRUD、测试、发布等功能
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from app.core.database import get_db_connection
from app.core.config import settings

# 问题 9：添加日志记录
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# 常量定义
# ============================================

# 有效的状态流转规则
VALID_STATUS_TRANSITIONS = {
    'draft': ['simulation_passed', 'simulation_failed', 'archived'],
    'simulation_passed': ['ab_test_passed', 'ab_test_failed', 'draft', 'archived'],
    'simulation_failed': ['draft', 'archived'],
    'ab_test_passed': ['published', 'draft', 'archived'],
    'ab_test_failed': ['draft', 'archived'],
    'published': ['archived'],
    'archived': ['draft']  # 允许从归档重新启用
}

# 所有有效状态
VALID_STATUSES = list(VALID_STATUS_TRANSITIONS.keys())

# 允许排序的字段白名单
ALLOWED_SORT_FIELDS = {'created_at', 'updated_at', 'name', 'status'}

# ============================================
# 数据模型
# ============================================

class StrategyCreate(BaseModel):
    """创建策略请求"""
    name: str = Field(..., min_length=1, max_length=200, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    
    # 策略参数
    fixed_cost_ratio: float = Field(0.10, ge=0, le=1, description="固定成本率")
    target_loss_ratio: float = Field(0.75, ge=0, le=1, description="目标赔付率")
    market_expense_ratio: float = Field(0.12, ge=0, le=1, description="市场费用率")
    autonomous_discount_min: float = Field(0.50, ge=0, le=2, description="自主系数下限")
    autonomous_discount_max: float = Field(0.65, ge=0, le=2, description="自主系数上限")
    
    # 适用范围
    institutions: List[Dict[str, str]] = Field(default_factory=list, description="机构列表")
    business_units: List[Dict[str, str]] = Field(default_factory=list, description="业务单元列表")
    
    created_by: Optional[str] = Field(None, description="创建人")


class StrategyUpdate(BaseModel):
    """更新策略请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    fixed_cost_ratio: Optional[float] = Field(None, ge=0, le=1)
    target_loss_ratio: Optional[float] = Field(None, ge=0, le=1)
    market_expense_ratio: Optional[float] = Field(None, ge=0, le=1)
    autonomous_discount_min: Optional[float] = Field(None, ge=0, le=2)
    autonomous_discount_max: Optional[float] = Field(None, ge=0, le=2)
    institutions: Optional[List[Dict[str, str]]] = None
    business_units: Optional[List[Dict[str, str]]] = None


class StrategyStatusUpdate(BaseModel):
    """更新策略状态请求"""
    new_status: str = Field(..., description="新状态")


class StrategyResponse(BaseModel):
    """策略响应"""
    id: str
    name: str
    description: Optional[str]
    fixed_cost_ratio: float
    target_loss_ratio: float
    market_expense_ratio: float
    autonomous_discount_min: float
    autonomous_discount_max: float
    status: str
    institutions: List[str]
    business_units: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestResultCreate(BaseModel):
    """创建测试结果"""
    test_type: str = Field(..., description="测试类型（simulation/ab_test）")
    passed: bool = Field(..., description="是否通过")
    result_summary: str = Field(..., description="测试结果摘要")
    conversion_rate_lift: Optional[float] = None
    profit_lift: Optional[float] = None
    p_value: Optional[float] = None
    sample_size: Optional[int] = None
    test_duration_days: Optional[int] = None


class PublishCreate(BaseModel):
    """创建发布记录"""
    publish_scope: str = Field(..., description="发布范围（all/specified/channel）")
    publish_description: str = Field(..., description="发布描述")
    rollback_plan: str = Field(..., description="回滚预案")
    timing_type: str = Field("immediate", description="发布时间类型（immediate/scheduled）")
    scheduled_time: Optional[datetime] = None
    institutions: List[Dict[str, str]] = Field(default_factory=list)


# ============================================
# 辅助函数
# ============================================

def _get_strategy_with_relations(cursor, strategy_id: str) -> Optional[Dict]:
    """
    获取策略及其关联数据（机构、业务单元）
    
    Args:
        cursor: 数据库游标
        strategy_id: 策略 ID
        
    Returns:
        包含关联数据的策略字典，如果不存在则返回 None
    """
    # 使用 JOIN 一次性获取所有数据，避免 N+1 查询
    cursor.execute("""
        SELECT 
            s.*,
            COALESCE(GROUP_CONCAT(DISTINCT si.institution_name ORDER BY si.institution_name SEPARATOR ','), '') AS institutions_str,
            COALESCE(GROUP_CONCAT(DISTINCT sbu.unit_name ORDER BY sbu.unit_name SEPARATOR ','), '') AS business_units_str
        FROM strategies s
        LEFT JOIN strategy_institutions si ON s.id = si.strategy_id
        LEFT JOIN strategy_business_units sbu ON s.id = sbu.strategy_id
        WHERE s.id = %s
        GROUP BY s.id
    """, (strategy_id,))
    
    strategy = cursor.fetchone()
    if not strategy:
        return None
    
    # 解析关联数据
    strategy['institutions'] = [
        inst.strip() for inst in strategy['institutions_str'].split(',') 
        if inst.strip()
    ] if strategy['institutions_str'] else []
    
    strategy['business_units'] = [
        unit.strip() for unit in strategy['business_units_str'].split(',') 
        if unit.strip()
    ] if strategy['business_units_str'] else []
    
    # 移除临时字段
    del strategy['institutions_str']
    del strategy['business_units_str']
    
    return strategy


def _validate_status_transition(current_status: str, new_status: str) -> bool:
    """
    验证状态流转是否合法
    
    Args:
        current_status: 当前状态
        new_status: 新状态
        
    Returns:
        是否合法
    """
    if current_status not in VALID_STATUS_TRANSITIONS:
        return False
    
    return new_status in VALID_STATUS_TRANSITIONS[current_status]


# ============================================
# API 接口
# ============================================

@router.get("/strategies", response_model=List[StrategyResponse], summary="获取所有策略")
async def get_all_strategies(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("DESC", description="排序方向（ASC/DESC）")
):
    """
    获取所有策略，支持按状态筛选和分页
    
    - **status_filter**: 可选，按状态筛选（draft/simulation_passed/ab_test_passed/published 等）
    - **page**: 页码，默认 1
    - **page_size**: 每页数量，默认 20，最大 100
    - **sort_by**: 排序字段，默认 created_at
    - **sort_order**: 排序方向，默认 DESC
    """
    # 验证排序字段（防止 SQL 注入）
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"无效的排序字段，可用值：{list(ALLOWED_SORT_FIELDS)}")
    
    # 验证排序方向
    if sort_order.upper() not in ('ASC', 'DESC'):
        raise HTTPException(status_code=400, detail="无效的排序方向，可用值：ASC, DESC")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 计算分页参数
        offset = (page - 1) * page_size
        
        # 构建查询（使用 JOIN 一次性获取关联数据）
        base_query = """
            SELECT 
                s.*,
                COALESCE(GROUP_CONCAT(DISTINCT si.institution_name ORDER BY si.institution_name SEPARATOR ','), '') AS institutions_str,
                COALESCE(GROUP_CONCAT(DISTINCT sbu.unit_name ORDER BY sbu.unit_name SEPARATOR ','), '') AS business_units_str
            FROM strategies s
            LEFT JOIN strategy_institutions si ON s.id = si.strategy_id
            LEFT JOIN strategy_business_units sbu ON s.id = sbu.strategy_id
        """
        
        if status_filter:
            if status_filter not in VALID_STATUSES:
                raise HTTPException(status_code=400, detail=f"无效的状态值，可用值：{VALID_STATUSES}")
            where_clause = " WHERE s.status = %s"
            params = (status_filter,)
        else:
            where_clause = ""
            params = ()
        
        # 执行查询
        query = f"""
            {base_query}
            {where_clause}
            GROUP BY s.id
            ORDER BY s.{sort_by} {sort_order.upper()}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (*params, page_size, offset))
        strategies = cursor.fetchall()
        
        # 解析关联数据
        for strategy in strategies:
            strategy['institutions'] = [
                inst.strip() for inst in strategy['institutions_str'].split(',') 
                if inst.strip()
            ] if strategy['institutions_str'] else []
            
            strategy['business_units'] = [
                unit.strip() for unit in strategy['business_units_str'].split(',') 
                if unit.strip()
            ] if strategy['business_units_str'] else []
            
            # 移除临时字段
            del strategy['institutions_str']
            del strategy['business_units_str']
        
        return strategies
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"获取策略列表失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取策略列表失败")
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse, summary="获取策略详情")
async def get_strategy(strategy_id: str):
    """获取策略详细信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        strategy = _get_strategy_with_relations(cursor, strategy_id)
        
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"获取策略详情失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取策略详情失败")
    finally:
        conn.close()


@router.post("/strategies", response_model=StrategyResponse, summary="创建策略")
async def create_strategy(strategy_data: StrategyCreate):
    """
    创建新策略
    
    策略配置中心保存策略时使用此接口
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 生成策略 ID
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        # 插入策略主数据
        cursor.execute("""
            INSERT INTO strategies (
                id, name, description,
                fixed_cost_ratio, target_loss_ratio, market_expense_ratio,
                autonomous_discount_min, autonomous_discount_max,
                status, created_by, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            strategy_id,
            strategy_data.name,
            strategy_data.description,
            strategy_data.fixed_cost_ratio,
            strategy_data.target_loss_ratio,
            strategy_data.market_expense_ratio,
            strategy_data.autonomous_discount_min,
            strategy_data.autonomous_discount_max,
            'draft',  # 初始状态为草稿
            strategy_data.created_by or 'system',
            datetime.now(),
            datetime.now()
        ))
        
        # 插入机构关联
        for inst in strategy_data.institutions:
            cursor.execute("""
                INSERT INTO strategy_institutions (strategy_id, institution_code, institution_name)
                VALUES (%s, %s, %s)
            """, (strategy_id, inst.get('code', ''), inst.get('name', '')))
        
        # 插入业务单元关联
        for unit in strategy_data.business_units:
            cursor.execute("""
                INSERT INTO strategy_business_units (strategy_id, unit_id, unit_name)
                VALUES (%s, %s, %s)
            """, (strategy_id, unit.get('id', ''), unit.get('name', '')))
        
        conn.commit()
        
        # 返回创建的策略
        return await get_strategy(strategy_id)
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"创建策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail="创建策略失败")
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse, summary="更新策略")
async def update_strategy(strategy_id: str, strategy_data: StrategyUpdate):
    """更新策略信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查策略是否存在
        cursor.execute("SELECT id FROM strategies WHERE id = %s", (strategy_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 构建更新字段
        update_fields = []
        values = []
        
        for field, value in strategy_data.model_dump().items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有要更新的字段")
        
        values.append(strategy_id)
        
        # 更新策略主数据
        cursor.execute(f"""
            UPDATE strategies 
            SET {', '.join(update_fields)}, updated_at = %s
            WHERE id = %s
        """, [*values, datetime.now(), strategy_id])
        
        # 更新机构关联（先删除后插入）
        if strategy_data.institutions is not None:
            cursor.execute("DELETE FROM strategy_institutions WHERE strategy_id = %s", (strategy_id,))
            for inst in strategy_data.institutions:
                cursor.execute("""
                    INSERT INTO strategy_institutions (strategy_id, institution_code, institution_name)
                    VALUES (%s, %s, %s)
                """, (strategy_id, inst.get('code', ''), inst.get('name', '')))
        
        # 更新业务单元关联
        if strategy_data.business_units is not None:
            cursor.execute("DELETE FROM strategy_business_units WHERE strategy_id = %s", (strategy_id,))
            for unit in strategy_data.business_units:
                cursor.execute("""
                    INSERT INTO strategy_business_units (strategy_id, unit_id, unit_name)
                    VALUES (%s, %s, %s)
                """, (strategy_id, unit.get('id', ''), unit.get('name', '')))
        
        conn.commit()
        
        return await get_strategy(strategy_id)
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"更新策略失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail="更新策略失败")
    finally:
        conn.close()


@router.patch("/strategies/{strategy_id}/status", response_model=StrategyResponse, summary="更新策略状态")
async def update_strategy_status(strategy_id: str, status_data: StrategyStatusUpdate):
    """
    更新策略状态（带状态流转校验）
    
    可用状态：
    - draft: 草稿
    - simulation_passed: 模拟测试通过
    - simulation_failed: 模拟测试失败
    - ab_test_passed: A/B 测试通过
    - ab_test_failed: A/B 测试失败
    - published: 已发布
    - archived: 已归档
    
    状态流转规则：
    - draft → simulation_passed/failed, archived
    - simulation_passed → ab_test_passed/failed, draft, archived
    - simulation_failed → draft, archived
    - ab_test_passed → published, draft, archived
    - ab_test_failed → draft, archived
    - published → archived
    - archived → draft (重新启用)
    """
    new_status = status_data.new_status
    
    # 验证新状态是否有效
    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"无效的状态值，可用值：{VALID_STATUSES}")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute("SELECT status FROM strategies WHERE id = %s", (strategy_id,))
        current = cursor.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        current_status = current['status']
        
        # 验证状态流转是否合法
        if not _validate_status_transition(current_status, new_status):
            raise HTTPException(
                status_code=400, 
                detail=f"不允许的状态流转：{current_status} → {new_status}。"
                       f"允许的目标状态：{VALID_STATUS_TRANSITIONS.get(current_status, [])}"
            )
        
        # 更新状态
        cursor.execute("""
            UPDATE strategies 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """, (new_status, datetime.now(), strategy_id))
        
        conn.commit()
        
        return await get_strategy(strategy_id)
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"更新策略状态失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail="更新策略状态失败")
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/test-results", summary="记录测试结果")
async def record_test_result(strategy_id: str, test_data: TestResultCreate):
    """
    记录策略测试结果
    
    测试完成后调用此接口，会自动更新策略状态
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查策略是否存在
        cursor.execute("SELECT id FROM strategies WHERE id = %s", (strategy_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 生成测试记录 ID
        test_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        # 插入测试记录
        cursor.execute("""
            INSERT INTO strategy_test_results (
                id, strategy_id, test_type, passed, result_summary,
                conversion_rate_lift, profit_lift, p_value,
                sample_size, test_duration_days,
                completed_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_id,
            strategy_id,
            test_data.test_type,
            test_data.passed,
            test_data.result_summary,
            test_data.conversion_rate_lift,
            test_data.profit_lift,
            test_data.p_value,
            test_data.sample_size,
            test_data.test_duration_days,
            datetime.now(),
            datetime.now()
        ))
        
        # 更新策略状态
        new_status = 'simulation_passed' if (test_data.test_type == 'simulation' and test_data.passed) else \
                     'simulation_failed' if (test_data.test_type == 'simulation' and not test_data.passed) else \
                     'ab_test_passed' if (test_data.test_type == 'ab_test' and test_data.passed) else \
                     'ab_test_failed'
        
        cursor.execute("""
            UPDATE strategies 
            SET status = %s, updated_at = %s
            WHERE id = %s
        """, (new_status, datetime.now(), strategy_id))
        
        conn.commit()
        
        return {"message": "测试结果已记录", "test_id": test_id, "new_status": new_status}
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"记录测试结果失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail="记录测试结果失败")
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/publish", summary="发布策略")
async def publish_strategy(strategy_id: str, publish_data: PublishCreate):
    """
    发布策略到生产环境
    
    发布成功后会自动更新策略状态为 published
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查策略是否存在
        cursor.execute("SELECT id, status FROM strategies WHERE id = %s", (strategy_id,))
        strategy = cursor.fetchone()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        # 生成发布记录 ID
        publish_id = f"PUB_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        # 插入发布记录
        cursor.execute("""
            INSERT INTO strategy_publish_records (
                id, strategy_id, publish_scope, publish_description, rollback_plan,
                timing_type, scheduled_time, publish_status,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            publish_id,
            strategy_id,
            publish_data.publish_scope,
            publish_data.publish_description,
            publish_data.rollback_plan,
            publish_data.timing_type,
            publish_data.scheduled_time,
            'published' if publish_data.timing_type == 'immediate' else 'pending',
            datetime.now(),
            datetime.now()
        ))
        
        # 插入发布机构关联
        for inst in publish_data.institutions:
            cursor.execute("""
                INSERT INTO strategy_publish_institutions (publish_id, institution_code, institution_name)
                VALUES (%s, %s, %s)
            """, (publish_id, inst.get('code', ''), inst.get('name', '')))
        
        # 更新策略状态为 published
        cursor.execute("""
            UPDATE strategies 
            SET status = 'published', updated_at = %s
            WHERE id = %s
        """, (datetime.now(), strategy_id))
        
        conn.commit()
        
        return {
            "message": "策略发布成功",
            "publish_id": publish_id,
            "status": "published"
        }
    except HTTPException:
        raise
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"发布策略失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail="发布策略失败")
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}/test-history", summary="获取策略测试历史")
async def get_strategy_test_history(strategy_id: str):
    """获取策略的所有测试记录"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM strategy_test_results 
            WHERE strategy_id = %s 
            ORDER BY completed_at DESC
        """, (strategy_id,))
        
        return cursor.fetchall()
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"获取测试历史失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取测试历史失败")
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}/publish-history", summary="获取策略发布历史")
async def get_strategy_publish_history(strategy_id: str):
    """获取策略的所有发布记录"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 使用 JOIN 一次性获取发布记录和机构，避免 N+1 查询
        cursor.execute("""
            SELECT spr.*, 
                   COALESCE(GROUP_CONCAT(spi.institution_name ORDER BY spi.institution_name SEPARATOR ','), '') AS institutions_str
            FROM strategy_publish_records spr
            LEFT JOIN strategy_publish_institutions spi ON spr.id = spi.publish_id
            WHERE spr.strategy_id = %s 
            GROUP BY spr.id
            ORDER BY spr.published_at DESC
        """, (strategy_id,))
        
        records = cursor.fetchall()
        
        # 解析机构列表
        for record in records:
            record['institutions'] = [
                inst.strip() for inst in record['institutions_str'].split(',') 
                if inst.strip()
            ] if record['institutions_str'] else []
            del record['institutions_str']
        
        return records
    except Exception as e:
        # 问题 9：添加详细日志记录
        logger.error(f"获取发布历史失败 (strategy_id={strategy_id}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取发布历史失败")
    finally:
        conn.close()
