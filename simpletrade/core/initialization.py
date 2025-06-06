
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
import json
from pathlib import Path

from vnpy_custom.vnpy.event import EventEngine
from vnpy_custom.vnpy.trader.setting import SETTINGS # Needed for reading config for connect
from vnpy_custom.vnpy.trader.gateway import BaseGateway

# --- Import project specific config ---
from simpletrade.config.settings import DB_CONFIG, API_CONFIG, LOG_CONFIG # Import needed configs

# Import Core Engine
from simpletrade.core.engine import STMainEngine

# Import SimpleTrade Apps
from simpletrade.apps.st_message import STMessageApp
from simpletrade.apps.st_trader import STTraderApp
from simpletrade.apps.st_datamanager import STDataManagerApp
from simpletrade.apps.st_analysis import STAnalysisApp
from simpletrade.apps.st_backtest import STBacktestApp

# Import Optional External/VnPy Apps & Gateways with Error Handling
logger = logging.getLogger(__name__)

try:
    from vnpy_datamanager import DataManagerApp
    logger.info("Optional app 'vnpy_datamanager' imported successfully.")
except ImportError:
    logger.warning("Optional app 'vnpy_datamanager' not found.")
    DataManagerApp = None

try:
    from vnpy_ib import IbGateway
    logger.info("Optional gateway 'vnpy_ib' imported successfully.")
except ImportError:
    logger.warning("Optional gateway 'vnpy_ib' not found.")
    IbGateway = None

try:
    from vnpy_tiger import TigerGateway
    logger.info("Optional gateway 'vnpy_tiger' imported successfully.")
except ImportError as e:
    logger.error(f"Optional gateway 'vnpy_tiger' not found. Error: {e}")
    TigerGateway = None

# Import VnPy built-in Apps (might require vnpy installation)
try:
    from vnpy.app.cta_strategy import CtaStrategyApp # Import CtaStrategyApp
    logger.info("CtaStrategyApp imported successfully.")
except ImportError:
    logger.warning("Could not import CtaStrategyApp (might be intended to load by name).")

def _configure_vnpy_settings():
    """Helper function to configure VnPy global SETTINGS."""
    logger.info("Configuring VnPy global SETTINGS...")
    try:
        # Database Configuration
        logger.debug("Applying database settings...")
        SETTINGS["database.driver"] = "mysql"  # 使用database.driver而不是database.name
        SETTINGS["database.host"] = DB_CONFIG["DB_HOST"]
        SETTINGS["database.port"] = int(DB_CONFIG["DB_PORT"])
        SETTINGS["database.database"] = DB_CONFIG["DB_NAME"]
        SETTINGS["database.user"] = DB_CONFIG["DB_USER"]
        SETTINGS["database.password"] = DB_CONFIG["DB_PASSWORD"]
        logger.info("Database settings applied (using mysql).")
        logger.debug(f"  DB Driver: {SETTINGS.get('database.driver')}")
        logger.debug(f"  DB Host: {SETTINGS.get('database.host')}")
        # Add more debug logs if needed, avoid logging password

        # Datafeed Placeholder Configuration (to suppress warning)
        logger.debug("Applying dummy datafeed settings...")
        SETTINGS["datafeed.name"] = "dummy"
        SETTINGS["datafeed.username"] = ""
        SETTINGS["datafeed.password"] = ""
        logger.info("Dummy datafeed settings applied.")

        # You could potentially configure other SETTINGS here if needed
        # e.g., SETTINGS["log.active"] = True
        #       SETTINGS["log.level"] = LOG_CONFIG["LEVEL"]

        logger.info("VnPy global SETTINGS configuration complete.")

    except KeyError as e:
        logger.error(f"FATAL: Missing key in DB_CONFIG during SETTINGS configuration: {e}. Exiting.")
        # Depending on desired behavior, you might exit or raise the error
        raise e # Re-raise to be caught by the caller
    except Exception as e:
        logger.error(f"FATAL: Error during VnPy SETTINGS configuration: {e}. Exiting.", exc_info=True)
        raise e # Re-raise

def initialize_core_components():
    """
    Initializes the core components of SimpleTrade: EventEngine, STMainEngine,
    loads standard Apps and Gateways.
    Applies necessary configurations to VnPy SETTINGS.
    Returns main_engine, event_engine, and the configured database instance.
    """
    logger.info("Initializing core components...")
    db_instance = None # Initialize db_instance

    # +++ Configure VnPy SETTINGS first +++
    try:
        _configure_vnpy_settings()
        # 使用get_database()而不是直接实例化MysqlDatabase
        logger.info("Getting database instance after configuration...")
        from vnpy.trader.database import get_database
        db_instance = get_database()
        logger.info(f"Successfully obtained database instance: {type(db_instance)}")

        # 注释掉直接实例化MysqlDatabase的代码
        # logger.info("Attempting to import and instantiate vnpy_mysql.MysqlDatabase...")
        # try:
        #     from vnpy_mysql.mysql_database import MysqlDatabase
        #     db_instance = MysqlDatabase()
        #     logger.info(f"Successfully instantiated MysqlDatabase: {type(db_instance)}")
        # except ImportError as import_err:
        #     logger.critical(f"Failed to import vnpy_mysql: {import_err}. MySQL database cannot be used.")
        #     db_instance = None
        # except Exception as init_err:
        #     logger.critical(f"Failed to instantiate MysqlDatabase: {init_err}", exc_info=True)
        #     db_instance = None
        # +++ End explicit instantiation +++

    except Exception as config_e:
        logger.critical(f"Core component initialization failed due to SETTINGS configuration error: {config_e}")
        # Ensure db_instance is None if settings config itself failed
        db_instance = None
        raise RuntimeError(f"Failed to configure VnPy settings: {config_e}") from config_e

    # Ensure db_instance is valid before proceeding
    if not db_instance:
         logger.critical("Database instance (MySQL) could not be obtained/instantiated. Exiting.")
         # Decide how to handle - perhaps raise the RuntimeError again or a specific DB error
         raise RuntimeError("Failed to obtain/instantiate necessary MySQL database instance.")

    # 1. Create Engines (Now done after settings are configured)

    # 1. Create Engines (Now done after settings are configured)
    logger.debug("Creating EventEngine...")
    event_engine = EventEngine()
    logger.debug("Creating STMainEngine...")
    main_engine = STMainEngine(event_engine)
    logger.debug("Engines created.")

    # 2. Add Gateways
    logger.debug("Adding gateways...")
    if IbGateway:
        main_engine.add_gateway(IbGateway)
        logger.info("IB Gateway added.")
    if TigerGateway:
        main_engine.add_gateway(TigerGateway)
        logger.info("Tiger Gateway added.")
        # Attempt to connect Tiger Gateway automatically if config exists
        try:
            tiger_config_path = Path.home().joinpath(".vnpy", "connect_tiger.json")
            if tiger_config_path.exists():
                logger.info(f"Found Tiger connection config at {tiger_config_path}")
                with open(tiger_config_path, "r") as f:
                    tiger_configs = json.load(f)
                    if tiger_configs and isinstance(tiger_configs, list) and len(tiger_configs) > 0:
                        # Use the first config entry
                        tiger_config = tiger_configs[0]
                        logger.info(f"Attempting to connect Tiger: ID={tiger_config.get('tiger_id')}, Account={tiger_config.get('account')}")
                        # Construct setting dict carefully, handle potential missing keys
                        setting = {
                            "tiger_id": tiger_config.get("tiger_id", ""),
                            "account": tiger_config.get("account", ""),
                            "private_key": tiger_config.get("private_key", ""),
                            "server": tiger_config.get("server", "标准"), # Default to standard
                            "language": tiger_config.get("language", "中文") # Default to Chinese
                        }
                        # Filter out empty essential keys before connecting
                        if all([setting["tiger_id"], setting["account"], setting["private_key"]]):
                             main_engine.connect(setting, "TIGER")
                             # Note: Connection might happen asynchronously. We log the attempt here.
                             logger.info("Tiger Gateway connection initiated.")
                        else:
                            logger.warning("Tiger config found but missing essential keys (tiger_id, account, private_key). Connection skipped.")
            else:
                logger.info(f"Tiger connection config not found at {tiger_config_path}. Auto-connection skipped.")
        except Exception as e:
            logger.error(f"Error during automatic Tiger Gateway connection: {e}", exc_info=True)
    logger.debug("Gateways added.")

    # 3. Add Apps
    logger.debug("Adding applications...")
    # Add SimpleTrade Apps first (MessageApp often needs to be early)
    # 直接传递应用类，而不是应用实例
    main_engine.add_app(STMessageApp)
    logger.info("ST Message App added.")
    main_engine.add_app(STTraderApp)
    logger.info("ST Trader App added.")
    main_engine.add_app(STDataManagerApp)
    logger.info("ST Data Manager App added.")
    main_engine.add_app(STAnalysisApp)
    logger.info("ST Analysis App added.")
    main_engine.add_app(STBacktestApp)
    logger.info("ST Backtest App added.")

    # Add original VnPy DataManager App if available
    if DataManagerApp:
        main_engine.add_app(DataManagerApp)
        logger.info("Original VnPy DataManager App added.")

    # Add VnPy CTA Strategy App (using the class)
    try:
        main_engine.add_app(CtaStrategyApp) # 使用类名而不是字符串
        logger.info("VnPy CTA Strategy App added.")
    except Exception as e:
        # Catch potential errors if the app isn't found or fails to load
        logger.error(f"Failed to add CTA Strategy App: {e}", exc_info=True)
    logger.debug("Applications added.")

    # 4. 同步策略到数据库
    try:
        logger.info("正在同步策略到数据库...")
        from simpletrade.scripts.sync_strategies_to_db import sync_strategies_to_db
        sync_strategies_to_db()
        logger.info("策略同步完成")
    except Exception as e:
        logger.error(f"同步策略到数据库失败: {e}", exc_info=True)

    logger.info("Core components initialization complete.")
    # +++ Return db_instance along with engines +++
    return main_engine, event_engine, db_instance