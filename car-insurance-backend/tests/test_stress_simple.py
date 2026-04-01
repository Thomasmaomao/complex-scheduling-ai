"""
压力测试脚本 - 简单并发测试
"""

import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"

# 测试数据
QUOTE_REQUEST = {
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

# 统计信息
class Stats:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_time = 0
        self.min_time = float('inf')
        self.max_time = 0
        self.lock = threading.Lock()
    
    def record(self, success, elapsed):
        with self.lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            self.total_time += elapsed
            self.min_time = min(self.min_time, elapsed)
            self.max_time = max(self.max_time, elapsed)
    
    def report(self):
        if self.total_requests == 0:
            return "No requests"
        
        return f"""
压力测试结果
============================================================
总请求数：{self.total_requests}
成功请求：{self.successful_requests}
失败请求：{self.failed_requests}
成功率：{self.successful_requests / self.total_requests * 100:.2f}%
平均响应时间：{self.total_time / self.total_requests:.2f}ms
最小响应时间：{self.min_time:.2f}ms
最大响应时间：{self.max_time:.2f}ms
吞吐量：{self.total_requests / (self.total_time / 1000):.2f} 请求/秒
============================================================"""

def make_request(stats, request_id):
    """发送单个请求"""
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/quote/calculate", json=QUOTE_REQUEST, timeout=10)
        elapsed = (time.time() - start_time) * 1000
        
        success = response.status_code == 200
        stats.record(success, elapsed)
        
        return success, elapsed
    except Exception as e:
        stats.record(False, 0)
        return False, 0

def run_stress_test(concurrent_users, duration_seconds):
    """运行压力测试"""
    print("=" * 60)
    print("压力测试")
    print("=" * 60)
    print(f"并发用户数：{concurrent_users}")
    print(f"测试持续时间：{duration_seconds}秒")
    print("=" * 60)
    
    stats = Stats()
    stop_flag = threading.Event()
    
    def worker():
        """工作线程"""
        request_id = 0
        while not stop_flag.is_set():
            request_id += 1
            make_request(stats, request_id)
            time.sleep(0.1)  # 每个用户每秒约 10 个请求
    
    # 启动线程
    threads = []
    print(f"\n启动 {concurrent_users} 个并发用户...")
    for i in range(concurrent_users):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    # 等待测试结束
    print(f"测试运行中...")
    time.sleep(duration_seconds)
    stop_flag.set()
    
    # 等待所有线程结束
    for t in threads:
        t.join(timeout=1)
    
    # 输出报告
    print("\n" + stats.report())
    
    # 性能评估
    avg_time = stats.total_time / stats.total_requests if stats.total_requests > 0 else 0
    success_rate = stats.successful_requests / stats.total_requests * 100 if stats.total_requests > 0 else 0
    
    print("\n性能评估:")
    if avg_time < 100 and success_rate > 99:
        print("  🟢 优秀 - 响应时间 < 100ms，成功率 > 99%")
    elif avg_time < 200 and success_rate > 95:
        print("  🟡 良好 - 响应时间 < 200ms，成功率 > 95%")
    elif avg_time < 500 and success_rate > 90:
        print("  🟠 合格 - 响应时间 < 500ms，成功率 > 90%")
    else:
        print("  🔴 需要优化 - 响应时间或成功率不达标")
    
    print("=" * 60)
    
    return stats

if __name__ == "__main__":
    import sys
    
    # 测试场景
    test_scenarios = [
        (10, 30, "10 并发 30 秒"),
        (50, 30, "50 并发 30 秒"),
        (100, 30, "100 并发 30 秒"),
    ]
    
    print("车险询价系统压力测试")
    print("=" * 60)
    
    all_results = []
    
    for concurrent_users, duration, name in test_scenarios:
        print(f"\n\n测试场景：{name}")
        print("=" * 60)
        
        stats = run_stress_test(concurrent_users, duration)
        all_results.append((name, stats))
    
    # 总结
    print("\n\n" + "=" * 60)
    print("压力测试总结")
    print("=" * 60)
    
    for name, stats in all_results:
        avg_time = stats.total_time / stats.total_requests if stats.total_requests > 0 else 0
        success_rate = stats.successful_requests / stats.total_requests * 100 if stats.total_requests > 0 else 0
        print(f"{name}: 平均响应 {avg_time:.2f}ms, 成功率 {success_rate:.2f}%")
    
    print("=" * 60)
