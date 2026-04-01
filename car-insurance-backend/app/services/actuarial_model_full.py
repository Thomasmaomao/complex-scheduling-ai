"""
精算模型 - 完整版本（集成 Redis 缓存）

基于中国车险行业标准的精算模型实现
包含：车型映射、费率表、系数模拟、风险损失计算、赔付率分析
"""

import logging
from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json

from app.services.rate_cache import rate_table_cache

logger = logging.getLogger(__name__)


# ========== 15 个测试车型映射表 ==========
TEST_VEHICLES_MAP = {
    "TC001": {
        "name": "经济型轿车 - 大众朗逸",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 1.6,
        "base_price": 120000,
        "risk_level": "low",
    },
    "TC002": {
        "name": "豪华型轿车 - 宝马 5 系",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 2.0,
        "base_price": 450000,
        "risk_level": "medium",
    },
    "TC003": {
        "name": "电动车 - 特斯拉 Model 3",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 0,
        "base_price": 250000,
        "risk_level": "medium",
    },
    "TC004": {
        "name": "SUV-本田 CR-V",
        "vehicle_type": "suv",
        "seat_count": 5,
        "displacement": 1.5,
        "base_price": 180000,
        "risk_level": "low",
    },
    "TC005": {
        "name": "MPV-别克 GL8",
        "vehicle_type": "mpv",
        "seat_count": 7,
        "displacement": 2.0,
        "base_price": 300000,
        "risk_level": "medium",
    },
    "TC006": {
        "name": "紧凑型 SUV-哈弗 H6",
        "vehicle_type": "suv",
        "seat_count": 5,
        "displacement": 1.5,
        "base_price": 130000,
        "risk_level": "low",
    },
    "TC007": {
        "name": "中型轿车 - 丰田凯美瑞",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 2.0,
        "base_price": 200000,
        "risk_level": "low",
    },
    "TC008": {
        "name": "豪华 SUV-奔驰 GLC",
        "vehicle_type": "suv",
        "seat_count": 5,
        "displacement": 2.0,
        "base_price": 400000,
        "risk_level": "medium",
    },
    "TC009": {
        "name": "小型车 - 本田飞度",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 1.5,
        "base_price": 80000,
        "risk_level": "low",
    },
    "TC010": {
        "name": "混合动力 - 丰田卡罗拉双擎",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 1.8,
        "base_price": 150000,
        "risk_level": "low",
    },
    "TC011": {
        "name": "纯电动 - 比亚迪汉 EV",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 0,
        "base_price": 220000,
        "risk_level": "medium",
    },
    "TC012": {
        "name": "中大型 SUV-奥迪 Q7",
        "vehicle_type": "suv",
        "seat_count": 7,
        "displacement": 2.0,
        "base_price": 650000,
        "risk_level": "high",
    },
    "TC013": {
        "name": "微型车 - 五菱宏光 MINI",
        "vehicle_type": "sedan",
        "seat_count": 4,
        "displacement": 0,
        "base_price": 30000,
        "risk_level": "low",
    },
    "TC014": {
        "name": "性能车 - 宝马 M3",
        "vehicle_type": "sedan",
        "seat_count": 5,
        "displacement": 3.0,
        "base_price": 850000,
        "risk_level": "high",
    },
    "TC015": {
        "name": "豪华 MPV-丰田埃尔法",
        "vehicle_type": "mpv",
        "seat_count": 7,
        "displacement": 2.5,
        "base_price": 800000,
        "risk_level": "high",
    },
}

# ========== 费率表 ==========
RATE_TABLE = {
    # 交强险基础保费（按座位数）
    "compulsory": {
        "6_seat_below": 950,
        "6_10_seat": 1100,
        "10_seat_above": 1320,
    },
    
    # 三者险基础保费（按保额）
    "third_party": {
        1000000: 980,
        1500000: 1120,
        2000000: 1260,
        3000000: 1520,
        5000000: 1890,
    },
    
    # 车型风险系数
    "vehicle_type_factors": {
        "sedan": 1.0,
        "suv": 1.1,
        "mpv": 1.15,
        "truck": 1.3,
        "bus": 1.4,
    },
    
    # 地区系数
    "region_factors": {
        "beijing": 1.2,
        "shanghai": 1.2,
        "guangzhou": 1.15,
        "shenzhen": 1.15,
        "hangzhou": 1.1,
        "chengdu": 1.05,
        "default": 1.0,
    },
    
    # 燃料类型系数
    "fuel_type_factors": {
        "gasoline": 1.0,
        "diesel": 0.95,
        "electric": 1.1,
        "hybrid": 1.05,
    },
    
    # 车损险基础费率
    "vehicle_damage_base_rate": 0.018,
    
    # 司机险/乘客险费率
    "driver_base_rate": 80,
    "passenger_base_rate": 60,
}


class ActuarialModel:
    """精算模型 - 完整版本（集成 Redis 缓存）"""
    
    def __init__(self):
        self.rate_table = RATE_TABLE
        self.test_vehicles = TEST_VEHICLES_MAP
        self.cache = rate_table_cache
    
    # ========== 系数模拟 ==========
    
    def calculate_ncd_factor(self, claim_history: List[dict]) -> float:
        """
        计算 NCD 系数（无赔款优待）
        
        claim_history: 历史出险记录
        - 连续 3 年无赔：0.6
        - 连续 2 年无赔：0.7
        - 连续 1 年无赔：0.85
        - 上年有赔：1.0
        - 连续 2 年有赔：1.25
        - 连续 3 年及以上有赔：1.5
        """
        if not claim_history:
            return 1.0
        
        # 尝试从缓存获取
        cache_key = str(sorted([str(h) for h in claim_history]))
        cached = self.cache.get_ncd_factor(cache_key)
        if cached:
            return cached
        
        consecutive_no_claim = 0
        consecutive_claim = 0
        
        for record in sorted(claim_history, key=lambda x: x.get('year', 0), reverse=True):
            if record.get('claim_count', 0) == 0:
                consecutive_no_claim += 1
                consecutive_claim = 0
            else:
                consecutive_claim += 1
                consecutive_no_claim = 0
        
        if consecutive_no_claim >= 3:
            factor = 0.6
        elif consecutive_no_claim == 2:
            factor = 0.7
        elif consecutive_no_claim == 1:
            factor = 0.85
        elif consecutive_claim >= 3:
            factor = 1.5
        elif consecutive_claim == 2:
            factor = 1.25
        else:
            factor = 1.0
        
        # 缓存结果
        self.cache.set_ncd_factor(cache_key, factor)
        return factor
    
    def calculate_violation_factor(self, violation_count: int = 0) -> float:
        """
        计算交通违法系数
        
        上年无违法：0.9
        上年违法 1-5 次：1.0
        上年违法 6-10 次：1.1
        上年违法 11-15 次：1.2
        上年违法 16-20 次：1.3
        上年违法 20 次以上：1.5
        """
        if violation_count == 0:
            return 0.9
        elif violation_count <= 5:
            return 1.0
        elif violation_count <= 10:
            return 1.1
        elif violation_count <= 15:
            return 1.2
        elif violation_count <= 20:
            return 1.3
        else:
            return 1.5
    
    def calculate_discount_factor(self, channel: str = "direct", customer_value: str = "normal") -> float:
        """
        计算自主折扣系数
        
        channel: 销售渠道 (direct/agent/broker)
        customer_value: 客户价值 (high/normal/low)
        """
        base_factor = 1.0
        
        # 渠道系数
        channel_factors = {
            "direct": 0.85,
            "agent": 0.9,
            "broker": 0.95,
        }
        
        # 客户价值系数
        value_factors = {
            "high": 0.9,
            "normal": 1.0,
            "low": 1.05,
        }
        
        factor = base_factor * channel_factors.get(channel, 1.0) * value_factors.get(customer_value, 1.0)
        return max(0.5, min(1.5, factor))  # 限制在 0.5-1.5 范围
    
    # ========== 纯风险损失计算 ==========
    
    def calculate_pure_risk_loss(self, vehicle_info: dict, insurance_types: List[str]) -> dict:
        """
        计算纯风险损失（按险别组合）
        
        返回各险别的预期损失率
        """
        vehicle_type = vehicle_info.get('vehicle_type', 'sedan')
        vehicle_value = vehicle_info.get('vehicle_value', 100000)
        region = vehicle_info.get('region', 'default')
        driver_age = vehicle_info.get('driver_age', 35)
        
        # 基础损失率
        base_loss_rates = {
            "compulsory": 0.035,
            "third_party": 0.025,
            "vehicle_damage": 0.045,
            "driver": 0.008,
            "passenger": 0.006,
        }
        
        # 车型调整系数
        vehicle_type_adj = {
            "sedan": 1.0,
            "suv": 1.1,
            "mpv": 1.15,
            "truck": 1.4,
            "bus": 1.5,
        }
        
        # 地区调整系数
        region_adj = self.rate_table["region_factors"].get(region, 1.0)
        
        # 年龄调整系数
        if driver_age < 25:
            age_adj = 1.2
        elif driver_age > 60:
            age_adj = 1.15
        else:
            age_adj = 1.0
        
        # 计算各险别损失率
        loss_rates = {}
        for ins_type in insurance_types:
            base_rate = base_loss_rates.get(ins_type, 0.03)
            adj_rate = base_rate * vehicle_type_adj.get(vehicle_type, 1.0) * region_adj * age_adj
            loss_rates[ins_type] = round(adj_rate, 4)
        
        return loss_rates
    
    # ========== 赔付率计算与偏差分析 ==========
    
    def calculate_loss_ratio(self, actual_claims: float, earned_premium: float) -> dict:
        """
        计算赔付率与偏差分析
        
        actual_claims: 实际赔付金额
        earned_premium: 已赚保费
        """
        if earned_premium <= 0:
            return {
                "loss_ratio": 0,
                "expected_loss_ratio": 0.65,
                "deviation": 0,
                "status": "error",
                "message": "已赚保费必须大于 0"
            }
        
        loss_ratio = actual_claims / earned_premium
        expected_loss_ratio = 0.65  # 行业平均赔付率
        deviation = loss_ratio - expected_loss_ratio
        
        # 判断状态
        if abs(deviation) < 0.05:
            status = "normal"
        elif deviation > 0.1:
            status = "high_risk"
        elif deviation < -0.1:
            status = "low_risk"
        else:
            status = "warning"
        
        return {
            "loss_ratio": round(loss_ratio, 4),
            "expected_loss_ratio": expected_loss_ratio,
            "deviation": round(deviation, 4),
            "deviation_percentage": round(deviation * 100, 2),
            "status": status,
        }
    
    # ========== 保费计算核心方法 ==========
    
    def calculate_compulsory_premium(self, vehicle_info: dict, claim_history: List[dict] = None, 
                                      violation_count: int = 0) -> float:
        """
        计算交强险保费（完整版）
        
        公式：交强险保费 = 基础保费 × NCD 系数 × 交通违法系数
        """
        # 确定座位数
        seat_count = vehicle_info.get('seat_count', 5)
        if seat_count <= 6:
            seat_category = "6_seat_below"
        elif seat_count <= 10:
            seat_category = "6_10_seat"
        else:
            seat_category = "10_seat_above"
        
        base_premium = self.rate_table["compulsory"][seat_category]
        
        # NCD 系数
        ncd_factor = self.calculate_ncd_factor(claim_history or [])
        
        # 交通违法系数
        violation_factor = self.calculate_violation_factor(violation_count)
        
        premium = base_premium * ncd_factor * violation_factor
        return round(premium, 2)
    
    def calculate_third_party_premium(self, coverage: int = 2000000, vehicle_info: dict = None,
                                       discount_factor: float = 1.0) -> float:
        """
        计算三者险保费（完整版）
        """
        # 获取基础保费
        base_premium = self.rate_table["third_party"].get(coverage, 1260)
        
        # 应用车型系数
        vehicle_type = vehicle_info.get('vehicle_type', 'sedan') if vehicle_info else 'sedan'
        vehicle_factor = self.rate_table["vehicle_type_factors"].get(vehicle_type, 1.0)
        
        # 应用地区系数
        region = vehicle_info.get('region', 'default') if vehicle_info else 'default'
        region_factor = self.rate_table["region_factors"].get(region, 1.0)
        
        premium = base_premium * vehicle_factor * region_factor * discount_factor
        return round(premium, 2)
    
    def calculate_vehicle_damage_premium(self, vehicle_value: float, vehicle_info: dict = None,
                                          discount_factor: float = 1.0) -> float:
        """
        计算车损险保费（完整版）
        """
        # 基础保费
        base_rate = self.rate_table["vehicle_damage_base_rate"]
        base_premium = vehicle_value * base_rate
        
        # 应用车型系数
        vehicle_type = vehicle_info.get('vehicle_type', 'sedan') if vehicle_info else 'sedan'
        vehicle_factor = self.rate_table["vehicle_type_factors"].get(vehicle_type, 1.0)
        
        # 应用地区系数
        region = vehicle_info.get('region', 'default') if vehicle_info else 'default'
        region_factor = self.rate_table["region_factors"].get(region, 1.0)
        
        premium = base_premium * vehicle_factor * region_factor * discount_factor
        return round(premium, 2)
    
    def calculate_driver_premium(self, seats: int = 1, discount_factor: float = 1.0) -> float:
        """计算司机险保费"""
        return self.rate_table["driver_base_rate"] * seats * discount_factor
    
    def calculate_passenger_premium(self, seats: int = 4, discount_factor: float = 1.0) -> float:
        """计算乘客险保费"""
        return self.rate_table["passenger_base_rate"] * seats * discount_factor
    
    def calculate_full_premium(self, quote_request: dict) -> dict:
        """
        计算完整保费（完整版）
        
        考虑所有系数和风险因子
        """
        # 提取车辆信息
        vehicle_info = {
            'region': quote_request.get('region', 'default'),
            'fuel_type': quote_request.get('fuel_type', 'gasoline'),
            'vehicle_type': 'sedan',
            'seat_count': 5,
            'vehicle_value': quote_request.get('vehicle_value', 0),
            'driver_age': self._calculate_age_from_id(quote_request.get('id_card', '')),
        }
        
        # 计算系数
        claim_history = quote_request.get('claim_history', [])
        violation_count = quote_request.get('violation_count', 0)
        channel = quote_request.get('channel', 'direct')
        customer_value = quote_request.get('customer_value', 'normal')
        
        ncd_factor = self.calculate_ncd_factor(claim_history)
        violation_factor = self.calculate_violation_factor(violation_count)
        discount_factor = self.calculate_discount_factor(channel, customer_value)
        
        # 交强险
        compulsory = self.calculate_compulsory_premium(vehicle_info, claim_history, violation_count)
        
        # 商业险
        third_party = 0
        vehicle_damage = 0
        driver = 0
        passenger = 0
        
        insurance_types = quote_request.get('insurance_types', ['compulsory'])
        
        if 'third_party' in insurance_types:
            third_party = self.calculate_third_party_premium(2000000, vehicle_info, discount_factor)
        
        if 'vehicle_damage' in insurance_types:
            vehicle_damage = self.calculate_vehicle_damage_premium(
                quote_request.get('vehicle_value', 0),
                vehicle_info,
                discount_factor
            )
        
        if 'driver' in insurance_types:
            driver = self.calculate_driver_premium(1, discount_factor)
        
        if 'passenger' in insurance_types:
            passenger = self.calculate_passenger_premium(4, discount_factor)
        
        commercial = third_party + vehicle_damage + driver + passenger
        total = compulsory + commercial
        
        # 计算损失率
        loss_rates = self.calculate_pure_risk_loss(vehicle_info, insurance_types)
        
        return {
            "compulsory": compulsory,
            "third_party": third_party,
            "vehicle_damage": vehicle_damage,
            "driver": driver,
            "passenger": passenger,
            "commercial": commercial,
            "total": total,
            "coefficients": {
                "ncd": ncd_factor,
                "violation": violation_factor,
                "discount": discount_factor,
            },
            "loss_rates": loss_rates,
        }
    
    def _calculate_age_from_id(self, id_card: str) -> int:
        """从身份证号计算年龄"""
        if len(id_card) < 18:
            return 35  # 默认年龄
        birth_year = int(id_card[6:10])
        return datetime.now().year - birth_year
    
    def calculate_platform_risk_score(self, quote_request: dict) -> int:
        """
        计算平台风险评分（0-100 分，10 档）
        
        考虑因素：
        - 车辆价值
        - 地区风险
        - 车主年龄
        - 燃料类型
        - 历史出险
        - 交通违法
        """
        score = 50  # 基础分
        
        # 车辆价值因素
        vehicle_value = quote_request.get('vehicle_value', 0)
        if vehicle_value > 500000:
            score += 15
        elif vehicle_value > 300000:
            score += 10
        elif vehicle_value > 150000:
            score += 5
        elif vehicle_value < 50000:
            score -= 5
        
        # 地区风险因素
        region = quote_request.get('region', 'default')
        region_factor = self.rate_table["region_factors"].get(region, 1.0)
        score += int((region_factor - 1.0) * 20)
        
        # 年龄因素
        id_card = quote_request.get('id_card', '')
        age = self._calculate_age_from_id(id_card)
        if age < 25:
            score += 10
        elif age > 60:
            score += 8
        elif 30 <= age <= 50:
            score -= 5
        
        # 燃料类型因素
        fuel_type = quote_request.get('fuel_type', 'gasoline')
        fuel_factor = self.rate_table["fuel_type_factors"].get(fuel_type, 1.0)
        score += int((fuel_factor - 1.0) * 15)
        
        # 历史出险因素
        claim_history = quote_request.get('claim_history', [])
        if claim_history:
            recent_claims = sum(1 for c in claim_history[-3:] if c.get('claim_count', 0) > 0)
            score += recent_claims * 5
        
        # 交通违法因素
        violation_count = quote_request.get('violation_count', 0)
        score += min(violation_count, 20)
        
        # 限制在 0-100 范围
        score = max(0, min(100, score))
        
        return score
    
    def generate_request_id(self, quote_request: dict) -> str:
        """生成请求 ID"""
        content = f"{quote_request.get('vin', '')}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_test_vehicle(self, case_id: str) -> Optional[dict]:
        """获取测试车型信息"""
        return self.test_vehicles.get(case_id)
    
    def get_all_test_vehicles(self) -> List[dict]:
        """获取所有测试车型"""
        return [
            {"case_id": k, **v}
            for k, v in self.test_vehicles.items()
        ]
