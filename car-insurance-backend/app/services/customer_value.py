"""
客户价值评估模型

评估客户价值，支持差异化定价和精准营销
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CustomerValueAssessment:
    """客户价值评估模型"""
    
    def __init__(self):
        # 评估维度权重
        self.weights = {
            "economic_value": 0.35,     # 经济价值
            "loyalty_value": 0.25,      # 忠诚度价值
            "risk_value": 0.20,         # 风险价值
            "growth_value": 0.20,       # 成长价值
        }
        
        # 客户等级划分
        self.customer_levels = {
            "high": {"min_score": 80, "label": "高价值客户", "discount": 0.9},
            "medium": {"min_score": 60, "label": "中等价值客户", "discount": 0.95},
            "low": {"min_score": 0, "label": "普通价值客户", "discount": 1.0},
        }
    
    def assess_customer_value(self, customer_data: dict) -> dict:
        """
        评估客户综合价值
        
        customer_data: 客户数据
        - economic: 经济价值相关数据
        - loyalty: 忠诚度相关数据
        - risk: 风险相关数据
        - growth: 成长价值相关数据
        
        返回:
        {
            "overall_score": 综合得分,
            "level": 客户等级,
            "dimension_scores": 各维度得分,
            "suggestions": 营销建议
        }
        """
        # 计算各维度得分
        dimension_scores = {
            "economic_value": self._calculate_economic_value(customer_data.get('economic', {})),
            "loyalty_value": self._calculate_loyalty_value(customer_data.get('loyalty', {})),
            "risk_value": self._calculate_risk_value(customer_data.get('risk', {})),
            "growth_value": self._calculate_growth_value(customer_data.get('growth', {})),
        }
        
        # 计算综合得分
        overall_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in dimension_scores
        )
        overall_score = round(overall_score, 2)
        
        # 确定客户等级
        level = self._determine_level(overall_score)
        
        # 生成营销建议
        suggestions = self._generate_suggestions(level, dimension_scores)
        
        return {
            "overall_score": overall_score,
            "level": level,
            "dimension_scores": dimension_scores,
            "suggestions": suggestions,
            "discount_factor": self.customer_levels[level]["discount"],
        }
    
    def _calculate_economic_value(self, economic_data: dict) -> float:
        """
        计算经济价值得分（0-100）
        
        考虑因素：
        - 年缴费保费
        - 险种数量
        - 附加险购买情况
        """
        score = 50  # 基础分
        
        # 年缴费保费
        annual_premium = economic_data.get('annual_premium', 0)
        if annual_premium >= 10000:
            score += 30
        elif annual_premium >= 6000:
            score += 20
        elif annual_premium >= 4000:
            score += 10
        elif annual_premium >= 2000:
            score += 5
        
        # 险种数量
        insurance_count = economic_data.get('insurance_count', 1)
        score += min(insurance_count * 3, 15)
        
        # 附加险购买
        if economic_data.get('has_additional_insurance', False):
            score += 5
        
        return min(100, max(0, score))
    
    def _calculate_loyalty_value(self, loyalty_data: dict) -> float:
        """
        计算忠诚度价值得分（0-100）
        
        考虑因素：
        - 投保年限
        - 续保情况
        - 推荐新客户
        - 投诉记录
        """
        score = 50  # 基础分
        
        # 投保年限
        years = loyalty_data.get('insurance_years', 0)
        if years >= 5:
            score += 25
        elif years >= 3:
            score += 15
        elif years >= 1:
            score += 8
        
        # 续保情况
        renewal_rate = loyalty_data.get('renewal_rate', 0)
        score += int(renewal_rate * 20)
        
        # 推荐新客户
        referrals = loyalty_data.get('referrals', 0)
        score += min(referrals * 5, 15)
        
        # 投诉记录（扣分项）
        complaints = loyalty_data.get('complaints', 0)
        score -= min(complaints * 10, 30)
        
        return min(100, max(0, score))
    
    def _calculate_risk_value(self, risk_data: dict) -> float:
        """
        计算风险价值得分（0-100）
        
        考虑因素：
        - 历史出险次数
        - 出险金额
        - 交通违法记录
        - 车型风险等级
        """
        score = 70  # 基础分（假设大多数客户风险较低）
        
        # 历史出险次数
        claim_count = risk_data.get('claim_count', 0)
        if claim_count == 0:
            score += 15
        elif claim_count <= 2:
            score += 5
        elif claim_count <= 5:
            score -= 10
        else:
            score -= 25
        
        # 出险金额
        claim_amount = risk_data.get('claim_amount', 0)
        if claim_amount > 50000:
            score -= 20
        elif claim_amount > 20000:
            score -= 10
        elif claim_amount > 10000:
            score -= 5
        
        # 交通违法记录
        violations = risk_data.get('violations', 0)
        score -= min(violations * 3, 20)
        
        # 车型风险等级
        vehicle_risk = risk_data.get('vehicle_risk_level', 'medium')
        if vehicle_risk == 'low':
            score += 5
        elif vehicle_risk == 'high':
            score -= 10
        
        return min(100, max(0, score))
    
    def _calculate_growth_value(self, growth_data: dict) -> float:
        """
        计算成长价值得分（0-100）
        
        考虑因素：
        - 年龄阶段
        - 收入增长潜力
        - 家庭结构变化
        - 车辆升级可能性
        """
        score = 50  # 基础分
        
        # 年龄阶段
        age = growth_data.get('age', 35)
        if 25 <= age <= 35:
            score += 20  # 年轻客户成长潜力大
        elif 36 <= age <= 45:
            score += 15
        elif 46 <= age <= 55:
            score += 10
        
        # 收入增长潜力
        income_growth = growth_data.get('income_growth_potential', 'medium')
        if income_growth == 'high':
            score += 15
        elif income_growth == 'medium':
            score += 8
        
        # 家庭结构变化
        if growth_data.get('family_expansion_expected', False):
            score += 10  # 预计家庭扩张
        
        # 车辆升级可能性
        if growth_data.get('vehicle_upgrade_likely', False):
            score += 10
        
        return min(100, max(0, score))
    
    def _determine_level(self, overall_score: float) -> str:
        """确定客户等级"""
        if overall_score >= self.customer_levels["high"]["min_score"]:
            return "high"
        elif overall_score >= self.customer_levels["medium"]["min_score"]:
            return "medium"
        else:
            return "low"
    
    def _generate_suggestions(self, level: str, dimension_scores: dict) -> List[str]:
        """生成营销建议"""
        suggestions = []
        
        if level == "high":
            suggestions.append("提供 VIP 服务通道和专属客服")
            suggestions.append("推荐高端附加险产品")
            suggestions.append("提供续保优惠和积分奖励")
        elif level == "medium":
            suggestions.append("提供标准服务和适度优惠")
            suggestions.append"推荐性价比高的险种组合")
            suggestions.append("关注续保提醒和客户服务")
        else:
            suggestions.append("加强风险教育和安全意识")
            suggestions.append("提供基础保障方案")
            suggestions.append("关注服务质量和满意度提升")
        
        # 根据维度得分提供针对性建议
        min_dim = min(dimension_scores, key=dimension_scores.get)
        if min_dim == "economic_value":
            suggestions.append("可推荐更全面的险种组合提升保障")
        elif min_dim == "loyalty_value":
            suggestions.append("加强客户关系维护和互动")
        elif min_dim == "risk_value":
            suggestions.append("提供安全驾驶培训和风险预防建议")
        elif min_dim == "growth_value":
            suggestions.append("关注客户生命周期管理和需求变化")
        
        return suggestions
    
    def batch_assess(self, customers_data: List[dict]) -> List[dict]:
        """批量评估客户价值"""
        results = []
        for customer_data in customers_data:
            result = self.assess_customer_value(customer_data)
            result["customer_id"] = customer_data.get('customer_id', 'unknown')
            results.append(result)
        
        # 按综合得分排序
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return results
    
    def get_value_distribution(self, customers: List[dict]) -> dict:
        """获取客户价值分布"""
        distribution = {
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        
        total_score = 0
        for customer in customers:
            level = customer.get('level', 'low')
            distribution[level] += 1
            total_score += customer.get('overall_score', 0)
        
        total = len(customers)
        return {
            "distribution": distribution,
            "percentages": {
                k: round(v / total * 100, 2) if total > 0 else 0
                for k, v in distribution.items()
            },
            "average_score": round(total_score / total, 2) if total > 0 else 0,
        }
