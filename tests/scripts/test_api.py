"""
测试后端API

用于测试后端API的功能。
"""

import requests
import json

def test_api():
    """测试后端API"""
    print("开始测试后端API...")
    
    # 测试基本API
    base_url = "http://localhost:8000"
    
    # 测试健康检查API
    try:
        response = requests.get(f"{base_url}/health")
        print(f"健康检查API响应: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"健康检查API请求失败: {str(e)}")
    
    # 测试数据管理API
    try:
        response = requests.get(f"{base_url}/api/datamanager/symbols")
        print(f"数据管理API响应: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"数据管理API请求失败: {str(e)}")

if __name__ == "__main__":
    test_api()
