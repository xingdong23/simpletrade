"""
数据可视化模块

提供回测结果的可视化功能。
"""

import logging
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import io
import base64

logger = logging.getLogger("simpletrade.core.analysis.visualization")

def plot_equity_curve(equity_data: List[Dict[str, Any]], title: str = "资金曲线") -> str:
    """
    绘制资金曲线
    
    参数:
        equity_data (List[Dict[str, Any]]): 资金曲线数据
        title (str, optional): 图表标题
        
    返回:
        str: Base64编码的图表图像
    """
    try:
        # 转换为DataFrame
        df = pd.DataFrame(equity_data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 绘制资金曲线
        plt.plot(df.index, df["capital"], label="资金曲线", color="blue")
        
        # 绘制回撤
        if "drawdown" in df.columns:
            plt.fill_between(df.index, df["capital"], df["capital"] - df["drawdown"], 
                            color="red", alpha=0.3, label="回撤")
        
        # 设置图表属性
        plt.title(title)
        plt.xlabel("日期")
        plt.ylabel("资金")
        plt.grid(True)
        plt.legend()
        
        # 保存图表为Base64编码的图像
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"绘制资金曲线失败: {e}")
        return ""

def plot_drawdown_curve(equity_data: List[Dict[str, Any]], title: str = "回撤曲线") -> str:
    """
    绘制回撤曲线
    
    参数:
        equity_data (List[Dict[str, Any]]): 资金曲线数据
        title (str, optional): 图表标题
        
    返回:
        str: Base64编码的图表图像
    """
    try:
        # 转换为DataFrame
        df = pd.DataFrame(equity_data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 绘制回撤曲线
        if "drawdown_pct" in df.columns:
            plt.fill_between(df.index, 0, -df["drawdown_pct"] * 100, 
                            color="red", alpha=0.5, label="回撤百分比")
        elif "drawdown" in df.columns:
            # 计算回撤百分比
            drawdown_pct = df["drawdown"] / df["capital"].max() * 100
            plt.fill_between(df.index, 0, -drawdown_pct, 
                            color="red", alpha=0.5, label="回撤百分比")
        
        # 设置图表属性
        plt.title(title)
        plt.xlabel("日期")
        plt.ylabel("回撤百分比 (%)")
        plt.grid(True)
        plt.legend()
        
        # 保存图表为Base64编码的图像
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"绘制回撤曲线失败: {e}")
        return ""

def plot_trade_distribution(trades: List[Dict[str, Any]], title: str = "交易分布") -> str:
    """
    绘制交易分布
    
    参数:
        trades (List[Dict[str, Any]]): 交易记录
        title (str, optional): 图表标题
        
    返回:
        str: Base64编码的图表图像
    """
    try:
        # 转换为DataFrame
        df = pd.DataFrame(trades)
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 计算盈亏
        if "profit" in df.columns:
            # 绘制盈亏分布
            plt.hist(df["profit"], bins=20, alpha=0.7, color="blue", label="盈亏分布")
            
            # 绘制盈利和亏损的分布
            profit_trades = df[df["profit"] > 0]["profit"]
            loss_trades = df[df["profit"] < 0]["profit"]
            
            if not profit_trades.empty:
                plt.hist(profit_trades, bins=10, alpha=0.5, color="green", label="盈利交易")
            
            if not loss_trades.empty:
                plt.hist(loss_trades, bins=10, alpha=0.5, color="red", label="亏损交易")
        
        # 设置图表属性
        plt.title(title)
        plt.xlabel("盈亏")
        plt.ylabel("交易次数")
        plt.grid(True)
        plt.legend()
        
        # 保存图表为Base64编码的图像
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"绘制交易分布失败: {e}")
        return ""

def plot_monthly_returns(equity_data: List[Dict[str, Any]], title: str = "月度收益率") -> str:
    """
    绘制月度收益率
    
    参数:
        equity_data (List[Dict[str, Any]]): 资金曲线数据
        title (str, optional): 图表标题
        
    返回:
        str: Base64编码的图表图像
    """
    try:
        # 转换为DataFrame
        df = pd.DataFrame(equity_data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        
        # 计算月度收益率
        monthly_returns = df["capital"].resample("M").last().pct_change() * 100
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 绘制月度收益率
        colors = ["green" if x > 0 else "red" for x in monthly_returns]
        monthly_returns.plot(kind="bar", color=colors)
        
        # 设置图表属性
        plt.title(title)
        plt.xlabel("月份")
        plt.ylabel("收益率 (%)")
        plt.grid(True)
        
        # 保存图表为Base64编码的图像
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"绘制月度收益率失败: {e}")
        return ""

def generate_backtest_report(backtest_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成回测报告
    
    参数:
        backtest_result (Dict[str, Any]): 回测结果
        
    返回:
        Dict[str, Any]: 回测报告，包含图表和统计数据
    """
    try:
        # 提取数据
        summary = backtest_result.get("summary", {})
        trades = backtest_result.get("trades", [])
        equity_curve = backtest_result.get("equity_curve", [])
        
        # 生成图表
        equity_curve_chart = plot_equity_curve(equity_curve)
        drawdown_curve_chart = plot_drawdown_curve(equity_curve)
        trade_distribution_chart = plot_trade_distribution(trades)
        monthly_returns_chart = plot_monthly_returns(equity_curve)
        
        # 构建报告
        report = {
            "summary": summary,
            "charts": {
                "equity_curve": equity_curve_chart,
                "drawdown_curve": drawdown_curve_chart,
                "trade_distribution": trade_distribution_chart,
                "monthly_returns": monthly_returns_chart
            }
        }
        
        return report
    except Exception as e:
        logger.error(f"生成回测报告失败: {e}")
        return {
            "summary": {},
            "charts": {}
        }
