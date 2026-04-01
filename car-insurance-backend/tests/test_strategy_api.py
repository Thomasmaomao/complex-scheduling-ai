"""
策略管理 API 单元测试
测试覆盖率目标：≥80%
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import get_db_connection

client = TestClient(app)

# ============================================
# Fixtures
# ============================================

@pytest.fixture
def test_strategy():
    """创建测试策略"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        strategy_id = f"strategy_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建测试策略
        cursor.execute("""
            INSERT INTO strategies (
                id, name, description, status, version, created_by, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            strategy_id,
            '测试策略',
            '用于单元测试',
            'draft',
            1,
            'system',
            datetime.now(),
            datetime.now()
        ))
        
        # 创建权限
        cursor.execute("""
            INSERT INTO strategy_permissions (strategy_id, user_id, role, granted_at)
            VALUES (%s, %s, %s, %s)
        """, (strategy_id, 'system', 'owner', datetime.now()))
        
        # 创建初始版本记录（用于回滚测试）
        import json
        cursor.execute("""
            INSERT INTO strategy_versions (
                id, strategy_id, version_number, snapshot_data, change_summary, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            f'version_{strategy_id}_v1',
            strategy_id,
            1,
            json.dumps({'name': '测试策略', 'description': '用于单元测试'}),
            '初始创建',
            'system',
            datetime.now()
        ))
        
        conn.commit()
        
        yield strategy_id
        
        # 清理
        cursor.execute('DELETE FROM strategy_versions WHERE strategy_id = %s', (strategy_id,))
        cursor.execute('DELETE FROM strategy_permissions WHERE strategy_id = %s', (strategy_id,))
        cursor.execute('DELETE FROM strategies WHERE id = %s', (strategy_id,))
        conn.commit()
    finally:
        conn.close()


# ============================================
# 策略总览 API 测试
# ============================================

class TestStrategyOverview:
    """策略总览 API 测试"""
    
    def test_list_strategies_success(self):
        """测试获取策略列表 - 成功"""
        response = client.get('/api/v1/strategy/strategies?page=1&page_size=20')
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'strategies' in data
        assert isinstance(data['strategies'], list)
    
    def test_list_strategies_with_filter(self):
        """测试获取策略列表 - 带筛选"""
        response = client.get('/api/v1/strategy/strategies?status=draft&page=1')
        assert response.status_code == 200
        data = response.json()
        assert data['page'] == 1
    
    def test_list_strategies_invalid_status(self):
        """测试获取策略列表 - 无效状态"""
        response = client.get('/api/v1/strategy/strategies?status=invalid_status')
        assert response.status_code == 400
    
    def test_list_strategies_invalid_sort_field(self):
        """测试获取策略列表 - 无效排序字段"""
        response = client.get('/api/v1/strategy/strategies?sort_by=invalid_field')
        assert response.status_code == 400
    
    def test_create_strategy_success(self):
        """测试创建策略 - 成功"""
        payload = {
            'name': f'新策略_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'description': '测试创建',
            'institutions': [
                {'code': 'shanghai', 'name': '上海'}
            ]
        }
        response = client.post('/api/v1/strategy/strategies', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'id' in data['data']
        assert data['data']['status'] == 'draft'
        assert data['data']['permission'] == 'owner'
    
    def test_create_strategy_empty_name(self):
        """测试创建策略 - 空名称"""
        payload = {'name': '', 'institutions': []}
        response = client.post('/api/v1/strategy/strategies', json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_strategy_detail_success(self, test_strategy):
        """测试获取策略详情 - 成功"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_strategy
        assert 'name' in data
        assert 'status' in data
        assert 'version' in data
    
    def test_get_strategy_detail_not_found(self):
        """测试获取策略详情 - 不存在"""
        response = client.get('/api/v1/strategy/strategies/non_existent_id')
        assert response.status_code == 404
    
    def test_update_strategy_success(self, test_strategy):
        """测试更新策略 - 成功"""
        # 先获取当前版本
        detail_response = client.get(f'/api/v1/strategy/strategies/{test_strategy}')
        current_version = detail_response.json()['version']
        
        payload = {
            'name': '更新后的策略名称',
            'description': '更新的描述',
            'expected_version': current_version
        }
        response = client.put(f'/api/v1/strategy/strategies/{test_strategy}', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['version'] == current_version + 1
    
    def test_update_strategy_conflict(self, test_strategy):
        """测试更新策略 - 版本冲突"""
        payload = {
            'name': '更新后的名称',
            'expected_version': 999  # 错误的版本号
        }
        response = client.put(f'/api/v1/strategy/strategies/{test_strategy}', json=payload)
        assert response.status_code == 409
    
    def test_update_strategy_status_disable(self, test_strategy):
        """测试禁用策略"""
        payload = {'status': 'disabled'}
        response = client.patch(f'/api/v1/strategy/strategies/{test_strategy}/status', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['data']['status'] == 'disabled'
        
        # 恢复为 draft
        payload = {'status': 'draft'}
        client.patch(f'/api/v1/strategy/strategies/{test_strategy}/status', json=payload)
    
    def test_update_strategy_status_invalid(self, test_strategy):
        """测试更新策略状态 - 无效状态"""
        payload = {'status': 'invalid_status'}
        response = client.patch(f'/api/v1/strategy/strategies/{test_strategy}/status', json=payload)
        assert response.status_code == 400
    
    def test_delete_strategy_success(self, test_strategy):
        """测试删除策略 - 成功（软删除）"""
        response = client.delete(f'/api/v1/strategy/strategies/{test_strategy}')
        assert response.status_code == 200
        data = response.json()
        assert data['data']['status'] == 'disabled'


# ============================================
# 策略向导 API 测试
# ============================================

class TestStrategyWizard:
    """策略向导 API 测试"""
    
    def test_wizard_step_basic_success(self, test_strategy):
        """测试步骤 0：保存基本信息"""
        payload = {
            'name': '测试策略名称',
            'description': '测试描述'
        }
        response = client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/basic',
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
    
    def test_wizard_step_business_unit_success(self, test_strategy):
        """测试步骤 1：业务单元划分"""
        payload = {
            'business_units': [
                {'id': 'BU001', 'name': '燃油车 - 续保'},
                {'id': 'BU002', 'name': '燃油车 - 新保'}
            ]
        }
        response = client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/business-unit',
            json=payload
        )
        assert response.status_code == 200
    
    def test_wizard_step_cost_simulation_success(self, test_strategy):
        """测试步骤 2：成本模拟参数"""
        payload = {
            'global_params': {
                'fixed_cost_ratio': 0.10,
                'target_loss_ratio': 0.75,
                'market_expense_ratio': 0.12,
                'autonomous_discount_min': 0.50,
                'autonomous_discount_max': 0.65,
                'is_calculate': True
            },
            'business_unit_params': [
                {
                    'unit_id': 'BU001',
                    'fixed_cost_ratio': 0.10,
                    'target_loss_ratio': 0.72,
                    'market_expense_ratio': 0.10,
                    'autonomous_discount_min': 0.55,
                    'autonomous_discount_max': 0.60,
                    'is_calculate': True
                }
            ]
        }
        response = client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/cost-simulation',
            json=payload
        )
        assert response.status_code == 200
    
    def test_wizard_step_cost_simulation_validation_error(self, test_strategy):
        """测试步骤 2：参数校验错误"""
        payload = {
            'global_params': {
                'fixed_cost_ratio': 1.5,  # 超出范围 0-1
                'target_loss_ratio': 0.75,
                'market_expense_ratio': 0.12,
                'autonomous_discount_min': 0.50,
                'autonomous_discount_max': 0.40,  # 下限 > 上限
                'is_calculate': True
            }
        }
        response = client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/cost-simulation',
            json=payload
        )
        assert response.status_code == 400
    
    def test_wizard_step_revenue_simulation(self, test_strategy):
        """测试步骤 3：收益模拟"""
        payload = {
            'adjusted_params': {'fixed_cost_ratio': 0.12},
            'simulation_scope': 'all'
        }
        response = client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/revenue-simulation',
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert 'simulation_id' in data['data']
    
    def test_wizard_confirm_success(self, test_strategy):
        """测试步骤 4：确认保存"""
        # 先完成前面的步骤
        client.post(
            f'/api/v1/strategy/strategies/{test_strategy}/wizard/step/basic',
            json={'name': '测试', 'description': '测试'}
        )
        
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/wizard/confirm')
        assert response.status_code == 200
        data = response.json()
        assert data['version'] > 1
        # 修复后状态为 simulation_passed（有效状态）
        assert data['status'] == 'simulation_passed'
    
    def test_get_wizard_config(self, test_strategy):
        """测试获取策略完整配置"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}/wizard')
        assert response.status_code == 200
        data = response.json()
        assert 'global_params' in data
        assert 'business_unit_params' in data
        assert 'institutions' in data


# ============================================
# 策略测试 API 测试
# ============================================

class TestStrategyTests:
    """策略测试 API 测试"""
    
    def test_run_simulation_test(self, test_strategy):
        """测试执行模拟测试"""
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/tests/simulation')
        assert response.status_code == 200
        data = response.json()
        assert 'test_id' in data['data']
    
    def test_run_ab_test(self, test_strategy):
        """测试执行 A/B 测试"""
        payload = {
            'traffic_split': 50,
            'duration_days': 14,
            'institutions': ['上海', '北京'],
            'business_units': ['BU001', 'BU002']
        }
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/tests/ab', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'test_id' in data['data']
    
    def test_get_test_history(self, test_strategy):
        """测试获取测试历史"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}/tests')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_test_detail_not_found(self, test_strategy):
        """测试获取测试详情 - 不存在"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}/tests/non_existent_test')
        assert response.status_code == 404


# ============================================
# 策略发布 API 测试
# ============================================

class TestStrategyPublish:
    """策略发布 API 测试"""
    
    def test_publish_strategy_not_passed(self, test_strategy):
        """测试发布策略 - 未通过测试"""
        payload = {
            'publish_scope': 'specified',
            'publish_description': '正式发布',
            'rollback_plan': '回滚预案',
            'timing_type': 'immediate',
            'institutions': [{'code': 'shanghai', 'name': '上海'}]
        }
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/publish', json=payload)
        # 策略状态为 draft，不能发布
        assert response.status_code == 400
    
    def test_get_publish_history(self, test_strategy):
        """测试获取发布历史"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}/publish/history')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_rollback_strategy(self, test_strategy):
        """测试回滚策略"""
        # 先创建一个版本
        client.post(f'/api/v1/strategy/strategies/{test_strategy}/wizard/confirm')
        
        payload = {
            'target_version': 1,
            'reason': '测试回滚'
        }
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/rollback', json=payload)
        assert response.status_code == 200


# ============================================
# 策略权限 API 测试
# ============================================

class TestStrategyPermissions:
    """策略权限 API 测试"""
    
    def test_get_permissions(self, test_strategy):
        """测试获取权限列表"""
        response = client.get(f'/api/v1/strategy/strategies/{test_strategy}/permissions')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_add_permission_success(self, test_strategy):
        """测试添加权限 - 成功"""
        payload = {
            'user_id': 'new_user',
            'role': 'editor'
        }
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/permissions', json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['data']['role'] == 'editor'
    
    def test_add_permission_invalid_role(self, test_strategy):
        """测试添加权限 - 无效角色"""
        payload = {
            'user_id': 'new_user',
            'role': 'invalid_role'
        }
        response = client.post(f'/api/v1/strategy/strategies/{test_strategy}/permissions', json=payload)
        assert response.status_code == 400


# ============================================
# 中间件测试
# ============================================

class TestMiddleware:
    """中间件测试"""
    
    def test_optimistic_lock_check_version(self):
        """测试乐观锁版本校验"""
        from app.core.middleware import OptimisticLock
        
        # 测试不存在的策略
        with pytest.raises(Exception) as exc_info:
            OptimisticLock.check_version('non_existent_strategy', 1)
        assert exc_info.value.status_code == 404
    
    def test_strategy_validator_valid_params(self):
        """测试策略参数校验 - 有效参数"""
        from app.core.middleware import StrategyValidator
        
        params = {
            'fixed_cost_ratio': 0.10,
            'target_loss_ratio': 0.75,
            'market_expense_ratio': 0.12,
            'autonomous_discount_min': 0.50,
            'autonomous_discount_max': 0.65
        }
        errors = StrategyValidator.validate_params(params)
        assert len(errors) == 0
    
    def test_strategy_validator_invalid_range(self):
        """测试策略参数校验 - 范围错误"""
        from app.core.middleware import StrategyValidator
        
        params = {'fixed_cost_ratio': 1.5}  # 超出 0-1 范围
        errors = StrategyValidator.validate_params(params)
        assert len(errors) > 0
    
    def test_strategy_validator_min_greater_than_max(self):
        """测试策略参数校验 - 下限大于上限"""
        from app.core.middleware import StrategyValidator
        
        params = {
            'autonomous_discount_min': 0.70,
            'autonomous_discount_max': 0.60
        }
        errors = StrategyValidator.validate_params(params)
        assert any('下限不能大于上限' in error for error in errors)
    
    def test_status_transition_valid(self):
        """测试状态流转校验 - 有效流转"""
        from app.api.strategy import _validate_status_transition
        
        assert _validate_status_transition('draft', 'simulation_passed') is True
        assert _validate_status_transition('simulation_passed', 'ab_test_passed') is True
        assert _validate_status_transition('ab_test_passed', 'published') is True
    
    def test_status_transition_invalid(self):
        """测试状态流转校验 - 无效流转"""
        from app.api.strategy import _validate_status_transition
        
        assert _validate_status_transition('draft', 'published') is False
        assert _validate_status_transition('published', 'draft') is False


# ============================================
# 运行测试
# ============================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=app/api/strategy', '--cov-report=html'])
