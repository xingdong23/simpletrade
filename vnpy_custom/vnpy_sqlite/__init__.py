"""
SQLite数据库接口
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple

from vnpy_custom.vnpy.trader.constant import Exchange, Interval
from vnpy_custom.vnpy.trader.object import BarData, TickData
from vnpy_custom.vnpy.trader.database import (
    BaseDatabase,
    BarOverview,
    TickOverview,
    DB_TZ,
    convert_tz
)

class Database:
    """SQLite数据库"""

    def __init__(self) -> None:
        """构造函数"""
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bar_data (
            symbol TEXT,
            exchange TEXT,
            datetime TIMESTAMP,
            interval TEXT,
            volume FLOAT,
            open_price FLOAT,
            high_price FLOAT,
            low_price FLOAT,
            close_price FLOAT,
            open_interest FLOAT,
            turnover FLOAT,
            PRIMARY KEY (symbol, exchange, interval, datetime)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tick_data (
            symbol TEXT,
            exchange TEXT,
            datetime TIMESTAMP,
            name TEXT,
            volume FLOAT,
            open_interest FLOAT,
            last_price FLOAT,
            last_volume FLOAT,
            limit_up FLOAT,
            limit_down FLOAT,
            open_price FLOAT,
            high_price FLOAT,
            low_price FLOAT,
            pre_close FLOAT,
            bid_price_1 FLOAT,
            bid_price_2 FLOAT,
            bid_price_3 FLOAT,
            bid_price_4 FLOAT,
            bid_price_5 FLOAT,
            ask_price_1 FLOAT,
            ask_price_2 FLOAT,
            ask_price_3 FLOAT,
            ask_price_4 FLOAT,
            ask_price_5 FLOAT,
            bid_volume_1 FLOAT,
            bid_volume_2 FLOAT,
            bid_volume_3 FLOAT,
            bid_volume_4 FLOAT,
            bid_volume_5 FLOAT,
            ask_volume_1 FLOAT,
            ask_volume_2 FLOAT,
            ask_volume_3 FLOAT,
            ask_volume_4 FLOAT,
            ask_volume_5 FLOAT,
            PRIMARY KEY (symbol, exchange, datetime)
        )
        """)
        
        self.connection.commit()
    
    def save_bar_data(self, bars: List[BarData]) -> bool:
        """保存K线数据"""
        if not bars:
            return False
        
        for bar in bars:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO bar_data (
                    symbol, exchange, datetime, interval, volume,
                    open_price, high_price, low_price, close_price,
                    open_interest, turnover
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    bar.symbol, bar.exchange.value, bar.datetime, bar.interval.value, bar.volume,
                    bar.open_price, bar.high_price, bar.low_price, bar.close_price,
                    bar.open_interest, bar.turnover
                )
            )
        
        self.connection.commit()
        return True
    
    def save_tick_data(self, ticks: List[TickData]) -> bool:
        """保存Tick数据"""
        if not ticks:
            return False
        
        for tick in ticks:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO tick_data (
                    symbol, exchange, datetime, name, volume,
                    open_interest, last_price, last_volume,
                    limit_up, limit_down, open_price, high_price,
                    low_price, pre_close,
                    bid_price_1, bid_price_2, bid_price_3, bid_price_4, bid_price_5,
                    ask_price_1, ask_price_2, ask_price_3, ask_price_4, ask_price_5,
                    bid_volume_1, bid_volume_2, bid_volume_3, bid_volume_4, bid_volume_5,
                    ask_volume_1, ask_volume_2, ask_volume_3, ask_volume_4, ask_volume_5
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tick.symbol, tick.exchange.value, tick.datetime, tick.name, tick.volume,
                    tick.open_interest, tick.last_price, tick.last_volume,
                    tick.limit_up, tick.limit_down, tick.open_price, tick.high_price,
                    tick.low_price, tick.pre_close,
                    tick.bid_price_1, tick.bid_price_2, tick.bid_price_3, tick.bid_price_4, tick.bid_price_5,
                    tick.ask_price_1, tick.ask_price_2, tick.ask_price_3, tick.ask_price_4, tick.ask_price_5,
                    tick.bid_volume_1, tick.bid_volume_2, tick.bid_volume_3, tick.bid_volume_4, tick.bid_volume_5,
                    tick.ask_volume_1, tick.ask_volume_2, tick.ask_volume_3, tick.ask_volume_4, tick.ask_volume_5
                )
            )
        
        self.connection.commit()
        return True
    
    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> List[BarData]:
        """读取K线数据"""
        self.cursor.execute(
            """
            SELECT * FROM bar_data
            WHERE symbol = ? AND exchange = ? AND interval = ? AND datetime >= ? AND datetime <= ?
            """,
            (symbol, exchange.value, interval.value, start, end)
        )
        
        data = self.cursor.fetchall()
        bars = []
        
        for row in data:
            bar = BarData(
                symbol=row[0],
                exchange=Exchange(row[1]),
                datetime=row[2],
                interval=Interval(row[3]),
                volume=row[4],
                open_price=row[5],
                high_price=row[6],
                low_price=row[7],
                close_price=row[8],
                open_interest=row[9],
                turnover=row[10],
                gateway_name="DB"
            )
            bars.append(bar)
        
        return bars
    
    def load_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
    ) -> List[TickData]:
        """读取Tick数据"""
        self.cursor.execute(
            """
            SELECT * FROM tick_data
            WHERE symbol = ? AND exchange = ? AND datetime >= ? AND datetime <= ?
            """,
            (symbol, exchange.value, start, end)
        )
        
        data = self.cursor.fetchall()
        ticks = []
        
        for row in data:
            tick = TickData(
                symbol=row[0],
                exchange=Exchange(row[1]),
                datetime=row[2],
                name=row[3],
                volume=row[4],
                open_interest=row[5],
                last_price=row[6],
                last_volume=row[7],
                limit_up=row[8],
                limit_down=row[9],
                open_price=row[10],
                high_price=row[11],
                low_price=row[12],
                pre_close=row[13],
                bid_price_1=row[14],
                bid_price_2=row[15],
                bid_price_3=row[16],
                bid_price_4=row[17],
                bid_price_5=row[18],
                ask_price_1=row[19],
                ask_price_2=row[20],
                ask_price_3=row[21],
                ask_price_4=row[22],
                ask_price_5=row[23],
                bid_volume_1=row[24],
                bid_volume_2=row[25],
                bid_volume_3=row[26],
                bid_volume_4=row[27],
                bid_volume_5=row[28],
                ask_volume_1=row[29],
                ask_volume_2=row[30],
                ask_volume_3=row[31],
                ask_volume_4=row[32],
                ask_volume_5=row[33],
                gateway_name="DB"
            )
            ticks.append(tick)
        
        return ticks
    
    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """删除K线数据"""
        self.cursor.execute(
            """
            DELETE FROM bar_data
            WHERE symbol = ? AND exchange = ? AND interval = ?
            """,
            (symbol, exchange.value, interval.value)
        )
        
        count = self.cursor.rowcount
        self.connection.commit()
        return count
    
    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> int:
        """删除Tick数据"""
        self.cursor.execute(
            """
            DELETE FROM tick_data
            WHERE symbol = ? AND exchange = ?
            """,
            (symbol, exchange.value)
        )
        
        count = self.cursor.rowcount
        self.connection.commit()
        return count
    
    def get_bar_data_statistics(self) -> List[Dict[str, Any]]:
        """查询K线数据统计"""
        self.cursor.execute(
            """
            SELECT 
                symbol, exchange, interval,
                COUNT(1) as count,
                MIN(datetime) as start,
                MAX(datetime) as end
            FROM bar_data
            GROUP BY symbol, exchange, interval
            """
        )
        
        data = self.cursor.fetchall()
        statistics = []
        
        for row in data:
            statistics.append({
                "symbol": row[0],
                "exchange": row[1],
                "interval": row[2],
                "count": row[3],
                "start": row[4],
                "end": row[5]
            })
        
        return statistics
    
    def get_tick_data_statistics(self) -> List[Dict[str, Any]]:
        """查询Tick数据统计"""
        self.cursor.execute(
            """
            SELECT 
                symbol, exchange,
                COUNT(1) as count,
                MIN(datetime) as start,
                MAX(datetime) as end
            FROM tick_data
            GROUP BY symbol, exchange
            """
        )
        
        data = self.cursor.fetchall()
        statistics = []
        
        for row in data:
            statistics.append({
                "symbol": row[0],
                "exchange": row[1],
                "count": row[2],
                "start": row[3],
                "end": row[4]
            })
        
        return statistics
    
    def clean(self) -> None:
        """清空数据库"""
        self.cursor.execute("DELETE FROM bar_data")
        self.cursor.execute("DELETE FROM tick_data")
        self.connection.commit()
    
    def close(self) -> None:
        """关闭数据库"""
        self.connection.close()
