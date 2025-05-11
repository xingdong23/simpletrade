"""
同步策略到数据库

该脚本将simpletrade/strategies目录下的所有策略同步到数据库中。
如果策略已存在（通过identifier字段匹配），则更新其信息；
如果策略不存在，则创建新记录。
"""

import os
import sys
import inspect
import logging
from pathlib import Path
from typing import Dict, Any, List, Type

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from simpletrade.config.database import SessionLocal
from simpletrade.models.database import Strategy
from simpletrade.strategies import (
    get_strategy_class_names,
    get_strategy_class,
    get_strategy_category,
    get_strategy_description
)
from vnpy_ctastrategy.template import CtaTemplate

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sync_strategies")

def get_strategy_parameters(strategy_class: Type) -> Dict[str, Any]:
    """
    获取策略参数的详细信息

    Args:
        strategy_class (Type): 策略类

    Returns:
        Dict[str, Any]: 参数信息字典
    """
    parameters = {}

    # 获取策略参数列表
    param_list = getattr(strategy_class, "parameters", [])

    for param_name in param_list:
        # 获取参数默认值
        default_value = getattr(strategy_class, param_name, None)

        # 确定参数类型
        param_type = "string"
        if isinstance(default_value, int):
            param_type = "int"
        elif isinstance(default_value, float):
            param_type = "float"
        elif isinstance(default_value, bool):
            param_type = "boolean"

        # 创建参数信息
        parameters[param_name] = {
            "type": param_type,
            "default": default_value,
            "description": f"{param_name}参数"
        }

    return parameters

def sync_strategies_to_db():
    """
    将策略同步到数据库
    """
    db = SessionLocal()
    try:
        # 获取所有策略类名
        strategy_class_names = get_strategy_class_names()
        logger.info(f"发现 {len(strategy_class_names)} 个策略类")

        # 获取数据库中已有的策略
        existing_strategies = db.query(Strategy).all()
        existing_identifiers = {s.identifier: s for s in existing_strategies if s.identifier}

        # 同步每个策略
        for class_name in strategy_class_names:
            strategy_class = get_strategy_class(class_name)
            if not strategy_class:
                logger.warning(f"无法获取策略类 {class_name}")
                continue

            # 获取策略信息
            category = get_strategy_category(class_name)
            description = get_strategy_description(class_name)
            parameters = get_strategy_parameters(strategy_class)

            # 确定策略复杂度和资源需求
            complexity = 1  # 默认复杂度
            resource_requirement = 1  # 默认资源需求

            # 根据参数数量估计复杂度
            param_count = len(parameters)
            if param_count > 10:
                complexity = 4
            elif param_count > 5:
                complexity = 3
            elif param_count > 2:
                complexity = 2

            # 如果策略已存在，更新信息
            if class_name in existing_identifiers:
                strategy = existing_identifiers[class_name]
                logger.info(f"更新策略: {class_name}")

                # 更新策略信息

                # 为策略生成中文名称
                chinese_name = class_name
                if class_name == "GridStrategy":
                    chinese_name = "网格交易策略"
                elif class_name == "DoubleMaStrategy":
                    chinese_name = "双均线策略"
                elif class_name == "TurtleSignalStrategy":
                    chinese_name = "海龟交易策略"

                # 确定策略类型
                strategy_type = "cta"  # 默认为CTA策略类型

                strategy.name = chinese_name
                strategy.description = description
                strategy.category = category
                strategy.parameters = parameters
                strategy.complexity = complexity
                strategy.resource_requirement = resource_requirement
                strategy.strategy_type = strategy_type  # 设置策略类型字段
            else:
                # 创建新策略
                logger.info(f"创建新策略: {class_name}")

                # 为策略生成中文名称
                chinese_name = class_name
                if class_name == "GridStrategy":
                    chinese_name = "网格交易策略"
                elif class_name == "DoubleMaStrategy":
                    chinese_name = "双均线策略"
                elif class_name == "TurtleSignalStrategy":
                    chinese_name = "海龟交易策略"

                # 确定策略类型
                strategy_type = "cta"  # 默认为CTA策略类型

                strategy = Strategy(
                    name=chinese_name,
                    description=description,
                    category=category,
                    type="cta",  # 默认为CTA策略类型
                    complexity=complexity,
                    resource_requirement=resource_requirement,
                    parameters=parameters,
                    identifier=class_name,  # 使用类名作为标识符
                    strategy_type=strategy_type  # 设置策略类型字段
                )
                db.add(strategy)

        # 提交事务
        db.commit()
        logger.info("策略同步完成")
    except Exception as e:
        db.rollback()
        logger.error(f"同步策略时发生错误: {str(e)}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    sync_strategies_to_db()
