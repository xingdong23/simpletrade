"""
策略管理服务

提供策略的加载、初始化、启动、停止等功能。
"""


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
import logging
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session, joinedload
from pathlib import Path

from simpletrade.core.engine import STMainEngine
from simpletrade.api.deps import get_db
from simpletrade.models.database import Strategy, UserStrategy
from simpletrade.strategies import get_strategy_class, get_strategy_class_names, get_strategy_class_details
from vnpy.app.cta_strategy.template import CtaTemplate

logger = logging.getLogger("simpletrade.services.strategy_service")

class StrategyService:
    """策略管理服务"""

    def __init__(self, main_engine: STMainEngine):
        """
        初始化

        参数:
            main_engine (STMainEngine): 主引擎实例
        """
        self.main_engine = main_engine
        self.cta_engine = main_engine.get_cta_engine()

    def get_strategy_types(self, db: Session) -> List[str]:
        """
        获取数据库中所有活跃策略的不重复类型列表

        参数:
            db (Session): 数据库会话
        返回:
            List[str]: 策略类型列表
        """
        # 查询数据库获取不重复的 type
        query = db.query(Strategy.type).filter(Strategy.is_active == True).distinct()
        # SQLAlchemy 返回的是元组列表，例如 [('DoubleMaStrategy',), ('AtrRsiStrategy',)]
        # 需要将其转换为字符串列表
        types = [item[0] for item in query.all() if item[0]] # 确保类型不是 None 或空字符串

        # 如果数据库中没有策略类型，返回默认类型
        if not types:
            logger.warning("数据库中没有找到策略类型，返回默认类型")
            return ["cta"]  # 默认返回 CTA 类型

        return types

    def get_strategy_details(self) -> List[Dict[str, Any]]:
        """
        获取所有策略类的详细信息

        返回:
            List[Dict[str, Any]]: 策略类详细信息列表
        """
        return get_strategy_class_details()

    def get_strategies(self, db: Session, type: Optional[str] = None, category: Optional[str] = None) -> List[Strategy]:
        """
        获取所有策略记录 (使用传入的 db session)

        参数:
            db (Session): 数据库会话
            type (str, optional): 策略类型
            category (str, optional): 策略分类

        返回:
            List[Strategy]: 策略记录列表
        """
        query = db.query(Strategy).filter(Strategy.is_active == True)

        # 应用过滤条件
        if type:
            query = query.filter(Strategy.type == type)
        if category:
            query = query.filter(Strategy.category == category)

        return query.all()

    def get_strategy(self, db: Session, strategy_id: int) -> Optional[Strategy]:
        """
        获取策略记录 (使用传入的 db session)

        参数:
            db (Session): 数据库会话
            strategy_id (int): 策略ID

        返回:
            Strategy: 策略记录，如果不存在则返回None
        """
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.is_active == True).first()
        if strategy:
            logger.info(f"StrategyService.get_strategy: Found strategy ID {strategy_id}. Name: {strategy.name}, Identifier from DB object: {getattr(strategy, 'identifier', '[identifier attribute not found]')}")
        else:
            logger.info(f"StrategyService.get_strategy: Strategy ID {strategy_id} not found in DB.")
        return strategy

    def load_strategy_code(self, strategy: Strategy) -> Optional[str]:
        """
        从文件加载策略代码

        参数:
            strategy (Strategy): 策略记录

        返回:
            Optional[str]: 策略代码，如果无法加载则返回None
        """
        if not strategy:
            return None

        strategy_code = None
        file_path_str = ""

        if hasattr(strategy, 'identifier') and strategy.identifier:
            try:
                # 找到策略目录
                current_file_path = Path(__file__).resolve()  # 服务文件的绝对路径
                # simpletrade/services/strategy_service.py -> simpletrade/services/ -> simpletrade/
                simpletrade_root = current_file_path.parent.parent
                strategies_dir = simpletrade_root / "strategies"

                file_path = strategies_dir / f"{strategy.identifier}.py"
                file_path_str = str(file_path)

                if file_path.is_file():
                    strategy_code = file_path.read_text(encoding='utf-8')
                    logger.info(f"成功加载策略代码文件: {file_path_str}")
                else:
                    logger.warning(f"策略代码文件未找到: {file_path_str}")
            except FileNotFoundError:
                logger.warning(f"策略代码文件未找到 (FileNotFoundError): {file_path_str}")
            except Exception as e:
                logger.error(f"读取策略代码文件失败 ({file_path_str}): {e}")
        else:
            logger.warning(f"策略 {strategy.id} ({strategy.name}) 没有有效的 identifier 字段，无法加载代码。")

        return strategy_code

    def get_user_strategies(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户策略记录列表，并包含实时状态和创建时间

        参数:
            db (Session): 数据库会话
            user_id (int): 用户ID

        返回:
            List[Dict[str, Any]]: 包含策略信息、状态和创建时间字典的列表
        """
        user_strategies_orm = db.query(UserStrategy).filter(
            UserStrategy.user_id == user_id,
            UserStrategy.is_active == True
        ).options(joinedload(UserStrategy.strategy)).all() # 预加载关联的 Strategy

        result_list = []
        for us in user_strategies_orm:
            strategy_template = us.strategy # 从预加载中获取关联的 Strategy
            if not strategy_template:
                # 如果关联的 Strategy 被删除了或不存在，跳过这个用户策略
                logger.warning(f"UserStrategy {us.id} ({us.name}) references a non-existent Strategy {us.strategy_id}. Skipping.")
                continue

            # 尝试从 cta_engine 获取策略实例和状态
            strategy_instance = self.cta_engine.strategies.get(us.name)

            status = "已停止" # 默认状态
            if strategy_instance:
                if strategy_instance.trading:
                    status = "运行中"
                elif strategy_instance.inited:
                    status = "已初始化"
                # else: status remains "已停止" (or could be '未初始化' if needed)
            else:
                 # 如果 cta_engine 中没有实例，也认为是停止状态
                 status = "未加载"

            # 获取策略类型，优先使用strategy_type字段
            strategy_type = None
            if hasattr(strategy_template, 'strategy_type') and strategy_template.strategy_type:
                strategy_type = strategy_template.strategy_type
            elif hasattr(strategy_template, 'type') and strategy_template.type:
                strategy_type = strategy_template.type.lower()

            # 如果策略类型仍然为空，使用默认的CTA类型
            if not strategy_type:
                strategy_type = "cta"
                logger.warning(f"策略 ID {strategy_template.id} 的类型为空，使用默认的CTA类型")

            strategy_dict = {
                "id": us.id,
                "name": us.name,
                "strategy_id": strategy_template.id,
                "strategy_name": strategy_template.name,
                "category": strategy_template.category,
                "type": strategy_template.type,
                "strategy_type": strategy_type,  # 添加策略类型字段
                # 假设 UserStrategy 模型有 created_at 字段
                "createTime": us.created_at.strftime("%Y-%m-%d %H:%M:%S") if us.created_at else None,
                "status": status, # 添加状态字段
                "parameters": us.parameters,
                # 可以选择性添加其他需要的字段
                # "complexity": strategy_template.complexity,
                # "resource_requirement": strategy_template.resource_requirement,
            }
            result_list.append(strategy_dict)

        return result_list

    def get_user_strategy(self, db: Session, user_strategy_id: int) -> Optional[UserStrategy]:
        """
        获取用户策略记录 (使用传入的 db session)

        参数:
            db (Session): 数据库会话
            user_strategy_id (int): 用户策略ID

        返回:
            UserStrategy: 用户策略记录，如果不存在则返回None
        """
        return db.query(UserStrategy).filter(
            UserStrategy.id == user_strategy_id,
            UserStrategy.is_active == True
        ).first()

    def get_user_strategy_detail(self, db: Session, user_strategy_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户策略详情，包括关联的策略模板信息

        参数:
            db (Session): 数据库会话
            user_strategy_id (int): 用户策略ID

        返回:
            Dict[str, Any]: 用户策略详情字典，如果不存在则返回None
        """
        # 获取用户策略记录，并预加载关联的策略模板
        user_strategy = db.query(UserStrategy).filter(
            UserStrategy.id == user_strategy_id,
            UserStrategy.is_active == True
        ).options(joinedload(UserStrategy.strategy)).first()

        if not user_strategy:
            return None

        # 获取关联的策略模板
        strategy_template = user_strategy.strategy

        # 获取策略类型，优先使用user_strategy的strategy_type字段
        strategy_type = None
        if hasattr(user_strategy, 'strategy_type') and user_strategy.strategy_type:
            strategy_type = user_strategy.strategy_type
        elif strategy_template and hasattr(strategy_template, 'strategy_type') and strategy_template.strategy_type:
            strategy_type = strategy_template.strategy_type
        elif strategy_template and hasattr(strategy_template, 'type') and strategy_template.type:
            strategy_type = strategy_template.type.lower()

        # 如果策略类型仍然为空，使用默认的CTA类型
        if not strategy_type:
            strategy_type = "cta"
            logger.warning(f"用户策略 ID {user_strategy_id} 的类型为空，使用默认的CTA类型")

        # 构建用户策略详情字典
        user_strategy_dict = {
            "id": user_strategy.id,
            "user_id": user_strategy.user_id,
            "strategy_id": user_strategy.strategy_id,
            "name": user_strategy.name,
            "parameters": user_strategy.parameters,
            "created_at": user_strategy.created_at.isoformat() if user_strategy.created_at else None,
            "updated_at": user_strategy.updated_at.isoformat() if user_strategy.updated_at else None,
            "is_active": user_strategy.is_active,
            "strategy_type": strategy_type,
        }

        # 如果有关联的策略模板，添加模板信息
        if strategy_template:
            user_strategy_dict.update({
                "strategy_name": strategy_template.name,
                "category": strategy_template.category,
                "type": strategy_template.type,
                "identifier": getattr(strategy_template, 'identifier', None),
                "complexity": strategy_template.complexity,
                "resource_requirement": strategy_template.resource_requirement,
                "template_parameters": strategy_template.parameters,
            })

            # 尝试加载策略代码
            strategy_code = self.load_strategy_code(strategy_template)
            if strategy_code:
                user_strategy_dict["code"] = strategy_code

        # 尝试获取策略实例状态
        strategy_instance = self.cta_engine.strategies.get(user_strategy.name)
        status = "未加载"  # 默认状态
        if strategy_instance:
            if strategy_instance.trading:
                status = "运行中"
            elif strategy_instance.inited:
                status = "已初始化"
        user_strategy_dict["status"] = status

        return user_strategy_dict

    def create_strategy(self, name: str, description: str, type: str,
                       category: str, parameters: Dict[str, Any]) -> Optional[Strategy]:
        """
        创建策略

        参数:
            name (str): 策略名称
            description (str): 策略描述
            type (str): 策略类型
            category (str): 策略分类
            parameters (Dict[str, Any]): 策略参数

        返回:
            Strategy: 创建的策略记录，如果失败则返回None
        """
        # 验证策略类型是否存在
        if type not in get_strategy_class_names():
            logger.error(f"Strategy type {type} not found")
            return None

        try:
            db = next(get_db())  # 获取数据库会话
            try:
                strategy = Strategy(
                    name=name,
                    description=description,
                    type=type,
                    category=category,
                    parameters=parameters,
                    is_active=True
                )
                db.add(strategy)
                db.commit()
                db.refresh(strategy)
                logger.info(f"Strategy {name} created successfully")
                return strategy
            finally:
                db.close()  # 确保会话被关闭
        except Exception as e:
            logger.error(f"Failed to create strategy: {e}")
            return None

    def create_user_strategy(self, user_id: int, strategy_id: int, name: str,
                           parameters: Dict[str, Any]) -> Optional[UserStrategy]:
        """
        创建用户策略

        参数:
            user_id (int): 用户ID
            strategy_id (int): 策略ID
            name (str): 策略名称
            parameters (Dict[str, Any]): 策略参数

        返回:
            UserStrategy: 创建的用户策略记录，如果失败则返回None
        """
        try:
            db = next(get_db())  # 获取数据库会话
            try:
                # 检查策略是否存在
                strategy = db.query(Strategy).filter(
                    Strategy.id == strategy_id,
                    Strategy.is_active == True
                ).first()

                if not strategy:
                    logger.error(f"Strategy {strategy_id} not found")
                    return None

                # 获取策略类型，优先使用strategy_type字段
                strategy_type = None
                if hasattr(strategy, 'strategy_type') and strategy.strategy_type:
                    strategy_type = strategy.strategy_type
                elif hasattr(strategy, 'type') and strategy.type:
                    strategy_type = strategy.type.lower()

                # 如果策略类型仍然为空，使用默认的CTA类型
                if not strategy_type:
                    strategy_type = "cta"
                    logger.warning(f"策略 ID {strategy_id} 的类型为空，使用默认的CTA类型")

                # 创建用户策略
                user_strategy = UserStrategy(
                    user_id=user_id,
                    strategy_id=strategy_id,
                    name=name,
                    parameters=parameters,
                    is_active=True,
                    strategy_type=strategy_type  # 添加策略类型字段
                )
                db.add(user_strategy)
                db.commit()
                db.refresh(user_strategy)
                logger.info(f"User strategy {name} created successfully")
                return user_strategy
            finally:
                db.close()  # 确保会话被关闭
        except Exception as e:
            logger.error(f"Failed to create user strategy: {e}")
            return None

    def update_user_strategy(self, user_strategy_id: int, name: str,
                           parameters: Dict[str, Any]) -> Optional[UserStrategy]:
        """
        更新用户策略

        参数:
            user_strategy_id (int): 用户策略ID
            name (str): 策略名称
            parameters (Dict[str, Any]): 策略参数

        返回:
            UserStrategy: 更新后的用户策略记录，如果失败则返回None
        """
        try:
            db = next(get_db())  # 获取数据库会话
            try:
                user_strategy = db.query(UserStrategy).filter(
                    UserStrategy.id == user_strategy_id,
                    UserStrategy.is_active == True
                ).first()

                if not user_strategy:
                    logger.error(f"User strategy {user_strategy_id} not found")
                    return None

                user_strategy.name = name
                user_strategy.parameters = parameters
                db.commit()
                db.refresh(user_strategy)
                logger.info(f"User strategy {name} updated successfully")
                return user_strategy
            finally:
                db.close()  # 确保会话被关闭
        except Exception as e:
            logger.error(f"Failed to update user strategy: {e}")
            return None

    def delete_user_strategy(self, user_strategy_id: int) -> bool:
        """
        删除用户策略

        参数:
            user_strategy_id (int): 用户策略ID

        返回:
            bool: 是否删除成功
        """
        try:
            db = next(get_db())  # 获取数据库会话
            try:
                user_strategy = db.query(UserStrategy).filter(
                    UserStrategy.id == user_strategy_id,
                    UserStrategy.is_active == True
                ).first()

                if not user_strategy:
                    logger.error(f"User strategy {user_strategy_id} not found")
                    return False

                user_strategy.is_active = False
                db.commit()
                logger.info(f"User strategy {user_strategy_id} deleted successfully")
                return True
            finally:
                db.close()  # 确保会话被关闭
        except Exception as e:
            logger.error(f"Failed to delete user strategy: {e}")
            return False

    def load_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """
        加载策略配置

        参数:
            strategy_id (int): 策略ID

        返回:
            Dict[str, Any]: 策略配置，包含策略名称、类型和参数
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            logger.error(f"Strategy {strategy_id} not found")
            return {}

        # 获取策略类
        strategy_class = get_strategy_class(strategy.type)
        if not strategy_class:
            logger.error(f"Strategy class {strategy.type} not found")
            return {}

        # 构建策略配置
        strategy_config = {
            "strategy_name": strategy.name,
            "strategy_class": strategy.type,
            "setting": strategy.parameters
        }

        return strategy_config

    def load_user_strategy(self, user_strategy_id: int) -> Dict[str, Any]:
        """
        加载用户策略配置

        参数:
            user_strategy_id (int): 用户策略ID

        返回:
            Dict[str, Any]: 策略配置，包含策略名称、Python类对象和参数
        """
        # 使用 with get_db() 来确保会话关闭
        db = next(get_db()) # 获取 db 会话
        try:
            user_strategy = db.query(UserStrategy).filter(
                UserStrategy.id == user_strategy_id,
                UserStrategy.is_active == True
            ).options(joinedload(UserStrategy.strategy)).first() # 预加载 Strategy

            if not user_strategy:
                logger.error(f"User strategy {user_strategy_id} not found")
                return {}

            strategy = user_strategy.strategy # 使用预加载的 Strategy
            if not strategy:
                logger.error(f"Strategy {user_strategy.strategy_id} associated with user strategy {user_strategy_id} not found")
                return {}

            # --- 修正获取策略类的逻辑 ---
            # 检查 strategy 对象是否有 identifier 属性
            if not hasattr(strategy, 'identifier') or not strategy.identifier:
                logger.error(f"Strategy {strategy.id} ({strategy.name}) is missing a valid identifier.")
                return {}

            # 使用 identifier 获取策略类
            strategy_class_object = get_strategy_class(strategy.identifier)
            if not strategy_class_object:
                logger.error(f"Strategy class for identifier '{strategy.identifier}' not found")
                return {}
            # --------------------------

            # 构建策略配置
            strategy_config = {
                "strategy_name": user_strategy.name,
                # "strategy_class": strategy.type, # <-- 不再使用 type
                "strategy_class": strategy_class_object, # <-- 使用获取到的类对象
                "setting": user_strategy.parameters
            }

            return strategy_config
        finally:
            db.close() # 确保关闭会话

    def start_strategy(self, user_strategy_id: int) -> bool:
        """
        启动策略

        参数:
            user_strategy_id (int): 用户策略ID

        返回:
            bool: 是否启动成功
        """
        strategy_config = self.load_user_strategy(user_strategy_id)
        if not strategy_config:
            return False

        try:
            # 启动策略
            self.cta_engine.start_strategy(strategy_config["strategy_name"])
            logger.info(f"Strategy {strategy_config['strategy_name']} started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start strategy: {e}")
            return False

    def stop_strategy(self, user_strategy_id: int) -> bool:
        """
        停止策略

        参数:
            user_strategy_id (int): 用户策略ID

        返回:
            bool: 是否停止成功
        """
        strategy_config = self.load_user_strategy(user_strategy_id)
        if not strategy_config:
            return False

        try:
            # 停止策略
            self.cta_engine.stop_strategy(strategy_config["strategy_name"])
            logger.info(f"Strategy {strategy_config['strategy_name']} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop strategy: {e}")
            return False
