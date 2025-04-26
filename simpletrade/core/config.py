"""
SimpleTrade 配置管理模块

提供统一的配置管理，支持从环境变量和配置文件加载。
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast
from pydantic import BaseModel, Field, validator

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()

# 配置模型
class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    host: str = Field("localhost", description="数据库主机地址")
    port: int = Field(3306, description="数据库端口")
    username: str = Field("root", description="数据库用户名")
    password: str = Field("", description="数据库密码")
    database: str = Field("simpletrade", description="数据库名称")
    driver: str = Field("mysql+pymysql", description="数据库驱动")
    pool_size: int = Field(5, description="连接池大小")
    max_overflow: int = Field(10, description="最大溢出连接数")
    pool_timeout: int = Field(30, description="连接池超时时间")
    pool_recycle: int = Field(1800, description="连接回收时间")
    echo: bool = Field(False, description="是否打印SQL语句")

    def get_connection_url(self) -> str:
        """获取数据库连接URL"""
        return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class CORSConfig(BaseModel):
    """CORS配置模型"""
    allow_origins: List[str] = Field(["*"], description="允许的源")
    allow_methods: List[str] = Field(["*"], description="允许的方法")
    allow_headers: List[str] = Field(["*"], description="允许的头部")
    allow_credentials: bool = Field(True, description="是否允许凭证")

class ServerConfig(BaseModel):
    """服务器配置模型"""
    host: str = Field("0.0.0.0", description="服务器主机地址")
    port: int = Field(8000, description="服务器端口")
    debug: bool = Field(False, description="是否开启调试模式")
    reload: bool = Field(False, description="是否开启热重载")
    workers: int = Field(1, description="工作进程数")
    cors: CORSConfig = Field(default_factory=CORSConfig, description="CORS配置")

class LoggingConfig(BaseModel):
    """日志配置模型"""
    level: str = Field("INFO", description="日志级别")
    format: str = Field("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", description="日志格式")
    date_format: str = Field("%Y-%m-%d %H:%M:%S", description="日期格式")
    directory: str = Field("logs", description="日志目录")
    file_output: bool = Field(True, description="是否输出到文件")
    console_output: bool = Field(True, description="是否输出到控制台")
    colored_console: bool = Field(True, description="控制台是否使用颜色")
    rotation: str = Field("midnight", description="轮换时间")
    backup_count: int = Field(30, description="备份文件数量")

class AppConfig(BaseModel):
    """应用配置模型"""
    debug: bool = Field(False, description="调试模式")
    environment: str = Field("production", description="运行环境")
    server: ServerConfig = Field(default_factory=ServerConfig, description="服务器配置")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")

    @validator('environment')
    def validate_environment(cls, v):
        """验证环境变量"""
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"环境必须是以下之一: {', '.join(allowed)}")
        return v

# 配置管理器单例
class ConfigManager:
    """配置管理器类
    
    负责加载和管理应用配置。
    """
    _instance = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._config = None
        return cls._instance
    
    def load_from_file(self, config_path: Union[str, Path]) -> None:
        """从文件加载配置
        
        Args:
            config_path: 配置文件路径
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        self._config = AppConfig.parse_obj(config_data)
        
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        # 数据库配置
        db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "username": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "simpletrade"),
        }
        
        # 服务器配置
        server_config = {
            "host": os.getenv("SERVER_HOST", "0.0.0.0"),
            "port": int(os.getenv("SERVER_PORT", "8000")),
            "debug": os.getenv("SERVER_DEBUG", "").lower() in ("true", "1", "yes"),
            "reload": os.getenv("SERVER_RELOAD", "").lower() in ("true", "1", "yes"),
            "workers": int(os.getenv("SERVER_WORKERS", "1")),
        }
        
        # 日志配置
        log_config = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "directory": os.getenv("LOG_DIR", "logs"),
        }
        
        # 应用配置
        app_config = {
            "debug": os.getenv("APP_DEBUG", "").lower() in ("true", "1", "yes"),
            "environment": os.getenv("APP_ENV", "production"),
            "server": server_config,
            "database": db_config,
            "logging": log_config,
        }
        
        self._config = AppConfig.parse_obj(app_config)
    
    def set_config(self, config: AppConfig) -> None:
        """设置配置
        
        Args:
            config: 配置对象
        """
        self._config = config
    
    def get_config(self) -> AppConfig:
        """获取配置
        
        Returns:
            AppConfig: 配置对象
        
        Raises:
            RuntimeError: 如果配置未初始化
        """
        if self._config is None:
            raise RuntimeError("配置未初始化，请先调用 load_from_file/load_from_env/set_config")
        return self._config
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置
        
        Returns:
            ServerConfig: 服务器配置对象
        """
        return self.get_config().server
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置
        
        Returns:
            DatabaseConfig: 数据库配置对象
        """
        return self.get_config().database
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置
        
        Returns:
            LoggingConfig: 日志配置对象
        """
        return self.get_config().logging

# 全局配置管理器实例
_config_manager = ConfigManager()

def initialize_config(config_path: Optional[Union[str, Path]] = None) -> AppConfig:
    """初始化配置
    
    如果提供了配置文件路径，则从文件加载；
    否则尝试从环境变量加载。
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        AppConfig: 配置对象
    """
    if config_path:
        _config_manager.load_from_file(config_path)
    else:
        _config_manager.load_from_env()
    
    return _config_manager.get_config()

def get_config() -> AppConfig:
    """获取配置对象
    
    Returns:
        AppConfig: 配置对象
    """
    return _config_manager.get_config()

def get_server_config() -> ServerConfig:
    """获取服务器配置对象
    
    Returns:
        ServerConfig: 服务器配置对象
    """
    return _config_manager.get_server_config()

def get_database_config() -> DatabaseConfig:
    """获取数据库配置对象
    
    Returns:
        DatabaseConfig: 数据库配置对象
    """
    return _config_manager.get_database_config()

def get_logging_config() -> LoggingConfig:
    """获取日志配置对象
    
    Returns:
        LoggingConfig: 日志配置对象
    """
    return _config_manager.get_logging_config() 