"""
集成测试脚本 - 完整流程测试
"""

import requests
import json
import time
from datetime import date

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """测试完整询价流程"""
    print("=" * 60)
    print("集成测试 - 完整询价流程")
    print("=" * 60)
    
    results = []
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"   ✅ 服务正常：{response.json()}")
    results.append(("健康检查", "通过"))
    
    # 2. 计算报价
    print("\n2. 计算报价...")
    quote_request = {
        "license_plate": "京 A12345",
        "vin": "LSVAV64R8DN123456",
        "registration_date": "2020-01-01",
        "fuel_type": "gasoline",
        "vehicle_value": 200000,
        "region": "beijing",
        "owner_name": "张三",
        "id_card": "110101199001011234",
        "insurance_types": ["compulsory", "third_party", "vehicle_damage"]
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/quote/calculate", json=quote_request)
    elapsed = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    result = response.json()
    assert "request_id" in result
    assert "quotes" in result
    assert len(result["quotes"]) >= 3
    assert result["recommended_quote"] is not None
    
    print(f"   ✅ 报价计算成功")
    print(f"   - 请求 ID: {result['request_id']}")
    print(f"   - 推荐保司：{result['recommended_quote']['insurer_name']}")
    print(f"   - 总保费：¥{result['recommended_quote']['premiums']['total']:.2f}")
    print(f"   - 综合评分：{result['recommended_quote']['scores']['overall']}")
    print(f"   - 耗时：{elapsed:.2f}ms")
    results.append(("计算报价", f"通过 ({elapsed:.2f}ms)"))
    
    # 3. 获取策略配置
    print("\n3. 获取策略配置...")
    response = requests.get(f"{BASE_URL}/api/v1/strategy/config", params={"strategy_id": "default_v1"})
    assert response.status_code == 200
    config = response.json()
    print(f"   ✅ 策略配置获取成功")
    print(f"   - 策略名称：{config.get('strategy_name', 'N/A')}")
    print(f"   - 权重：价格{config.get('priority_weights', {}).get('price', 0)*100:.0f}% / 服务{config.get('priority_weights', {}).get('service', 0)*100:.0f}% / 赔付{config.get('priority_weights', {}).get('claim', 0)*100:.0f}%")
    results.append(("获取策略配置", "通过"))
    
    # 4. 获取测试用例
    print("\n4. 获取测试用例...")
    response = requests.get(f"{BASE_URL}/api/v1/quote/test-cases")
    assert response.status_code == 200
    test_cases = response.json()
    print(f"   ✅ 获取到 {len(test_cases.get('test_cases', []))} 个测试用例")
    results.append(("获取测试用例", "通过"))
    
    # 5. 批量计算
    print("\n5. 批量计算（2 个请求）...")
    batch_requests = [
        {
            "license_plate": "京 A12345",
            "vin": "LSVAV64R8DN123456",
            "registration_date": "2020-01-01",
            "fuel_type": "gasoline",
            "vehicle_value": 200000,
            "region": "beijing",
            "owner_name": "张三",
            "id_card": "110101199001011234",
            "insurance_types": ["compulsory", "third_party"]
        },
        {
            "license_plate": "沪 B67890",
            "vin": "LSVAV64R8DN123457",
            "registration_date": "2019-01-01",
            "fuel_type": "electric",
            "vehicle_value": 250000,
            "region": "shanghai",
            "owner_name": "李四",
            "id_card": "310101198501011234",
            "insurance_types": ["compulsory", "vehicle_damage"]
        }
    ]
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/quote/batch-calculate", json=batch_requests)
    elapsed = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    batch_result = response.json()
    assert batch_result["total"] == 2
    success_count = sum(1 for r in batch_result["results"] if r["status"] == "success")
    
    print(f"   ✅ 批量计算完成")
    print(f"   - 成功：{success_count}/{batch_result['total']}")
    print(f"   - 耗时：{elapsed:.2f}ms")
    results.append(("批量计算", f"通过 ({elapsed:.2f}ms)"))
    
    # 6. 保司列表
    print("\n6. 获取保司列表...")
    response = requests.get(f"{BASE_URL}/api/v1/insurer/list")
    assert response.status_code == 200
    insurers = response.json()
    print(f"   ✅ 获取到 {len(insurers.get('insurers', []))} 家保司")
    results.append(("获取保司列表", "通过"))
    
    # 7. 效果看板
    print("\n7. 获取效果看板...")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard")
    assert response.status_code == 200
    dashboard = response.json()
    print(f"   ✅ 效果看板获取成功")
    print(f"   - 总保费：¥{dashboard.get('total_premium', 0) / 10000:.1f}万")
    print(f"   - 利润贡献：¥{dashboard.get('total_profit', 0) / 10000:.1f}万")
    results.append(("获取效果看板", "通过"))
    
    # 总结
    print("\n" + "=" * 60)
    print("集成测试结果总结")
    print("=" * 60)
    for test_name, result in results:
        print(f"   {test_name}: {result}")
    
    all_passed = all("通过" in r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有集成测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_complete_flow()
    exit(0 if success else 1)
