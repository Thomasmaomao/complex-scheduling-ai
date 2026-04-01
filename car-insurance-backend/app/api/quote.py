"""
询价 API 路由（完整版）
"""

from fastapi import APIRouter, HTTPException
from typing import List
import time
import logging

from app.schemas.quote import (
    QuoteRequest,
    QuoteResponse,
    InsurerQuote,
    PremiumDetail,
    ScoreDetail,
)
from app.services.actuarial_model_full import ActuarialModel
from app.services.strategy_engine import StrategyEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化服务
actuarial_model = ActuarialModel()
strategy_engine = StrategyEngine()


@router.post("/calculate", response_model=QuoteResponse)
async def calculate_quote(request: QuoteRequest):
    """
    计算车险报价
    
    基于精算模型和策略引擎，返回多家保司的智能报价
    """
    start_time = time.time()
    
    try:
        # 转换请求数据
        quote_data = request.model_dump()
        
        # 1. 计算保费
        premiums = actuarial_model.calculate_full_premium(quote_data)
        
        # 2. 计算平台风险评分
        risk_score = actuarial_model.calculate_platform_risk_score(quote_data)
        
        # 3. 获取所有保司报价
        all_quotes = strategy_engine.get_all_insurer_quotes(
            quote_data,
            premiums,
            risk_score
        )
        
        # 4. 找出推荐报价
        recommended = None
        for quote in all_quotes:
            if quote.get("is_recommended"):
                recommended = quote
                break
        
        # 5. 生成响应
        calculation_time_ms = int((time.time() - start_time) * 1000)
        request_id = actuarial_model.generate_request_id(quote_data)
        
        response = QuoteResponse(
            request_id=request_id,
            quotes=all_quotes,
            recommended_quote=recommended,
            calculation_time_ms=calculation_time_ms,
        )
        
        logger.info(f"询价成功：request_id={request_id}, time={calculation_time_ms}ms")
        return response
        
    except Exception as e:
        logger.error(f"询价失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"计算失败：{str(e)}")


@router.get("/test-cases")
async def get_test_cases():
    """获取测试用例列表"""
    test_vehicles = actuarial_model.get_all_test_vehicles()
    
    test_cases = [
        {
            "case_id": vehicle["case_id"],
            "name": vehicle["name"],
            "vehicle_value": vehicle["base_price"],
            "region": "beijing" if "北京" in vehicle["name"] else "shanghai",
            "fuel_type": "electric" if "电动" in vehicle["name"] else "gasoline",
        }
        for vehicle in test_vehicles
    ]
    
    return {"test_cases": test_cases}


@router.post("/batch-calculate")
async def batch_calculate(requests: List[QuoteRequest]):
    """批量计算报价（用于测试）"""
    results = []
    
    for req in requests:
        try:
            result = await calculate_quote(req)
            results.append({
                "vin": req.vin,
                "status": "success",
                "total_premium": result.recommended_quote.premiums.total if result.recommended_quote else 0,
            })
        except Exception as e:
            results.append({
                "vin": req.vin,
                "status": "error",
                "error": str(e),
            })
    
    return {"results": results, "total": len(results)}
