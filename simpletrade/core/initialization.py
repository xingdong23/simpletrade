import logging
import json
from pathlib import Path

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS # Needed for reading config for connect

# Import Core Engine
from simpletrade.core.engine import STMainEngine

# Import SimpleTrade Apps
from simpletrade.apps.st_message import STMessageApp
from simpletrade.apps.st_trader import STTraderApp
from simpletrade.apps.st_datamanager import STDataManagerApp
from simpletrade.apps.st_analysis import STAnalysisApp

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
    # CTA Strategy App is typically added by string name
    # from vnpy_ctastrategy import CtaStrategyApp # Import if adding by class instance
    pass
except ImportError:
    logger.warning("Could not import CtaStrategyApp (might be intended to load by name).")


def initialize_core_components():
    """
    Initializes the core components of SimpleTrade: EventEngine, STMainEngine,
    loads standard Apps and Gateways.
    """
    logger.info("Initializing core components...")

    # 1. Create Engines
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

    # Add original VnPy DataManager App if available
    if DataManagerApp:
        main_engine.add_app(DataManagerApp)
        logger.info("Original VnPy DataManager App added.")

    # Add VnPy CTA Strategy App (using string name)
    try:
        main_engine.add_app("CtaStrategy") # Use string name
        logger.info("VnPy CTA Strategy App added.")
    except Exception as e:
        # Catch potential errors if the app isn't found or fails to load
        logger.error(f"Failed to add CTA Strategy App: {e}", exc_info=True)
    logger.debug("Applications added.")

    logger.info("Core components initialization complete.")
    return main_engine, event_engine