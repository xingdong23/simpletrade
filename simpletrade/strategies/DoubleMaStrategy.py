"""
移动平均线策略

基于双均线的交易策略，当快速均线上穿慢速均线时做多，下穿时做空。
"""

# from vnpy.app.cta_strategy.template import CtaTemplate
from vnpy_ctastrategy.template import CtaTemplate
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval, Direction
from vnpy.trader.utility import ArrayManager


class DoubleMaStrategy(CtaTemplate):
    """
    移动平均线策略
    
    当快速均线上穿慢速均线时做多，下穿时做空。
    """
    
    author = "SimpleTrade"
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    # 策略变量
    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0
    
    # 参数列表，用于UI显示
    parameters = ["fast_window", "slow_window"]
    
    # 变量列表，用于UI显示
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]
    
    def __init__(self, cta_engine, strategy_name, setting):
        """
        初始化
        
        参数:
            cta_engine (CtaEngine): CTA策略引擎
            strategy_name (str): 策略实例名称
            setting (dict): 策略参数设置
        """
        super().__init__(cta_engine, strategy_name, setting)
        
        # 创建K线时间序列管理工具
        self.am = ArrayManager()
    
    def on_init(self):
        """
        策略初始化
        """
        self.write_log("策略初始化")
        
        # 加载历史数据，用于初始化指标
        self.load_bar(10)
    
    def on_start(self):
        """
        策略启动
        """
        self.write_log("策略启动")
    
    def on_stop(self):
        """
        策略停止
        """
        self.write_log("策略停止")
    
    def on_tick(self, tick):
        """
        Tick更新
        """
        self.bg.update_tick(tick)
    
    def on_bar(self, bar):
        """
        K线更新
        """
        am = self.am
        am.update_bar(bar)
        
        # 更新指标
        if not am.inited:
            return
        
        # 计算快速均线
        self.fast_ma1 = self.fast_ma0
        self.fast_ma0 = am.sma(self.fast_window)
        
        # 计算慢速均线
        self.slow_ma1 = self.slow_ma0
        self.slow_ma0 = am.sma(self.slow_window)
        
        # 判断是否完成了指标初始化
        if not self.fast_ma1 or not self.slow_ma1:
            return
        
        # 当前持仓
        pos = self.pos
        
        # 金叉做多
        if self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1:
            # 如果当前持空仓，先平仓
            if pos < 0:
                self.cover(bar.close_price, abs(pos))
            # 做多
            self.buy(bar.close_price, 1)
        
        # 死叉做空
        elif self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1:
            # 如果当前持多仓，先平仓
            if pos > 0:
                self.sell(bar.close_price, abs(pos))
            # 做空
            self.short(bar.close_price, 1)
