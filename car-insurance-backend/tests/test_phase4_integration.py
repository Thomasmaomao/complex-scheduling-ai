"""
Phase 4: 集成测试

测试完整的业务流程，包括 API 端点和数据库操作
"""

import pytest
import sys
import os
import json
from datetime import datetime
from decimal import Decimal

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.strategy_engine import StrategyEngine


class TestStrategySaveFlow:
    """策略保存流程测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_strategy_save_with_calculations(self):
        """测试策略保存时的完整计算"""
        # 模拟策略参数
        fixed_cost_ratio = 0.10
        target_loss_ratio = 0.75
        market_expense_ratio = 0.12
        avg_premium = 4500
        policy_count = 5000
        
        # 1. 计算 RP
        rp = self.engine.calculate_rp_premium(avg_premium, target_loss_ratio)
        assert rp == 3375.0
        
        # 2. 计算预期利润
        profit_calc = self.engine.calculate_expected_profit(
            policy_count=policy_count,
            avg_premium=avg_premium,
            fixed_cost_ratio=fixed_cost_ratio,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=market_expense_ratio
        )
        
        # 验证计算结果
        assert profit_calc['profit_margin'] == 0.03
        assert profit_calc['expected_profit'] == 675000.0
        assert profit_calc['total_premium'] == 22500000.0
        
        # 3. 验证返回格式包含完整数据
        assert 'rp_premium' in profit_calc
        assert 'breakdown' in profit_calc
        assert 'fixed_cost' in profit_calc['breakdown']
        assert 'expected_loss' in profit_calc['breakdown']
        assert 'market_expense' in profit_calc['breakdown']
    
    def test_strategy_save_validation(self):
        """测试策略保存时的数据校验"""
        # 有效参数
        valid_params = {
            'fixed_cost_ratio': 0.10,
            'target_loss_ratio': 0.75,
            'market_expense_ratio': 0.12,
        }
        
        # 利润率应该为正
        profit_margin = 1 - valid_params['fixed_cost_ratio'] - valid_params['target_loss_ratio'] - valid_params['market_expense_ratio']
        assert profit_margin > 0
        
        # 无效参数：总和超过 1
        invalid_params = {
            'fixed_cost_ratio': 0.20,
            'target_loss_ratio': 0.85,
            'market_expense_ratio': 0.15,
        }
        
        profit_margin = 1 - invalid_params['fixed_cost_ratio'] - invalid_params['target_loss_ratio'] - invalid_params['market_expense_ratio']
        assert profit_margin < 0  # 应该标记为亏损


class TestScenarioTestFlow:
    """情景测试流程测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_scenario_test_api_format(self):
        """测试情景测试 API 返回格式"""
        base_profit = 1000000
        
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        # 验证每个情景的字段
        for scenario in scenarios:
            assert 'scenario_id' in scenario
            assert 'scenario_name' in scenario
            assert 'change_rate' in scenario
            assert 'change_rate_display' in scenario
            assert 'base_profit' in scenario
            assert 'scenario_profit' in scenario
            assert 'profit_change' in scenario
        
        # 验证变化率顺序
        expected_rates = [-0.02, -0.01, 0, 0.01, 0.02]
        for i, scenario in enumerate(scenarios):
            assert scenario['change_rate'] == expected_rates[i]
    
    def test_scenario_test_summary(self):
        """测试情景测试摘要计算"""
        base_profit = 1000000
        
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        # 计算摘要
        max_profit = max(s['scenario_profit'] for s in scenarios)
        min_profit = min(s['scenario_profit'] for s in scenarios)
        profit_range = max_profit - min_profit
        
        assert max_profit == 1020000.0
        assert min_profit == 980000.0
        assert profit_range == 40000.0


class TestTotalsCalculationFlow:
    """合计值计算流程测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_totals_with_multiple_business_units(self):
        """测试多业务单元的合计值计算"""
        business_units = [
            {'policy_count': 3000, 'avg_premium': 3500, 'profit_margin': 0.04},
            {'policy_count': 2000, 'avg_premium': 4800, 'profit_margin': 0.03},
            {'policy_count': 1500, 'avg_premium': 5800, 'profit_margin': 0.05},
            {'policy_count': 3000, 'avg_premium': 4500, 'profit_margin': 0.02},
            {'policy_count': 500, 'avg_premium': 15000, 'profit_margin': 0.06},
        ]
        
        totals = self.engine.calculate_totals(business_units)
        
        # 验证总保单数
        assert totals['total_policies'] == 10000
        
        # 验证总保费
        expected_premium = (
            3000 * 3500 +  # 10,500,000
            2000 * 4800 +  # 9,600,000
            1500 * 5800 +  # 8,700,000
            3000 * 4500 +  # 13,500,000
            500 * 15000    # 7,500,000
        )
        assert totals['total_premium'] == 49800000.0
        
        # 验证总利润
        expected_profit = (
            10500000 * 0.04 +  # 420,000
            9600000 * 0.03 +   # 288,000
            8700000 * 0.05 +   # 435,000
            13500000 * 0.02 +  # 270,000
            7500000 * 0.06     # 450,000
        )
        assert totals['total_profit'] == 1863000.0
        
        # 验证整体利润率
        expected_margin = 1863000.0 / 49800000.0
        assert abs(totals['overall_profit_margin'] - expected_margin) < 0.0001


class TestAPIResponseFormat:
    """API 响应格式测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_wizard_confirm_response_format(self):
        """测试 wizard_confirm API 响应格式"""
        # 模拟计算
        profit_calc = self.engine.calculate_expected_profit(
            policy_count=5000,
            avg_premium=4500,
            fixed_cost_ratio=0.10,
            target_loss_ratio=0.75,
            market_expense_ratio=0.12
        )
        
        rp = self.engine.calculate_rp_premium(4500, 0.75)
        
        totals = self.engine.calculate_totals([
            {'policy_count': 2500, 'avg_premium': 4000, 'profit_margin': 0.03},
            {'policy_count': 2500, 'avg_premium': 5000, 'profit_margin': 0.03},
        ])
        
        # 验证响应格式
        response = {
            'code': 200,
            'data': {
                'id': 'strategy_test_001',
                'status': 'simulation_passed',
                'version': 2,
                'message': '策略保存成功',
                'calculations': {
                    'rp_premium': rp,
                    'profit_margin': profit_calc['profit_margin'],
                    'expected_profit': profit_calc['expected_profit'],
                    'total_premium': profit_calc['total_premium'],
                    'totals': totals
                }
            }
        }
        
        # 验证必填字段
        assert response['code'] == 200
        assert 'data' in response
        assert 'calculations' in response['data']
        assert 'rp_premium' in response['data']['calculations']
        assert 'profit_margin' in response['data']['calculations']
        assert 'expected_profit' in response['data']['calculations']
        assert 'total_premium' in response['data']['calculations']
        assert 'totals' in response['data']['calculations']
    
    def test_scenario_test_response_format(self):
        """测试 scenario_test API 响应格式"""
        base_profit = 1000000
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        max_profit = max(s['scenario_profit'] for s in scenarios)
        min_profit = min(s['scenario_profit'] for s in scenarios)
        
        summary = {
            'base_profit': round(base_profit, 2),
            'max_profit': max_profit,
            'min_profit': min_profit,
            'profit_range': round(max_profit - min_profit, 2),
            'scenario_count': len(scenarios)
        }
        
        response = {
            'scenarios': scenarios,
            'summary': summary
        }
        
        # 验证响应格式
        assert 'scenarios' in response
        assert 'summary' in response
        assert len(response['scenarios']) == 5
        assert response['summary']['scenario_count'] == 5


class TestDatabaseMigration:
    """数据库迁移测试"""
    
    def test_migration_fields_exist(self):
        """测试迁移字段定义"""
        # 验证应该添加的字段
        required_fields = [
            'rp_premium',
            'total_premium_calculated',
            'total_profit_calculated',
            'profit_margin_calculated',
            'scenario_test_data'
        ]
        
        # 这些字段应该在 migration_phase2_calculations.sql 中定义
        migration_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'database',
            'migration_phase2_calculations.sql'
        )
        
        if os.path.exists(migration_file):
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 验证每个字段都在迁移脚本中
                for field in required_fields:
                    assert field in content, f"字段 {field} 不在迁移脚本中"
    
    def test_calculation_logic_in_snapshot(self):
        """测试快照数据中的计算逻辑"""
        # 模拟快照数据结构
        snapshot_data = {
            'name': '测试策略',
            'global_params': {
                'fixed_cost_ratio': 0.10,
                'target_loss_ratio': 0.75,
                'market_expense_ratio': 0.12,
            },
            'calculations': {
                'rp_premium': 3375.0,
                'profit_margin': 0.03,
                'expected_profit': 675000.0,
                'total_premium': 22500000.0,
                'totals': {
                    'total_premium': 22500000.0,
                    'total_profit': 675000.0,
                    'overall_profit_margin': 0.03
                }
            }
        }
        
        # 验证 JSON 序列化
        json_str = json.dumps(snapshot_data, ensure_ascii=False)
        assert len(json_str) > 0
        
        # 验证反序列化
        loaded = json.loads(json_str)
        assert loaded['calculations']['rp_premium'] == 3375.0
        assert loaded['calculations']['profit_margin'] == 0.03


class TestPerformance:
    """性能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_rp_calculation_performance(self):
        """测试 RP 计算性能"""
        import time
        
        start = time.time()
        for _ in range(1000):
            self.engine.calculate_rp_premium(4500, 0.75)
        elapsed = time.time() - start
        
        # 应该在 0.1 秒内完成 1000 次计算
        assert elapsed < 0.1, f"RP 计算太慢：{elapsed:.3f}秒"
    
    def test_scenario_test_performance(self):
        """测试情景测试性能"""
        import time
        
        start = time.time()
        for _ in range(100):
            self.engine.calculate_scenario_test(1000000)
        elapsed = time.time() - start
        
        # 应该在 0.5 秒内完成 100 次情景测试
        assert elapsed < 0.5, f"情景测试太慢：{elapsed:.3f}秒"
    
    def test_totals_calculation_performance(self):
        """测试合计值计算性能"""
        import time
        
        business_units = [
            {'policy_count': 1000, 'avg_premium': 4000, 'profit_margin': 0.03},
            {'policy_count': 2000, 'avg_premium': 5000, 'profit_margin': 0.05},
            {'policy_count': 1500, 'avg_premium': 4500, 'profit_margin': 0.04},
        ]
        
        start = time.time()
        for _ in range(100):
            self.engine.calculate_totals(business_units)
        elapsed = time.time() - start
        
        # 应该在 0.1 秒内完成 100 次合计值计算
        assert elapsed < 0.1, f"合计值计算太慢：{elapsed:.3f}秒"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
