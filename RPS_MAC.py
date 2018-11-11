from rqalpha.api import *
from rqalpha import  run_func
import numpy as np

import pandas as pd
import talib



"""
自定义指标：https://www.ricequant.com/api/python/chn#technical-analysis-user-defined

RPS 选股

RPS120 & RPS250 大于 90

"""


def init(context):
    context.window_120 = 120
    context.window_250 = 250
    # context.stocks = index_components('000300.XSHG')
    context.stocks = []
    context.availStocks = []
    context.window_60 = 60
    scheduler.run_monthly(getHightRPS, tradingday=1)


def handle_bar(context, bar_dict):
    positions = context.portfolio.positions
    for stock in list(context.availStocks):
        # 因为策略需要用到均线，所以需要读取历史数据
        prices = history_bars(stock, 250 + 1, '1d', 'close')
        # 计算60日移动均线
        if np.nan in prices:
            continue
        avg60 = talib.SMA(prices, context.window_60)
        # avg30 = talib.SMA(prices, 30)
        if prices[-1] >= avg60[-1] and positions[stock].quantity == 0:
            order_percent(stock, 0.1)

        #if prices[-1] < avg60[-1] and positions[stock].quantity > 0:
        #    order_shares(stock, 0)
    for security in context.portfolio.positions:
        # 全部卖出
        prices = history_bars(stock, 250, '1d', 'close')
        avg30 = talib.SMA(prices, 30)
        if prices[-1] < avg30:
            order_target_value(security, 0)



def handle_tick(context, tick):
    pass


def before_trading(context):
    # 获取沪深A股所有股票
    stocks = list(all_instruments("CS").order_book_id)
    # 获取的股票数
    logger.info(len(stocks))
    available_stocks = []
    for stock in stocks:
        # 过滤出上市时间大于一年的股票
        if not is_suspended(stock) and (not str(is_suspended(stock)) == 'None') and moreThanOneYear(stock):
            available_stocks.append(stock)
    context.stocks = available_stocks


def after_trading(context):
    pass


# 计算 RPS250, RPS120都大于 90
def getHightRPS(context, bar_dict):
    rps_120 = calRPS(context.stocks, context.window_120)
    rps_250 = calRPS(context.stocks, context.window_250)
    codes = []
    stocks = []
    RPS250 = []
    RPS120 = []

    for i in range(rps_250.shape[0]):
        if rps_250.rpsValue[i] >= 90:
            for index, stock in enumerate(list(rps_120.code)):
                if rps_250.code[i] == stock and rps_120.rpsValue[index] >= 90:
                    codes.append(stock)
                    stocks.append(instruments(stock).symbol)
                    RPS120.append(rps_120.rpsValue[index])
                    RPS250.append(rps_250.rpsValue[i])
    rpsStocks = {'code': codes, 'stock': stocks, 'RPS250': RPS250, 'RPS120': RPS120}
    rpsStocks = pd.DataFrame(rpsStocks)
    rpsStocks = rpsStocks.sort_values('RPS120', ascending=False)

    context.availStocks = codes


# 上市时间大于一年
def moreThanOneYear(stock):
    # 获取合约已上市天数
    days = instruments(stock).days_from_listed()
    return True if days > 250 else False


# 计算相对强弱RPS值
def calRPS(stocks, n):
    numStocks = len(stocks)

    rankValue = []

    # 计算涨跌幅
    for stock in stocks:
        price = history_bars(stock, n, '1d', 'close')
        firstClosePrice = price[0]
        lastClosePrice = price[-1]
        # 计算涨跌幅
        errCloseOpen = [lastClosePrice - firstClosePrice]
        rankValue += errCloseOpen

    # 计算排名
    rpsStocks = {'code': stocks, 'rankValue': rankValue}
    rpsStocks = pd.DataFrame(rpsStocks)
    rpsStocks = rpsStocks.sort_values('rankValue', ascending=False)
    stocks = list(rpsStocks['code'])

    # 计算RPS值
    rpsValue = [99 - (100 * i / numStocks) for i in range(numStocks)]
    rpsStocks = {'code': stocks, 'rpsValue': rpsValue}
    rpsStocks = pd.DataFrame(rpsStocks)

    return rpsStocks


config = {
  "base": {
    "start_date": "2017-01-01",
    "end_date": "2018-11-09",
    "benchmark": "000300.XSHG",
    "accounts": {
        "stock": 1000000
    }
  },
  "extra": {
    "log_level": "verbose",
    "locale": "zh_Hans_CN"
  },
  "mod": {
    "sys_analyser": {
      "enabled": True,
      "plot": True
    }
  }
}

# 您可以指定您要传递的参数
run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=config)
