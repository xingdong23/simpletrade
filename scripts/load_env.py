"""
加载环境变量脚本

从 .env 文件加载环境变量。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.absolute()
    
    # 加载 .env 文件
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"Loading environment variables from {env_file}")
        load_dotenv(dotenv_path=env_file)
    else:
        print(f"Warning: .env file not found at {env_file}")
        print("Using default environment variables.")
    
    # 打印当前环境变量
    print("\nCurrent environment variables:")
    for key in sorted(os.environ.keys()):
        if key.startswith('SIMPLETRADE_'):
            print(f"  {key}={os.environ[key]}")
    
    print("\nDatabase connection parameters:")
    print(f"  Host: {os.environ.get('SIMPLETRADE_DB_HOST', 'localhost')}:{os.environ.get('SIMPLETRADE_DB_PORT', '3306')}")
    print(f"  Database: {os.environ.get('SIMPLETRADE_DB_NAME', 'simpletrade')}")
    print(f"  User: {os.environ.get('SIMPLETRADE_DB_USER', 'root')}")

if __name__ == "__main__":
    main()
