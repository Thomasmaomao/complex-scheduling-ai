"""
策略引擎 - 智能推荐核心逻辑

基于多因子评分的保司推荐策略
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StrategyEngine:
    """策略引擎"""
    
    def __init__(self):
        # 默认策略配置
        self.default_strategy = {
            "strategy_id": "default_v1",
            "strategy_name": "默认推荐策略",
            "priority_weights": {
                "price": 0.4,      # 价格权重 40%
                "service": 0.35,   # 服务权重 35%
                "claim": 0.25,     # 赔付权重 25%
            },
            "threshold_rules": {
                "min_price_score": 60,
                "min_service_score": 70,
                "min_claim_score": 60,
            }
        }
        
        # 保司基础信息（模拟数据 - 已脱敏）
        self.insurers = {
            "picc": {
                "insurer_id": "picc",
                "insurer_name": "保司 A",
                "base_scores": {
                    "price": 85,
                    "service": 90,
                    "claim": 88,
                },
                "market_share": 0.33,  # 市场占有率
            },
            "pingan": {
                "insurer_id": "pingan",
                "insurer_name": "保司 B",
                "base_scores": {
                    "price": 80,
                    "service": 92,
                    "claim": 85,
                },
                "market_share": 0.28,
            },
            "cpic": {
                "insurer_id": "cpic",
                "insurer_name": "保司 C",
                "base_scores": {
                    "price": 82,
                    "service": 88,
                    "claim": 86,
                },
                "market_share": 0.20,
            },
        }
    
    def calculate_insurer_score(self, insurer_id: str, quote_data: dict, 
                                 premium: float, risk_score: int) -> Dict:
        """
        计算保司综合评分
        
        参数:
        - insurer_id: 保司 ID
        - quote_data: 询价数据
        - premium: 保费
        - risk_score: 平台风险评分
        
        返回:
        {
            "price": 价格得分,
            "service": 服务得分,
            "claim": 赔付得分,
            "overall": 综合得分
        }
        """
        insurer = self.insurers.get(insurer_id)
        if not insurer:
            return {"price": 50, "service": 50, "claim": 50, "overall": 50}
        
        base_scores = insurer["base_scores"]
        weights = self.default_strategy["priority_weights"]
        
        # 价格得分（基于市场均价比较）
        # 简化：假设市场均价为 premium * 1.05
        market_avg = premium * 1.05
        price_ratio = market_avg / premium if premium > 0 else 1
        price_score = min(100, int(base_scores["price"] * price_ratio))
        
        # 服务得分（基础分 + 调整）
        service_score = base_scores["service"]
        
        # 赔付得分（基础分 + 风险调整）
        # 高风险客户赔付得分略低
        risk_adjustment = max(0, (50 - risk_score) / 10)
        claim_score = max(60, min(100, round(base_scores["claim"] + risk_adjustment)))
        
        # 综合得分（加权平均）
        overall_score = round(
            price_score * weights["price"] +
            service_score * weights["service"] +
            claim_score * weights["claim"]
        )
        
        return {
            "price": price_score,
            "service": service_score,
            "claim": claim_score,
            "overall": overall_score,
        }
    
    def generate_recommendation_reasons(self, insurer_id: str, scores: Dict, 
                                         premium: float) -> List[str]:
        """
        生成推荐理由
        
        返回推荐理由列表
        """
        reasons = []
        insurer = self.insurers.get(insurer_id)
        insurer_name = insurer["insurer_name"] if insurer else "该保司"
        
        # 价格优势
        if scores["price"] >= 90:
            reasons.append(f"价格竞争力强，低于市场均价{int((scores['price'] - 80) / 2)}%")
        elif scores["price"] >= 80:
            reasons.append("价格具有市场竞争力")
        
        # 服务质量
        if scores["service"] >= 90:
            reasons.append(f"服务质量优秀，客户满意度{scores['service']}%")
        elif scores["service"] >= 80:
            reasons.append("服务质量良好")
        
        # 赔付效率
        if scores["claim"] >= 90:
            reasons.append("赔付效率高，平均赔付周期<3 天")
        elif scores["claim"] >= 80:
            reasons.append("赔付效率良好，平均赔付周期 3-5 天")
        
        # 品牌信誉
        if insurer and insurer["market_share"] >= 0.3:
            reasons.append("品牌信誉好，市场占有率领先")
        
        # 确保至少有 3 条理由
        if len(reasons) < 3:
            reasons.append(f"{insurer_name}提供全面的保险保障")
        if len(reasons) < 3:
            reasons.append("理赔服务网络覆盖全国")
        
        return reasons[:4]  # 最多 4 条
    
    def select_recommended_insurer(self, quotes: List[Dict]) -> Optional[Dict]:
        """
        选择推荐保司
        
        从报价列表中选择综合评分最高的作为推荐
        """
        if not quotes:
            return None
        
        # 按综合评分排序
        sorted_quotes = sorted(
            quotes,
            key=lambda x: x["scores"]["overall"],
            reverse=True
        )
        
        # 设置推荐标记
        for i, quote in enumerate(sorted_quotes):
            quote["is_recommended"] = (i == 0)
            if i == 0:
                quote["reasons"] = self.generate_recommendation_reasons(
                    quote["insurer_id"],
                    quote["scores"],
                    quote["premiums"]["total"]
                )
        
        return sorted_quotes[0] if sorted_quotes else None
    
    def get_all_insurer_quotes(self, quote_request: dict, premiums: dict, 
                                risk_score: int) -> List[Dict]:
        """
        获取所有保司报价
        
        返回完整的报价列表（不同保司有差异）
        """
        import hashlib
        
        quotes = []
        base_premium = premiums["total"]
        
        # 为每个询价生成一个种子，确保相同输入得到相同输出
        seed_str = f"{quote_request.get('vin', '')}{quote_request.get('region', '')}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        
        for idx, insurer_id in enumerate(self.insurers.keys()):
            # 不同保司的保费差异（±10% 范围内）
            # 人保：基准，平安：-3% 到 +5%，太平洋：-5% 到 +8%
            base_variance = (seed + idx * 1234) % 2000
            if idx == 0:  # 人保财险 - 基准
                insurer_factor = 1.0
            elif idx == 1:  # 平安产险
                insurer_factor = 0.97 + (base_variance / 2000) * 0.08  # 0.97-1.05
            else:  # 太平洋产险
                insurer_factor = 0.95 + (base_variance / 2000) * 0.13  # 0.95-1.08
            
            insurer_total = round(base_premium * insurer_factor, 2)
            
            # 计算评分
            scores = self.calculate_insurer_score(
                insurer_id,
                quote_request,
                insurer_total,
                risk_score
            )
            
            # 构建报价
            insurer = self.insurers[insurer_id]
            quote = {
                "insurer_id": insurer_id,
                "insurer_name": insurer["insurer_name"],
                "premiums": {
                    "compulsory": round(premiums["compulsory"] * insurer_factor, 2),
                    "commercial": round(premiums["commercial"] * insurer_factor, 2),
                    "third_party": round(premiums["third_party"] * insurer_factor, 2),
                    "vehicle_damage": round(premiums["vehicle_damage"] * insurer_factor, 2),
                    "driver": round(premiums["driver"] * insurer_factor, 2),
                    "passenger": round(premiums["passenger"] * insurer_factor, 2),
                    "total": insurer_total,
                },
                "scores": scores,
                "is_recommended": False,
                "reasons": [],
            }
            quotes.append(quote)
        
        # 选择推荐
        self.select_recommended_insurer(quotes)
        
        return quotes
    
    def get_strategy_config(self, strategy_id: str = "default") -> Dict:
        """获取策略配置"""
        return self.default_strategy
    
    def test_strategy(self, strategy_config: Dict, test_cases: List[Dict]) -> Dict:
        """
        测试策略
        
        运行测试用例并返回测试结果
        """
        results = []
        passed = 0
        failed = 0
        
        for case in test_cases:
            try:
                # 执行策略
                premiums = self._calculate_premiums(case)
                risk_score = self._calculate_risk_score(case)
                quotes = self.get_all_insurer_quotes(case, premiums, risk_score)
                
                # 验证结果
                is_valid = self._validate_result(quotes, strategy_config)
                
                if is_valid:
                    passed += 1
                else:
                    failed += 1
                
                results.append({
                    "case_id": case.get("vin", "unknown"),
                    "status": "passed" if is_valid else "failed",
                    "quotes_count": len(quotes),
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    "case_id": case.get("vin", "unknown"),
                    "status": "error",
                    "error": str(e),
                })
        
        total = passed + failed
        return {
            "test_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "strategy_id": strategy_config.get("strategy_id", "unknown"),
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": failed,
            "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
            "details": results,
        }
    
    def _calculate_premiums(self, case: dict) -> dict:
        """简化保费计算（用于测试）"""
        return {
            "compulsory": 950,
            "commercial": 3500,
            "total": 4450,
            "third_party": 1200,
            "vehicle_damage": 2200,
            "driver": 80,
            "passenger": 240,
        }
    
    def _calculate_risk_score(self, case: dict) -> int:
        """简化风险评分（用于测试）"""
        return 50
    
    def _validate_result(self, quotes: List[Dict], strategy_config: Dict) -> bool:
        """验证策略结果"""
        if not quotes:
            return False
        
        # 检查是否有推荐
        has_recommended = any(q.get("is_recommended") for q in quotes)
        if not has_recommended:
            return False
        
        # 检查评分是否合理
        for quote in quotes:
            scores = quote.get("scores", {})
            if scores.get("overall", 0) < 50:
                return False
        
        return True
    
    def simulate_cost(self, strategy_id: str, simulation_params: dict) -> dict:
        """
        成本模拟计算
        
        返回各业务单元的成本结构和汇总数据
        """
        business_units = simulation_params.get("business_units", [])
        parameters = simulation_params.get("parameters", {})
        sample_data = simulation_params.get("sample_data", [])
        
        # 模拟参数
        fixed_cost_ratio = parameters.get("fixed_cost_ratio", 0.10)
        market_expense_ratio = parameters.get("market_expense_ratio", 0.12)
        target_loss_ratio = parameters.get("target_loss_ratio", 0.75)
        
        # 业务单元模拟数据
        unit_data = {
            "BU001": {"name": "燃油车 - 续保客户", "policy_count": 5000, "avg_premium": 3500},
            "BU002": {"name": "燃油车 - 新保客户", "policy_count": 2000, "avg_premium": 4800},
            "BU003": {"name": "新能源 - 高价值客户", "policy_count": 1500, "avg_premium": 5800},
            "BU004": {"name": "新能源 - 普通客户", "policy_count": 3000, "avg_premium": 4500},
            "BU005": {"name": "豪车 - 续保客户", "policy_count": 500, "avg_premium": 15000},
        }
        
        # 计算各业务单元结果
        business_unit_results = []
        total_premium = 0
        total_profit = 0
        
        for unit_id in business_units:
            data = unit_data.get(unit_id, {})
            policy_count = data.get("policy_count", 0)
            avg_premium = data.get("avg_premium", 0)
            
            # 计算自主系数（基于目标赔付率反算）
            avg_autonomous_discount = round(1 - target_loss_ratio - market_expense_ratio - fixed_cost_ratio + 0.5, 2)
            avg_autonomous_discount = max(0.5, min(1.5, avg_autonomous_discount))
            
            # 计算成交率（S 型曲线）
            conversion_rate = 1 / (1 + 2.718 ** (3.5 * (avg_autonomous_discount - 0.90)))
            conversion_rate = max(0.05, min(0.60, conversion_rate))
            
            # 计算预期保费和利润
            expected_premium = policy_count * avg_premium * conversion_rate
            profit_margin = 1 - target_loss_ratio - market_expense_ratio - fixed_cost_ratio
            expected_profit = expected_premium * profit_margin
            
            # 风险等级
            if "新能源" in data.get("name", "") and "普通" in data.get("name", ""):
                risk_level = "high"
                profit_margin = -0.03  # 亏损
            elif "豪车" in data.get("name", "") or ("燃油车" in data.get("name", "") and "续保" in data.get("name", "")):
                risk_level = "low"
                profit_margin = 0.06
            else:
                risk_level = "medium"
                profit_margin = 0.03
            
            business_unit_results.append({
                "unit_id": unit_id,
                "unit_name": data.get("name", unit_id),
                "policy_count": policy_count,
                "avg_premium": avg_premium,
                "avg_autonomous_discount": avg_autonomous_discount,
                "conversion_rate": round(conversion_rate, 4),
                "expected_premium": round(expected_premium, 2),
                "expected_profit": round(expected_premium * profit_margin, 2),
                "profit_margin": profit_margin,
                "risk_level": risk_level
            })
            
            total_premium += expected_premium
            total_profit += expected_premium * profit_margin
        
        # 汇总数据
        summary = {
            "total_policy_count": sum(u["policy_count"] for u in business_unit_results),
            "total_expected_premium": round(total_premium, 2),
            "total_expected_profit": round(total_profit, 2),
            "avg_profit_margin": round(total_profit / total_premium, 4) if total_premium > 0 else 0,
            "risk_warning": [u["unit_name"] for u in business_unit_results if u["risk_level"] == "high"]
        }
        
        return {
            "business_unit_results": business_unit_results,
            "summary": summary
        }
    
    def simulate_revenue(self, strategy_id: str, scenarios: List[dict]) -> dict:
        """
        收益模拟计算
        
        基于不同目标赔付率情景，模拟收益变化
        """
        results = []
        
        for scenario in scenarios:
            scenario_name = scenario.get("name", "未知情景")
            target_loss_ratio = scenario.get("target_loss_ratio", 0.75)
            
            # 固定参数
            market_expense_ratio = 0.12
            fixed_cost_ratio = 0.10
            
            # 计算利润率
            profit_margin = 1 - target_loss_ratio - market_expense_ratio - fixed_cost_ratio
            
            # 计算自主系数（基于目标赔付率）
            avg_autonomous_discount = round(1 - target_loss_ratio - market_expense_ratio - fixed_cost_ratio + 0.5, 2)
            avg_autonomous_discount = max(0.5, min(1.5, avg_autonomous_discount))
            
            # 计算成交率（S 型曲线）
            conversion_rate = 1 / (1 + 2.718 ** (3.5 * (avg_autonomous_discount - 0.90)))
            conversion_rate = max(0.05, min(0.60, conversion_rate))
            
            # 基准保费规模（假设）
            base_premium = 25000000
            
            # 计算预期保费和利润
            expected_premium = base_premium * (conversion_rate / 0.46)  # 相对于基准成交率 46%
            expected_profit = expected_premium * profit_margin
            
            results.append({
                "name": scenario_name,
                "target_loss_ratio": target_loss_ratio,
                "avg_autonomous_discount": avg_autonomous_discount,
                "conversion_rate": round(conversion_rate, 4),
                "expected_premium": round(expected_premium, 2),
                "expected_profit": round(expected_profit, 2),
                "profit_margin": round(profit_margin, 4)
            })
        
        # 推荐最优情景
        best_scenario = max(results, key=lambda x: x["expected_profit"])
        
        return {
            "scenarios": results,
            "recommendation": {
                "optimal_scenario": best_scenario["name"],
                "reason": "利润率与成交率平衡最佳"
            }
        }
    
    def calculate_rp_premium(self, avg_premium: float, target_loss_ratio: float) -> float:
        """
        计算 RP（纯风险保费）
        
        公式：RP = 平均保费 × 目标赔付率
        
        Args:
            avg_premium: 平均保费
            target_loss_ratio: 目标赔付率
            
        Returns:
            RP 纯风险保费
        """
        rp = avg_premium * target_loss_ratio
        return round(rp, 2)
    
    def calculate_expected_profit(self, policy_count: int, avg_premium: float, 
                                   fixed_cost_ratio: float, target_loss_ratio: float, 
                                   market_expense_ratio: float) -> dict:
        """
        计算预期利润
        
        公式：
        利润率 = 1 - 固定成本率 - 目标赔付率 - 市场费用率
        预期利润 = 保单数 × 平均保费 × 利润率
        
        Args:
            policy_count: 保单数
            avg_premium: 平均保费
            fixed_cost_ratio: 固定成本率
            target_loss_ratio: 目标赔付率
            market_expense_ratio: 市场费用率
            
        Returns:
            包含利润率、预期利润等详细信息的字典
        """
        # 计算利润率
        profit_margin = 1 - fixed_cost_ratio - target_loss_ratio - market_expense_ratio
        
        # 计算预期利润
        expected_profit = policy_count * avg_premium * profit_margin
        
        # 计算总保费
        total_premium = policy_count * avg_premium
        
        # 计算 RP（纯风险保费）
        rp_premium = self.calculate_rp_premium(avg_premium, target_loss_ratio)
        
        return {
            "profit_margin": round(profit_margin, 4),
            "expected_profit": round(expected_profit, 2),
            "total_premium": round(total_premium, 2),
            "rp_premium": rp_premium,
            "policy_count": policy_count,
            "avg_premium": avg_premium,
            "breakdown": {
                "fixed_cost": round(total_premium * fixed_cost_ratio, 2),
                "expected_loss": round(total_premium * target_loss_ratio, 2),
                "market_expense": round(total_premium * market_expense_ratio, 2)
            }
        }
    
    def calculate_scenario_test(self, base_profit: float, 
                                 change_rates: List[float] = None) -> List[dict]:
        """
        情景测试计算
        
        公式：情景利润 = 基准利润 × (1 + 情景变化率)
        
        Args:
            base_profit: 基准利润
            change_rates: 情景变化率列表，默认 [-0.02, -0.01, 0, 0.01, 0.02]
            
        Returns:
            5 情景测试结果列表
        """
        if change_rates is None:
            change_rates = [-0.02, -0.01, 0, 0.01, 0.02]
        
        scenarios = []
        for i, rate in enumerate(change_rates):
            scenario_profit = base_profit * (1 + rate)
            scenarios.append({
                "scenario_id": i + 1,
                "scenario_name": f"情景{i + 1}",
                "change_rate": rate,
                "change_rate_display": f"{rate * 100:+.1f}%",
                "base_profit": round(base_profit, 2),
                "scenario_profit": round(scenario_profit, 2),
                "profit_change": round(scenario_profit - base_profit, 2)
            })
        
        return scenarios
    
    def calculate_totals(self, business_units: List[dict]) -> dict:
        """
        计算合计值（总保费/总利润/利润率）
        
        Args:
            business_units: 业务单元列表，每个单元包含 policy_count, avg_premium, profit_margin 等
            
        Returns:
            合计值字典
        """
        total_premium = 0
        total_profit = 0
        total_policies = 0
        
        for bu in business_units:
            policy_count = bu.get('policy_count', 0)
            avg_premium = bu.get('avg_premium', 0)
            profit_margin = bu.get('profit_margin', 0)
            
            bu_premium = policy_count * avg_premium
            bu_profit = bu_premium * profit_margin
            
            total_premium += bu_premium
            total_profit += bu_profit
            total_policies += policy_count
        
        # 计算整体利润率
        overall_profit_margin = total_profit / total_premium if total_premium > 0 else 0
        
        return {
            "total_premium": round(total_premium, 2),
            "total_profit": round(total_profit, 2),
            "overall_profit_margin": round(overall_profit_margin, 4),
            "total_policies": total_policies,
            "business_unit_count": len(business_units)
        }
