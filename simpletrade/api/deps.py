from simpletrade.config.database import SessionLocal # Need SessionLocal

def get_db():
    """FastAPI 依赖项：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add other dependencies here later if needed
# e.g., def get_current_user(...) 