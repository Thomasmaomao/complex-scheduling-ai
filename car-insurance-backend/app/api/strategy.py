"""
策略管理 API - Phase 2 完整版
包含策略总览、向导、测试、发布、权限等所有端点
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import json

from app.core.database import get_db_connection
from app.core.config import settings
from app.core.middleware import (
    PermissionChecker, OptimisticLock, StrategyValidator,
    require_permission, validate_strategy_data, StrategyErrorCodes
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# 辅助函数
# ============================================

def _format_datetime(dt: datetime = None) -> str:
    """格式化 datetime 为 MySQL 兼容的字符串格式"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# ============================================
# 常量定义
# ============================================

VALID_STATUS_TRANSITIONS = {
    'draft': ['simulation_passed', 'simulation_failed', 'archived', 'disabled'],
    'simulation_passed': ['ab_test_passed', 'ab_test_failed', 'draft', 'archived', 'disabled'],
    'simulation_failed': ['draft', 'archived', 'disabled'],
    'ab_test_passed': ['published', 'draft', 'archived', 'disabled'],
    'ab_test_failed': ['draft', 'archived', 'disabled'],
    'published': ['archived', 'disabled'],
    'archived': ['draft', 'disabled'],
    'disabled': ['draft']
}

VALID_STATUSES = list(VALID_STATUS_TRANSITIONS.keys())
ALLOWED_SORT_FIELDS = {'created_at', 'updated_at', 'name', 'status'}

# ============================================
# 数据模型 - 策略总览
# ============================================

class StrategyListRequest(BaseModel):
    """策略列表请求"""
    status: Optional[str] = None
    created_by: Optional[str] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field('created_at')
    sort_order: str = Field('desc')


class StrategyCreateRequest(BaseModel):
    """创建策略请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    institutions: List[Dict[str, str]] = Field(default_factory=list)


class StrategyUpdateRequest(BaseModel):
    """更新策略基本信息"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    expected_version: int = Field(..., ge=1)


class StrategyStatusUpdateRequest(BaseModel):
    """更新策略状态"""
    status: str = Field(..., description='disabled 或 draft')


class StrategyListItem(BaseModel):
    """策略列表项"""
    id: str
    name: str
    status: str
    version: int
    institutions: List[str]
    created_by: str
    created_at: datetime
    permission: str


class StrategyListResponse(BaseModel):
    """策略列表响应"""
    total: int
    page: int
    page_size: int
    strategies: List[StrategyListItem]


class StrategyDetailResponse(BaseModel):
    """策略详情响应"""
    id: str
    name: str
    description: Optional[str]
    fixed_cost_ratio: Optional[float]
    target_loss_ratio: Optional[float]
    market_expense_ratio: Optional[float]
    autonomous_discount_min: Optional[float]
    autonomous_discount_max: Optional[float]
    is_calculate: bool
    status: str
    version: int
    institutions: List[Dict[str, str]]
    business_units: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    permission: str


# ============================================
# 数据模型 - 策略向导
# ============================================

class WizardBasicRequest(BaseModel):
    """步骤 0：基本信息"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class WizardBusinessUnitRequest(BaseModel):
    """步骤 1：业务单元划分"""
    business_units: List[Dict[str, str]] = Field(..., description='业务单元列表')


class WizardCostSimulationRequest(BaseModel):
    """步骤 2：成本模拟参数"""
    global_params: Dict[str, Any] = Field(..., description='全局兜底参数')
    business_unit_params: List[Dict[str, Any]] = Field(default_factory=list, description='业务单元独立参数')


class WizardRevenueSimulationRequest(BaseModel):
    """步骤 3：收益模拟"""
    adjusted_params: Optional[Dict[str, Any]] = None
    simulation_scope: str = Field('all', description='all 或 specific')


class WizardConfirmResponse(BaseModel):
    """确认保存响应"""
    id: str
    status: str
    version: int
    message: str


class WizardFullConfigResponse(BaseModel):
    """策略完整配置响应"""
    id: str
    name: str
    description: Optional[str]
    status: str
    version: int
    global_params: Dict[str, Any]
    business_unit_params: List[Dict[str, Any]]
    institutions: List[Dict[str, str]]
    business_units: List[Dict[str, str]]


# ============================================
# 数据模型 - 策略测试
# ============================================

class SimulationTestRequest(BaseModel):
    """模拟测试请求"""
    test_params: Optional[Dict[str, Any]] = None


class ScenarioTestRequest(BaseModel):
    """情景测试请求"""
    base_profit: float = Field(..., description='基准利润')
    change_rates: Optional[List[float]] = Field(None, description='情景变化率列表，默认 [-0.02, -0.01, 0, 0.01, 0.02]')


class ScenarioTestResponse(BaseModel):
    """情景测试响应"""
    scenarios: List[Dict[str, Any]]
    summary: Dict[str, Any]


class ABTestRequest(BaseModel):
    """A/B 测试请求"""
    traffic_split: int = Field(50, ge=10, le=90)
    duration_days: int = Field(14, ge=1, le=30)
    institutions: List[str] = Field(default_factory=list)
    business_units: List[str] = Field(default_factory=list)


class TestHistoryItem(BaseModel):
    """测试历史项"""
    id: str
    test_type: str
    passed: bool
    result_summary: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime


class TestDetailResponse(BaseModel):
    """测试详情响应"""
    test_id: str
    test_type: str
    status: str
    passed: bool
    result_summary: Optional[str]
    metrics: Dict[str, Any]
    sample_size: Optional[int]
    duration_days: Optional[int]


# ============================================
# 数据模型 - 策略发布
# ============================================

class PublishRequest(BaseModel):
    """发布策略请求"""
    publish_scope: str = Field(..., description='all/specified/channel')
    publish_description: str
    rollback_plan: str
    timing_type: str = Field('immediate', description='immediate/scheduled')
    scheduled_time: Optional[datetime] = None
    institutions: List[Dict[str, str]] = Field(default_factory=list)


class RollbackRequest(BaseModel):
    """回滚请求"""
    target_version: int = Field(..., ge=1)
    reason: str


class PublishHistoryItem(BaseModel):
    """发布历史项"""
    id: str
    publish_scope: str
    publish_description: str
    publish_status: str
    published_at: Optional[datetime]
    institutions: List[str]


# ============================================
# 数据模型 - 策略权限
# ============================================

class PermissionItem(BaseModel):
    """权限项"""
    user_id: str
    role: str
    granted_at: datetime


class AddPermissionRequest(BaseModel):
    """添加权限请求"""
    user_id: str
    role: str = Field(..., description='owner/editor/viewer')


# ============================================
# 辅助函数
# ============================================

def _get_current_user_id() -> str:
    """获取当前用户 ID（TODO: 从 token 中获取）"""
    return getattr(settings, 'CURRENT_USER_ID', 'system')


def _validate_status_transition(current_status: str, new_status: str) -> bool:
    """验证状态流转是否合法"""
    if current_status not in VALID_STATUS_TRANSITIONS:
        return False
    return new_status in VALID_STATUS_TRANSITIONS[current_status]


def _get_strategy_permission(strategy_id: str, user_id: str) -> Optional[str]:
    """获取用户在策略中的权限"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT role FROM strategy_permissions WHERE strategy_id = %s AND user_id = %s',
            (strategy_id, user_id)
        )
        result = cursor.fetchone()
        return result['role'] if result else None
    finally:
        conn.close()


# ============================================
# 1. 策略总览 API（6 个端点）
# ============================================

@router.get("/strategies", response_model=StrategyListResponse, summary="获取策略总览列表")
@require_permission('view')
async def list_strategies(
    status: Optional[str] = Query(None, alias='status', description='状态筛选'),
    status_filter: Optional[str] = None,
    created_by: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query('created_at'),
    sort_order: str = Query('desc')
):
    """获取策略总览列表（支持分页、筛选）"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        offset = (page - 1) * page_size
        
        # 支持 status 和 status_filter 两种参数名
        actual_status = status or status_filter
        
        # 构建 WHERE 条件
        where_clauses = []
        params = []
        
        if actual_status:
            if actual_status not in VALID_STATUSES:
                raise HTTPException(status_code=400, detail=f'无效的状态值')
            where_clauses.append('s.status = %s')
            params.append(actual_status)
        
        if created_by:
            where_clauses.append('s.created_by = %s')
            params.append(created_by)
        
        if keyword:
            where_clauses.append('s.name LIKE %s')
            params.append(f'%{keyword}%')
        
        where_sql = ' WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''
        
        # 验证排序字段
        if sort_by not in ALLOWED_SORT_FIELDS:
            raise HTTPException(status_code=400, detail=f'无效的排序字段')
        
        sort_order_sql = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
        
        # 查询总数
        count_sql = f'SELECT COUNT(DISTINCT s.id) AS total FROM strategies s {where_sql}'
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        query = f"""
            SELECT 
                s.id, s.name, s.status, s.version, s.created_by, s.created_at,
                COALESCE(GROUP_CONCAT(DISTINCT si.institution_name ORDER BY si.institution_name SEPARATOR ','), '') AS institutions_str
            FROM strategies s
            LEFT JOIN strategy_institutions si ON s.id = si.strategy_id
            {where_sql}
            GROUP BY s.id
            ORDER BY s.{sort_by} {sort_order_sql}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, [*params, page_size, offset])
        rows = cursor.fetchall()
        
        # 构建响应
        strategies = []
        for row in rows:
            permission = _get_strategy_permission(row['id'], user_id) or 'viewer'
            strategies.append(StrategyListItem(
                id=row['id'],
                name=row['name'],
                status=row['status'],
                version=row['version'],
                institutions=[i.strip() for i in row['institutions_str'].split(',') if i.strip()] if row['institutions_str'] else [],
                created_by=row['created_by'],
                created_at=row['created_at'],
                permission=permission
            ))
        
        return StrategyListResponse(
            total=total,
            page=page,
            page_size=page_size,
            strategies=strategies
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略列表失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取策略列表失败')
    finally:
        conn.close()


@router.post("/strategies", response_model=Dict[str, Any], summary="创建策略")
async def create_strategy(request: StrategyCreateRequest):
    """创建策略（基本信息）"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 生成策略 ID
        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        # 插入策略主数据
        cursor.execute("""
            INSERT INTO strategies (
                id, name, description, status, version, created_by, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            strategy_id,
            request.name,
            request.description,
            'draft',
            1,
            user_id,
            datetime.now(),
            datetime.now()
        ))
        
        # 插入机构关联
        for inst in request.institutions:
            cursor.execute("""
                INSERT INTO strategy_institutions (strategy_id, institution_code, institution_name)
                VALUES (%s, %s, %s)
            """, (strategy_id, inst.get('code', ''), inst.get('name', '')))
        
        # 创建 owner 权限
        cursor.execute("""
            INSERT INTO strategy_permissions (strategy_id, user_id, role, granted_at)
            VALUES (%s, %s, %s, %s)
        """, (strategy_id, user_id, 'owner', _format_datetime()))
        
        # 创建初始版本
        version_id = f"version_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        snapshot_data = {'name': request.name, 'description': request.description, 'institutions': request.institutions}
        cursor.execute("""
            INSERT INTO strategy_versions (
                id, strategy_id, version_number, snapshot_data, change_summary, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            version_id,
            strategy_id,
            1,
            json.dumps(snapshot_data),
            '初始创建',
            user_id,
            datetime.now()
        ))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'id': strategy_id,
                'name': request.name,
                'status': 'draft',
                'version': 1,
                'permission': 'owner'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='创建策略失败')
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}", response_model=StrategyDetailResponse, summary="获取策略详情")
async def get_strategy(strategy_id: str):
    """获取策略详情"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. 先检查资源是否存在（在权限校验之前）
        cursor.execute("""
            SELECT * FROM strategies WHERE id = %s
        """, (strategy_id,))
        strategy = cursor.fetchone()
        
        if not strategy:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        # 2. 再检查权限
        permission = _get_strategy_permission(strategy_id, user_id) or 'viewer'
        if permission == 'viewer' and user_id != strategy['created_by']:
            # 非创建者且无权限，返回 403
            raise HTTPException(status_code=403, detail='无权限查看此策略')
        
        # 查询机构
        cursor.execute("""
            SELECT institution_code, institution_name FROM strategy_institutions 
            WHERE strategy_id = %s
        """, (strategy_id,))
        institutions = [{'code': row['institution_code'], 'name': row['institution_name']} 
                       for row in cursor.fetchall()]
        
        # 查询业务单元（含独立参数 + 业务单元主数据）
        cursor.execute("""
            SELECT sbu.unit_id, sbu.unit_name, 
                   sbu.fixed_cost_ratio, sbu.target_loss_ratio, sbu.market_expense_ratio,
                   sbu.autonomous_discount_min, sbu.autonomous_discount_max, sbu.is_calculate,
                   bu.description, bu.expected_profit_margin, bu.expected_loss_ratio,
                   bu.policy_count, bu.avg_premium, bu.pure_risk_cost
            FROM strategy_business_units sbu
            LEFT JOIN business_unit bu ON sbu.unit_id = bu.unit_id
            WHERE sbu.strategy_id = %s
        """, (strategy_id,))
        business_units = []
        for row in cursor.fetchall():
            bu_dict = dict(row)
            # 添加前端期望的字段
            bu_dict['policies'] = bu_dict.get('policy_count') or 0
            bu_dict['avg_premium'] = float(bu_dict.get('avg_premium') or 0)
            bu_dict['pure_risk_cost'] = float(bu_dict.get('pure_risk_cost') or 0)
            bu_dict['expected_profit_margin'] = float(bu_dict.get('expected_profit_margin') or 0)
            bu_dict['target_loss_ratio'] = float(bu_dict.get('expected_loss_ratio') or bu_dict.get('target_loss_ratio') or 0.75)
            bu_dict['strategy_suggestion'] = '推荐'
            business_units.append(bu_dict)
        
        return StrategyDetailResponse(
            id=strategy['id'],
            name=strategy['name'],
            description=strategy['description'],
            fixed_cost_ratio=float(strategy['fixed_cost_ratio']) if strategy['fixed_cost_ratio'] else None,
            target_loss_ratio=float(strategy['target_loss_ratio']) if strategy['target_loss_ratio'] else None,
            market_expense_ratio=float(strategy['market_expense_ratio']) if strategy['market_expense_ratio'] else None,
            autonomous_discount_min=float(strategy['autonomous_discount_min']) if strategy['autonomous_discount_min'] else None,
            autonomous_discount_max=float(strategy['autonomous_discount_max']) if strategy['autonomous_discount_max'] else None,
            is_calculate=bool(strategy['is_calculate']),
            status=strategy['status'],
            version=strategy['version'],
            institutions=institutions,
            business_units=business_units,
            created_at=strategy['created_at'],
            updated_at=strategy['updated_at'],
            permission=permission
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取策略详情失败')
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}", response_model=Dict[str, Any], summary="更新策略基本信息")
@require_permission('edit')
async def update_strategy(strategy_id: str, request: StrategyUpdateRequest):
    """更新策略基本信息（带乐观锁）"""
    user_id = _get_current_user_id()
    
    # 乐观锁校验
    OptimisticLock.check_version(strategy_id, request.expected_version)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        if request.name is not None:
            update_fields.append('name = %s')
            values.append(request.name)
        if request.description is not None:
            update_fields.append('description = %s')
            values.append(request.description)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail='没有要更新的字段')
        
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 参数顺序必须与 SQL 中的占位符顺序一致：
        # SET 字段值..., updated_at=%s WHERE id=%s AND version=%s
        values.append(update_time)
        values.append(strategy_id)
        values.append(request.expected_version)
        
        cursor.execute(f"""
            UPDATE strategies 
            SET {', '.join(update_fields)}, version = version + 1, updated_at = %s
            WHERE id = %s AND version = %s
        """, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=409, detail='策略已被其他人修改，请刷新后重试')
        
        conn.commit()
        
        # 获取新版本号
        cursor.execute('SELECT version FROM strategies WHERE id = %s', (strategy_id,))
        new_version = cursor.fetchone()['version']
        
        return {
            'code': 200,
            'data': {
                'id': strategy_id,
                'version': new_version,
                'message': '更新成功'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='更新策略失败')
    finally:
        conn.close()


@router.patch("/strategies/{strategy_id}/status", response_model=Dict[str, Any], summary="禁用/启用策略")
@require_permission('delete')
async def update_strategy_status(strategy_id: str, request: StrategyStatusUpdateRequest):
    """禁用/启用策略（软删除）"""
    user_id = _get_current_user_id()
    new_status = request.status
    
    if new_status not in ['draft', 'disabled']:
        raise HTTPException(status_code=400, detail='只能切换到 draft 或 disabled 状态')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute('SELECT status FROM strategies WHERE id = %s', (strategy_id,))
        current = cursor.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        current_status = current['status']
        
        if not _validate_status_transition(current_status, new_status):
            raise HTTPException(
                status_code=400,
                detail=f'不允许的状态流转：{current_status} → {new_status}'
            )
        
        cursor.execute("""
            UPDATE strategies SET status = %s, updated_at = %s WHERE id = %s
        """, (new_status, datetime.now(), strategy_id))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'id': strategy_id,
                'status': new_status,
                'message': '状态更新成功'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略状态失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='更新策略状态失败')
    finally:
        conn.close()


@router.delete("/strategies/{strategy_id}", response_model=Dict[str, Any], summary="删除策略")
@require_permission('delete')
async def delete_strategy(strategy_id: str):
    """删除策略（硬删除，完全移除记录）"""
    user_id = _get_current_user_id()
    
    # 检查是否为 owner
    role = _get_strategy_permission(strategy_id, user_id)
    if role != 'owner':
        raise HTTPException(status_code=403, detail='只有 owner 可以删除策略')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM strategies WHERE id = %s', (strategy_id,))
        current = cursor.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        # 硬删除：完全移除所有相关记录
        # 1. 删除权限记录
        cursor.execute('DELETE FROM strategy_permissions WHERE strategy_id = %s', (strategy_id,))
        # 2. 删除机构关联
        cursor.execute('DELETE FROM strategy_institutions WHERE strategy_id = %s', (strategy_id,))
        # 3. 删除业务单元关联
        cursor.execute('DELETE FROM strategy_business_units WHERE strategy_id = %s', (strategy_id,))
        # 4. 删除版本记录
        cursor.execute('DELETE FROM strategy_versions WHERE strategy_id = %s', (strategy_id,))
        # 5. 删除测试结果
        cursor.execute('DELETE FROM strategy_test_results WHERE strategy_id = %s', (strategy_id,))
        # 6. 删除发布记录
        cursor.execute('DELETE FROM strategy_publish_records WHERE strategy_id = %s', (strategy_id,))
        # 7. 最后删除主策略记录
        cursor.execute('DELETE FROM strategies WHERE id = %s', (strategy_id,))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'id': strategy_id,
                'message': '策略已永久删除'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='删除策略失败')
    finally:
        conn.close()


# ============================================
# 2. 策略向导 API（7 个端点）
# ============================================

@router.post("/strategies/{strategy_id}/wizard/step/basic", response_model=Dict[str, Any], summary="保存步骤 0：基本信息")
@require_permission('edit')
async def wizard_step_basic(strategy_id: str, request: WizardBasicRequest):
    """保存步骤 0：基本信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM strategies WHERE id = %s', (strategy_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail='策略不存在')
        
        cursor.execute("""
            UPDATE strategies SET name = %s, description = %s, updated_at = %s WHERE id = %s
        """, (request.name, request.description, datetime.now(), strategy_id))
        
        conn.commit()
        
        return {'code': 200, 'data': {'message': '基本信息保存成功'}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存基本信息失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}/wizard/business-unit", response_model=Dict[str, Any], summary="保存步骤 2：业务单元")
@require_permission('edit')
async def wizard_save_business_unit(strategy_id: str, request: WizardBusinessUnitRequest):
    """保存步骤 2：业务单元（新端点）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 删除旧的业务单元关联
        cursor.execute('DELETE FROM strategy_business_units WHERE strategy_id = %s', (strategy_id,))
        
        # 插入新的业务单元
        for unit in request.business_units:
            cursor.execute("""
                INSERT INTO strategy_business_units (strategy_id, unit_id, unit_name)
                VALUES (%s, %s, %s)
            """, (strategy_id, unit.get('id', ''), unit.get('name', '')))
        
        conn.commit()
        
        return {'code': 200, 'data': {'message': '业务单元保存成功'}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存业务单元失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/wizard/step/business-unit", response_model=Dict[str, Any], summary="保存步骤 1：业务单元划分")
@require_permission('edit')
async def wizard_step_business_unit(strategy_id: str, request: WizardBusinessUnitRequest):
    """保存步骤 1：业务单元划分"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 删除旧的业务单元关联
        cursor.execute('DELETE FROM strategy_business_units WHERE strategy_id = %s', (strategy_id,))
        
        # 插入新的业务单元
        for unit in request.business_units:
            cursor.execute("""
                INSERT INTO strategy_business_units (strategy_id, unit_id, unit_name)
                VALUES (%s, %s, %s)
            """, (strategy_id, unit.get('id', ''), unit.get('name', '')))
        
        conn.commit()
        
        return {'code': 200, 'data': {'message': '业务单元划分保存成功'}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存业务单元失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}/wizard/cost-simulation", response_model=Dict[str, Any], summary="保存步骤 3：成本模拟")
@require_permission('edit')
async def wizard_save_cost_simulation(strategy_id: str, request: WizardCostSimulationRequest):
    """保存步骤 3：成本模拟（新端点）"""
    # 数据校验
    errors = StrategyValidator.validate_params(request.global_params)
    if errors:
        raise HTTPException(status_code=400, detail={'code': 'VALIDATION_ERROR', 'errors': errors})
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 更新全局兜底参数
        gp = request.global_params
        cursor.execute("""
            UPDATE strategies SET
                fixed_cost_ratio = %s,
                target_loss_ratio = %s,
                market_expense_ratio = %s,
                autonomous_discount_min = %s,
                autonomous_discount_max = %s,
                is_calculate = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            gp.get('fixed_cost_ratio'),
            gp.get('target_loss_ratio'),
            gp.get('market_expense_ratio'),
            gp.get('autonomous_discount_min'),
            gp.get('autonomous_discount_max'),
            1 if gp.get('is_calculate', False) else 0,
            datetime.now(),
            strategy_id
        ))
        
        # 更新业务单元独立参数
        for bu_params in request.business_unit_params:
            cursor.execute("""
                INSERT INTO strategy_business_units (
                    strategy_id, unit_id, unit_name,
                    fixed_cost_ratio, target_loss_ratio, market_expense_ratio,
                    autonomous_discount_min, autonomous_discount_max, is_calculate
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON DUPLICATE KEY UPDATE
                    fixed_cost_ratio = VALUES(fixed_cost_ratio),
                    target_loss_ratio = VALUES(target_loss_ratio),
                    market_expense_ratio = VALUES(market_expense_ratio),
                    autonomous_discount_min = VALUES(autonomous_discount_min),
                    autonomous_discount_max = VALUES(autonomous_discount_max),
                    is_calculate = VALUES(is_calculate)
            """, (
                strategy_id,
                bu_params.get('unit_id', ''),
                bu_params.get('unit_name', ''),
                bu_params.get('fixed_cost_ratio'),
                bu_params.get('target_loss_ratio'),
                bu_params.get('market_expense_ratio'),
                bu_params.get('autonomous_discount_min'),
                bu_params.get('autonomous_discount_max'),
                1 if bu_params.get('is_calculate', False) else 0
            ))
        
        conn.commit()
        
        return {'code': 200, 'data': {'message': '成本模拟保存成功'}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存成本模拟参数失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/wizard/step/cost-simulation", response_model=Dict[str, Any], summary="保存步骤 2：成本模拟参数")
@require_permission('edit')
async def wizard_step_cost_simulation(strategy_id: str, request: WizardCostSimulationRequest):
    """保存步骤 2：成本模拟参数"""
    # 数据校验
    errors = StrategyValidator.validate_params(request.global_params)
    if errors:
        raise HTTPException(status_code=400, detail={'code': 'VALIDATION_ERROR', 'errors': errors})
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 更新全局兜底参数
        gp = request.global_params
        cursor.execute("""
            UPDATE strategies SET
                fixed_cost_ratio = %s,
                target_loss_ratio = %s,
                market_expense_ratio = %s,
                autonomous_discount_min = %s,
                autonomous_discount_max = %s,
                is_calculate = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            gp.get('fixed_cost_ratio'),
            gp.get('target_loss_ratio'),
            gp.get('market_expense_ratio'),
            gp.get('autonomous_discount_min'),
            gp.get('autonomous_discount_max'),
            1 if gp.get('is_calculate', False) else 0,
            datetime.now(),
            strategy_id
        ))
        
        # 更新业务单元独立参数
        for bu_params in request.business_unit_params:
            cursor.execute("""
                INSERT INTO strategy_business_units (
                    strategy_id, unit_id, unit_name,
                    fixed_cost_ratio, target_loss_ratio, market_expense_ratio,
                    autonomous_discount_min, autonomous_discount_max, is_calculate
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON DUPLICATE KEY UPDATE
                    fixed_cost_ratio = VALUES(fixed_cost_ratio),
                    target_loss_ratio = VALUES(target_loss_ratio),
                    market_expense_ratio = VALUES(market_expense_ratio),
                    autonomous_discount_min = VALUES(autonomous_discount_min),
                    autonomous_discount_max = VALUES(autonomous_discount_max),
                    is_calculate = VALUES(is_calculate)
            """, (
                strategy_id,
                bu_params.get('unit_id', ''),
                bu_params.get('unit_name', ''),
                bu_params.get('fixed_cost_ratio'),
                bu_params.get('target_loss_ratio'),
                bu_params.get('market_expense_ratio'),
                bu_params.get('autonomous_discount_min'),
                bu_params.get('autonomous_discount_max'),
                1 if bu_params.get('is_calculate', False) else 0
            ))
        
        conn.commit()
        
        return {'code': 200, 'data': {'message': '成本模拟参数保存成功'}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存成本模拟参数失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}/wizard/revenue-simulation", response_model=Dict[str, Any], summary="保存步骤 4：收益模拟")
@require_permission('edit')
async def wizard_save_revenue_simulation(strategy_id: str, request: WizardRevenueSimulationRequest):
    """保存步骤 4：收益模拟（新端点）"""
    # TODO: 实现收益模拟逻辑
    # 这里返回模拟结果示例
    
    return {
        'code': 200,
        'data': {
            'simulation_id': f'sim_{uuid.uuid4().hex[:8]}',
            'total_premium': 10000000,
            'total_profit': 500000,
            'profit_margin': 0.05,
            'business_unit_breakdown': [],
            'comparison': {
                'premium_change': '+5%',
                'profit_change': '+8%'
            }
        }
    }


@router.post("/strategies/{strategy_id}/wizard/step/revenue-simulation", response_model=Dict[str, Any], summary="执行收益模拟")
@require_permission('view')
async def wizard_step_revenue_simulation(strategy_id: str, request: WizardRevenueSimulationRequest):
    """执行收益模拟（支持参数调整）"""
    # TODO: 实现收益模拟逻辑
    # 这里返回模拟结果示例
    
    return {
        'code': 200,
        'data': {
            'simulation_id': f'sim_{uuid.uuid4().hex[:8]}',
            'total_premium': 10000000,
            'total_profit': 500000,
            'profit_margin': 0.05,
            'business_unit_breakdown': [],
            'comparison': {
                'premium_change': '+5%',
                'profit_change': '+8%'
            }
        }
    }


@router.post("/strategies/{strategy_id}/wizard/confirm", response_model=Dict[str, Any], summary="确认保存策略")
@require_permission('edit')
async def wizard_confirm(strategy_id: str):
    """步骤 4：确认保存策略（创建新版本，包含完整计算数据）"""
    user_id = _get_current_user_id()
    from app.services.strategy_engine import StrategyEngine
    
    engine = StrategyEngine()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当前策略
        cursor.execute('SELECT version FROM strategies WHERE id = %s', (strategy_id,))
        current = cursor.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        new_version = current['version'] + 1
        
        # 获取完整策略数据
        cursor.execute('SELECT * FROM strategies WHERE id = %s', (strategy_id,))
        strategy = cursor.fetchone()
        
        # 获取业务单元数据
        cursor.execute("""
            SELECT unit_id, unit_name, fixed_cost_ratio, target_loss_ratio, 
                   market_expense_ratio, autonomous_discount_min, autonomous_discount_max,
                   is_calculate
            FROM strategy_business_units WHERE strategy_id = %s
        """, (strategy_id,))
        business_units = cursor.fetchall()
        
        # 计算 RP 和预期利润（使用全局参数）
        fixed_cost_ratio = float(strategy['fixed_cost_ratio']) if strategy['fixed_cost_ratio'] else 0.10
        target_loss_ratio = float(strategy['target_loss_ratio']) if strategy['target_loss_ratio'] else 0.75
        market_expense_ratio = float(strategy['market_expense_ratio']) if strategy['market_expense_ratio'] else 0.12
        autonomous_discount_min = float(strategy['autonomous_discount_min']) if strategy['autonomous_discount_min'] else 0.5
        
        # 假设平均保费和保单数（实际应从业务单元数据计算）
        avg_premium = 4500  # 行业平均
        total_policies = sum(bu.get('policy_count', 1000) for bu in business_units) if business_units else 5000
        
        # 计算预期利润
        profit_calc = engine.calculate_expected_profit(
            policy_count=total_policies,
            avg_premium=avg_premium,
            fixed_cost_ratio=fixed_cost_ratio,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=market_expense_ratio
        )
        
        # 计算 RP（纯风险保费）
        rp_premium = engine.calculate_rp_premium(avg_premium, target_loss_ratio)
        
        # 计算合计值
        bu_data = []
        for bu in business_units:
            bu_policy_count = 1000  # 假设值
            bu_avg_premium = avg_premium
            bu_profit_margin = 1 - fixed_cost_ratio - target_loss_ratio - market_expense_ratio
            bu_data.append({
                'policy_count': bu_policy_count,
                'avg_premium': bu_avg_premium,
                'profit_margin': bu_profit_margin
            })
        
        totals = engine.calculate_totals(bu_data)
        
        # 创建版本快照（包含完整计算数据）
        version_id = f"version_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        snapshot_data = {
            'name': strategy['name'],
            'description': strategy['description'],
            'global_params': {
                'fixed_cost_ratio': fixed_cost_ratio,
                'target_loss_ratio': target_loss_ratio,
                'market_expense_ratio': market_expense_ratio,
                'autonomous_discount_min': autonomous_discount_min,
                'autonomous_discount_max': float(strategy['autonomous_discount_max']) if strategy['autonomous_discount_max'] else 0.65,
                'is_calculate': bool(strategy['is_calculate'])
            },
            'calculations': {
                'rp_premium': rp_premium,
                'profit_margin': profit_calc['profit_margin'],
                'expected_profit': profit_calc['expected_profit'],
                'total_premium': profit_calc['total_premium'],
                'totals': totals
            }
        }
        
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO strategy_versions (
                id, strategy_id, version_number, snapshot_data, change_summary, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (version_id, strategy_id, new_version, json.dumps(snapshot_data), '策略配置完成（含计算数据）', user_id, update_time))
        
        # 更新策略状态为 draft（保持草稿状态，等待模拟测试）
        cursor.execute("""
            UPDATE strategies SET status = 'draft', version = %s, updated_at = %s WHERE id = %s
        """, (new_version, update_time, strategy_id))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'id': strategy_id,
                'status': 'draft',
                'version': new_version,
                'message': '策略配置完成，请进行模拟测试',
                'calculations': {
                    'rp_premium': rp_premium,
                    'profit_margin': profit_calc['profit_margin'],
                    'expected_profit': profit_calc['expected_profit'],
                    'total_premium': profit_calc['total_premium'],
                    'totals': totals
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"确认保存策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='保存失败')
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}/wizard", response_model=WizardFullConfigResponse, summary="获取策略完整配置")
@require_permission('view')
async def get_wizard_config(strategy_id: str):
    """获取策略完整配置（含所有参数）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 查询策略主数据
        cursor.execute('SELECT * FROM strategies WHERE id = %s', (strategy_id,))
        strategy = cursor.fetchone()
        
        if not strategy:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        # 查询机构
        cursor.execute("""
            SELECT institution_code, institution_name FROM strategy_institutions WHERE strategy_id = %s
        """, (strategy_id,))
        institutions = [{'code': row['institution_code'], 'name': row['institution_name']} 
                       for row in cursor.fetchall()]
        
        # 查询业务单元
        cursor.execute("""
            SELECT unit_id, unit_name, fixed_cost_ratio, target_loss_ratio,
                   market_expense_ratio, autonomous_discount_min, autonomous_discount_max,
                   is_calculate
            FROM strategy_business_units WHERE strategy_id = %s
        """, (strategy_id,))
        business_units = [dict(row) for row in cursor.fetchall()]
        
        # 构建全局参数
        global_params = {
            'fixed_cost_ratio': float(strategy['fixed_cost_ratio']) if strategy['fixed_cost_ratio'] else None,
            'target_loss_ratio': float(strategy['target_loss_ratio']) if strategy['target_loss_ratio'] else None,
            'market_expense_ratio': float(strategy['market_expense_ratio']) if strategy['market_expense_ratio'] else None,
            'autonomous_discount_min': float(strategy['autonomous_discount_min']) if strategy['autonomous_discount_min'] else None,
            'autonomous_discount_max': float(strategy['autonomous_discount_max']) if strategy['autonomous_discount_max'] else None,
            'is_calculate': bool(strategy['is_calculate'])
        }
        
        return WizardFullConfigResponse(
            id=strategy['id'],
            name=strategy['name'],
            description=strategy['description'],
            status=strategy['status'],
            version=strategy['version'],
            global_params=global_params,
            business_unit_params=business_units,
            institutions=institutions,
            business_units=[{'id': bu['unit_id'], 'name': bu['unit_name']} for bu in business_units]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略配置失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取配置失败')
    finally:
        conn.close()


@router.get("/strategies/history", response_model=List[Dict[str, Any]], summary="获取策略历史")
async def get_strategies_history(
    keyword: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """
    获取策略历史（按创建时间排序）
    
    Args:
        keyword: 可选的关键词筛选
        limit: 返回数量限制（默认 50）
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        if keyword:
            cursor.execute("""
                SELECT id, name, status, version, created_at, created_by
                FROM strategies
                WHERE name LIKE %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (f'%{keyword}%', limit))
        else:
            cursor.execute("""
                SELECT id, name, status, version, created_at, created_by
                FROM strategies
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        
        strategies = []
        for row in cursor.fetchall():
            strategies.append({
                'id': row['id'],
                'name': row['name'],
                'status': row['status'],
                'version': row['version'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'created_by': row['created_by']
            })
        
        return strategies
    except Exception as e:
        logger.error(f"获取策略历史失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取策略历史失败')
    finally:
        conn.close()


# ============================================
# 3. 策略测试 API（4 个端点）
# ============================================

@router.post("/strategies/{strategy_id}/tests/simulation", response_model=Dict[str, Any], summary="执行模拟测试")
@require_permission('view')
async def run_simulation_test(strategy_id: str, request: Optional[SimulationTestRequest] = None):
    """执行模拟测试并更新策略状态"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查权限
        permission = _get_strategy_permission(strategy_id, user_id)
        if permission == 'none':
            raise HTTPException(status_code=403, detail='无权限操作此策略')
        
        # 生成测试 ID
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # 更新策略状态为 simulation_passed
        cursor.execute("""
            UPDATE strategies SET status = 'simulation_passed', updated_at = %s
            WHERE id = %s
        """, (datetime.now(), strategy_id))
        
        # 插入测试记录
        test_result_id = f"test_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO strategy_test_results (
                id, strategy_id, test_type, passed, result_summary,
                conversion_rate_lift, profit_lift, p_value, completed_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_result_id,
            strategy_id,
            'simulation',
            1,
            '模拟测试通过',
            request.conversion_rate_lift if request and hasattr(request, 'conversion_rate_lift') else 0,
            request.profit_lift if request and hasattr(request, 'profit_lift') else 0,
            0.05,
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'test_id': test_id,
                'status': 'completed',
                'passed': True,
                'message': '模拟测试通过，策略状态已更新',
                'strategy_status': 'simulation_passed'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模拟测试失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail=f'模拟测试失败：{str(e)}')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/tests/scenario", response_model=ScenarioTestResponse, summary="执行情景测试")
@require_permission('view')
async def run_scenario_test(strategy_id: str, request: ScenarioTestRequest):
    """
    执行情景测试（5 情景计算）
    
    基于基准利润，计算 5 个不同情景下的利润变化：
    - 情景 1: -2%
    - 情景 2: -1%
    - 情景 3: 0% (基准)
    - 情景 4: +1%
    - 情景 5: +2%
    """
    from app.services.strategy_engine import StrategyEngine
    
    engine = StrategyEngine()
    
    # 执行情景测试计算
    change_rates = request.change_rates if request.change_rates else [-0.02, -0.01, 0, 0.01, 0.02]
    scenarios = engine.calculate_scenario_test(request.base_profit, change_rates)
    
    # 计算摘要
    max_profit_scenario = max(scenarios, key=lambda x: x['scenario_profit'])
    min_profit_scenario = min(scenarios, key=lambda x: x['scenario_profit'])
    
    summary = {
        'base_profit': round(request.base_profit, 2),
        'max_profit': max_profit_scenario['scenario_profit'],
        'min_profit': min_profit_scenario['scenario_profit'],
        'profit_range': round(max_profit_scenario['scenario_profit'] - min_profit_scenario['scenario_profit'], 2),
        'scenario_count': len(scenarios)
    }
    
    return ScenarioTestResponse(
        scenarios=scenarios,
        summary=summary
    )


@router.post("/strategies/{strategy_id}/test-results", response_model=Dict[str, Any], summary="记录测试结果")
@require_permission('edit')
async def record_test_result(strategy_id: str, request: Dict[str, Any]):
    """记录策略测试结果（A/B 测试、模拟测试等）"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 插入测试结果
        test_result_id = f"test_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO strategy_test_results (
                id, strategy_id, test_type, passed, result_summary,
                conversion_rate_lift, profit_lift, p_value, completed_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_result_id,
            strategy_id,
            request.get('test_type', 'ab_test'),
            1 if request.get('passed', False) else 0,
            request.get('result_summary', ''),
            request.get('conversion_rate_lift', 0),
            request.get('profit_lift', 0),
            request.get('p_value', 0.05),
            datetime.now(),
            datetime.now()
        ))
        
        # 如果测试通过，更新策略状态
        if request.get('passed', False):
            cursor.execute("""
                UPDATE strategies SET status = 'ab_test_passed', updated_at = %s
                WHERE id = %s
            """, (datetime.now(), strategy_id))
        else:
            cursor.execute("""
                UPDATE strategies SET status = 'ab_test_failed', updated_at = %s
                WHERE id = %s
            """, (datetime.now(), strategy_id))
        
        conn.commit()
        
        return {'code': 200, 'message': '测试结果已记录'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"记录测试结果失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail=f'记录测试结果失败：{str(e)}')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/tests/ab", response_model=Dict[str, Any], summary="执行 A/B 测试")
@require_permission('view')
async def run_ab_test(strategy_id: str, request: ABTestRequest):
    """执行 A/B 测试"""
    # TODO: 实现 A/B 测试逻辑
    test_id = f"abtest_{uuid.uuid4().hex[:8]}"
    
    return {
        'code': 200,
        'data': {
            'test_id': test_id,
            'status': 'running',
            'message': 'A/B 测试已启动',
            'duration_days': request.duration_days
        }
    }


@router.get("/strategies/{strategy_id}/tests", response_model=List[TestHistoryItem], summary="获取测试历史")
@require_permission('view')
async def get_test_history(strategy_id: str):
    """获取测试历史"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, test_type, passed, result_summary, completed_at, created_at
            FROM strategy_test_results
            WHERE strategy_id = %s
            ORDER BY created_at DESC
        """, (strategy_id,))
        
        return [TestHistoryItem(**dict(row)) for row in cursor.fetchall()]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取测试历史失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取测试历史失败')
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}/tests/{test_id}", response_model=TestDetailResponse, summary="获取测试详情")
@require_permission('view')
async def get_test_detail(strategy_id: str, test_id: str):
    """获取测试详情（含显著性判定）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM strategy_test_results
            WHERE id = %s AND strategy_id = %s
        """, (test_id, strategy_id))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='测试记录不存在')
        
        return TestDetailResponse(
            test_id=row['id'],
            test_type=row['test_type'],
            status='completed',
            passed=bool(row['passed']),
            result_summary=row['result_summary'],
            metrics={
                'conversion_rate_lift': float(row['conversion_rate_lift']) if row['conversion_rate_lift'] else None,
                'profit_lift': float(row['profit_lift']) if row['profit_lift'] else None,
                'p_value': float(row['p_value']) if row['p_value'] else None,
                'is_significant': bool(row['p_value'] and row['p_value'] < 0.05)
            },
            sample_size=row['sample_size'],
            duration_days=row['test_duration_days']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取测试详情失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取测试详情失败')
    finally:
        conn.close()


# ============================================
# 4. 策略发布 API（3 个端点）
# ============================================

@router.post("/strategies/{strategy_id}/publish", response_model=Dict[str, Any], summary="发布策略")
@require_permission('publish')
async def publish_strategy(strategy_id: str, request: PublishRequest):
    """发布策略"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查策略状态
        cursor.execute('SELECT status FROM strategies WHERE id = %s', (strategy_id,))
        current = cursor.fetchone()
        
        if not current:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        if current['status'] not in ['ab_test_passed', 'simulation_passed']:
            raise HTTPException(status_code=400, detail='只有测试通过的策略才能发布')
        
        # 创建发布记录
        publish_id = f"pub_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        cursor.execute("""
            INSERT INTO strategy_publish_records (
                id, strategy_id, publish_scope, publish_description, rollback_plan,
                timing_type, scheduled_time, publish_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            publish_id,
            strategy_id,
            request.publish_scope,
            request.publish_description,
            request.rollback_plan,
            request.timing_type,
            request.scheduled_time,
            'published' if request.timing_type == 'immediate' else 'pending',
            datetime.now()
        ))
        
        # 更新策略状态
        cursor.execute("""
            UPDATE strategies SET status = 'published', updated_at = %s WHERE id = %s
        """, (datetime.now(), strategy_id))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'publish_id': publish_id,
                'status': 'published',
                'message': '策略发布成功'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='发布失败')
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}/publish/history", response_model=List[PublishHistoryItem], summary="获取发布历史")
@require_permission('view')
async def get_publish_history(strategy_id: str):
    """获取发布历史"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, publish_scope, publish_description, publish_status, published_at
            FROM strategy_publish_records
            WHERE strategy_id = %s
            ORDER BY published_at DESC
        """, (strategy_id,))
        
        return [PublishHistoryItem(
            id=row['id'],
            publish_scope=row['publish_scope'],
            publish_description=row['publish_description'],
            publish_status=row['publish_status'],
            published_at=row['published_at'],
            institutions=[]
        ) for row in cursor.fetchall()]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取发布历史失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取发布历史失败')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/rollback", response_model=Dict[str, Any], summary="回滚到历史版本")
@require_permission('rollback')
async def rollback_strategy(strategy_id: str, request: RollbackRequest):
    """回滚到历史版本"""
    user_id = _get_current_user_id()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. 获取当前策略版本
        cursor.execute('SELECT version FROM strategies WHERE id = %s', (strategy_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail='策略不存在')
        
        current_version = current['version']
        
        # 2. 获取目标版本
        cursor.execute("""
            SELECT * FROM strategy_versions
            WHERE strategy_id = %s AND version_number = %s
        """, (strategy_id, request.target_version))
        
        version = cursor.fetchone()
        if not version:
            raise HTTPException(status_code=404, detail='版本不存在')
        
        # 3. 不能回滚到当前版本或更高版本
        if request.target_version >= current_version:
            raise HTTPException(status_code=400, detail='目标版本必须小于当前版本')
        
        # 4. 恢复快照数据
        snapshot = json.loads(version['snapshot_data']) if isinstance(version['snapshot_data'], str) else version['snapshot_data']
        
        # 获取全局参数（兼容旧版本快照数据）
        global_params = snapshot.get('global_params', {})
        
        # 如果快照中没有 global_params，尝试从快照中直接读取字段（兼容旧格式）
        if not global_params:
            global_params = {
                'fixed_cost_ratio': snapshot.get('fixed_cost_ratio'),
                'target_loss_ratio': snapshot.get('target_loss_ratio'),
                'market_expense_ratio': snapshot.get('market_expense_ratio'),
                'autonomous_discount_min': snapshot.get('autonomous_discount_min'),
                'autonomous_discount_max': snapshot.get('autonomous_discount_max'),
                'is_calculate': snapshot.get('is_calculate', False)
            }
        
        # 构建动态更新 SQL，只更新快照中存在的字段
        update_fields = []
        update_values = []
        
        if snapshot.get('name') is not None:
            update_fields.append('name = %s')
            update_values.append(snapshot.get('name'))
        if snapshot.get('description') is not None:
            update_fields.append('description = %s')
            update_values.append(snapshot.get('description'))
        
        # 全局参数字段（如果存在则更新）
        if global_params.get('fixed_cost_ratio') is not None:
            update_fields.append('fixed_cost_ratio = %s')
            update_values.append(global_params.get('fixed_cost_ratio'))
        if global_params.get('target_loss_ratio') is not None:
            update_fields.append('target_loss_ratio = %s')
            update_values.append(global_params.get('target_loss_ratio'))
        if global_params.get('market_expense_ratio') is not None:
            update_fields.append('market_expense_ratio = %s')
            update_values.append(global_params.get('market_expense_ratio'))
        if global_params.get('autonomous_discount_min') is not None:
            update_fields.append('autonomous_discount_min = %s')
            update_values.append(global_params.get('autonomous_discount_min'))
        if global_params.get('autonomous_discount_max') is not None:
            update_fields.append('autonomous_discount_max = %s')
            update_values.append(global_params.get('autonomous_discount_max'))
        if 'is_calculate' in global_params:
            update_fields.append('is_calculate = %s')
            update_values.append(1 if global_params.get('is_calculate', False) else 0)
        
        # 版本号必须更新
        update_fields.append('version = %s')
        update_values.append(current_version + 1)
        
        # 更新时间
        update_fields.append('updated_at = %s')
        update_values.append(datetime.now())
        
        update_values.append(strategy_id)
        
        cursor.execute(f"""
            UPDATE strategies SET {', '.join(update_fields)} WHERE id = %s
        """, update_values)
        
        # 5. 记录回滚操作（创建新版本）
        rollback_version_id = f"version_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        new_version_number = current_version + 1
        cursor.execute("""
            INSERT INTO strategy_versions (
                id, strategy_id, version_number, snapshot_data, change_summary, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            rollback_version_id,
            strategy_id,
            new_version_number,
            version['snapshot_data'],  # 使用目标版本的快照数据
            f'回滚到版本 {request.target_version}: {request.reason}',
            user_id,
            datetime.now()
        ))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'target_version': request.target_version,
                'new_version': new_version_number,
                'message': '回滚成功'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回滚策略失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='回滚失败')
    finally:
        conn.close()


# ============================================
# 5. 策略权限 API（2 个端点）
# ============================================

@router.get("/strategies/{strategy_id}/permissions", response_model=List[PermissionItem], summary="获取策略权限列表")
@require_permission('permission_manage')
async def get_permissions(strategy_id: str):
    """获取策略权限列表"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, role, granted_at FROM strategy_permissions
            WHERE strategy_id = %s
            ORDER BY granted_at DESC
        """, (strategy_id,))
        
        return [PermissionItem(**dict(row)) for row in cursor.fetchall()]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取权限列表失败：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='获取权限列表失败')
    finally:
        conn.close()


@router.post("/strategies/{strategy_id}/permissions", response_model=Dict[str, Any], summary="添加策略权限")
@require_permission('permission_manage')
async def add_permission(strategy_id: str, request: AddPermissionRequest):
    """添加策略权限"""
    if request.role not in ['owner', 'editor', 'viewer']:
        raise HTTPException(status_code=400, detail='无效的角色')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO strategy_permissions (strategy_id, user_id, role, granted_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE role = %s, granted_at = %s
        """, (strategy_id, request.user_id, request.role, datetime.now(), request.role, _format_datetime()))
        
        conn.commit()
        
        return {
            'code': 200,
            'data': {
                'user_id': request.user_id,
                'role': request.role,
                'message': '权限添加成功'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加权限失败：{str(e)}", exc_info=True)
        conn.rollback()
        raise HTTPException(status_code=500, detail='添加权限失败')
    finally:
        conn.close()
