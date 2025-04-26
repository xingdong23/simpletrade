"""
通用API响应模型定义
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

# 用于泛型响应的类型变量
T = TypeVar('T')

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": None
            }
        }

class PaginatedResponse(ApiResponse, Generic[T]):
    """分页响应模型"""
    data: Optional[List[T]] = Field(None, description="分页数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "查询成功",
                "data": [],
                "total": 100,
                "page": 1,
                "size": 10,
                "pages": 10
            }
        }

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "操作失败",
                "code": "E1001",
                "details": {
                    "field": "username",
                    "reason": "已存在"
                }
            }
        } 