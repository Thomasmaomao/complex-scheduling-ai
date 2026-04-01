"""
策略引擎测试
"""

import pytest
from app.services.strategy_engine import StrategyEngine


class TestStrategyEngine:
    """策略引擎测试类"""
    
    @pytest.fixture
    def engine(self):
        """测试夹具"""
        return StrategyEngine()
    
    @pytest.fixture
    def sample_quote_data(self):
        """示例询价数据"""
        return {
            "license_plate": "京 A12345",
            "vin": "LSVAV64R8DN123456",
            "region": "beijing",
            "fuel_type": "gasoline",
            "vehicle_value": 200000,
        }
    
    def test_calculate_insurer_score(self, engine, sample_quote_data):
        """测试保司评分计算"""
        scores = engine.calculate_insurer_score(
            "picc",
            sample_quote_data,
            premium=4500,
            risk_score=50
        )
        
        assert "price" in scores
        assert "service" in scores
        assert "claim" in scores
        assert "overall" in scores
        assert 0 <= scores["overall"] <= 100
    
    def test_generate_recommendation_reasons(self, engine):
        """测试推荐理由生成"""
        scores = {"price": 92, "service": 95, "claim": 88}
        reasons = engine.generate_recommendation_reasons("picc", scores, 4500)
        
        assert isinstance(reasons, list)
        assert len(reasons) >= 3
        assert len(reasons) <= 4
    
    def test_select_recommended_insurer(self, engine):
        """测试推荐保司选择"""
        quotes = [
            {
                "insurer_id": "picc",
                "insurer_name": "人保财险",
                "premiums": {"total": 4500},
                "scores": {"price": 92, "service": 95, "claim": 88, "overall": 95},
                "is_recommended": False,
                "reasons": [],
            },
            {
                "insurer_id": "pingan",
                "insurer_name": "平安产险",
                "premiums": {"total": 4600},
                "scores": {"price": 88, "service": 92, "claim": 85, "overall": 92},
                "is_recommended": False,
                "reasons": [],
            },
        ]
        
        recommended = engine.select_recommended_insurer(quotes)
        
        assert recommended is not None
        assert recommended["insurer_id"] == "picc"
        assert recommended["is_recommended"] == True
        assert len(recommended["reasons"]) > 0
    
    def test_get_all_insurer_quotes(self, engine, sample_quote_data):
        """测试获取所有保司报价"""
        premiums = {
            "compulsory": 950,
            "commercial": 3550,
            "total": 4500,
            "third_party": 1260,
            "vehicle_damage": 2200,
            "driver": 80,
            "passenger": 240,
        }
        
        quotes = engine.get_all_insurer_quotes(sample_quote_data, premiums, 50)
        
        assert isinstance(quotes, list)
        assert len(quotes) >= 3  # 至少 3 家保司
        
        # 检查是否有推荐
        has_recommended = any(q["is_recommended"] for q in quotes)
        assert has_recommended
        
        # 检查推荐的是否评分最高
        recommended = [q for q in quotes if q["is_recommended"]][0]
        max_score = max(q["scores"]["overall"] for q in quotes)
        assert recommended["scores"]["overall"] == max_score
    
    def test_get_strategy_config(self, engine):
        """测试获取策略配置"""
        config = engine.get_strategy_config()
        
        assert "strategy_id" in config
        assert "strategy_name" in config
        assert "priority_weights" in config
        assert "threshold_rules" in config
    
    def test_test_strategy(self, engine):
        """测试策略测试"""
        config = engine.get_strategy_config()
        test_cases = [
            {
                "vin": f"LSVAV64R8DN12345{i}",
                "region": "beijing",
                "fuel_type": "gasoline",
                "vehicle_value": 200000,
            }
            for i in range(5)
        ]
        
        result = engine.test_strategy(config, test_cases)
        
        assert "test_id" in result
        assert "total_cases" in result
        assert "passed_cases" in result
        assert "failed_cases" in result
        assert "pass_rate" in result
        assert result["total_cases"] == 5
        assert result["pass_rate"] >= 0
    
    def test_strategy_weights(self, engine):
        """测试策略权重"""
        config = engine.get_strategy_config()
        weights = config["priority_weights"]
        
        # 权重总和应为 1
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01
        
        # 检查权重分配
        assert "price" in weights
        assert "service" in weights
        assert "claim" in weights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
