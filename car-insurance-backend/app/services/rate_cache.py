"""
费率表缓存服务
"""

from typing import Optional, Dict, List
from app.core.redis_client import redis_client


class RateTableCache:
    """费率表缓存服务"""
    
    # 缓存键前缀
    RATE_KEY_PREFIX = "rate_table:"
    RATE_TTL = 86400  # 24 小时
    
    def get_rate(self, rate_type: str, vehicle_type: str, region: str) -> Optional[Dict]:
        """
        获取费率缓存
        
        参数:
            rate_type: 费率类型（compulsory/commercial/ncd）
            vehicle_type: 车辆类型
            region: 地区
        
        返回:
            费率数据字典
        """
        key = f"{self.RATE_KEY_PREFIX}{rate_type}:{vehicle_type}:{region}"
        return redis_client.get(key)
    
    def set_rate(self, rate_type: str, vehicle_type: str, region: str, 
                 rate_data: Dict) -> bool:
        """
        设置费率缓存
        
        参数:
            rate_type: 费率类型
            vehicle_type: 车辆类型
            region: 地区
            rate_data: 费率数据
        
        返回:
            是否成功
        """
        key = f"{self.RATE_KEY_PREFIX}{rate_type}:{vehicle_type}:{region}"
        return redis_client.set(key, rate_data, self.RATE_TTL)
    
    def get_ncd_factor(self, claim_history: str) -> Optional[float]:
        """
        获取 NCD 系数缓存
        
        参数:
            claim_history: 出险历史标识
        
        返回:
            NCD 系数
        """
        key = f"{self.RATE_KEY_PREFIX}ncd:{claim_history}"
        return redis_client.get(key)
    
    def set_ncd_factor(self, claim_history: str, factor: float) -> bool:
        """
        设置 NCD 系数缓存
        
        参数:
            claim_history: 出险历史标识
            factor: NCD 系数值
        
        返回:
            是否成功
        """
        key = f"{self.RATE_KEY_PREFIX}ncd:{claim_history}"
        return redis_client.set(key, factor, self.RATE_TTL)
    
    def clear_rates(self, rate_type: Optional[str] = None) -> bool:
        """
        清除费率缓存
        
        参数:
            rate_type: 费率类型（可选，不传则清除所有）
        
        返回:
            是否成功
        """
        try:
            client = redis_client.get_client()
            if rate_type:
                pattern = f"{self.RATE_KEY_PREFIX}{rate_type}:*"
            else:
                pattern = f"{self.RATE_KEY_PREFIX}*"
            
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
            return True
        except Exception as e:
            print(f"Clear rate cache error: {e}")
            return False


# 全局费率表缓存实例
rate_table_cache = RateTableCache()
