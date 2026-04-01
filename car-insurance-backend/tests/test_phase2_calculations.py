"""
Phase 4: 计算逻辑测试

测试 RP 计算、利润计算、情景测试等核心计算逻辑
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.strategy_engine import StrategyEngine


class TestRPCalculation:
    """RP（纯风险保费）计算测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_rp_calculation_basic(self):
        """测试基础 RP 计算"""
        avg_premium = 4500
        target_loss_ratio = 0.75
        
        rp = self.engine.calculate_rp_premium(avg_premium, target_loss_ratio)
        
        assert rp == 3375.0  # 4500 * 0.75 = 3375
    
    def test_rp_calculation_different_ratios(self):
        """测试不同赔付率下的 RP 计算"""
        test_cases = [
            (4500, 0.65, 2925.0),
            (4500, 0.70, 3150.0),
            (4500, 0.75, 3375.0),
            (4500, 0.80, 3600.0),
            (5000, 0.75, 3750.0),
        ]
        
        for avg_premium, target_loss_ratio, expected in test_cases:
            rp = self.engine.calculate_rp_premium(avg_premium, target_loss_ratio)
            assert rp == expected, f"RP 计算失败：{avg_premium} * {target_loss_ratio} != {expected}"
    
    def test_rp_calculation_precision(self):
        """测试 RP 计算精度（保留 2 位小数）"""
        avg_premium = 4567.89
        target_loss_ratio = 0.7533
        
        rp = self.engine.calculate_rp_premium(avg_premium, target_loss_ratio)
        
        # 应该四舍五入到 2 位小数
        assert rp == round(4567.89 * 0.7533, 2)


class TestExpectedProfitCalculation:
    """预期利润计算测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_expected_profit_basic(self):
        """测试基础预期利润计算"""
        policy_count = 5000
        avg_premium = 4500
        fixed_cost_ratio = 0.10
        target_loss_ratio = 0.75
        market_expense_ratio = 0.12
        
        result = self.engine.calculate_expected_profit(
            policy_count=policy_count,
            avg_premium=avg_premium,
            fixed_cost_ratio=fixed_cost_ratio,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=market_expense_ratio
        )
        
        # 利润率 = 1 - 0.10 - 0.75 - 0.12 = 0.03
        assert result['profit_margin'] == 0.03
        
        # 总保费 = 5000 * 4500 = 22,500,000
        assert result['total_premium'] == 22500000.0
        
        # 预期利润 = 5000 * 4500 * 0.03 = 675,000
        assert result['expected_profit'] == 675000.0
        
        # RP = 4500 * 0.75 = 3375
        assert result['rp_premium'] == 3375.0
    
    def test_expected_profit_breakdown(self):
        """测试利润明细分解"""
        policy_count = 1000
        avg_premium = 5000
        fixed_cost_ratio = 0.10
        target_loss_ratio = 0.70
        market_expense_ratio = 0.12
        
        result = self.engine.calculate_expected_profit(
            policy_count=policy_count,
            avg_premium=avg_premium,
            fixed_cost_ratio=fixed_cost_ratio,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=market_expense_ratio
        )
        
        total_premium = 5000000  # 1000 * 5000
        
        assert result['breakdown']['fixed_cost'] == total_premium * 0.10
        assert result['breakdown']['expected_loss'] == total_premium * 0.70
        assert result['breakdown']['market_expense'] == total_premium * 0.12
    
    def test_expected_profit_negative_margin(self):
        """测试负利润率情况"""
        policy_count = 1000
        avg_premium = 4000
        fixed_cost_ratio = 0.15
        target_loss_ratio = 0.80
        market_expense_ratio = 0.12
        
        result = self.engine.calculate_expected_profit(
            policy_count=policy_count,
            avg_premium=avg_premium,
            fixed_cost_ratio=fixed_cost_ratio,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=market_expense_ratio
        )
        
        # 利润率 = 1 - 0.15 - 0.80 - 0.12 = -0.07 (亏损)
        assert result['profit_margin'] == -0.07
        assert result['expected_profit'] < 0


class TestScenarioCalculation:
    """情景测试计算测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_scenario_test_default_rates(self):
        """测试默认情景变化率"""
        base_profit = 1000000
        
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        # 应该返回 5 个情景
        assert len(scenarios) == 5
        
        # 验证变化率
        expected_rates = [-0.02, -0.01, 0, 0.01, 0.02]
        for i, scenario in enumerate(scenarios):
            assert scenario['change_rate'] == expected_rates[i]
    
    def test_scenario_test_profit_calculation(self):
        """测试情景利润计算"""
        base_profit = 1000000
        
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        # 情景 1: -2%
        assert scenarios[0]['scenario_profit'] == 980000.0
        assert scenarios[0]['change_rate'] == -0.02
        
        # 情景 2: -1%
        assert scenarios[1]['scenario_profit'] == 990000.0
        assert scenarios[1]['change_rate'] == -0.01
        
        # 情景 3: 0% (基准)
        assert scenarios[2]['scenario_profit'] == 1000000.0
        assert scenarios[2]['change_rate'] == 0
        
        # 情景 4: +1%
        assert scenarios[3]['scenario_profit'] == 1010000.0
        assert scenarios[3]['change_rate'] == 0.01
        
        # 情景 5: +2%
        assert scenarios[4]['scenario_profit'] == 1020000.0
        assert scenarios[4]['change_rate'] == 0.02
    
    def test_scenario_test_custom_rates(self):
        """测试自定义情景变化率"""
        base_profit = 500000
        custom_rates = [-0.05, 0, 0.05, 0.10]
        
        scenarios = self.engine.calculate_scenario_test(base_profit, custom_rates)
        
        assert len(scenarios) == 4
        assert scenarios[0]['scenario_profit'] == 475000.0  # -5%
        assert scenarios[1]['scenario_profit'] == 500000.0  # 0%
        assert scenarios[2]['scenario_profit'] == 525000.0  # +5%
        assert scenarios[3]['scenario_profit'] == 550000.0  # +10%
    
    def test_scenario_test_display_format(self):
        """测试情景显示格式"""
        base_profit = 1000000
        
        scenarios = self.engine.calculate_scenario_test(base_profit)
        
        # 验证显示格式
        assert scenarios[0]['change_rate_display'] == '-2.0%'
        assert scenarios[1]['change_rate_display'] == '-1.0%'
        assert scenarios[2]['change_rate_display'] == '+0.0%'
        assert scenarios[3]['change_rate_display'] == '+1.0%'
        assert scenarios[4]['change_rate_display'] == '+2.0%'


class TestTotalsCalculation:
    """合计值计算测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_totals_basic(self):
        """测试基础合计值计算"""
        business_units = [
            {'policy_count': 1000, 'avg_premium': 4000, 'profit_margin': 0.03},
            {'policy_count': 2000, 'avg_premium': 5000, 'profit_margin': 0.05},
            {'policy_count': 1500, 'avg_premium': 4500, 'profit_margin': 0.04},
        ]
        
        totals = self.engine.calculate_totals(business_units)
        
        # 总保费 = 1000*4000 + 2000*5000 + 1500*4500 = 4,000,000 + 10,000,000 + 6,750,000 = 20,750,000
        assert totals['total_premium'] == 20750000.0
        
        # 总利润 = 4,000,000*0.03 + 10,000,000*0.05 + 6,750,000*0.04 = 120,000 + 500,000 + 270,000 = 890,000
        assert totals['total_profit'] == 890000.0
        
        # 总保单数 = 1000 + 2000 + 1500 = 4500
        assert totals['total_policies'] == 4500
        
        # 整体利润率 = 890,000 / 20,750,000 = 0.0429
        assert abs(totals['overall_profit_margin'] - 0.0429) < 0.0001
    
    def test_totals_empty_units(self):
        """测试空业务单元列表"""
        business_units = []
        
        totals = self.engine.calculate_totals(business_units)
        
        assert totals['total_premium'] == 0
        assert totals['total_profit'] == 0
        assert totals['total_policies'] == 0
        assert totals['overall_profit_margin'] == 0
    
    def test_totals_single_unit(self):
        """测试单个业务单元"""
        business_units = [
            {'policy_count': 5000, 'avg_premium': 4500, 'profit_margin': 0.03},
        ]
        
        totals = self.engine.calculate_totals(business_units)
        
        assert totals['total_premium'] == 22500000.0
        assert totals['total_profit'] == 675000.0
        assert totals['total_policies'] == 5000
        assert totals['overall_profit_margin'] == 0.03


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = StrategyEngine()
    
    def test_full_calculation_flow(self):
        """测试完整计算流程"""
        # 1. 计算 RP
        avg_premium = 4500
        target_loss_ratio = 0.75
        rp = self.engine.calculate_rp_premium(avg_premium, target_loss_ratio)
        assert rp == 3375.0
        
        # 2. 计算预期利润
        profit_calc = self.engine.calculate_expected_profit(
            policy_count=5000,
            avg_premium=avg_premium,
            fixed_cost_ratio=0.10,
            target_loss_ratio=target_loss_ratio,
            market_expense_ratio=0.12
        )
        assert profit_calc['profit_margin'] == 0.03
        assert profit_calc['expected_profit'] == 675000.0
        
        # 3. 计算情景测试
        scenarios = self.engine.calculate_scenario_test(profit_calc['expected_profit'])
        assert len(scenarios) == 5
        assert scenarios[0]['scenario_profit'] == 661500.0  # 675000 * 0.98
        assert scenarios[4]['scenario_profit'] == 688500.0  # 675000 * 1.02
        
        # 4. 计算合计值
        business_units = [
            {'policy_count': 2500, 'avg_premium': 4000, 'profit_margin': 0.03},
            {'policy_count': 2500, 'avg_premium': 5000, 'profit_margin': 0.03},
        ]
        totals = self.engine.calculate_totals(business_units)
        assert totals['total_premium'] == 22500000.0
        assert totals['total_profit'] == 675000.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
