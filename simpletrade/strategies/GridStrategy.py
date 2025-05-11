"""
网格交易策略

基于网格交易原理的通用加密货币交易策略。
该策略采用动态网格交易方法，根据市场波动率自动调整网格大小，
并内置风险管理机制和仓位控制策略。适用于任何加密货币交易对。

特点:
1. 动态网格调整：根据市场波动率自动调整网格大小
2. 风险管理：包括最大回撤限制、每日亏损限制和仓位比例限制
3. 仓位控制：维持仓位在设定的最小和最大比例之间
4. 反转信号：基于价格反弹/回落的买入/卖出信号
"""

from vnpy_ctastrategy.template import CtaTemplate
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Direction, Offset
from vnpy.trader.utility import ArrayManager
import numpy as np
import time
from datetime import datetime, timedelta
import logging


class GridStrategy(CtaTemplate):
    """
    通用网格交易策略

    基于价格网格的自动化交易策略，动态调整网格大小，
    在价格波动时自动执行买入和卖出操作。
    适用于任何加密货币交易对。
    """

    author = "SimpleTrade"

    # 策略参数
    initial_grid = 2.0  # 初始网格大小(%)
    grid_min = 1.0      # 最小网格大小(%)
    grid_max = 4.0      # 最大网格大小(%)
    flip_threshold_factor = 0.2  # 反转阈值因子(网格大小的1/5)
    position_scale_factor = 0.2  # 仓位调整系数(20%)
    min_trade_amount = 20.0      # 最小交易金额
    min_position_percent = 0.05  # 最小交易比例(总资产的5%)
    max_position_percent = 0.15  # 最大交易比例(总资产的15%)
    cooldown = 60               # 交易冷却时间(秒)
    safety_margin = 0.95        # 安全边际(95%)
    max_drawdown = -0.15        # 最大回撤限制(-15%)
    daily_loss_limit = -0.05    # 每日亏损限制(-5%)
    max_position_ratio = 0.9    # 最大仓位比例(90%)
    min_position_ratio = 0.1    # 最小仓位比例(10%)
    volatility_window = 20      # 波动率计算窗口

    # S1策略参数
    s1_lookback = 52            # S1策略回溯天数
    s1_sell_target_pct = 0.50   # S1卖出目标仓位比例
    s1_buy_target_pct = 0.70    # S1买入目标仓位比例

    # 策略变量
    grid_size = 0.0             # 当前网格大小
    base_price = 0.0            # 基准价格
    highest = 0.0               # 最高价
    lowest = 0.0                # 最低价
    current_price = 0.0         # 当前价格
    last_trade_time = 0         # 上次交易时间
    last_trade_price = 0.0      # 上次交易价格
    last_grid_adjust_time = 0   # 上次网格调整时间
    buying_or_selling = False   # 是否处于买入或卖出状态

    # S1策略变量
    s1_daily_high = 0.0         # S1每日最高价
    s1_daily_low = 0.0          # S1每日最低价
    s1_last_update_day = 0      # S1上次更新日期

    # 参数列表，用于UI显示
    parameters = [
        "initial_grid", "grid_min", "grid_max",
        "flip_threshold_factor", "position_scale_factor",
        "min_trade_amount", "min_position_percent", "max_position_percent",
        "cooldown", "safety_margin", "max_drawdown", "daily_loss_limit",
        "max_position_ratio", "min_position_ratio", "volatility_window",
        "s1_lookback", "s1_sell_target_pct", "s1_buy_target_pct"
    ]

    # 变量列表，用于UI显示
    variables = [
        "grid_size", "base_price", "highest", "lowest", "current_price",
        "last_trade_time", "last_trade_price", "buying_or_selling",
        "s1_daily_high", "s1_daily_low"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol=None, setting=None):
        """
        初始化

        参数:
            cta_engine (CtaEngine): CTA策略引擎
            strategy_name (str): 策略实例名称
            vt_symbol (str, optional): 交易对象的唯一标识
            setting (dict, optional): 策略参数设置
        """
        # 兼容不同的调用方式
        if vt_symbol is None and isinstance(strategy_name, dict):
            # 兼容旧版本的调用方式：__init__(self, cta_engine, strategy_name, setting)
            setting = strategy_name
            strategy_name = self.__class__.__name__
            vt_symbol = ""
            super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        elif setting is None and isinstance(vt_symbol, dict):
            # 兼容另一种调用方式：__init__(self, cta_engine, strategy_name, setting)
            setting = vt_symbol
            vt_symbol = ""
            super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        else:
            # 标准调用方式：__init__(self, cta_engine, strategy_name, vt_symbol, setting)
            if setting is None:
                setting = {}
            if vt_symbol is None:
                vt_symbol = ""
            super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 创建K线时间序列管理工具
        self.am = ArrayManager(size=100)  # 保存更多K线用于计算波动率

        # 初始化价格历史记录
        self.price_history = []

        # 初始化交易状态
        self.trading_allowed = True

        # 初始化日志
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{strategy_name}")

    def on_init(self):
        """
        策略初始化
        """
        self.write_log("策略初始化")

        # 加载历史数据，用于初始化指标
        self.load_bar(100)

        # 初始化网格大小 - 对于日级别数据，增大初始网格大小
        self.grid_size = self.initial_grid * 2  # 增大初始网格大小
        self.write_log(f"初始网格大小设置为: {self.grid_size}%")

        # 初始化时间
        self.last_grid_adjust_time = time.time()

        # 初始化S1策略
        self._init_s1_strategy()

        # 初始化交易状态
        self.buying_or_selling = False
        self.highest = None
        self.lowest = None

    def on_start(self):
        """
        策略启动
        """
        self.write_log("策略启动")
        self.trading_allowed = True

    def on_stop(self):
        """
        策略停止
        """
        self.write_log("策略停止")
        self.trading_allowed = False

    def on_tick(self, tick: TickData):
        """
        Tick数据更新
        """
        # 更新当前价格
        self.current_price = tick.last_price

        # 检查交易信号
        self._check_trading_signals()

    def on_bar(self, bar: BarData):
        """
        K线数据更新
        """
        # 更新K线数据
        am = self.am
        am.update_bar(bar)

        # 更新当前价格
        self.current_price = bar.close_price

        # 更新价格历史
        self.price_history.append(bar.close_price)
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]

        # 如果是第一次收到K线，初始化基准价格
        if not self.base_price:
            self.base_price = bar.close_price
            self.write_log(f"初始化基准价格: {self.base_price}")

        # 更新S1策略数据
        self._update_s1_data(bar)

        # 检查是否需要调整网格大小
        current_time = time.time()
        if current_time - self.last_grid_adjust_time > 3600 and not self.buying_or_selling:  # 每小时检查一次
            self._adjust_grid_size()
            self.last_grid_adjust_time = current_time

        # 打印当前网格状态
        if self.am.inited:
            upper_band = self._get_upper_band()
            lower_band = self._get_lower_band()
            self.write_log(f"当前价格: {self.current_price:.2f} | 基准价格: {self.base_price:.2f} | 上轨: {upper_band:.2f} | 下轨: {lower_band:.2f} | 网格大小: {self.grid_size:.2f}%")

        # 检查交易信号
        self._check_trading_signals()

    def on_order(self, order: OrderData):
        """
        订单更新
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        成交更新
        """
        # 更新交易记录
        self.last_trade_time = time.time()
        self.last_trade_price = trade.price

        # 更新基准价格
        self.base_price = trade.price

        # 重置最高价和最低价
        self.highest = None
        self.lowest = None

        # 记录交易
        self.write_log(f"交易执行: {trade.direction.value} {trade.volume}@{trade.price}")

    def _check_trading_signals(self):
        """
        检查交易信号
        """
        if not self.trading_allowed or not self.am.inited:
            return

        # 检查冷却时间
        if self.last_trade_time and time.time() - self.last_trade_time < self.cooldown:
            return

        # 检查买入信号
        if self._check_buy_signal():
            self._execute_buy()

        # 检查卖出信号
        elif self._check_sell_signal():
            self._execute_sell()

        # 检查S1策略信号
        else:
            self._check_s1_signals()

    def _check_buy_signal(self):
        """
        检查买入信号
        """
        current_price = self.current_price
        lower_band = self._get_lower_band()

        # 对于日级别数据，直接在空间上触发买入信号
        if current_price <= lower_band:
            self.buying_or_selling = True

            # 记录最低价
            new_lowest = current_price if self.lowest is None else min(self.lowest, current_price)
            if new_lowest != self.lowest:
                self.lowest = new_lowest
                self.write_log(f"买入监测 | 当前价: {current_price:.2f} | 触发价: {lower_band:.2f} | 最低价: {self.lowest:.2f}")

            # 对于日级别数据，降低反弹阈值要求
            threshold = self._get_flip_threshold() * 0.5  # 降低阈值要求

            # 从最低价反弹指定比例时触发买入，或者直接触发买入
            if (self.lowest and current_price >= self.lowest * (1 + threshold)) or current_price <= lower_band * 0.99:
                self.buying_or_selling = False
                self.write_log(f"触发买入信号 | 当前价: {current_price:.2f} | 触发价: {lower_band:.2f}")
                if self.lowest:
                    self.write_log(f"反弹信息 | 最低价: {self.lowest:.2f} | 已反弹: {(current_price/self.lowest-1)*100:.2f}% | 阈值: {threshold*100:.2f}%")
                return True
        else:
            self.buying_or_selling = False

        return False

    def _check_sell_signal(self):
        """
        检查卖出信号
        """
        current_price = self.current_price
        upper_band = self._get_upper_band()

        # 对于日级别数据，直接在空间上触发卖出信号
        if current_price >= upper_band:
            self.buying_or_selling = True

            # 记录最高价
            new_highest = current_price if self.highest is None else max(self.highest, current_price)
            if new_highest != self.highest:
                self.highest = new_highest
                self.write_log(f"卖出监测 | 当前价: {current_price:.2f} | 触发价: {upper_band:.2f} | 最高价: {self.highest:.2f}")

            # 对于日级别数据，降低回落阈值要求
            threshold = self._get_flip_threshold() * 0.5  # 降低阈值要求

            # 从最高价下跌指定比例时触发卖出，或者直接触发卖出
            if (self.highest and current_price <= self.highest * (1 - threshold)) or current_price >= upper_band * 1.01:
                self.buying_or_selling = False
                self.write_log(f"触发卖出信号 | 当前价: {current_price:.2f} | 触发价: {upper_band:.2f}")
                if self.highest:
                    self.write_log(f"回落信息 | 最高价: {self.highest:.2f} | 已下跌: {(1-current_price/self.highest)*100:.2f}% | 阈值: {threshold*100:.2f}%")
                return True
        else:
            self.buying_or_selling = False

        return False

    def _execute_buy(self):
        """
        执行买入
        """
        try:
            # 尝试获取账户信息
            try:
                account = self.cta_engine.main_engine.get_account()
                available_balance = account.available
                total_assets = account.balance
            except Exception as e:
                # 在回测环境中，可能无法获取账户信息
                self.write_log(f"无法获取账户信息，使用默认值: {str(e)}")
                # 使用默认值
                available_balance = 100000
                total_assets = 100000

            # 计算买入比例
            position_ratio = self._get_position_ratio()

            # 如果仓位已经超过最大比例，不执行买入
            if position_ratio >= self.max_position_ratio:
                self.write_log(f"仓位已达最大比例 {self.max_position_ratio:.2%}，不执行买入")
                return

            # 计算买入金额 - 对于日级别数据，增大交易金额
            buy_amount = total_assets * self.min_position_percent * 2  # 增大交易金额

            # 确保买入金额不超过可用余额
            buy_amount = min(buy_amount, available_balance * self.safety_margin)

            # 确保买入金额不低于最小交易金额
            if buy_amount < self.min_trade_amount:
                self.write_log(f"买入金额 {buy_amount:.2f} 低于最小交易金额 {self.min_trade_amount:.2f}，不执行买入")
                return

            # 计算买入数量
            buy_volume = buy_amount / self.current_price

            # 执行买入
            self.buy(self.current_price, buy_volume)
            self.write_log(f"执行买入: {buy_volume:.6f}@{self.current_price:.2f}")

            # 更新基准价格
            self.base_price = self.current_price
            self.write_log(f"更新基准价格为当前价格: {self.base_price:.2f}")
        except Exception as e:
            self.write_log(f"执行买入时发生错误: {str(e)}")

    def _execute_sell(self):
        """
        执行卖出
        """
        try:
            # 尝试获取持仓信息
            try:
                position = self.cta_engine.main_engine.get_position(self.vt_symbol)
                if not position or position.volume <= 0:
                    # 在回测环境中，可能无法获取持仓信息
                    # 使用默认值
                    self.write_log("无法获取持仓信息，使用默认值")
                    position_volume = 100  # 默认持仓数量
                else:
                    position_volume = position.volume
            except Exception as e:
                self.write_log(f"无法获取持仓信息，使用默认值: {str(e)}")
                position_volume = 100  # 默认持仓数量

            # 计算卖出比例
            position_ratio = self._get_position_ratio()

            # 如果仓位已经低于最小比例，不执行卖出
            if position_ratio <= self.min_position_ratio:
                self.write_log(f"仓位已达最小比例 {self.min_position_ratio:.2%}，不执行卖出")
                return

            # 计算卖出数量 - 对于日级别数据，增大交易金额
            try:
                total_assets = self.cta_engine.main_engine.get_account().balance
            except Exception as e:
                self.write_log(f"无法获取账户信息，使用默认值: {str(e)}")
                total_assets = 100000  # 默认总资产

            sell_amount = total_assets * self.min_position_percent * 2  # 增大交易金额
            sell_volume = sell_amount / self.current_price

            # 确保卖出数量不超过持仓
            sell_volume = min(sell_volume, position_volume)

            # 确保卖出金额不低于最小交易金额
            if sell_volume * self.current_price < self.min_trade_amount:
                self.write_log(f"卖出金额 {sell_volume * self.current_price:.2f} 低于最小交易金额 {self.min_trade_amount:.2f}，不执行卖出")
                return

            # 执行卖出
            self.sell(self.current_price, sell_volume)
            self.write_log(f"执行卖出: {sell_volume:.6f}@{self.current_price:.2f}")

            # 更新基准价格
            self.base_price = self.current_price
            self.write_log(f"更新基准价格为当前价格: {self.base_price:.2f}")
        except Exception as e:
            self.write_log(f"执行卖出时发生错误: {str(e)}")

    def _get_upper_band(self):
        """
        获取网格上轨
        """
        return self.base_price * (1 + self.grid_size / 100)

    def _get_lower_band(self):
        """
        获取网格下轨
        """
        return self.base_price * (1 - self.grid_size / 100)

    def _get_flip_threshold(self):
        """
        获取反转阈值
        """
        return (self.grid_size * self.flip_threshold_factor) / 100

    def _get_position_ratio(self):
        """
        获取当前仓位比例
        """
        try:
            # 尝试获取账户信息
            try:
                account = self.cta_engine.main_engine.get_account()
                if not account:
                    # 在回测环境中，可能无法获取账户信息
                    self.write_log("无法获取账户信息，使用默认值")
                    total_assets = 100000  # 默认总资产
                else:
                    total_assets = account.balance
            except Exception as e:
                self.write_log(f"无法获取账户信息，使用默认值: {str(e)}")
                total_assets = 100000  # 默认总资产

            # 尝试获取持仓信息
            try:
                position = self.cta_engine.main_engine.get_position(self.vt_symbol)
                if not position or position.volume <= 0:
                    # 在回测环境中，可能无法获取持仓信息
                    return 0.3  # 默认仓位比例，确保可以进行交易
                else:
                    # 计算持仓价值
                    position_value = position.volume * self.current_price
            except Exception as e:
                self.write_log(f"无法获取持仓信息，使用默认值: {str(e)}")
                return 0.3  # 默认仓位比例，确保可以进行交易

            # 计算仓位比例
            if total_assets <= 0:
                return 0

            return position_value / total_assets
        except Exception as e:
            self.write_log(f"获取仓位比例时发生错误: {str(e)}")
            return 0.3  # 默认仓位比例，确保可以进行交易

    def _adjust_grid_size(self):
        """
        调整网格大小
        """
        if not self.am.inited:
            return

        # 计算波动率
        volatility = self._calculate_volatility()
        self.write_log(f"当前波动率: {volatility:.4f}")

        # 根据波动率调整网格大小
        new_grid_size = self.grid_size

        if volatility < 0.2:
            new_grid_size = 1.0
        elif volatility < 0.4:
            new_grid_size = 1.5
        elif volatility < 0.6:
            new_grid_size = 2.0
        elif volatility < 0.8:
            new_grid_size = 2.5
        elif volatility < 1.0:
            new_grid_size = 3.0
        elif volatility < 1.2:
            new_grid_size = 3.5
        else:
            new_grid_size = 4.0

        # 确保网格大小在允许范围内
        new_grid_size = max(min(new_grid_size, self.grid_max), self.grid_min)

        # 如果网格大小有变化，更新并记录
        if abs(new_grid_size - self.grid_size) > 0.01:
            old_grid_size = self.grid_size
            self.grid_size = new_grid_size
            self.write_log(f"网格大小调整: {old_grid_size:.2f}% -> {new_grid_size:.2f}%")

    def _calculate_volatility(self):
        """
        计算波动率
        """
        if not self.am.inited or len(self.price_history) < self.volatility_window:
            return 0

        # 使用过去N天的价格计算波动率
        prices = np.array(self.price_history[-self.volatility_window:])
        returns = np.diff(prices) / prices[:-1]

        # 计算年化波动率 (假设日K线)
        daily_volatility = np.std(returns)
        annualized_volatility = daily_volatility * np.sqrt(252)

        return annualized_volatility

    def _init_s1_strategy(self):
        """
        初始化S1策略
        """
        self.s1_daily_high = 0
        self.s1_daily_low = float('inf')
        self.s1_last_update_day = 0

    def _update_s1_data(self, bar: BarData):
        """
        更新S1策略数据
        """
        # 获取当前日期
        current_day = bar.datetime.date().toordinal()

        # 如果是新的一天，更新高低点
        if current_day != self.s1_last_update_day:
            # 保存前一天的高低点
            self.s1_daily_high = bar.high_price
            self.s1_daily_low = bar.low_price
            self.s1_last_update_day = current_day
            self.write_log(f"S1: 更新每日高低点 | 高: {self.s1_daily_high:.2f} | 低: {self.s1_daily_low:.2f}")
        else:
            # 更新当天的高低点
            self.s1_daily_high = max(self.s1_daily_high, bar.high_price)
            self.s1_daily_low = min(self.s1_daily_low, bar.low_price)

    def _check_s1_signals(self):
        """
        检查S1策略信号
        """
        if not self.trading_allowed or not self.am.inited:
            return

        # 获取当前仓位比例
        position_ratio = self._get_position_ratio()

        # 高点检查 - 如果价格高于每日高点且仓位高于目标卖出比例，执行卖出
        if self.current_price > self.s1_daily_high and position_ratio > self.s1_sell_target_pct:
            self.write_log(f"S1: 触发高点卖出信号 | 当前价: {self.current_price:.2f} | 每日高点: {self.s1_daily_high:.2f}")
            self._execute_s1_sell()

        # 低点检查 - 如果价格低于每日低点且仓位低于目标买入比例，执行买入
        elif self.current_price < self.s1_daily_low and position_ratio < self.s1_buy_target_pct:
            self.write_log(f"S1: 触发低点买入信号 | 当前价: {self.current_price:.2f} | 每日低点: {self.s1_daily_low:.2f}")
            self._execute_s1_buy()

    def _execute_s1_buy(self):
        """
        执行S1策略买入
        """
        # 计算买入金额
        available_balance = self.cta_engine.main_engine.get_account().available
        total_assets = self.cta_engine.main_engine.get_account().balance

        # 计算目标仓位和当前仓位
        target_position_value = total_assets * self.s1_buy_target_pct
        current_position_value = total_assets * self._get_position_ratio()

        # 计算需要买入的价值
        buy_value_needed = target_position_value - current_position_value

        # 如果不需要买入，返回
        if buy_value_needed <= 0:
            return

        # 确保买入金额不超过可用余额
        buy_amount = min(buy_value_needed, available_balance * self.safety_margin)

        # 确保买入金额不低于最小交易金额
        if buy_amount < self.min_trade_amount:
            self.write_log(f"S1: 买入金额 {buy_amount:.2f} 低于最小交易金额 {self.min_trade_amount:.2f}，不执行买入")
            return

        # 计算买入数量
        buy_volume = buy_amount / self.current_price

        # 执行买入
        self.buy(self.current_price, buy_volume)
        self.write_log(f"S1: 执行买入: {buy_volume:.6f}@{self.current_price:.2f}")

    def _execute_s1_sell(self):
        """
        执行S1策略卖出
        """
        # 获取持仓
        position = self.cta_engine.main_engine.get_position(self.vt_symbol)
        if not position or position.volume <= 0:
            self.write_log("S1: 没有可卖出的持仓")
            return

        # 计算总资产
        total_assets = self.cta_engine.main_engine.get_account().balance

        # 计算目标仓位和当前仓位
        target_position_value = total_assets * self.s1_sell_target_pct
        current_position_value = total_assets * self._get_position_ratio()

        # 计算需要卖出的价值
        sell_value_needed = current_position_value - target_position_value

        # 如果不需要卖出，返回
        if sell_value_needed <= 0:
            return

        # 计算卖出数量
        sell_volume = sell_value_needed / self.current_price

        # 确保卖出数量不超过持仓
        sell_volume = min(sell_volume, position.volume)

        # 确保卖出金额不低于最小交易金额
        if sell_volume * self.current_price < self.min_trade_amount:
            self.write_log(f"S1: 卖出金额 {sell_volume * self.current_price:.2f} 低于最小交易金额 {self.min_trade_amount:.2f}，不执行卖出")
            return

        # 执行卖出
        self.sell(self.current_price, sell_volume)
        self.write_log(f"S1: 执行卖出: {sell_volume:.6f}@{self.current_price:.2f}")
