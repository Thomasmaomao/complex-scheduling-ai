"""
15 个测试车型验证脚本
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

# 15 个测试车型
TEST_CASES = [
    {"case_id": "TC001", "vehicle_value": 120000, "region": "beijing", "fuel_type": "gasoline"},
    {"case_id": "TC002", "vehicle_value": 450000, "region": "shanghai", "fuel_type": "gasoline"},
    {"case_id": "TC003", "vehicle_value": 250000, "region": "beijing", "fuel_type": "electric"},
    {"case_id": "TC004", "vehicle_value": 180000, "region": "chengdu", "fuel_type": "gasoline"},
    {"case_id": "TC005", "vehicle_value": 300000, "region": "shanghai", "fuel_type": "gasoline"},
    {"case_id": "TC006", "vehicle_value": 130000, "region": "chengdu", "fuel_type": "gasoline"},
    {"case_id": "TC007", "vehicle_value": 200000, "region": "beijing", "fuel_type": "gasoline"},
    {"case_id": "TC008", "vehicle_value": 400000, "region": "shanghai", "fuel_type": "gasoline"},
    {"case_id": "TC009", "vehicle_value": 80000, "region": "chengdu", "fuel_type": "gasoline"},
    {"case_id": "TC010", "vehicle_value": 150000, "region": "beijing", "fuel_type": "hybrid"},
    {"case_id": "TC011", "vehicle_value": 220000, "region": "shenzhen", "fuel_type": "electric"},
    {"case_id": "TC012", "vehicle_value": 650000, "region": "beijing", "fuel_type": "gasoline"},
    {"case_id": "TC013", "vehicle_value": 30000, "region": "chengdu", "fuel_type": "electric"},
    {"case_id": "TC014", "vehicle_value": 850000, "region": "shanghai", "fuel_type": "gasoline"},
    {"case_id": "TC015", "vehicle_value": 800000, "region": "beijing", "fuel_type": "gasoline"},
]

def calculate_age_from_id(id_card: str) -> int:
    """从身份证号计算年龄"""
    if len(id_card) < 18:
        return 35
    birth_year = int(id_card[6:10])
    from datetime import datetime
    return datetime.now().year - birth_year

def test_vehicle(case: dict) -> dict:
    """测试单个车型"""
    # 生成测试 VIN（17 位）- 使用固定 VIN + 序号
    vin_num = int(case['case_id'][-3:])
    vin = f"LSVAV64R8DN1234{vin_num:02d}"
    
    # 计算年龄（模拟 35 岁）
    test_date = date.today() - timedelta(days=35*365)
    id_card = f"110101{test_date.year}01011234"
    
    payload = {
        "license_plate": f"京 A{case['case_id']}",
        "vin": vin,
        "registration_date": "2020-01-01",
        "fuel_type": case["fuel_type"],
        "vehicle_value": case["vehicle_value"],
        "region": case["region"],
        "owner_name": "测试用户",
        "id_card": id_card,
        "insurance_types": ["compulsory", "third_party", "vehicle_damage"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/quote/calculate", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        recommended = result.get("recommended_quote")
        if not recommended:
            return {
                "case_id": case["case_id"],
                "status": "error",
                "error": "No recommended quote"
            }
        return {
            "case_id": case["case_id"],
            "status": "success",
            "total_premium": recommended["premiums"]["total"],
            "overall_score": recommended["scores"]["overall"],
            "calculation_time_ms": result.get("calculation_time_ms", 0)
        }
    else:
        return {
            "case_id": case["case_id"],
            "status": "error",
            "error": response.text
        }

def main():
    """主测试函数"""
    print("=" * 60)
    print("15 个测试车型验证")
    print("=" * 60)
    
    results = []
    total_time = 0
    success_count = 0
    
    for case in TEST_CASES:
        result = test_vehicle(case)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
            total_time += result.get("calculation_time_ms", 0)
            print(f"✅ {result['case_id']}: ¥{result['total_premium']:.2f} "
                  f"(评分：{result['overall_score']}, 耗时：{result['calculation_time_ms']}ms)")
        else:
            print(f"❌ {result['case_id']}: {result['error']}")
    
    print("=" * 60)
    print(f"测试结果：{success_count}/15 通过")
    print(f"平均耗时：{total_time/success_count:.2f}ms" if success_count > 0 else "N/A")
    print("=" * 60)
    
    # 保存测试结果
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_cases": 15,
            "success_count": success_count,
            "pass_rate": success_count / 15 * 100,
            "avg_time_ms": total_time / success_count if success_count > 0 else 0,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n测试结果已保存到 test_results.json")
    
    return success_count == 15

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
