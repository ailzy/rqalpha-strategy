from rqalpha.api import *
from rqalpha import  run_func
import numpy as np
import pandas as pd

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


def handle_bar(context, bar_dict):
    result = task(context)
    logger.info(result)


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
def task(context):
    rps_120 = calRPS(context.stocks, context.window_120)
    rps_250 = calRPS(context.stocks, context.window_250)
    stocks = []
    RPS250 = []
    RPS120 = []

    for i in range(rps_250.shape[0]):
        if rps_250.rpsValue[i] >= 90:
            for index, stock in enumerate(list(rps_120.code)):
                if rps_250.code[i] == stock and rps_120.rpsValue[index] >= 90:
                    stocks.append(instruments(stock).symbol)
                    RPS120.append(rps_120.rpsValue[index])
                    RPS250.append(rps_250.rpsValue[i])
    rpsStocks = {'stock': stocks, 'RPS250': RPS250, 'RPS120': RPS120}
    rpsStocks = pd.DataFrame(rpsStocks)
    rpsStocks = rpsStocks.sort_values('RPS120', ascending=False)
    return rpsStocks


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
    "start_date": "2018-11-09",
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
