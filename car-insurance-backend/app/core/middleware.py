"""
策略管理中间件
包含权限控制、并发控制、数据校验等功能
"""
from functools import wraps
from fastapi import HTTPException, status, Request
from typing import Optional, Dict, Any, List
import logging

from app.core.database import get_db_connection
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================
# 权限控制中间件
# ============================================

class PermissionChecker:
    """权限校验器"""
    
    # 角色层级（数字越大权限越高）
    ROLE_HIERARCHY = {
        'viewer': 0,
        'editor': 1,
        'owner': 2,
        'admin': 3
    }
    
    # API 操作所需的最低角色
    OPERATION_ROLES = {
        'view': 'viewer',
        'create': 'owner',
        'edit': 'editor',
        'delete': 'owner',
        'publish': 'owner',
        'rollback': 'owner',
        'permission_manage': 'owner'
    }
    
    @classmethod
    def check_permission(cls, strategy_id: str, user_id: str, required_operation: str = 'view') -> bool:
        """
        检查用户是否有权限操作策略
        
        Args:
            strategy_id: 策略 ID
            user_id: 用户 ID
            required_operation: 操作类型（view/create/edit/delete/publish/rollback/permission_manage）
            
        Returns:
            是否有权限
            
        Raises:
            HTTPException: 无权限时抛出 403 错误
        """
        # 管理员拥有所有权限
        if cls._is_admin(user_id):
            return True
        
        # 创建操作不需要检查策略权限（会在路由层检查）
        if required_operation == 'create':
            return True
        
        # 查询用户权限
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT role FROM strategy_permissions WHERE strategy_id = %s AND user_id = %s',
                (strategy_id, user_id)
            )
            result = cursor.fetchone()
            
            if not result:
                # 用户无任何权限
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='无权限操作此策略'
                )
            
            user_role = result['role']
            required_role = cls.OPERATION_ROLES.get(required_operation, 'viewer')
            
            # 检查角色层级
            if cls.ROLE_HIERARCHY.get(user_role, 0) < cls.ROLE_HIERARCHY.get(required_role, 0):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f'无权限执行此操作，需要 {required_role} 或更高权限'
                )
            
            return True
        finally:
            conn.close()
    
    @staticmethod
    def _is_admin(user_id: str) -> bool:
        """检查用户是否为管理员"""
        # TODO: 实现管理员检查逻辑
        # 目前简单返回 False，实际应从用户服务获取
        return False
    
    @classmethod
    def get_user_role(cls, strategy_id: str, user_id: str) -> Optional[str]:
        """获取用户在策略中的角色"""
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


def require_permission(required_operation: str = 'view'):
    """
    权限校验装饰器
    
    Usage:
        @router.get("/strategies/{id}")
        @require_permission('view')
        async def get_strategy(request: Request, strategy_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取 strategy_id 和 user_id
            strategy_id = kwargs.get('strategy_id')
            
            # TODO: 从 request 或 token 中获取 user_id
            # 目前从 settings 获取默认用户
            user_id = getattr(settings, 'CURRENT_USER_ID', 'system')
            
            if strategy_id:
                PermissionChecker.check_permission(strategy_id, user_id, required_operation)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================
# 并发控制（乐观锁）
# ============================================

class OptimisticLock:
    """乐观锁校验器"""
    
    @staticmethod
    def check_version(strategy_id: str, expected_version: int) -> int:
        """
        校验版本号并返回当前版本
        
        Args:
            strategy_id: 策略 ID
            expected_version: 期望的版本号
            
        Returns:
            当前版本号
            
        Raises:
            HTTPException: 版本冲突时抛出 409 错误
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 获取当前版本
            cursor.execute('SELECT version FROM strategies WHERE id = %s', (strategy_id,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='策略不存在'
                )
            
            current_version = result['version']
            
            # 校验版本
            if expected_version != current_version:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        'code': 'CONFLICT',
                        'message': '策略已被其他人修改，请刷新后重试',
                        'current_version': current_version,
                        'expected_version': expected_version
                    }
                )
            
            return current_version
        finally:
            conn.close()
    
    @staticmethod
    def update_with_version(
        strategy_id: str,
        update_fields: Dict[str, Any],
        expected_version: int
    ) -> bool:
        """
        带版本号校验的更新操作
        
        Args:
            strategy_id: 策略 ID
            update_fields: 要更新的字段
            expected_version: 期望的版本号
            
        Returns:
            是否更新成功
            
        Raises:
            HTTPException: 版本冲突时抛出 409 错误
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 构建更新 SQL
            set_clause = ', '.join([f"{field} = %s" for field in update_fields.keys()])
            values = list(update_fields.values())
            
            # 增加版本号
            values.append(strategy_id)
            values.append(expected_version)
            
            sql = f"""
                UPDATE strategies 
                SET {set_clause}, version = version + 1, updated_at = %s
                WHERE id = %s AND version = %s
            """
            values.append(__import__('datetime').datetime.now())
            
            cursor.execute(sql, values)
            
            if cursor.rowcount == 0:
                # 获取当前版本用于错误信息
                cursor.execute('SELECT version FROM strategies WHERE id = %s', (strategy_id,))
                result = cursor.fetchone()
                current_version = result['version'] if result else 'unknown'
                
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        'code': 'CONFLICT',
                        'message': '策略已被其他人修改，请刷新后重试',
                        'current_version': current_version,
                        'expected_version': expected_version
                    }
                )
            
            conn.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            logger.error(f"乐观锁更新失败：{str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='更新失败'
            )
        finally:
            conn.close()


# ============================================
# 数据校验中间件
# ============================================

class StrategyValidator:
    """策略数据校验器"""
    
    # 字段校验规则
    FIELD_RULES = {
        'fixed_cost_ratio': {'min': 0, 'max': 1, 'required': False},
        'target_loss_ratio': {'min': 0, 'max': 1, 'required': False},
        'market_expense_ratio': {'min': 0, 'max': 1, 'required': False},
        'autonomous_discount_min': {'min': 0.5, 'max': 1.5, 'required': False},
        'autonomous_discount_max': {'min': 0.5, 'max': 1.5, 'required': False},
        'is_calculate': {'values': [0, 1, True, False], 'required': False},
    }
    
    @classmethod
    def validate_params(cls, params: Dict[str, Any]) -> List[str]:
        """
        校验策略参数
        
        Args:
            params: 参数字典
            
        Returns:
            错误信息列表，空列表表示校验通过
        """
        errors = []
        
        # 字段范围校验
        for field, value in params.items():
            if value is None:
                continue
                
            rule = cls.FIELD_RULES.get(field)
            if not rule:
                continue
            
            # 范围校验
            if 'min' in rule and 'max' in rule:
                if not isinstance(value, (int, float)):
                    errors.append(f'{field} 必须是数字')
                elif value < rule['min'] or value > rule['max']:
                    errors.append(f'{field} 必须在 {rule["min"]}-{rule["max"]} 之间')
            
            # 枚举值校验
            if 'values' in rule:
                if value not in rule['values']:
                    errors.append(f'{field} 必须是 {rule["values"]} 之一')
        
        # 业务规则校验
        if 'autonomous_discount_min' in params and 'autonomous_discount_max' in params:
            min_val = params['autonomous_discount_min']
            max_val = params['autonomous_discount_max']
            if min_val is not None and max_val is not None and min_val > max_val:
                errors.append('自主系数下限不能大于上限')
        
        # 总和校验（可选）
        total = sum(
            params.get(field, 0) or 0 
            for field in ['fixed_cost_ratio', 'target_loss_ratio', 'market_expense_ratio']
        )
        if total > 1:
            errors.append('固定成本率 + 目标赔付率 + 市场费用率 不能大于 1')
        
        return errors
    
    @classmethod
    def validate_business_unit_params(cls, bu_params: List[Dict[str, Any]]) -> List[str]:
        """
        校验业务单元参数
        
        Args:
            bu_params: 业务单元参数列表
            
        Returns:
            错误信息列表
        """
        errors = []
        
        for i, params in enumerate(bu_params):
            field_errors = cls.validate_params(params)
            for error in field_errors:
                errors.append(f'业务单元 {i+1}: {error}')
        
        return errors
    
    @classmethod
    def validate_institutions(cls, institutions: List[Dict[str, str]]) -> List[str]:
        """校验机构列表"""
        errors = []
        
        if not institutions:
            errors.append('至少需要选择一个机构')
            return errors
        
        for i, inst in enumerate(institutions):
            if not inst.get('code'):
                errors.append(f'机构 {i+1} 缺少 code 字段')
            if not inst.get('name'):
                errors.append(f'机构 {i+1} 缺少 name 字段')
        
        return errors


def validate_strategy_data(data: Dict[str, Any]) -> None:
    """
    校验策略数据装饰器
    
    Raises:
        HTTPException: 校验失败时抛出 400 错误
    """
    errors = StrategyValidator.validate_params(data)
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'code': 'VALIDATION_ERROR',
                'errors': errors
            }
        )


# ============================================
# 统一错误处理
# ============================================

class StrategyErrorCodes:
    """策略模块错误码定义"""
    
    SUCCESS = ('200', '操作成功')
    VALIDATION_ERROR = ('400', '参数校验失败')
    FORBIDDEN = ('403', '无权限操作')
    NOT_FOUND = ('404', '资源不存在')
    CONFLICT = ('409', '并发冲突（版本不一致）')
    INTERNAL_ERROR = ('500', '服务器内部错误')
    STATUS_TRANSITION_ERROR = ('400', '不允许的状态流转')
    TEST_NOT_PASSED = ('400', '测试未通过，无法发布')
    VERSION_NOT_FOUND = ('404', '版本不存在')


def create_error_response(error_code: tuple, detail: Optional[str] = None) -> Dict[str, Any]:
    """创建统一错误响应"""
    code, message = error_code
    return {
        'code': int(code),
        'error_code': code,
        'message': detail or message
    }
