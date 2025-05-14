#!/usr/bin/env python3
"""
更新所有vnpy导入路径

这个脚本会自动修改所有使用vnpy的文件，将vnpy包的导入改为使用源码。
"""

import os
import re
import glob
from pathlib import Path
import sys

# 配置
PROJECT_ROOT = Path("/Users/chengzheng/workspace/trade/simpletrade")
VNPY_CUSTOM_DIR = PROJECT_ROOT / "vnpy_custom"
SIMPLETRADE_DIR = PROJECT_ROOT / "simpletrade"

def find_python_files(directory):
    """查找所有Python文件"""
    return glob.glob(f"{directory}/**/*.py", recursive=True)

def update_imports(file_path):
    """更新导入语句"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"无法读取文件: {file_path}，跳过")
        return

    # 检查文件是否包含vnpy导入
    if "import vnpy" in content or "from vnpy" in content or "vnpy_ctastrategy" in content:
        print(f"处理文件: {file_path}")

        # 添加导入路径设置
        import_path_code = """
# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent
while VNPY_CUSTOM_DIR.name != "simpletrade" and VNPY_CUSTOM_DIR != VNPY_CUSTOM_DIR.parent:
    VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent
VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
"""

        # 检查文件是否已经包含导入路径设置
        if "VNPY_CUSTOM_DIR" not in content and "sys.path.insert" not in content:
            # 在导入语句前添加导入路径设置
            pattern = r'((?:""".*?"""|\'\'\'.*?\'\'\')\s*)?(?:import|from)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # 如果有文档字符串，在文档字符串后添加
                if match.group(1):
                    pos = match.start() + len(match.group(1))
                    content = content[:pos] + import_path_code + content[pos:]
                else:
                    # 否则在文件开头添加
                    content = import_path_code + content
            else:
                # 如果没有找到导入语句，在文件开头添加
                content = import_path_code + content

        # 更新vnpy_ctastrategy导入
        content = re.sub(
            r'from vnpy_ctastrategy import (.*)',
            r'from vnpy.app.cta_strategy import \1',
            content
        )

        # 更新vnpy_ctastrategy.template导入
        content = re.sub(
            r'from vnpy_ctastrategy.template import (.*)',
            r'from vnpy.app.cta_strategy.template import \1',
            content
        )

        # 更新vnpy_ctastrategy.strategies导入
        content = re.sub(
            r'from vnpy_ctastrategy.strategies import (.*)',
            r'from vnpy.app.cta_strategy.strategies import \1',
            content
        )

        # 更新vnpy_ctastrategy.backtesting导入
        content = re.sub(
            r'from vnpy_ctastrategy.backtesting import (.*)',
            r'from vnpy.app.cta_strategy.backtesting import \1',
            content
        )

        # 写入修改后的内容
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def update_init_file():
    """更新__init__.py文件，确保导入路径设置在最前面"""
    init_file = SIMPLETRADE_DIR / "__init__.py"
    
    if not init_file.exists():
        print(f"创建__init__.py文件: {init_file}")
        
        content = """\"\"\"
SimpleTrade - 一个简单的交易系统
\"\"\"

# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
    print(f"Added vnpy_custom to sys.path: {VNPY_CUSTOM_DIR}")

# 导入其他模块
from simpletrade.version import __version__

# 设置日志格式
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
"""
        
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(f"更新__init__.py文件: {init_file}")
        
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查文件是否已经包含导入路径设置
        if "VNPY_CUSTOM_DIR" not in content and "sys.path.insert" not in content:
            # 添加导入路径设置
            import_path_code = """
# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
    print(f"Added vnpy_custom to sys.path: {VNPY_CUSTOM_DIR}")

"""
            
            # 在导入语句前添加导入路径设置
            pattern = r'((?:""".*?"""|\'\'\'.*?\'\'\')\s*)?(?:import|from)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # 如果有文档字符串，在文档字符串后添加
                if match.group(1):
                    pos = match.start() + len(match.group(1))
                    content = content[:pos] + import_path_code + content[pos:]
                else:
                    # 否则在文件开头添加
                    content = import_path_code + content
            else:
                # 如果没有找到导入语句，在文件开头添加
                content = import_path_code + content
            
            # 写入修改后的内容
            with open(init_file, "w", encoding="utf-8") as f:
                f.write(content)

def main():
    """主函数"""
    # 更新__init__.py文件
    update_init_file()
    
    # 查找所有Python文件
    python_files = find_python_files(SIMPLETRADE_DIR)
    
    # 更新导入语句
    for file_path in python_files:
        update_imports(file_path)
    
    print("更新完成！")

if __name__ == "__main__":
    main()
