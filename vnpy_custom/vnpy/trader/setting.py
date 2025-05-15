"""
全局设置
"""

from pathlib import Path
from typing import Dict, Any

# 默认设置
SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,

    "log.active": True,
    "log.level": "INFO",
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "database.timezone": "Asia/Shanghai",
    "database.driver": "sqlite",
    "database.database": "database.db",
    "database.host": "localhost",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "",
    "database.authentication_source": "admin",
}

# 导入本地配置
SETTING_FILENAME: str = "vt_setting.json"
SETTING_FILEPATH: Path = Path.cwd().joinpath(SETTING_FILENAME)

if SETTING_FILEPATH.exists():
    import json

    with open(SETTING_FILEPATH, mode="r") as f:
        local_setting = json.load(f)
    SETTINGS.update(local_setting)
