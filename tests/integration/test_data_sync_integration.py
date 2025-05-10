"""数据同步服务集成测试模块

包含对DataSyncService的集成测试，验证其与实际组件的交互。
"""

import os
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import tempfile
import shutil
import pandas as pd

from sqlalchemy.orm import Session

from simpletrade.services.data_sync_service import DataSyncService
from simpletrade.models.database import DataImportLog
from simpletrade.config.database import SessionLocal
from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData


class TestDataSyncIntegration(unittest.TestCase):
    """数据同步服务集成测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建临时目录模拟Qlib数据目录
        cls.temp_dir = tempfile.mkdtemp()
        cls.qlib_dir = os.path.join(cls.temp_dir, "qlib_data")
        cls.cn_data_dir = os.path.join(cls.qlib_dir, "cn_data")
        cls.us_data_dir = os.path.join(cls.qlib_dir, "us_data")
        
        # 创建必要的目录结构
        os.makedirs(cls.cn_data_dir, exist_ok=True)
        os.makedirs(os.path.join(cls.cn_data_dir, "calendars"), exist_ok=True)
        os.makedirs(cls.us_data_dir, exist_ok=True)
        
        # 创建模拟的交易日历文件
        calendar_path = os.path.join(cls.cn_data_dir, "calendars", "day.txt")
        with open(calendar_path, "w") as f:
            # 写入一些交易日期
            for i in range(1, 31):
                f.write(f"2023-01-{i:02d}\n")
            for i in range(1, 29):
                f.write(f"2023-02-{i:02d}\n")
        
        # 创建模拟的股票数据目录
        cls.stock_dir = os.path.join(cls.cn_data_dir, "features", "sh600000")
        os.makedirs(cls.stock_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 删除临时目录
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """测试前准备"""
        # 设置模拟数据
        self.mock_target = {
            "source": "qlib",
            "symbol": "600000",
            "exchange": "SSE",
            "interval": "1d"
        }
        
        # 创建服务实例
        self.service = DataSyncService()
        self.service.targets = [self.mock_target]
        
        # 补丁qlib_base_dir路径
        self.qlib_base_dir_patcher = patch('simpletrade.services.data_sync_service.qlib_base_dir', 
                                         new=self.qlib_dir)
        self.qlib_base_dir_mock = self.qlib_base_dir_patcher.start()

    def tearDown(self):
        """测试后清理"""
        # 停止所有补丁
        self.qlib_base_dir_patcher.stop()
        
        # 清理数据库中的测试数据
        try:
            db = SessionLocal()
            db.query(DataImportLog).filter(
                DataImportLog.source == self.mock_target['source'],
                DataImportLog.symbol == self.mock_target['symbol'],
                DataImportLog.exchange == self.mock_target['exchange'],
                DataImportLog.interval == self.mock_target['interval']
            ).delete()
            db.commit()
        except Exception as e:
            print(f"清理数据库时出错: {e}")
        finally:
            if 'db' in locals():
                db.close()

    def _create_mock_qlib_data(self):
        """创建模拟的Qlib数据文件"""
        import struct
        
        # 创建open.day.bin文件
        open_file = os.path.join(self.stock_dir, "open.day.bin")
        with open(open_file, "wb") as f:
            # 写入起始索引（假设为0）
            f.write(struct.pack('<f', 0.0))
            # 写入一些开盘价数据
            for i in range(50):
                price = 10.0 + i * 0.1
                f.write(struct.pack('<f', price))
        
        # 创建high.day.bin文件
        high_file = os.path.join(self.stock_dir, "high.day.bin")
        with open(high_file, "wb") as f:
            f.write(struct.pack('<f', 0.0))
            for i in range(50):
                price = 11.0 + i * 0.1
                f.write(struct.pack('<f', price))
        
        # 创建low.day.bin文件
        low_file = os.path.join(self.stock_dir, "low.day.bin")
        with open(low_file, "wb") as f:
            f.write(struct.pack('<f', 0.0))
            for i in range(50):
                price = 9.0 + i * 0.1
                f.write(struct.pack('<f', price))
        
        # 创建close.day.bin文件
        close_file = os.path.join(self.stock_dir, "close.day.bin")
        with open(close_file, "wb") as f:
            f.write(struct.pack('<f', 0.0))
            for i in range(50):
                price = 10.5 + i * 0.1
                f.write(struct.pack('<f', price))
        
        # 创建volume.day.bin文件
        volume_file = os.path.join(self.stock_dir, "volume.day.bin")
        with open(volume_file, "wb") as f:
            f.write(struct.pack('<f', 0.0))
            for i in range(50):
                volume = 1000.0 + i * 100.0
                f.write(struct.pack('<f', volume))
                
        # 创建factor.day.bin文件 (用于open_interest)
        factor_file = os.path.join(self.stock_dir, "factor.day.bin")
        with open(factor_file, "wb") as f:
            f.write(struct.pack('<f', 0.0))
            for i in range(50):
                factor = 1.0
                f.write(struct.pack('<f', factor))

    @unittest.skip("需要实际数据库连接，仅在集成测试环境中运行")
    def test_end_to_end_sync(self):
        """端到端测试：完整的数据同步流程
        
        测试从Qlib数据源导入数据到数据库的完整流程。
        注意：此测试需要实际的数据库连接，因此默认被跳过。
        在集成测试环境中运行时，请移除@unittest.skip装饰器。
        """
        # 创建模拟的Qlib数据
        self._create_mock_qlib_data()
        
        # 执行同步
        self.service.sync_target(self.mock_target)
        
        # 验证数据库中的记录
        db = SessionLocal()
        try:
            log_entry = db.query(DataImportLog).filter(
                DataImportLog.source == self.mock_target['source'],
                DataImportLog.symbol == self.mock_target['symbol'],
                DataImportLog.exchange == self.mock_target['exchange'],
                DataImportLog.interval == self.mock_target['interval']
            ).first()
            
            self.assertIsNotNone(log_entry, "应该创建DataImportLog记录")
            self.assertEqual(log_entry.status, 'success', "同步状态应该是success")
            self.assertIsNotNone(log_entry.last_import_date, "应该更新last_import_date")
            
            # 可以进一步验证导入的数据是否存在于VnPy数据库中
            # 这需要查询VnPy的数据库表
        finally:
            db.close()

    def test_qlib_importer_with_mock_data(self):
        """测试QlibDataImporter与模拟数据
        
        使用模拟的Qlib数据测试QlibDataImporter的功能。
        """
        # 创建模拟的Qlib数据
        self._create_mock_qlib_data()
        
        # 创建QlibDataImporter实例
        importer = QlibDataImporter()
        
        # 使用模拟的数据目录调用import_data
        success, message, bars = importer.import_data(
            qlib_dir=self.cn_data_dir,
            symbol="sh600000",  # 注意这里使用sh600000而不是600000
            exchange=Exchange.SSE,
            interval=Interval.DAILY,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 10)
        )
        
        # 验证结果
        self.assertTrue(success, f"导入应该成功，但失败了: {message}")
        self.assertGreater(len(bars), 0, "应该导入一些数据")
        
        # 验证导入的数据格式
        for bar in bars:
            self.assertEqual(bar.symbol, "sh600000")
            self.assertEqual(bar.exchange, Exchange.SSE)
            self.assertEqual(bar.interval, Interval.DAILY)
            self.assertIsInstance(bar.datetime, datetime)
            self.assertIsInstance(bar.open_price, float)
            self.assertIsInstance(bar.high_price, float)
            self.assertIsInstance(bar.low_price, float)
            self.assertIsInstance(bar.close_price, float)
            self.assertIsInstance(bar.volume, float)


if __name__ == "__main__":
    unittest.main()