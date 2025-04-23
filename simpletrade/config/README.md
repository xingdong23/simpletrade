# SimpleTrade 配置包 (config)

SimpleTrade 的配置包负责管理应用程序的全局配置参数，提供统一的配置接口和数据库连接管理。

## 主要文件

1. **settings.py** - 全局配置参数
2. **database.py** - 数据库连接配置和管理

## settings.py

`settings.py` 是配置包的核心文件，定义了应用程序的全局配置参数。它主要包含以下配置：

### 1. 数据库配置 (DB_CONFIG)

```python
DB_CONFIG = {
    # 数据库连接参数
    "DB_USER": os.environ.get("SIMPLETRADE_DB_USER", "root"),
    "DB_PASSWORD": os.environ.get("SIMPLETRADE_DB_PASSWORD", "Cz159csa"),
    "DB_HOST": os.environ.get("SIMPLETRADE_DB_HOST", "localhost"),
    "DB_PORT": os.environ.get("SIMPLETRADE_DB_PORT", "3306"),
    "DB_NAME": os.environ.get("SIMPLETRADE_DB_NAME", "simpletrade"),
    
    # 数据库连接池配置
    "POOL_SIZE": int(os.environ.get("SIMPLETRADE_DB_POOL_SIZE", "5")),
    "MAX_OVERFLOW": int(os.environ.get("SIMPLETRADE_DB_MAX_OVERFLOW", "10")),
    "POOL_RECYCLE": int(os.environ.get("SIMPLETRADE_DB_POOL_RECYCLE", "3600")),
    "ECHO": os.environ.get("SIMPLETRADE_DB_ECHO", "False").lower() == "true",
}
```

### 2. API 配置 (API_CONFIG)

```python
API_CONFIG = {
    "HOST": os.environ.get("SIMPLETRADE_API_HOST", "0.0.0.0"),
    "PORT": int(os.environ.get("SIMPLETRADE_API_PORT", "8003")),
    "DEBUG": os.environ.get("SIMPLETRADE_API_DEBUG", "True").lower() == "true",
}
```

### 3. 日志配置 (LOG_CONFIG)

```python
LOG_CONFIG = {
    "LEVEL": os.environ.get("SIMPLETRADE_LOG_LEVEL", "INFO"),
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}
```

### 4. 数据同步目标配置 (DATA_SYNC_TARGETS)

```python
DATA_SYNC_TARGETS = [
    {
        "source": "qlib",        # 数据源为 qlib
        "symbol": "AAPL",       # 品种代码
        "exchange": "NASDAQ",   # 交易所
        "interval": "d"         # K线周期 (日线)
    },
    # 可以添加更多目标...
]
```

## database.py

`database.py` 负责数据库连接配置和管理，主要功能包括：

1. **导入配置**：从 `settings.py` 导入数据库配置
2. **创建数据库引擎**：使用 SQLAlchemy 创建数据库引擎
3. **创建会话工厂**：提供数据库会话管理
4. **提供 Base 类**：用于创建 ORM 模型

```python
# 构建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    echo=ECHO
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于创建模型类
Base = declarative_base()

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
```

## 配置的使用方式

SimpleTrade 项目中的配置使用方式主要有以下几种：

### 1. 环境变量配置

项目支持通过环境变量覆盖默认配置，环境变量前缀为 `SIMPLETRADE_`。项目提供了 `.env.example` 文件作为模板，可以复制为 `.env` 并根据需要修改。

```bash
# 复制环境变量配置示例文件
cp .env.example .env

# 编辑环境变量配置文件
vim .env  # 或使用其他编辑器
```

### 2. 在代码中使用配置

在代码中使用配置的方式如下：

```python
# 导入配置
from simpletrade.config.settings import DB_CONFIG, API_CONFIG, LOG_CONFIG

# 使用配置
db_host = DB_CONFIG["DB_HOST"]
api_port = API_CONFIG["PORT"]
log_level = LOG_CONFIG["LEVEL"]
```

### 3. 数据库配置的使用

数据库配置主要通过 `database.py` 中的对象使用：

```python
from simpletrade.config.database import engine, SessionLocal, Base

# 使用会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建模型
class MyModel(Base):
    __tablename__ = "my_table"
    # ...
```

### 4. 与 vnpy 配置的集成

在 `main.py` 中，SimpleTrade 将自己的数据库配置同步到 vnpy 的全局配置中：

```python
from vnpy.trader.setting import SETTINGS
from simpletrade.config.settings import DB_CONFIG

# 设置 vnpy 数据库配置
SETTINGS["database.driver"] = "mysql"
SETTINGS["database.host"] = DB_CONFIG["DB_HOST"]
SETTINGS["database.port"] = int(DB_CONFIG["DB_PORT"])
SETTINGS["database.database"] = DB_CONFIG["DB_NAME"]
SETTINGS["database.user"] = DB_CONFIG["DB_USER"]
SETTINGS["database.password"] = DB_CONFIG["DB_PASSWORD"]
```

## 配置在 Docker 环境中的使用

在 Docker 环境中，配置通常通过环境变量传递，如 `docker-compose.yml` 中所示：

```yaml
environment:
  - PYTHONPATH=/app
  - SIMPLETRADE_DB_HOST=mysql
  - SIMPLETRADE_DB_PORT=3306
  - SIMPLETRADE_DB_USER=${SIMPLETRADE_DB_USER:-root}
  - SIMPLETRADE_DB_PASSWORD=${SIMPLETRADE_DB_PASSWORD:-Cz159csa}
  - SIMPLETRADE_DB_NAME=${SIMPLETRADE_DB_NAME:-simpletrade}
  - SIMPLETRADE_API_PORT=8003
```

这种设计使得配置可以在不同环境（开发、测试、生产）之间灵活切换，同时保持代码的一致性。

## 最佳实践

1. **使用环境变量**：尽量使用环境变量来配置应用程序，避免在代码中硬编码配置
2. **保持默认值合理**：为配置项提供合理的默认值，使应用程序在没有特定配置的情况下也能正常运行
3. **配置分组**：将相关的配置项分组，如数据库配置、API配置等
4. **配置文档化**：为配置项提供清晰的文档，说明其用途和可能的值
5. **敏感信息保护**：避免将敏感信息（如密码、密钥）直接存储在代码中，使用环境变量或配置文件来存储
