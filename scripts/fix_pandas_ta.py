#!/usr/bin/env python3
"""
修复pandas_ta与numpy的兼容性问题
"""

import os
import sys
import importlib.util
import numpy as np

def find_file(package_name, module_path):
    """查找模块文件路径"""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return None
    
    package_path = os.path.dirname(spec.origin)
    file_path = os.path.join(package_path, module_path)
    
    if os.path.exists(file_path):
        return file_path
    
    return None

def fix_squeeze_pro():
    """修复squeeze_pro.py文件"""
    file_path = find_file("pandas_ta", "momentum/squeeze_pro.py")
    
    if file_path is None:
        print("未找到squeeze_pro.py文件")
        return False
    
    print(f"找到squeeze_pro.py文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, "r") as f:
        content = f.read()
    
    # 替换导入语句
    if "from numpy import NaN as npNaN" in content:
        content = content.replace(
            "from numpy import NaN as npNaN",
            "import numpy as np\nnpNaN = np.nan  # 使用np.nan替代NaN"
        )
        
        # 写入修改后的内容
        with open(file_path, "w") as f:
            f.write(content)
        
        print("已修复squeeze_pro.py文件")
        return True
    else:
        print("squeeze_pro.py文件不需要修复")
        return False

def main():
    """主函数"""
    fixed = fix_squeeze_pro()
    
    if fixed:
        print("修复完成，请重新运行程序")
    else:
        print("无需修复或修复失败")

if __name__ == "__main__":
    main()
