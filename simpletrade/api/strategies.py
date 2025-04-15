"""
SimpleTrade策略API

提供策略相关的RESTful API接口。
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from simpletrade.config.database import get_db
from simpletrade.models.database import Strategy, UserStrategy

# 创建路由器
router = APIRouter(prefix="/api/strategies", tags=["strategies"])

# 数据模型
class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

class StrategyParameter(BaseModel):
    """策略参数模型"""
    type: str
    default: Any
    min: Optional[Any] = None
    max: Optional[Any] = None
    options: Optional[List[str]] = None
    description: str

class StrategyModel(BaseModel):
    """策略模型"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    type: str
    complexity: int
    resource_requirement: int
    parameters: Dict[str, StrategyParameter]

# API路由
@router.get("/", response_model=ApiResponse)
async def get_strategies(
    type: Optional[str] = None,
    category: Optional[str] = None
):
    """获取策略列表"""
    try:
        with get_db() as db:
            query = db.query(Strategy).filter(Strategy.is_active == True)
            
            # 应用过滤条件
            if type:
                query = query.filter(Strategy.type == type)
            if category:
                query = query.filter(Strategy.category == category)
                
            db_strategies = query.all()
            
            # 如果数据库中没有数据，返回空列表
            if not db_strategies:
                return {
                    "success": True,
                    "message": "没有找到符合条件的策略",
                    "data": []
                }
            
            # 将数据库对象转换为字典
            strategies = []
            for s in db_strategies:
                strategy_dict = {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "category": s.category,
                    "type": s.type,
                    "complexity": s.complexity,
                    "resource_requirement": s.resource_requirement,
                    "parameters": s.parameters
                }
                strategies.append(strategy_dict)
            
            return {
                "success": True,
                "message": f"获取策略成功，共 {len(strategies)} 个",
                "data": strategies
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略失败: {str(e)}"
        }

@router.get("/{strategy_id}", response_model=ApiResponse)
async def get_strategy(strategy_id: int):
    """获取策略详情"""
    try:
        with get_db() as db:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.is_active == True).first()
            
            if not strategy:
                return {
                    "success": False,
                    "message": f"未找到ID为 {strategy_id} 的策略"
                }
            
            # 将数据库对象转换为字典
            strategy_dict = {
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "category": strategy.category,
                "type": strategy.type,
                "complexity": strategy.complexity,
                "resource_requirement": strategy.resource_requirement,
                "parameters": strategy.parameters,
                "code": strategy.code
            }
            
            return {
                "success": True,
                "message": f"获取策略详情成功",
                "data": strategy_dict
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略详情失败: {str(e)}"
        }

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_strategies(user_id: int):
    """获取用户策略列表"""
    try:
        with get_db() as db:
            user_strategies = db.query(UserStrategy).filter(
                UserStrategy.user_id == user_id,
                UserStrategy.is_active == True
            ).all()
            
            # 如果数据库中没有数据，返回空列表
            if not user_strategies:
                return {
                    "success": True,
                    "message": f"用户 {user_id} 没有策略",
                    "data": []
                }
            
            # 将数据库对象转换为字典
            strategies = []
            for us in user_strategies:
                strategy = us.strategy
                strategy_dict = {
                    "id": us.id,
                    "name": us.name,
                    "strategy_id": strategy.id,
                    "strategy_name": strategy.name,
                    "category": strategy.category,
                    "type": strategy.type,
                    "complexity": strategy.complexity,
                    "resource_requirement": strategy.resource_requirement,
                    "parameters": us.parameters
                }
                strategies.append(strategy_dict)
            
            return {
                "success": True,
                "message": f"获取用户策略成功，共 {len(strategies)} 个",
                "data": strategies
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取用户策略失败: {str(e)}"
        }
