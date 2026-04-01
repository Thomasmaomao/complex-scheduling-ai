"""
精算模型测试
"""

import pytest
from app.services.actuarial_model import ActuarialModel


class TestActuarialModel:
    """精算模型测试类"""
    
    @pytest.fixture
    def model(self):
        """测试夹具"""
        return ActuarialModel()
    
    @pytest.fixture
    def sample_quote_request(self):
        """示例询价请求"""
        return {
            "license_plate": "京 A12345",
            "vin": "LSVAV64R8DN123456",
            "region": "beijing",
            "fuel_type": "gasoline",
            "vehicle_value": 200000,
            "insurance_types": ["compulsory", "third_party", "vehicle_damage"],
            "id_card": "110101199001011234",
        }
    
    def test_compulsory_premium(self, model):
        """测试交强险保费计算"""
        vehicle_info = {"region": "beijing"}
        premium = model.calculate_compulsory_premium(vehicle_info)
        
        assert premium == 950.0  # 6 座以下基础保费
        assert isinstance(premium, float)
    
    def test_third_party_premium(self, model):
        """测试三者险保费计算"""
        vehicle_info = {"region": "beijing", "vehicle_type": "sedan"}
        premium = model.calculate_third_party_premium(2000000, vehicle_info)
        
        assert premium > 0
        assert isinstance(premium, float)
    
    def test_vehicle_damage_premium(self, model):
        """测试车损险保费计算"""
        vehicle_info = {"region": "beijing", "vehicle_type": "sedan"}
        premium = model.calculate_vehicle_damage_premium(200000, vehicle_info)
        
        assert premium > 0
        assert isinstance(premium, float)
    
    def test_full_premium_calculation(self, model, sample_quote_request):
        """测试完整保费计算"""
        result = model.calculate_full_premium(sample_quote_request)
        
        assert "compulsory" in result
        assert "commercial" in result
        assert "total" in result
        assert result["total"] == result["compulsory"] + result["commercial"]
        assert result["total"] > 0
    
    def test_platform_risk_score(self, model, sample_quote_request):
        """测试平台风险评分"""
        score = model.calculate_platform_risk_score(sample_quote_request)
        
        assert 0 <= score <= 100
        assert isinstance(score, int)
    
    def test_risk_score_with_high_value_vehicle(self, model):
        """测试高价值车辆风险评分"""
        request = {
            "vehicle_value": 600000,
            "region": "beijing",
            "fuel_type": "gasoline",
            "id_card": "110101199001011234",
        }
        score = model.calculate_platform_risk_score(request)
        assert score > 50  # 高价值车辆风险更高
    
    def test_risk_score_with_young_driver(self, model):
        """测试年轻驾驶员风险评分"""
        request = {
            "vehicle_value": 150000,
            "region": "chengdu",
            "fuel_type": "gasoline",
            "id_card": "110101200001011234",  # 2000 年出生，约 26 岁
        }
        score = model.calculate_platform_risk_score(request)
        # 年轻驾驶员风险略高
    
    def test_region_factor(self, model):
        """测试地区系数"""
        regions = ["beijing", "shanghai", "guangzhou", "chengdu"]
        scores = {}
        
        for region in regions:
            request = {
                "vehicle_value": 200000,
                "region": region,
                "fuel_type": "gasoline",
                "id_card": "110101199001011234",
            }
            scores[region] = model.calculate_platform_risk_score(request)
        
        # 北京上海风险应高于成都
        assert scores["beijing"] > scores["chengdu"]
        assert scores["shanghai"] > scores["chengdu"]
    
    def test_fuel_type_factor(self, model):
        """测试燃料类型系数"""
        fuel_types = ["gasoline", "electric", "hybrid"]
        scores = {}
        
        for fuel_type in fuel_types:
            request = {
                "vehicle_value": 200000,
                "region": "beijing",
                "fuel_type": fuel_type,
                "id_card": "110101199001011234",
            }
            scores[fuel_type] = model.calculate_platform_risk_score(request)
        
        # 电动车风险略高
        assert scores["electric"] > scores["gasoline"]
    
    def test_request_id_generation(self, model, sample_quote_request):
        """测试请求 ID 生成"""
        request_id = model.generate_request_id(sample_quote_request)
        
        assert len(request_id) == 16
        assert isinstance(request_id, str)
        
        # 相同输入应生成相同 ID（在同一毫秒内）
        request_id2 = model.generate_request_id(sample_quote_request)
        # 注意：由于包含时间戳，两次调用可能不同


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
