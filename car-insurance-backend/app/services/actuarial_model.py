"""
精算模型 - 保费计算核心逻辑

基于中国车险行业标准的精算模型实现
考虑因素：车型、地区、历史出险、交通违法、险种组合等
"""

import logging
from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
import hashlib

logger = logging.getLogger(__name__)


class ActuarialModel:
    """精算模型"""
    
    # 交强险基础保费（按座位数）
    COMPULSORY_BASE_RATES = {
        "6_seat_below": 950,  # 6 座以下家庭自用
        "6_10_seat": 1100,   # 6-10 座家庭自用
        "10_seat_above": 1320,  # 10 座以上家庭自用
    }
    
    # 三者险基础保费（按保额）
    THIRD_PARTY_RATES = {
        1000000: 980,
        1500000: 1120,
        2000000: 1260,
        3000000: 1520,
        5000000: 1890,
    }
    
    # 车型风险系数（按车辆类型）
    VEHICLE_TYPE_FACTORS = {
        "sedan": 1.0,      # 轿车
        "suv": 1.1,        # SUV
        "mpv": 1.15,       # MPV
        "truck": 1.3,      # 货车
        "bus": 1.4,        # 客车
    }
    
    # 地区系数（按风险等级）
    REGION_FACTORS = {
        "beijing": 1.2,    # 北京 - 高风险
        "shanghai": 1.2,   # 上海 - 高风险
        "guangzhou": 1.15, # 广州 - 中高风险
        "shenzhen": 1.15,  # 深圳 - 中高风险
        "hangzhou": 1.1,   # 杭州 - 中风险
        "chengdu": 1.05,   # 成都 - 中低风险
        "default": 1.0,
    }
    
    # 燃料类型系数
    FUEL_TYPE_FACTORS = {
        "gasoline": 1.0,   # 汽油
        "diesel": 0.95,    # 柴油
        "electric": 1.1,   # 纯电动（维修成本高）
        "hybrid": 1.05,    # 混合动力
    }
    
    # 车损险基础费率
    VEHICLE_DAMAGE_BASE_RATE = 0.018  # 1.8%
    
    # 司机险/乘客险费率
    DRIVER_BASE_RATE = 80  # 每座 80 元
    PASSENGER_BASE_RATE = 60  # 每座 60 元
    
    def __init__(self):
        self.rate_table = {}
        self.test_vehicles = {}
    
    def calculate_compulsory_premium(self, vehicle_info: dict) -> float:
        """
        计算交强险保费
        
        公式：交强险保费 = 基础保费 × NCD 系数 × 交通违法系数
        """
        # 确定座位数（简化：假设家庭自用 6 座以下）
        seat_category = "6_seat_below"
        base_premium = self.COMPULSORY_BASE_RATES[seat_category]
        
        # NCD 系数（无赔款优待）- 简化为 1.0
        ncd_factor = 1.0
        
        # 交通违法系数 - 简化为 1.0
        violation_factor = 1.0
        
        premium = base_premium * ncd_factor * violation_factor
        return round(premium, 2)
    
    def calculate_third_party_premium(self, coverage: int = 2000000, vehicle_info: dict = None) -> float:
        """
        计算三者险保费
        
        coverage: 保额（元）
        """
        # 获取基础保费
        base_premium = self.THIRD_PARTY_RATES.get(coverage, 1260)
        
        # 应用车型系数
        vehicle_factor = self._get_vehicle_factor(vehicle_info)
        
        # 应用地区系数
        region_factor = self.REGION_FACTORS.get(
            vehicle_info.get('region', 'default'),
            self.REGION_FACTORS['default']
        )
        
        premium = base_premium * vehicle_factor * region_factor
        return round(premium, 2)
    
    def calculate_vehicle_damage_premium(self, vehicle_value: float, vehicle_info: dict = None) -> float:
        """
        计算车损险保费
        
        公式：车损险保费 = 保额 × 基础费率 × 车型系数 × 地区系数 × 自主折扣系数
        """
        # 保额（按实际价值）
        sum_insured = vehicle_value
        
        # 基础保费
        base_premium = sum_insured * self.VEHICLE_DAMAGE_BASE_RATE
        
        # 应用车型系数
        vehicle_factor = self._get_vehicle_factor(vehicle_info)
        
        # 应用地区系数
        region_factor = self.REGION_FACTORS.get(
            vehicle_info.get('region', 'default'),
            self.REGION_FACTORS['default']
        )
        
        # 自主折扣系数（简化为 1.0）
        discount_factor = 1.0
        
        premium = base_premium * vehicle_factor * region_factor * discount_factor
        return round(premium, 2)
    
    def calculate_driver_premium(self, seats: int = 1) -> float:
        """计算司机险保费"""
        return self.DRIVER_BASE_RATE * seats
    
    def calculate_passenger_premium(self, seats: int = 4) -> float:
        """计算乘客险保费"""
        return self.PASSENGER_BASE_RATE * seats
    
    def _get_vehicle_factor(self, vehicle_info: dict = None) -> float:
        """获取车型系数"""
        if not vehicle_info:
            return 1.0
        
        vehicle_type = vehicle_info.get('vehicle_type', 'sedan')
        return self.VEHICLE_TYPE_FACTORS.get(vehicle_type, 1.0)
    
    def calculate_platform_risk_score(self, quote_request: dict) -> int:
        """
        计算平台风险评分（0-100 分，10 档）
        
        考虑因素：
        - 车辆价值
        - 地区风险
        - 车主年龄
        - 燃料类型
        """
        score = 50  # 基础分
        
        # 车辆价值因素（越高越高风险）
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
        region_factor = self.REGION_FACTORS.get(region, 1.0)
        score += int((region_factor - 1.0) * 20)
        
        # 年龄因素（年轻和年老风险高）
        id_card = quote_request.get('id_card', '')
        if len(id_card) >= 18:
            birth_year = int(id_card[6:10])
            age = datetime.now().year - birth_year
            if age < 25:
                score += 10
            elif age > 60:
                score += 8
            elif 30 <= age <= 50:
                score -= 5
        
        # 燃料类型因素
        fuel_type = quote_request.get('fuel_type', 'gasoline')
        fuel_factor = self.FUEL_TYPE_FACTORS.get(fuel_type, 1.0)
        score += int((fuel_factor - 1.0) * 15)
        
        # 限制在 0-100 范围
        score = max(0, min(100, score))
        
        return score
    
    def calculate_full_premium(self, quote_request: dict) -> dict:
        """
        计算完整保费
        
        返回：
        {
            "compulsory": 交强险,
            "third_party": 三者险,
            "vehicle_damage": 车损险,
            "driver": 司机险,
            "passenger": 乘客险,
            "commercial": 商业险合计,
            "total": 总保费
        }
        """
        vehicle_info = {
            'region': quote_request.get('region', 'default'),
            'fuel_type': quote_request.get('fuel_type', 'gasoline'),
            'vehicle_type': 'sedan',  # 简化为轿车
        }
        
        # 交强险
        compulsory = self.calculate_compulsory_premium(vehicle_info)
        
        # 商业险
        third_party = 0
        vehicle_damage = 0
        driver = 0
        passenger = 0
        
        insurance_types = quote_request.get('insurance_types', ['compulsory'])
        
        if 'third_party' in insurance_types:
            third_party = self.calculate_third_party_premium(2000000, vehicle_info)
        
        if 'vehicle_damage' in insurance_types:
            vehicle_damage = self.calculate_vehicle_damage_premium(
                quote_request.get('vehicle_value', 0),
                vehicle_info
            )
        
        if 'driver' in insurance_types:
            driver = self.calculate_driver_premium(1)
        
        if 'passenger' in insurance_types:
            passenger = self.calculate_passenger_premium(4)
        
        commercial = third_party + vehicle_damage + driver + passenger
        total = compulsory + commercial
        
        return {
            "compulsory": compulsory,
            "third_party": third_party,
            "vehicle_damage": vehicle_damage,
            "driver": driver,
            "passenger": passenger,
            "commercial": commercial,
            "total": total,
        }
    
    def generate_request_id(self, quote_request: dict) -> str:
        """生成请求 ID"""
        content = f"{quote_request.get('vin', '')}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
