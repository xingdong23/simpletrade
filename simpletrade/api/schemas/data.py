from datetime import date
from typing import Optional
from pydantic import BaseModel

class DataRangeDetail(BaseModel):
    symbol: str
    exchange: str
    interval: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    count: int = 0
    message: Optional[str] = None # Optional message, e.g., if data is not found or partial
