"""
压力测试脚本 - 使用 locust 进行并发测试
"""

from locust import HttpUser, task, between, events
import json
import time

# 测试数据
QUOTE_REQUESTS = [
    {
        "license_plate": "京 A12345",
        "vin": "LSVAV64R8DN123456",
        "registration_date": "2020-01-01",
        "fuel_type": "gasoline",
        "vehicle_value": 200000,
        "region": "beijing",
        "owner_name": "张三",
        "id_card": "110101199001011234",
        "insurance_types": ["compulsory", "third_party", "vehicle_damage"]
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
    },
    {
        "license_plate": "粤 C11111",
        "vin": "LSVAV64R8DN123458",
        "registration_date": "2021-01-01",
        "fuel_type": "hybrid",
        "vehicle_value": 150000,
        "region": "guangzhou",
        "owner_name": "王五",
        "id_card": "440101199001011234",
        "insurance_types": ["compulsory", "third_party"]
    }
]

class QuoteUser(HttpUser):
    """询价用户"""
    wait_time = between(0.1, 0.5)  # 请求间隔 0.1-0.5 秒
    
    @task(3)
    def calculate_quote(self):
        """计算报价（权重 3）"""
        request_data = QUOTE_REQUESTS[hash(str(time.time())) % len(QUOTE_REQUESTS)]
        
        with self.client.post("/api/v1/quote/calculate", json=request_data, catch_response=True) as response:
            if response.status_code == 200:
                result = response.json()
                if "request_id" in result and "quotes" in result:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_test_cases(self):
        """获取测试用例（权重 1）"""
        self.client.get("/api/v1/quote/test-cases")
    
    @task(2)
    def batch_calculate(self):
        """批量计算（权重 2）"""
        self.client.post("/api/v1/quote/batch-calculate", json=QUOTE_REQUESTS[:2])


class StrategyUser(HttpUser):
    """策略管理用户"""
    wait_time = between(0.5, 1.0)
    
    @task(2)
    def get_strategy_config(self):
        """获取策略配置"""
        self.client.get("/api/v1/strategy/config", params={"strategy_id": "default_v1"})
    
    @task(1)
    def get_insurer_list(self):
        """获取保司列表"""
        self.client.get("/api/v1/insurer/list")


class AnalyticsUser(HttpUser):
    """分析用户"""
    wait_time = between(1.0, 2.0)
    
    @task(2)
    def get_dashboard(self):
        """获取效果看板"""
        self.client.get("/api/v1/analytics/dashboard")
    
    @task(1)
    def get_business_unit_analysis(self):
        """获取业务单元分析"""
        self.client.get("/api/v1/analytics/business-unit")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始"""
    print("\n" + "=" * 60)
    print("压力测试开始")
    print("=" * 60)
    print(f"目标地址：{environment.host}")
    print(f"并发用户数：{environment.runner.user_count if environment.runner else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束"""
    print("\n" + "=" * 60)
    print("压力测试完成")
    print("=" * 60)
    
    if environment.stats.total.num_requests > 0:
        print(f"\n总体统计:")
        print(f"  总请求数：{environment.stats.total.num_requests}")
        print(f"  失败请求数：{environment.stats.total.num_failures}")
        print(f"  成功率：{(1 - environment.stats.total.fail_ratio) * 100:.2f}%")
        print(f"  平均响应时间：{environment.stats.total.avg_response_time:.2f}ms")
        print(f"  最小响应时间：{environment.stats.total.min_response_time:.2f}ms")
        print(f"  最大响应时间：{environment.stats.total.max_response_time:.2f}ms")
        print(f"  请求/秒：{environment.stats.total.current_rps:.2f}")
        
        print(f"\n按接口统计:")
        for name, stats in environment.stats.entries:
            if stats.num_requests > 0:
                print(f"  {name}:")
                print(f"    请求数：{stats.num_requests}")
                print(f"    失败率：{stats.fail_ratio * 100:.2f}%")
                print(f"    平均响应时间：{stats.avg_response_time:.2f}ms")
                print(f"    请求/秒：{stats.current_rps:.2f}")
    
    print("=" * 60)


if __name__ == "__main__":
    import os
    os.system("locust -f tests/test_stress.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 60s")
