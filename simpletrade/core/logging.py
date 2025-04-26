"""
SimpleTrade 日志模块

提供统一的日志配置和管理功能。
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

# 默认配置
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_DIR = "logs"
LOG_ROTATION = "midnight"  # 每天午夜轮换日志
LOG_BACKUP_COUNT = 30  # 保留30天的日志

# 颜色格式
COLORS = {
    "DEBUG": "\033[36m",  # 青色
    "INFO": "\033[32m",   # 绿色
    "WARNING": "\033[33m", # 黄色
    "ERROR": "\033[31m",  # 红色
    "CRITICAL": "\033[41m", # 红底
    "RESET": "\033[0m"    # 重置
}

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    def format(self, record):
        """格式化日志记录，为不同级别添加颜色"""
        levelname = record.levelname
        if levelname in COLORS and sys.stdout.isatty():  # 仅在终端输出时启用颜色
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            if record.levelno >= logging.ERROR:
                record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['RESET']}"
        return super().format(record)


# 全局日志配置状态
_logging_configured = False
_log_dir = Path(DEFAULT_LOG_DIR)

def configure_logging(
    log_level: Union[int, str] = DEFAULT_LOG_LEVEL,
    log_dir: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    console_output: bool = True,
    file_output: bool = True,
    colored_console: bool = True
) -> None:
    """
    配置全局日志
    
    Args:
        log_level: 日志级别，可以是int或str
        log_dir: 日志文件目录
        log_format: 日志格式
        date_format: 日期格式
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
        colored_console: 控制台输出是否带颜色
    """
    global _logging_configured, _log_dir
    
    if _logging_configured:
        return
    
    # 转换日志级别字符串为int
    if isinstance(log_level, str):
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"无效的日志级别: {log_level}")
        log_level = numeric_level
    
    # 设置日志目录
    if log_dir:
        _log_dir = Path(log_dir)
    
    # 创建日志目录（如果不存在）
    if file_output:
        _log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        if colored_console:
            console_formatter = ColoredFormatter(log_format, date_format)
        else:
            console_formatter = logging.Formatter(log_format, date_format)
            
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    if file_output:
        log_file = _log_dir / f"simpletrade_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when=LOG_ROTATION,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 设置已配置标志
    _logging_configured = True
    
    # 记录初始日志消息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成，级别: {logging.getLevelName(log_level)}, 目录: {_log_dir if file_output else 'None'}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    如果全局日志尚未配置，将自动使用默认配置初始化
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    if not _logging_configured:
        configure_logging()
    
    return logging.getLogger(name) 