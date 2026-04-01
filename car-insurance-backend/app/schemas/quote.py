from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class FuelType(str, Enum):
    """燃料类型"""
    GASOLINE = "gasoline"  # 汽油
    DIESEL = "diesel"  # 柴油
    ELECTRIC = "electric"  # 纯电动
    HYBRID = "hybrid"  # 混合动力


class InsuranceType(str, Enum):
    """险种类型"""
    COMPULSORY = "compulsory"  # 交强险
    THIRD_PARTY = "third_party"  # 三者险
    VEHICLE_DAMAGE = "vehicle_damage"  # 车损险
    DRIVER = "driver"  # 司机险
    PASSENGER = "passenger"  # 乘客险


# ========== 请求 Schema ==========

class QuoteRequest(BaseModel):
    """询价请求"""
    license_plate: str = Field(..., description="车牌号", min_length=5, max_length=10)
    vin: str = Field(..., description="车架号", min_length=17, max_length=17)
    registration_date: date = Field(..., description="初登日期")
    fuel_type: FuelType = Field(..., description="燃料类型")
    vehicle_value: float = Field(..., description="新车购置价", gt=0)
    region: str = Field(..., description="地区")
    owner_name: str = Field(..., description="车主姓名")
    id_card: str = Field(..., description="身份证号", min_length=18, max_length=18)
    insurance_types: List[InsuranceType] = Field(
        default=[InsuranceType.COMPULSORY],
        description="险种选择"
    )
    
    class Config:
        use_enum_values = True


class StrategyTestRequest(BaseModel):
    """策略测试请求"""
    strategy_id: str = Field(..., description="策略 ID")
    test_cases: List[QuoteRequest] = Field(..., description="测试用例列表")


# ========== 响应 Schema ==========

class PremiumDetail(BaseModel):
    """保费明细"""
    compulsory: float = Field(0, description="交强险保费")
    commercial: float = Field(0, description="商业险保费")
    vehicle_damage: float = Field(0, description="车损险保费")
    third_party: float = Field(0, description="三者险保费")
    driver: float = Field(0, description="司机险保费")
    passenger: float = Field(0, description="乘客险保费")
    total: float = Field(0, description="总保费")


class ScoreDetail(BaseModel):
    """评分详情"""
    price: int = Field(0, description="价格得分", ge=0, le=100)
    service: int = Field(0, description="服务得分", ge=0, le=100)
    claim: int = Field(0, description="赔付得分", ge=0, le=100)
    overall: int = Field(0, description="综合得分", ge=0, le=100)


class InsurerQuote(BaseModel):
    """保司报价"""
    insurer_id: str = Field(..., description="保司 ID")
    insurer_name: str = Field(..., description="保司名称")
    premiums: PremiumDetail = Field(..., description="保费明细")
    scores: ScoreDetail = Field(..., description="评分详情")
    is_recommended: bool = Field(False, description="是否推荐")
    reasons: List[str] = Field(default=[], description="推荐理由")


class QuoteResponse(BaseModel):
    """询价响应"""
    request_id: str = Field(..., description="请求 ID")
    quotes: List[InsurerQuote] = Field(..., description="报价列表")
    recommended_quote: Optional[InsurerQuote] = Field(None, description="推荐报价")
    calculation_time_ms: int = Field(..., description="计算耗时 (毫秒)")


class StrategyConfig(BaseModel):
    """策略配置"""
    strategy_id: str = Field(..., description="策略 ID")
    strategy_name: str = Field(..., description="策略名称")
    description: str = Field("", description="策略描述")
    priority_weights: dict = Field(default={}, description="优先级权重")
    threshold_rules: dict = Field(default={}, description="阈值规则")
    is_active: bool = Field(True, description="是否启用")


class StrategyTestResult(BaseModel):
    """策略测试结果"""
    test_id: str = Field(..., description="测试 ID")
    strategy_id: str = Field(..., description="策略 ID")
    total_cases: int = Field(..., description="测试用例总数")
    passed_cases: int = Field(..., description="通过用例数")
    failed_cases: int = Field(..., description="失败用例数")
    pass_rate: float = Field(..., description="通过率")
    details: List[dict] = Field(default=[], description="详细结果")


# ========== 分析 Schema ==========

class AnalyticsDashboard(BaseModel):
    """分析看板"""
    total_quotes: int = Field(0, description="总询价数")
    total_premium: float = Field(0, description="总保费")
    avg_premium: float = Field(0, description="平均保费")
    conversion_rate: float = Field(0, description="转化率")
    insurer_distribution: List[dict] = Field(default=[], description="保司分布")
    daily_trend: List[dict] = Field(default=[], description="日趋势")
