"""
API 集成测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """测试客户端夹具"""
    return TestClient(app)


class TestQuoteAPI:
    """询价 API 测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_calculate_quote(self, client):
        """测试询价计算"""
        quote_request = {
            "license_plate": "京 A12345",
            "vin": "LSVAV64R8DN123456",
            "registration_date": "2020-01-01",
            "fuel_type": "gasoline",
            "vehicle_value": 200000,
            "region": "beijing",
            "owner_name": "张三",
            "id_card": "110101199001011234",
            "insurance_types": ["compulsory", "third_party", "vehicle_damage"],
        }
        
        response = client.post("/api/v1/quote/calculate", json=quote_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "request_id" in data
        assert "quotes" in data
        assert "recommended_quote" in data
        assert "calculation_time_ms" in data
        
        # 检查报价列表
        assert len(data["quotes"]) >= 3
        
        # 检查推荐报价
        recommended = data["recommended_quote"]
        assert recommended is not None
        assert recommended["is_recommended"] == True
        assert "premiums" in recommended
        assert "scores" in recommended
    
    def test_get_test_cases(self, client):
        """测试获取测试用例"""
        response = client.get("/api/v1/quote/test-cases")
        assert response.status_code == 200
        data = response.json()
        assert "test_cases" in data
        assert len(data["test_cases"]) > 0
    
    def test_batch_calculate(self, client):
        """测试批量计算"""
        requests = [
            {
                "license_plate": f"京 A1234{i}",
                "vin": f"LSVAV64R8DN12345{i}",
                "registration_date": "2020-01-01",
                "fuel_type": "gasoline",
                "vehicle_value": 200000,
                "region": "beijing",
                "owner_name": "张三",
                "id_card": "110101199001011234",
                "insurance_types": ["compulsory"],
            }
            for i in range(3)
        ]
        
        response = client.post("/api/v1/quote/batch-calculate", json=requests)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3


class TestStrategyAPI:
    """策略 API 测试"""
    
    def test_get_strategy_config(self, client):
        """测试获取策略配置"""
        response = client.get("/api/v1/strategy/config?strategy_id=default")
        assert response.status_code == 200
        data = response.json()
        assert "strategy_id" in data
        assert "strategy_name" in data
    
    def test_list_strategies(self, client):
        """测试策略列表"""
        response = client.get("/api/v1/strategy/list")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data


class TestInsurerAPI:
    """保司 API 测试"""
    
    def test_list_insurers(self, client):
        """测试保司列表"""
        response = client.get("/api/v1/insurer/list")
        assert response.status_code == 200
        data = response.json()
        assert "insurers" in data
        assert len(data["insurers"]) >= 3
    
    def test_get_insurer(self, client):
        """测试获取保司详情"""
        response = client.get("/api/v1/insurer/picc")
        assert response.status_code == 200
        data = response.json()
        assert "insurer_id" in data
        assert "insurer_name" in data


class TestAnalyticsAPI:
    """分析 API 测试"""
    
    def test_get_dashboard(self, client):
        """测试分析看板"""
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_quotes" in data
        assert "total_premium" in data
        assert "avg_premium" in data
    
    def test_strategy_comparison(self, client):
        """测试策略对比"""
        response = client.get("/api/v1/analytics/strategy/comparison")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
