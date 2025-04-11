"""
SimpleTrade微信小程序认证接口

提供微信小程序认证接口，用于用户登录和授权。
"""

import os
import time
import json
import hashlib
import hmac
import base64
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import requests
from fastapi import APIRouter, Depends, HTTPException, Header, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import JWTError, jwt

# 创建路由器
router = APIRouter(prefix="/api/wechat/auth", tags=["wechat_auth"])

# 配置信息
# 注意：在实际应用中，这些信息应该存储在环境变量或配置文件中
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "your_app_id")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "your_app_secret")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1天

# 数据模型
class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录code")

class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    openid: str = Field(..., description="用户openid")
    session_key: str = Field(..., description="会话密钥")

class TokenData(BaseModel):
    """令牌数据"""
    openid: Optional[str] = None
    exp: Optional[int] = None

# 内存中的用户数据（实际应用中应该使用数据库）
users_db = {}

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/wechat/auth/token")

# 工具函数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        openid: str = payload.get("openid")
        if openid is None:
            raise credentials_exception
        token_data = TokenData(openid=openid, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(openid)
    if user is None:
        raise credentials_exception
    return user

# API路由
@router.post("/login", response_model=WechatLoginResponse)
async def wechat_login(request: WechatLoginRequest):
    """微信登录"""
    # 调用微信登录API
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&js_code={request.code}&grant_type=authorization_code"
    response = requests.get(url)
    data = response.json()
    
    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(status_code=400, detail=f"微信登录失败: {data.get('errmsg', '未知错误')}")
    
    openid = data.get("openid")
    session_key = data.get("session_key")
    
    if not openid or not session_key:
        raise HTTPException(status_code=400, detail="微信登录失败: 未获取到openid或session_key")
    
    # 创建用户（如果不存在）
    if openid not in users_db:
        users_db[openid] = {
            "openid": openid,
            "session_key": session_key,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
    else:
        users_db[openid]["session_key"] = session_key
        users_db[openid]["last_login"] = datetime.now().isoformat()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"openid": openid},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "openid": openid,
        "session_key": session_key
    }

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """获取访问令牌（用于OAuth2密码流）"""
    # 在实际应用中，这里应该验证用户名和密码
    # 但在微信小程序中，我们通常使用code登录，所以这里只是为了兼容OAuth2密码流
    
    # 检查用户是否存在
    if form_data.username not in users_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"openid": form_data.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
